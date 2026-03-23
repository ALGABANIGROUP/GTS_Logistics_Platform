from __future__ import annotations

import asyncio
import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.config import get_db_async
from backend.routes.fleet_management_routes import _ensure_schema as _ensure_fleet_schema
from backend.security.auth import require_roles

router = APIRouter(
    prefix="/api/v1/fleet/live",
    tags=["Fleet Live Tracking"],
    dependencies=[Depends(require_roles(["admin", "owner", "super_admin"]))],
)

_live_schema_ready = False
_live_schema_lock = asyncio.Lock()

LIVE_SCHEMA_SQL = [
    """
    CREATE TABLE IF NOT EXISTS fleet_vehicle_locations (
        vehicle_id INTEGER PRIMARY KEY REFERENCES fleet_vehicles(id) ON DELETE CASCADE,
        lat NUMERIC(10, 7) NOT NULL,
        lng NUMERIC(10, 7) NOT NULL,
        speed NUMERIC(8, 2) NOT NULL DEFAULT 0,
        heading INTEGER NOT NULL DEFAULT 0,
        accuracy NUMERIC(8, 2) NOT NULL DEFAULT 0,
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS fleet_driver_locations (
        driver_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
        lat NUMERIC(10, 7) NOT NULL,
        lng NUMERIC(10, 7) NOT NULL,
        speed NUMERIC(8, 2) NOT NULL DEFAULT 0,
        heading INTEGER NOT NULL DEFAULT 0,
        status VARCHAR(20) NOT NULL DEFAULT 'offline',
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS fleet_location_history (
        id SERIAL PRIMARY KEY,
        entity_type VARCHAR(20) NOT NULL,
        entity_id INTEGER NOT NULL,
        lat NUMERIC(10, 7) NOT NULL,
        lng NUMERIC(10, 7) NOT NULL,
        recorded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    )
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_fleet_location_history_entity
    ON fleet_location_history (entity_type, entity_id, recorded_at DESC)
    """,
    """
    CREATE TABLE IF NOT EXISTS fleet_live_alerts (
        id SERIAL PRIMARY KEY,
        alert_type VARCHAR(30) NOT NULL,
        entity_type VARCHAR(20) NOT NULL,
        entity_id INTEGER NOT NULL,
        message TEXT,
        severity VARCHAR(20) NOT NULL DEFAULT 'medium',
        lat NUMERIC(10, 7),
        lng NUMERIC(10, 7),
        metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
        is_resolved BOOLEAN NOT NULL DEFAULT FALSE,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        resolved_at TIMESTAMPTZ
    )
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_fleet_live_alerts_open
    ON fleet_live_alerts (is_resolved, created_at DESC)
    """,
]


class VehicleLocationUpdate(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)
    speed: float = Field(default=0, ge=0, le=300)
    heading: int = Field(default=0, ge=0, le=360)
    accuracy: float = Field(default=0, ge=0, le=10000)


class DriverLocationUpdate(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)
    speed: float = Field(default=0, ge=0, le=300)
    heading: int = Field(default=0, ge=0, le=360)
    status: str = Field(default="busy")


class FleetLiveSocketHub:
    def __init__(self) -> None:
        self._connections: set[WebSocket] = set()
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        async with self._lock:
            self._connections.add(websocket)

    async def disconnect(self, websocket: WebSocket) -> None:
        async with self._lock:
            self._connections.discard(websocket)

    async def broadcast(self, payload: Dict[str, Any]) -> None:
        dead: list[WebSocket] = []
        async with self._lock:
            connections = list(self._connections)
        for websocket in connections:
            try:
                await websocket.send_json(payload)
            except Exception:
                dead.append(websocket)
        if dead:
            async with self._lock:
                for websocket in dead:
                    self._connections.discard(websocket)


socket_hub = FleetLiveSocketHub()


def _mapping_rows(result: Any) -> List[Dict[str, Any]]:
    return [dict(row) for row in result.mappings().all()]


async def _ensure_live_schema(db: AsyncSession) -> None:
    global _live_schema_ready
    await _ensure_fleet_schema(db)
    if _live_schema_ready:
        return
    async with _live_schema_lock:
        if _live_schema_ready:
            return
        for statement in LIVE_SCHEMA_SQL:
            await db.execute(text(statement))
        await db.commit()
        _live_schema_ready = True


