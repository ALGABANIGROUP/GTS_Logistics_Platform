"""
Freight Broker Bot
Carrier matching, rate intelligence, and shipment coordination.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
import copy
from sqlalchemy import select
from backend.database import async_session
from backend.models.freight import Carrier, Shipment, Rate


class FreightBrokerBot:
    """Freight brokerage bot with rates, carriers, shipments, and tracking actions."""

    def __init__(self) -> None:
    async def get_carriers(self) -> List[Dict]:
        """
        Get carriers from database
        """
        async with async_session() as session:
            query = select(Carrier).where(Carrier.is_active == True)
            result = await session.execute(query)
            carriers = result.scalars().all()

            return [
                {
                    "id": c.id,
                    "carrier_code": c.code,
                    "carrier_name": c.name,
                    "carrier_type": c.type,
                    "coverage_regions": c.coverage_regions or [],
                    "rating": c.rating or 0,
                    "base_rate": c.base_rate or 0,
                    "rate_per_km": c.rate_per_km or 0,
                    "on_time_performance": c.on_time_performance or 0,
                    "available_vehicles": c.fleet_size or 0,
                    "status": "active",
                    "is_preferred": c.is_preferred or False,
                }
                for c in carriers
            ]

    async def get_shipments(self, status: str = None) -> List[Dict]:
        """
        Get shipments from database
        """
        async with async_session() as session:
            query = select(Shipment)
            if status:
                query = query.where(Shipment.status == status)
            result = await session.execute(query)
            shipments = result.scalars().all()

            return [
                {
                    "id": s.id,
                    "shipment_number": s.number,
                    "customer_name": s.customer_name or "Unknown",
                    "weight": s.weight or 0,
                    "origin_city": s.origin or "",
                    "destination_city": s.destination or "",
                    "pickup_date": s.pickup_date.isoformat() if s.pickup_date else None,
                    "assigned_carrier_id": s.carrier_id,
                    "carrier_quote": s.carrier_quote or 0,
                    "our_price": s.our_price or 0,
                    "profit_margin": ((s.our_price - s.carrier_quote) / s.carrier_quote * 100) if s.carrier_quote and s.our_price else 0,
                    "tracking_number": s.tracking_number,
                    "tracking_status": s.tracking_status or "pending",
                    "status": s.status or "pending",
                }
                for s in shipments
            ]

    async def run(self, payload: dict) -> dict:
        """Main execution method."""
        context = payload.get("context", {}) or {}
        action = payload.get("action") or context.get("action") or payload.get("meta", {}).get("action") or "status"

        if action == "status":
            return await self.status()
        if action == "config":
            return await self.config()
        if action == "dashboard":
            return await self.get_dashboard()
        if action == "get_carriers":
            return await self.get_carriers_filtered(context.get("filters") or payload.get("filters"))
        if action == "register_carrier":
            return await self.register_carrier(context.get("carrier_data") or payload.get("carrier_data") or context)
        if action == "request_rate":
            return await self.request_rate(context.get("request_data") or payload.get("request_data") or context)
        if action == "compare_rates":
            return await self.compare_rates(context.get("origin"), context.get("destination"), float(context.get("weight", 0) or 0))
        if action == "create_shipment":
            return await self.create_shipment(context.get("shipment_data") or payload.get("shipment_data") or context)
        if action == "assign_carrier":
            return await self.assign_carrier(int(context.get("shipment_id") or payload.get("shipment_id") or 0), int(context.get("carrier_id") or payload.get("carrier_id") or 0), float(context.get("quoted_price") or payload.get("quoted_price") or 0))
        if action == "get_shipment":
            return await self.get_shipment(int(context.get("shipment_id") or payload.get("shipment_id") or 0))
        if action == "track_shipment":
            tracking_number = context.get("tracking_number") or payload.get("tracking_number")
            shipment_id = context.get("shipment_id") or payload.get("shipment_id")
            return await self.track_shipment(tracking_number=tracking_number, shipment_id=shipment_id)
        if action == "optimize_shipments":
            return await self.optimize_shipments(context.get("shipment_ids") or payload.get("shipment_ids") or [])
        if action == "find_backhaul":
            return await self.find_backhaul(int(context.get("shipment_id") or payload.get("shipment_id") or 0))
        return {"ok": False, "error": f"Unknown action: {action}"}

    async def process_message(self, message: str, context: Optional[dict] = None) -> dict:
        """Handle natural-language requests and explicit context actions."""
        context = context or {}
        if context.get("action"):
            return await self.run({"context": context})

        message_lower = (message or "").lower()
        if "dashboard" in message_lower or "overview" in message_lower:
            return await self.get_dashboard()
        if "carrier" in message_lower:
            return await self.get_carriers()
        if "rate" in message_lower or "quote" in message_lower:
            return await self.compare_rates("Riyadh", "Jeddah", 500)
        if "track" in message_lower:
            return await self.track_shipment(tracking_number="TRK001")
        if "shipment" in message_lower:
            return await self.get_shipment(101)
        return await self.status()

    async def status(self) -> dict:
        """Return current broker status."""
        carriers = await self.get_carriers()
        shipments = await self.get_shipments()

        return {
            "ok": True,
            "bot": self.name,
            "display_name": self.display_name,
            "version": self.version,
            "mode": self.mode,
            "is_active": self.is_active,
            "carriers_active": len([carrier for carrier in carriers if carrier["status"] == "active"]),
            "shipments_open": len([shipment for shipment in shipments if shipment["status"] != "completed"]),
            "message": "Freight brokerage runtime is operational",
        }

    async def config(self) -> dict:
        """Return bot configuration."""
        return {
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "version": self.version,
            "mode": self.mode,
            "capabilities": [
                "dashboard",
                "get_carriers",
                "register_carrier",
                "request_rate",
                "compare_rates",
                "create_shipment",
                "assign_carrier",
                "get_shipment",
                "track_shipment",
                "optimize_shipments",
                "find_backhaul",
            ],
        }

    async def get_carriers_filtered(self, filters: Optional[Dict[str, Any]] = None) -> dict:
        """Return carriers with optional filtering."""
        filters = filters or {}
        carriers = await self.get_carriers()

        if filters.get("city"):
            carriers = [carrier for carrier in carriers if filters["city"] in carrier.get("coverage_regions", [])]
        if filters.get("preferred") is True:
            carriers = [carrier for carrier in carriers if carrier.get("is_preferred", False)]

        return {"ok": True, "carriers": carriers}

    async def register_carrier(self, carrier_data: Dict[str, Any]) -> dict:
        """Register a new carrier in memory."""
        carrier = {
            "id": len(self.carriers) + 1,
            "carrier_code": f"CAR{len(self.carriers) + 1:03d}",
            "carrier_name": carrier_data.get("carrier_name", "New carrier"),
            "carrier_type": carrier_data.get("carrier_type", "truck"),
            "coverage_regions": carrier_data.get("coverage_regions", []),
            "rating": float(carrier_data.get("rating", 4.0) or 4.0),
            "base_rate": float(carrier_data.get("base_rate", 0) or 0),
            "rate_per_km": float(carrier_data.get("rate_per_km", 0) or 0),
            "on_time_performance": float(carrier_data.get("on_time_performance", 90.0) or 90.0),
            "available_vehicles": int(carrier_data.get("available_vehicles", 0) or 0),
            "status": "active",
            "is_preferred": bool(carrier_data.get("is_preferred", False)),
        }
        self.carriers.append(carrier)
        return {"ok": True, "carrier": carrier}

    async def request_rate(self, request_data: Dict[str, Any]) -> dict:
        """Create a quote request and return ranked offers."""
        comparison = await self.compare_rates(
            request_data.get("origin"),
            request_data.get("destination"),
            float(request_data.get("weight", 0) or 0),
        )
        offers = comparison.get("offers", [])
        request = {
            "request_id": f"REQ{len(self.rate_requests) + 1:03d}",
            "origin": request_data.get("origin"),
            "destination": request_data.get("destination"),
            "weight": float(request_data.get("weight", 0) or 0),
            "offers": offers,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self.rate_requests.insert(0, request)
        return {
            "ok": True,
            "request_id": request["request_id"],
            "offers": offers,
            "best_offer": offers[0] if offers else None,
        }

    async def compare_rates(self, origin: Optional[str], destination: Optional[str], weight: float) -> dict:
        """Compare carrier rates for a route."""
        if not origin or not destination or weight <= 0:
            return {"ok": False, "error": "Origin, destination, and weight are required"}

        offers = []
        for carrier in self.carriers:
            if carrier["status"] != "active":
                continue
            rate = carrier["base_rate"] + weight * (carrier["rate_per_km"] * 0.9)
            transit_days = 1 if origin == destination else 2 if {origin, destination} == {"Riyadh", "Dammam"} else 3
            offers.append(
                {
                    "carrier_id": carrier["id"],
                    "carrier_name": carrier["carrier_name"],
                    "price": round(rate, 2),
                    "transit_days": transit_days,
                    "rating": carrier["rating"],
                    "best_for": "price" if carrier["id"] == 2 else "rating" if carrier["id"] == 3 else "speed",
                }
            )

        offers.sort(key=lambda offer: offer["price"])
        best_value = max(
            offers,
            key=lambda offer: (offer["rating"] * 15) - offer["price"] / 100,
        ) if offers else None
        return {
            "ok": True,
            "origin": origin,
            "destination": destination,
            "weight": weight,
            "offers": offers,
            "best_by_price": offers[0] if offers else None,
            "best_by_time": min(offers, key=lambda offer: offer["transit_days"]) if offers else None,
            "best_by_rating": max(offers, key=lambda offer: offer["rating"]) if offers else None,
            "best_value": best_value,
        }

    async def create_shipment(self, shipment_data: Dict[str, Any]) -> dict:
        """Create a new shipment."""
        shipment = {
            "id": len(self.shipments) + 101,
            "shipment_number": f"SHP{len(self.shipments) + 1:03d}",
            "customer_name": shipment_data.get("customer_name", "New customer"),
            "weight": float(shipment_data.get("weight", 0) or 0),
            "origin_city": shipment_data.get("origin_city"),
            "destination_city": shipment_data.get("destination_city"),
            "pickup_date": shipment_data.get("pickup_date") or datetime.now(timezone.utc).date().isoformat(),
            "assigned_carrier_id": None,
            "carrier_quote": None,
            "our_price": float(shipment_data.get("our_price", 0) or 0),
            "profit_margin": 0.0,
            "tracking_number": None,
            "tracking_status": "pending",
            "status": "pending",
        }
        self.shipments.insert(0, shipment)
        return {"ok": True, "shipment": shipment}

    async def assign_carrier(self, shipment_id: int, carrier_id: int, quoted_price: float) -> dict:
        """Assign a carrier to a shipment."""
        shipment = next((item for item in self.shipments if item["id"] == shipment_id), None)
        carrier = next((item for item in self.carriers if item["id"] == carrier_id), None)
        if not shipment or not carrier:
            return {"ok": False, "error": "Shipment or carrier not found"}

        shipment["assigned_carrier_id"] = carrier_id
        shipment["carrier_quote"] = quoted_price
        shipment["tracking_number"] = shipment.get("tracking_number") or f"TRK{shipment_id}"
        shipment["tracking_status"] = "booked"
        shipment["status"] = "confirmed"
        shipment["profit_margin"] = round(((shipment["our_price"] - quoted_price) / shipment["our_price"]) * 100, 2) if shipment["our_price"] else 0.0
        self.tracking_history.setdefault(
            shipment["tracking_number"],
            [{"status": "booked", "location": shipment["origin_city"], "timestamp": datetime.now(timezone.utc).isoformat(), "description": f"Shipment booked with {carrier['carrier_name']}."}],
        )
        return {"ok": True, "shipment": copy.deepcopy(shipment), "carrier": copy.deepcopy(carrier)}

    async def get_shipment(self, shipment_id: int) -> dict:
        """Return shipment details."""
        shipment = next((item for item in self.shipments if item["id"] == shipment_id), None)
        if not shipment:
            return {"ok": False, "error": f"Shipment '{shipment_id}' not found"}
        return {
            "ok": True,
            "shipment": copy.deepcopy(shipment),
            "tracking_info": await self.track_shipment(
                tracking_number=shipment.get("tracking_number"),
                shipment_id=shipment_id,
            ),
        }

    async def track_shipment(self, tracking_number: Optional[str] = None, shipment_id: Optional[int] = None) -> dict:
        """Return shipment tracking information."""
        shipment = None
        if shipment_id is not None:
            shipment = next((item for item in self.shipments if item["id"] == int(shipment_id)), None)
            if shipment:
                tracking_number = shipment.get("tracking_number")
        elif tracking_number:
            shipment = next((item for item in self.shipments if item.get("tracking_number") == tracking_number), None)

        if not tracking_number or tracking_number not in self.tracking_history:
            return {"ok": False, "error": "Tracking number not found"}

        history = copy.deepcopy(self.tracking_history[tracking_number])
        current = history[-1]
        return {
            "ok": True,
            "tracking_number": tracking_number,
            "shipment_number": shipment.get("shipment_number") if shipment else None,
            "current_status": current["status"],
            "status_history": history,
            "estimated_delivery": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat() if current["status"] != "delivered" else None,
        }

    async def optimize_shipments(self, shipment_ids: List[int]) -> dict:
        """Suggest consolidation opportunities."""
        selected = [shipment for shipment in self.shipments if shipment["id"] in shipment_ids]
        if not selected:
            return {"ok": False, "error": "No shipments found for optimization"}

        by_destination: Dict[str, List[Dict[str, Any]]] = {}
        for shipment in selected:
            by_destination.setdefault(shipment["destination_city"], []).append(shipment)

        consolidations = []
        for destination, shipments in by_destination.items():
            total_weight = sum(item["weight"] for item in shipments)
            truck_type = "large_truck" if total_weight > 1000 else "medium_truck"
            consolidations.append(
                {
                    "destination": destination,
                    "shipments": [item["shipment_number"] for item in shipments],
                    "shipment_count": len(shipments),
                    "total_weight": total_weight,
                    "truck_type": truck_type,
                    "utilization_percent": round(min(100, total_weight / 1500 * 100), 2),
                }
            )

        return {
            "ok": True,
            "total_shipments": len(selected),
            "consolidations": consolidations,
            "trucks_needed": len(consolidations),
            "savings_estimate": round(len(selected) * 135.0, 2),
        }

    async def find_backhaul(self, shipment_id: int) -> dict:
        """Find return-load opportunities."""
        shipment = next((item for item in self.shipments if item["id"] == shipment_id), None)
        if not shipment:
            return {"ok": False, "error": "Shipment not found"}

        opportunities = [
            {
                "shipment_id": candidate["id"],
                "shipment_number": candidate["shipment_number"],
                "customer": candidate["customer_name"],
                "route": f'{shipment["origin_city"]} -> {shipment["destination_city"]} -> {candidate["destination_city"]}',
                "savings_estimate": 320.0,
            }
            for candidate in self.shipments
            if candidate["id"] != shipment_id and candidate["origin_city"] == shipment["destination_city"]
        ]
        return {
            "ok": True,
            "primary_shipment": shipment["shipment_number"],
            "opportunities": opportunities,
            "count": len(opportunities),
        }

    async def get_dashboard(self) -> dict:
        """Return freight broker dashboard."""
        top_carriers = sorted(
            self.carriers,
            key=lambda carrier: (carrier["rating"], carrier["on_time_performance"]),
            reverse=True,
        )[:3]
        completed = len([shipment for shipment in self.shipments if shipment["status"] == "completed"])
        in_progress = len([shipment for shipment in self.shipments if shipment["status"] == "in_progress"])
        pending = len([shipment for shipment in self.shipments if shipment["status"] == "pending"])
        avg_margin = round(
            sum(shipment["profit_margin"] for shipment in self.shipments if shipment["profit_margin"]) /
            max(1, len([shipment for shipment in self.shipments if shipment["profit_margin"]])),
            2,
        )
        return {
            "ok": True,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "overview": {
                "active_carriers": len([carrier for carrier in self.carriers if carrier["status"] == "active"]),
                "open_shipments": len([shipment for shipment in self.shipments if shipment["status"] != "completed"]),
                "pending_rate_requests": len(self.rate_requests),
                "avg_margin": avg_margin,
            },
            "shipments": {
                "total_shipments": len(self.shipments),
                "completed": completed,
                "in_progress": in_progress,
                "pending": pending,
                "recent": copy.deepcopy(self.shipments[:5]),
            },
            "rates": {
                "latest_request": copy.deepcopy(self.rate_requests[0]) if self.rate_requests else None,
                "best_offer": self.rate_requests[0]["offers"][0] if self.rate_requests else None,
            },
            "top_carriers": copy.deepcopy(top_carriers),
        }
