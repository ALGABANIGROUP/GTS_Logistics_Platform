from __future__ import annotations

import hashlib
import math
from datetime import datetime, timedelta
from typing import Any, Dict, Iterable, List, Optional, Sequence

from fastapi import HTTPException, status
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.models.dispatch_models import ShipmentAssignment, ShipmentLocation
from backend.models.models import Shipment
from backend.models.shipment_events import ShipmentEvent


class DispatchService:
    COLUMN_ORDER = ["Unassigned", "Assigned", "In Transit", "Delivered", "Cancelled"]
    TRAFFIC_MULTIPLIERS = {
        "low": 1.0,
        "normal": 1.15,
        "high": 1.4,
        "severe": 1.8,
    }

    def __init__(self, db: AsyncSession):
        self.db = db

    async def assign_shipment(
        self,
        *,
        shipment_id: int,
        driver_user_id: int,
        dispatcher_user_id: int,
        notes: Optional[str] = None,
        eta: Optional[datetime] = None,
    ) -> ShipmentAssignment:
        shipment = await self._get_shipment(shipment_id)
        if shipment.status in {"Delivered", "Cancelled"}:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"code": "INVALID_STATUS", "message": "Cannot assign a completed shipment."},
            )

        await self._deactivate_existing_assignments(shipment_id)

        assignment = ShipmentAssignment(
            shipment_id=shipment_id,
            driver_user_id=driver_user_id,
            dispatcher_user_id=dispatcher_user_id,
            notes=notes,
            eta=eta,
            status="active",
            is_active=True,
        )
        shipment.status = "Assigned"
        self.db.add(assignment)
        self.db.add(shipment)
        await self.db.flush()
        await self._create_event(
            shipment_id=shipment_id,
            event_type="assigned",
            payload={
                "driver_user_id": driver_user_id,
                "dispatcher_user_id": dispatcher_user_id,
                "notes": notes,
                "eta": eta.isoformat() if eta else None,
            },
            actor_user_id=dispatcher_user_id,
        )
        await self.db.commit()
        return assignment

    async def get_dispatch_board(
        self,
        *,
        status_filter: Optional[str] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 200,
    ) -> Dict[str, List[Dict[str, Any]]]:
        query = select(Shipment).order_by(Shipment.created_at.desc()).offset(skip).limit(limit)
        if status_filter:
            statuses = self._map_column_to_statuses(status_filter)
            if statuses:
                query = query.where(Shipment.status.in_(statuses))
        if search:
            pattern = f"%{search}%"
            query = query.where(
                (Shipment.pickup_location.ilike(pattern))
                | (Shipment.dropoff_location.ilike(pattern))
                | (Shipment.description.ilike(pattern))
            )
        result = await self.db.execute(query)
        shipments = result.scalars().unique().all()

        shipment_ids = [sh.id for sh in shipments]
        assignments = await self._load_assignments(shipment_ids)
        locations = await self._load_last_locations(shipment_ids)

        columns: Dict[str, List[Dict[str, Any]]] = {col: [] for col in self.COLUMN_ORDER}

        for shipment in shipments:
            column = self._status_to_column(shipment.status)
            payload = {
                "id": shipment.id,
                "pickup_location": shipment.pickup_location,
                "dropoff_location": shipment.dropoff_location,
                "status": shipment.status,
                "updated_at": shipment.updated_at,
                "driver": assignments.get(shipment.id),
                "last_location": locations.get(shipment.id),
            }
            columns.setdefault(column, []).append(payload)

        return columns

    async def get_driver_shipments(self, *, driver_user_id: int) -> List[Dict[str, Any]]:
        assignment_alias = ShipmentAssignment
        stmt = (
            select(Shipment, assignment_alias)
            .join(
                assignment_alias,
                and_(
                    assignment_alias.shipment_id == Shipment.id,
                    assignment_alias.driver_user_id == driver_user_id,
                    assignment_alias.is_active.is_(True),
                ),
            )
            .order_by(Shipment.created_at.desc())
        )
        result = await self.db.execute(stmt)
        rows = result.all()

        location_map = await self._load_last_locations([row.Shipment.id for row in rows])
        response = []
        for shipment, assignment in rows:
            response.append(
                {
                    "id": shipment.id,
                    "pickup_location": shipment.pickup_location,
                    "dropoff_location": shipment.dropoff_location,
                    "status": shipment.status,
                    "notes": assignment.notes,
                    "eta": assignment.eta,
                    "last_location": location_map.get(shipment.id),
                }
            )
        return response

    async def get_route_plan(self, *, shipment_id: int) -> Dict[str, Any]:
        shipment = await self._get_shipment(shipment_id)
        assignment = await self._load_assignments([shipment_id])
        location_map = await self._load_last_locations([shipment_id])

        origin = self._coordinate_from_label(shipment.pickup_location)
        destination = self._coordinate_from_label(shipment.dropoff_location)
        current_location = location_map.get(shipment_id)
        start_point = (
            current_location["lat"],
            current_location["lng"],
        ) if current_location else origin

        traffic_level = self._infer_traffic_level(shipment.status, current_location)
        distance_km = self._haversine_km(start_point, destination)
        duration_minutes = self._estimate_duration_minutes(distance_km, traffic_level)
        fuel_cost = round(distance_km * 0.42, 2)

        return {
            "shipment_id": shipment.id,
            "status": shipment.status,
            "traffic_level": traffic_level,
            "origin": {"label": shipment.pickup_location, "lat": origin[0], "lng": origin[1]},
            "destination": {"label": shipment.dropoff_location, "lat": destination[0], "lng": destination[1]},
            "current_location": current_location,
            "driver": assignment.get(shipment_id),
            "route": {
                "distance_km": round(distance_km, 2),
                "duration_minutes": duration_minutes,
                "estimated_fuel_cost_usd": fuel_cost,
                "estimated_arrival": self._estimate_arrival_iso(duration_minutes),
            },
            "alternatives": [
                {
                    "type": "fastest",
                    "distance_km": round(distance_km * 0.96, 2),
                    "duration_minutes": max(10, int(duration_minutes * 0.88)),
                    "description": "Fastest route with higher traffic exposure.",
                },
                {
                    "type": "balanced",
                    "distance_km": round(distance_km, 2),
                    "duration_minutes": duration_minutes,
                    "description": "Balanced route for ETA and fuel efficiency.",
                },
                {
                    "type": "fuel_saver",
                    "distance_km": round(distance_km * 1.08, 2),
                    "duration_minutes": int(duration_minutes * 1.12),
                    "description": "Lower fuel burn profile with a slightly longer ETA.",
                },
            ],
        }

    async def get_driver_guidance(
        self,
        *,
        shipment_id: int,
        driver_user_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        shipment = await self._get_shipment(shipment_id)
        assignments = await self._load_assignments([shipment_id])
        assignment = assignments.get(shipment_id)
        resolved_driver_id = driver_user_id or (assignment or {}).get("driver_user_id")
        if resolved_driver_id is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "NO_DRIVER", "message": "Shipment is not currently assigned to a driver."},
            )

        locations = await self._load_last_locations([shipment_id])
        route_plan = await self.get_route_plan(shipment_id=shipment_id)
        current_location = locations.get(shipment_id)
        current_speed = (current_location or {}).get("speed") or 0
        alerts: List[Dict[str, Any]] = []

        if current_speed and current_speed > 95:
            alerts.append({
                "type": "speeding_risk",
                "severity": "high",
                "message": "Reduce speed and confirm road conditions with dispatch.",
            })
        elif current_speed and current_speed > 80:
            alerts.append({
                "type": "speed_watch",
                "severity": "medium",
                "message": "Speed is elevated. Stay within the route safety threshold.",
            })

        if current_location and self._is_location_stale(current_location.get("recorded_at")):
            alerts.append({
                "type": "telemetry_stale",
                "severity": "medium",
                "message": "Driver location has not updated recently. Request a fresh location ping.",
            })

        guidance = {
            "shipment_id": shipment_id,
            "driver_user_id": resolved_driver_id,
            "next_action": "Proceed to destination" if shipment.status == "on_the_way" else "Confirm pickup and depart",
            "driver_message": self._build_driver_message(shipment.status, route_plan["route"]["duration_minutes"]),
            "alerts": alerts,
            "rest_recommendation": self._rest_recommendation(current_speed, route_plan["route"]["duration_minutes"]),
            "route": route_plan,
        }
        return guidance

    async def get_dispatch_alerts(self) -> Dict[str, Any]:
        board = await self.get_dispatch_board(limit=500)
        shipments_stmt = select(Shipment.id, Shipment.status, Shipment.pickup_location, Shipment.dropoff_location, Shipment.updated_at)
        shipment_rows = (await self.db.execute(shipments_stmt)).all()
        all_locations = await self._load_last_locations([row.id for row in shipment_rows])

        alerts: List[Dict[str, Any]] = []
        queue_size = len(board.get("Unassigned", []))
        if queue_size >= 5:
            alerts.append({
                "type": "assignment_backlog",
                "severity": "high" if queue_size >= 10 else "medium",
                "message": f"{queue_size} shipments are still waiting for assignment.",
            })

        for row in shipment_rows:
            location = all_locations.get(row.id)
            if row.status == "on_the_way" and (location is None or self._is_location_stale(location.get("recorded_at"), minutes=90)):
                alerts.append({
                    "type": "stale_tracking",
                    "severity": "medium",
                    "shipment_id": row.id,
                    "message": f"Shipment #{row.id} has stale driver telemetry.",
                })

        delivered = sum(1 for row in shipment_rows if row.status == "Delivered")
        total = len(shipment_rows)
        success_rate = (delivered / total) * 100 if total else 100
        if success_rate < 70:
            alerts.append({
                "type": "delivery_performance",
                "severity": "medium",
                "message": f"Delivery completion rate is {success_rate:.1f}%, below the desired operating threshold.",
            })

        return {
            "summary": {
                "active_alerts": len(alerts),
                "dispatch_queue": queue_size,
                "delivery_success_rate": round(success_rate, 1),
            },
            "alerts": alerts[:20],
        }

    async def get_maintenance_overview(self) -> Dict[str, Any]:
        stmt = (
            select(
                ShipmentAssignment.driver_user_id,
                func.count(ShipmentAssignment.id).label("active_assignments"),
                func.max(ShipmentLocation.speed).label("max_speed"),
                func.max(ShipmentLocation.recorded_at).label("last_ping"),
            )
            .select_from(ShipmentAssignment)
            .join(Shipment, Shipment.id == ShipmentAssignment.shipment_id)
            .outerjoin(ShipmentLocation, ShipmentLocation.shipment_id == Shipment.id)
            .where(ShipmentAssignment.is_active.is_(True))
            .group_by(ShipmentAssignment.driver_user_id)
        )
        rows = (await self.db.execute(stmt)).all()

        risks = []
        for row in rows:
            score = min(100, (row.active_assignments or 0) * 18 + min(35, int((row.max_speed or 0) / 3)))
            if row.last_ping and self._is_location_stale(row.last_ping, minutes=180):
                score = min(100, score + 20)
            health = "healthy" if score < 35 else "watch" if score < 65 else "critical"
            risks.append({
                "driver_user_id": row.driver_user_id,
                "risk_score": score,
                "health": health,
                "signals": {
                    "active_assignments": row.active_assignments or 0,
                    "max_speed_kmh": round(row.max_speed or 0, 1),
                    "last_ping_at": row.last_ping.isoformat() if row.last_ping else None,
                },
                "recommendation": self._maintenance_recommendation(score),
            })

        risks.sort(key=lambda item: item["risk_score"], reverse=True)
        return {
            "summary": {
                "tracked_drivers": len(risks),
                "critical": sum(1 for item in risks if item["health"] == "critical"),
                "watch": sum(1 for item in risks if item["health"] == "watch"),
                "healthy": sum(1 for item in risks if item["health"] == "healthy"),
            },
            "drivers": risks[:20],
        }

    async def record_checkpoint(
        self, *, shipment_id: int, driver_user_id: int, checkpoint: str, note: Optional[str] = None
    ) -> None:
        if checkpoint not in {
            "arrived_pickup",
            "loaded",
            "departed_pickup",
            "arrived_dropoff",
            "delivered",
        }:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "INVALID_CHECKPOINT", "message": "Unsupported checkpoint type."},
            )

        shipment = await self._get_shipment(shipment_id)
        assignment = await self._fetch_active_assignment(shipment_id, driver_user_id)
        if assignment is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"code": "NOT_ASSIGNED", "message": "Shipment is not assigned to this driver."},
            )

        milestone = f"checkpoint_{checkpoint}"
        new_status = self._status_from_checkpoint(checkpoint, shipment.status)
        if new_status:
            shipment.status = new_status
            self.db.add(shipment)

        await self._create_event(
            shipment_id=shipment_id,
            event_type=milestone,
            payload={"checkpoint": checkpoint, "note": note, "driver_user_id": driver_user_id},
            actor_user_id=driver_user_id,
        )

        await self.db.commit()

    async def record_location_ping(
        self,
        *,
        shipment_id: int,
        driver_user_id: int,
        lat: float,
        lng: float,
        accuracy: Optional[float] = None,
        speed: Optional[float] = None,
        heading: Optional[float] = None,
    ) -> None:
        await self._get_shipment(shipment_id)
        await self._fetch_active_assignment(shipment_id, driver_user_id)

        location = ShipmentLocation(
            shipment_id=shipment_id,
            driver_user_id=driver_user_id,
            lat=lat,
            lng=lng,
            accuracy=accuracy,
            speed=speed,
            heading=heading,
        )
        self.db.add(location)
        await self.db.flush()

        await self._create_event(
            shipment_id=shipment_id,
            event_type="location_ping",
            payload={
                "lat": lat,
                "lng": lng,
                "accuracy": accuracy,
                "speed": speed,
                "heading": heading,
            },
            actor_user_id=driver_user_id,
        )

        await self.db.commit()

    async def _get_shipment(self, shipment_id: int) -> Shipment:
        result = await self.db.execute(select(Shipment).where(Shipment.id == shipment_id))
        shipment = result.scalar_one_or_none()
        if shipment is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shipment not found.")
        return shipment

    async def _deactivate_existing_assignments(self, shipment_id: int) -> None:
        await self.db.execute(
            ShipmentAssignment.__table__
            .update()
            .where(ShipmentAssignment.shipment_id == shipment_id)
            .values(is_active=False, status="inactive")
        )

    async def _fetch_active_assignment(self, shipment_id: int, driver_user_id: int) -> Optional[ShipmentAssignment]:
        stmt = (
            select(ShipmentAssignment)
            .where(
                ShipmentAssignment.shipment_id == shipment_id,
                ShipmentAssignment.driver_user_id == driver_user_id,
                ShipmentAssignment.is_active.is_(True),
            )
            .limit(1)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def _load_assignments(self, shipment_ids: Sequence[int]) -> Dict[int, Dict[str, Any]]:
        if not shipment_ids:
            return {}
        stmt = (
            select(ShipmentAssignment)
            .where(ShipmentAssignment.shipment_id.in_(shipment_ids), ShipmentAssignment.is_active.is_(True))
            .order_by(ShipmentAssignment.created_at.desc())
        )
        rows = (await self.db.execute(stmt)).scalars().all()
        payload: Dict[int, Dict[str, Any]] = {}
        for assignment in rows:
            if assignment.shipment_id not in payload:
                payload[assignment.shipment_id] = {
                    "driver_user_id": assignment.driver_user_id,
                    "notes": assignment.notes,
                    "eta": assignment.eta,
                    "assigned_at": assignment.created_at,
                }
        return payload

    async def _load_last_locations(self, shipment_ids: Sequence[int]) -> Dict[int, Dict[str, Any]]:
        if not shipment_ids:
            return {}
        stmt = (
            select(ShipmentLocation)
            .where(ShipmentLocation.shipment_id.in_(shipment_ids))
            .order_by(ShipmentLocation.shipment_id, ShipmentLocation.recorded_at.desc())
        )
        result = await self.db.execute(stmt)
        payload: Dict[int, Dict[str, Any]] = {}
        for location in result.scalars().all():
            if location.shipment_id in payload:
                continue
            payload[location.shipment_id] = {
                "lat": location.lat,
                "lng": location.lng,
                "accuracy": location.accuracy,
                "speed": location.speed,
                "recorded_at": location.recorded_at,
            }
        return payload

    async def _create_event(
        self,
        *,
        shipment_id: int,
        event_type: str,
        payload: Optional[Dict[str, Any]] = None,
        actor_user_id: Optional[int] = None,
    ) -> ShipmentEvent:
        event = ShipmentEvent(
            shipment_id=shipment_id,
            event_type=event_type,
            payload=payload or {},
            actor_user_id=actor_user_id,
        )
        self.db.add(event)
        return event

    @staticmethod
    def _status_to_column(status: Optional[str]) -> str:
        if status in {"Assigned"}:
            return "Assigned"
        if status == "on_the_way":
            return "In Transit"
        if status == "Delivered":
            return "Delivered"
        if status == "Cancelled":
            return "Cancelled"
        return "Unassigned"

    @staticmethod
    def _map_column_to_statuses(column: str) -> List[str]:
        mapping = {
            "Unassigned": ["Draft", "Pending"],
            "Assigned": ["Assigned"],
            "In Transit": ["on_the_way"],
            "Delivered": ["Delivered"],
            "Cancelled": ["Cancelled"],
        }
        return mapping.get(column, [])

    @staticmethod
    def _status_from_checkpoint(checkpoint: str, current_status: Optional[str]) -> Optional[str]:
        mapping = {
            "departed_pickup": "on_the_way",
            "delivered": "Delivered",
        }
        return mapping.get(checkpoint)

    @staticmethod
    def _coordinate_from_label(label: Optional[str]) -> tuple[float, float]:
        text = (label or "unknown").strip().lower()
        digest = hashlib.md5(text.encode("utf-8")).hexdigest()
        lat_seed = int(digest[:8], 16)
        lng_seed = int(digest[8:16], 16)
        lat = 25 + (lat_seed % 2400) / 100
        lng = -124 + (lng_seed % 5700) / 100
        return lat, lng

    @staticmethod
    def _haversine_km(start: tuple[float, float], end: tuple[float, float]) -> float:
        lat1, lon1 = map(math.radians, start)
        lat2, lon2 = map(math.radians, end)
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return 6371 * c

    def _estimate_duration_minutes(self, distance_km: float, traffic_level: str) -> int:
        base_speed = 72
        multiplier = self.TRAFFIC_MULTIPLIERS.get(traffic_level, self.TRAFFIC_MULTIPLIERS["normal"])
        return max(15, int((distance_km / base_speed) * 60 * multiplier))

    @staticmethod
    def _estimate_arrival_iso(duration_minutes: int) -> str:
        return (datetime.utcnow() + timedelta(minutes=duration_minutes)).replace(microsecond=0).isoformat() + "Z"

    @staticmethod
    def _is_location_stale(recorded_at: Optional[datetime], minutes: int = 45) -> bool:
        if recorded_at is None:
            return True
        now = datetime.utcnow().replace(tzinfo=recorded_at.tzinfo)
        return (now - recorded_at).total_seconds() > minutes * 60

    @staticmethod
    def _infer_traffic_level(status: Optional[str], current_location: Optional[Dict[str, Any]]) -> str:
        speed = (current_location or {}).get("speed") or 0
        if status == "Assigned":
            return "normal"
        if speed and speed < 15:
            return "severe"
        if speed and speed < 35:
            return "high"
        if speed and speed > 75:
            return "low"
        return "normal"

    @staticmethod
    def _build_driver_message(status: Optional[str], duration_minutes: int) -> str:
        if status == "Assigned":
            return f"Proceed to pickup. Estimated arrival to the pickup window is {duration_minutes} minutes."
        if status == "on_the_way":
            return f"Stay on the active route and expect approximately {duration_minutes} minutes to destination."
        return "Review the next checkpoint and confirm shipment state with dispatch."

    @staticmethod
    def _rest_recommendation(current_speed: float, duration_minutes: int) -> Dict[str, Any]:
        if duration_minutes >= 240:
            return {
                "required": True,
                "message": "Schedule a rest stop within the next 90 minutes.",
            }
        if current_speed and current_speed > 85:
            return {
                "required": False,
                "message": "Monitor fatigue and keep a moderate cruising speed.",
            }
        return {
            "required": False,
            "message": "No immediate rest stop required.",
        }

    @staticmethod
    def _maintenance_recommendation(score: int) -> str:
        if score >= 65:
            return "Inspect the assigned vehicle before the next dispatch cycle."
        if score >= 35:
            return "Schedule a preventive check during the next idle window."
        return "No immediate maintenance action required."