async def _record_history(db: AsyncSession, entity_type: str, entity_id: int, lat: float, lng: float) -> None:
    recent = await db.execute(
        text(
            """
            SELECT recorded_at
            FROM fleet_location_history
            WHERE entity_type = :entity_type AND entity_id = :entity_id
            ORDER BY recorded_at DESC
            LIMIT 1
            """
        ),
        {"entity_type": entity_type, "entity_id": entity_id},
    )
    row = recent.mappings().first()
    if row and row["recorded_at"]:
        delta = datetime.utcnow() - row["recorded_at"].replace(tzinfo=None)
        if delta.total_seconds() < 300:
            return

    await db.execute(
        text(
            """
            INSERT INTO fleet_location_history (entity_type, entity_id, lat, lng, recorded_at)
            VALUES (:entity_type, :entity_id, :lat, :lng, NOW())
            """
        ),
        {"entity_type": entity_type, "entity_id": entity_id, "lat": lat, "lng": lng},
    )


async def _create_alert(
    db: AsyncSession,
    *,
    alert_type: str,
    entity_type: str,
    entity_id: int,
    severity: str,
    message: str,
    lat: float,
    lng: float,
    metadata: Optional[Dict[str, Any]] = None,
) -> Optional[Dict[str, Any]]:
    existing = await db.execute(
        text(
            """
            SELECT id
            FROM fleet_live_alerts
            WHERE alert_type = :alert_type
              AND entity_type = :entity_type
              AND entity_id = :entity_id
              AND is_resolved = FALSE
              AND created_at >= NOW() - INTERVAL '10 minutes'
            ORDER BY created_at DESC
            LIMIT 1
            """
        ),
        {"alert_type": alert_type, "entity_type": entity_type, "entity_id": entity_id},
    )
    if existing.scalar_one_or_none():
        return None

    created = await db.execute(
        text(
            """
            INSERT INTO fleet_live_alerts (
                alert_type, entity_type, entity_id, message, severity, lat, lng, metadata, created_at
            )
            VALUES (
                :alert_type, :entity_type, :entity_id, :message, :severity, :lat, :lng, CAST(:metadata AS JSONB), NOW()
            )
            RETURNING id, alert_type, entity_type, entity_id, message, severity, lat, lng, metadata, created_at
            """
        ),
        {
            "alert_type": alert_type,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "message": message,
            "severity": severity,
            "lat": lat,
            "lng": lng,
            "metadata": json.dumps(metadata or {}),
        },
    )
    return dict(created.mappings().one())


async def _broadcast_location(entity_type: str, data: Dict[str, Any]) -> None:
    await socket_hub.broadcast(
        {
            "type": "location_update",
            "entity_type": entity_type,
            "data": data,
            "timestamp": datetime.utcnow().isoformat(),
        }
    )


async def _broadcast_alert(alert: Dict[str, Any]) -> None:
    await socket_hub.broadcast(
        {
            "type": "location_update",
            "entity_type": "alert",
            "data": alert,
            "timestamp": datetime.utcnow().isoformat(),
        }
    )


@router.post("/vehicles/{vehicle_id}/location")
async def update_vehicle_location(
    vehicle_id: int,
    payload: VehicleLocationUpdate,
    db: AsyncSession = Depends(get_db_async),
) -> Dict[str, Any]:
    await _ensure_live_schema(db)

    vehicle = await db.execute(
        text(
            """
            SELECT id, vehicle_code, plate_number, status
            FROM fleet_vehicles
            WHERE id = :vehicle_id AND status <> 'inactive'
            """
        ),
        {"vehicle_id": vehicle_id},
    )
    vehicle_row = vehicle.mappings().first()
    if not vehicle_row:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    await db.execute(
        text(
            """
            INSERT INTO fleet_vehicle_locations (vehicle_id, lat, lng, speed, heading, accuracy, updated_at)
            VALUES (:vehicle_id, :lat, :lng, :speed, :heading, :accuracy, NOW())
            ON CONFLICT (vehicle_id) DO UPDATE
            SET lat = EXCLUDED.lat,
                lng = EXCLUDED.lng,
                speed = EXCLUDED.speed,
                heading = EXCLUDED.heading,
                accuracy = EXCLUDED.accuracy,
                updated_at = NOW()
            """
        ),
        {
            "vehicle_id": vehicle_id,
            "lat": payload.lat,
            "lng": payload.lng,
            "speed": payload.speed,
            "heading": payload.heading,
            "accuracy": payload.accuracy,
        },
    )
    await _record_history(db, "vehicle", vehicle_id, payload.lat, payload.lng)

    alert = None
    if payload.speed > 80:
        alert = await _create_alert(
            db,
            alert_type="speeding",
            entity_type="vehicle",
            entity_id=vehicle_id,
            severity="high" if payload.speed > 100 else "medium",
            message=f"Vehicle {vehicle_row['plate_number']} is speeding at {payload.speed:.0f} km/h.",
            lat=payload.lat,
            lng=payload.lng,
            metadata={"speed": payload.speed, "plate_number": vehicle_row["plate_number"]},
        )

    await db.commit()

    response = {
        "id": vehicle_id,
        "vehicle_id": vehicle_id,
        "vehicle_code": vehicle_row["vehicle_code"],
        "plate_number": vehicle_row["plate_number"],
        "vehicle_status": vehicle_row["status"],
        "lat": payload.lat,
        "lng": payload.lng,
        "speed": payload.speed,
        "heading": payload.heading,
        "accuracy": payload.accuracy,
        "last_update": datetime.utcnow().isoformat(),
    }
    await _broadcast_location("vehicle", response)
    if alert:
        await _broadcast_alert(alert)
    return {"ok": True, "vehicle": response}


@router.post("/drivers/{driver_id}/location")
async def update_driver_location(
    driver_id: int,
    payload: DriverLocationUpdate,
    db: AsyncSession = Depends(get_db_async),
) -> Dict[str, Any]:
    await _ensure_live_schema(db)

    driver = await db.execute(
        text(
            """
            SELECT u.id, u.full_name, p.driver_code
            FROM users u
            LEFT JOIN fleet_driver_profiles p ON p.user_id = u.id
            WHERE u.id = :driver_id
              AND LOWER(COALESCE(u.role, '')) = 'driver'
              AND COALESCE(u.is_deleted, FALSE) = FALSE
            """
        ),
        {"driver_id": driver_id},
    )
    driver_row = driver.mappings().first()
    if not driver_row:
        raise HTTPException(status_code=404, detail="Driver not found")

    await db.execute(
        text(
            """
            INSERT INTO fleet_driver_locations (driver_id, lat, lng, speed, heading, status, updated_at)
            VALUES (:driver_id, :lat, :lng, :speed, :heading, :status, NOW())
            ON CONFLICT (driver_id) DO UPDATE
            SET lat = EXCLUDED.lat,
                lng = EXCLUDED.lng,
                speed = EXCLUDED.speed,
                heading = EXCLUDED.heading,
                status = EXCLUDED.status,
                updated_at = NOW()
            """
        ),
        {
            "driver_id": driver_id,
            "lat": payload.lat,
            "lng": payload.lng,
            "speed": payload.speed,
            "heading": payload.heading,
            "status": payload.status,
        },
    )
    await _record_history(db, "driver", driver_id, payload.lat, payload.lng)
    await db.commit()

    response = {
        "id": driver_id,
        "driver_id": driver_id,
        "driver_code": driver_row["driver_code"],
        "driver_name": driver_row["full_name"],
        "driver_status": payload.status,
        "lat": payload.lat,
        "lng": payload.lng,
        "speed": payload.speed,
        "heading": payload.heading,
        "last_update": datetime.utcnow().isoformat(),
    }
    await _broadcast_location("driver", response)
    return {"ok": True, "driver": response}


@router.get("/map-data")
async def get_live_map_data(db: AsyncSession = Depends(get_db_async)) -> Dict[str, Any]:
    await _ensure_live_schema(db)

    vehicles_result = await db.execute(
        text(
            """
            SELECT
                v.id,
                v.vehicle_code,
                v.plate_number,
                v.type,
                v.status AS vehicle_status,
                vl.lat,
                vl.lng,
                vl.speed,
                vl.heading,
                vl.accuracy,
                vl.updated_at AS last_update,
                u.id AS driver_id,
                u.full_name AS driver_name,
                p.driver_code
            FROM fleet_vehicles v
            LEFT JOIN fleet_vehicle_locations vl ON vl.vehicle_id = v.id
            LEFT JOIN fleet_driver_vehicle_assignments a ON a.vehicle_id = v.id AND a.is_active = TRUE
            LEFT JOIN users u ON u.id = a.driver_id
            LEFT JOIN fleet_driver_profiles p ON p.user_id = u.id
            WHERE v.status <> 'inactive'
            ORDER BY v.plate_number ASC
            """
        )
    )
    drivers_result = await db.execute(
        text(
            """
            SELECT
                u.id,
                COALESCE(p.driver_code, 'DRV' || LPAD(u.id::text, 4, '0')) AS driver_code,
                u.full_name AS driver_name,
                COALESCE(dl.status, p.status, CASE WHEN u.is_active THEN 'available' ELSE 'inactive' END) AS driver_status,
                dl.lat,
                dl.lng,
                dl.speed,
                dl.heading,
                dl.updated_at AS last_update,
                v.id AS vehicle_id,
                v.vehicle_code,
                v.plate_number
            FROM users u
            LEFT JOIN fleet_driver_profiles p ON p.user_id = u.id
            LEFT JOIN fleet_driver_locations dl ON dl.driver_id = u.id
            LEFT JOIN fleet_driver_vehicle_assignments a ON a.driver_id = u.id AND a.is_active = TRUE
            LEFT JOIN fleet_vehicles v ON v.id = a.vehicle_id
            WHERE LOWER(COALESCE(u.role, '')) = 'driver'
              AND COALESCE(u.is_deleted, FALSE) = FALSE
            ORDER BY u.full_name ASC
            """
        )
    )
    alerts_result = await db.execute(
        text(
            """
            SELECT id, alert_type, entity_type, entity_id, message, severity, lat, lng, metadata, created_at
            FROM fleet_live_alerts
            WHERE is_resolved = FALSE
            ORDER BY created_at DESC
            LIMIT 10
            """
        )
    )

    vehicles = _mapping_rows(vehicles_result)
    drivers = _mapping_rows(drivers_result)
    alerts = _mapping_rows(alerts_result)

    stats = {
        "active_vehicles": sum(1 for item in vehicles if item.get("lat") is not None and item.get("vehicle_status") != "maintenance"),
        "active_drivers": sum(1 for item in drivers if item.get("lat") is not None),
        "available_drivers": sum(1 for item in drivers if item.get("driver_status") == "available"),
        "busy_drivers": sum(1 for item in drivers if item.get("driver_status") == "busy"),
        "maintenance_vehicles": sum(1 for item in vehicles if item.get("vehicle_status") == "maintenance"),
        "alerts_open": len(alerts),
        "total_vehicles": len(vehicles),
        "total_drivers": len(drivers),
    }

    return {
        "ok": True,
        "vehicles": vehicles,
        "drivers": drivers,
        "alerts": alerts,
        "stats": stats,
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/vehicles/{vehicle_id}/track")
async def get_vehicle_track(
    vehicle_id: int,
    hours: int = Query(default=24, ge=1, le=168),
    db: AsyncSession = Depends(get_db_async),
) -> Dict[str, Any]:
    await _ensure_live_schema(db)
    result = await db.execute(
        text(
            """
            SELECT lat, lng, recorded_at
            FROM fleet_location_history
            WHERE entity_type = 'vehicle'
              AND entity_id = :vehicle_id
              AND recorded_at >= NOW() - (:hours * INTERVAL '1 hour')
            ORDER BY recorded_at ASC
            """
        ),
        {"vehicle_id": vehicle_id, "hours": hours},
    )
    return {"ok": True, "track": _mapping_rows(result), "hours": hours, "vehicle_id": vehicle_id}


@router.get("/drivers/{driver_id}/track")
async def get_driver_track(
    driver_id: int,
    hours: int = Query(default=24, ge=1, le=168),
    db: AsyncSession = Depends(get_db_async),
) -> Dict[str, Any]:
    await _ensure_live_schema(db)
    result = await db.execute(
        text(
            """
            SELECT lat, lng, recorded_at
            FROM fleet_location_history
            WHERE entity_type = 'driver'
              AND entity_id = :driver_id
              AND recorded_at >= NOW() - (:hours * INTERVAL '1 hour')
            ORDER BY recorded_at ASC
            """
        ),
        {"driver_id": driver_id, "hours": hours},
    )
    return {"ok": True, "track": _mapping_rows(result), "hours": hours, "driver_id": driver_id}


@router.websocket("/ws")
async def fleet_live_websocket(websocket: WebSocket) -> None:
    await socket_hub.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await socket_hub.disconnect(websocket)
    except Exception:
        await socket_hub.disconnect(websocket)
