from __future__ import annotations
# backend/bots/freight_broker.py
from copy import deepcopy
from datetime import datetime, timezone
import logging
from typing import Any, Dict, List

from .base_bot import BaseBot

logger = logging.getLogger(__name__)

class FreightBrokerBot(BaseBot):
    """Freight Broker AI Assistant"""

    def __init__(self):
        super().__init__(
            name="FreightBrokerBot",
            description="AI assistant for freight brokerage operations"
        )

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process freight requests"""
        logger.info(f"FreightBrokerBot processing: {input_data.get('action')}")
        # Implement freight logic
        return {
            "status": "success",
            "response": "Freight request processed",
            "data": input_data
        }

    async def get_status(self) -> Dict[str, Any]:
        """Get bot status"""
        return {
            "name": self.name,
            "active": self.is_active,
            "description": self.description
        }
    """In-memory freight brokerage bot with stable runtime behavior."""

    name = "freight_broker"
    display_name = "AI Freight Broker"
    description = "Matches loads with carriers and negotiates optimal rates"
    version = "1.0"
    mode = "runtime"

    def __init__(self) -> None:
        self.is_active = True
        self.carriers: List[Dict[str, Any]] = [
            {
                "id": 1,
                "carrier_name": "Fast Freight Inc.",
                "carrier_type": "dry_van",
                "coverage_regions": ["Riyadh", "Jeddah", "Dammam"],
                "rating": 4.8,
                "base_rate": 850.0,
                "rate_per_km": 1.20,
                "on_time_performance": 97.0,
                "available_vehicles": 25,
                "status": "active",
                "is_preferred": True,
            },
            {
                "id": 2,
                "carrier_name": "Trans-Canada Logistics",
                "carrier_type": "reefer",
                "coverage_regions": ["Riyadh", "Jeddah", "Tabuk"],
                "rating": 4.7,
                "base_rate": 900.0,
                "rate_per_km": 1.15,
                "on_time_performance": 95.0,
                "available_vehicles": 42,
                "status": "active",
                "is_preferred": False,
            },
            {
                "id": 3,
                "carrier_name": "Northern Transport",
                "carrier_type": "flatbed",
                "coverage_regions": ["Riyadh", "Dammam", "Medina"],
                "rating": 4.9,
                "base_rate": 880.0,
                "rate_per_km": 1.10,
                "on_time_performance": 98.0,
                "available_vehicles": 18,
                "status": "active",
                "is_preferred": True,
            },
        ]
        self.shipments: List[Dict[str, Any]] = [
            {
                "id": 101,
                "shipment_number": "SHP-101",
                "customer_name": "Acme Trading",
                "weight": 500.0,
                "origin_city": "Riyadh",
                "destination_city": "Jeddah",
                "pickup_date": "2026-03-25T08:00:00+00:00",
                "assigned_carrier_id": None,
                "carrier_quote": 0.0,
                "our_price": 1580.0,
                "profit_margin": 0.0,
                "tracking_number": "TRK101",
                "tracking_status": "pending",
                "status": "open",
            },
            {
                "id": 102,
                "shipment_number": "SHP-102",
                "customer_name": "GTS Retail",
                "weight": 750.0,
                "origin_city": "Dammam",
                "destination_city": "Riyadh",
                "pickup_date": "2026-03-25T10:00:00+00:00",
                "assigned_carrier_id": 2,
                "carrier_quote": 1325.0,
                "our_price": 1680.0,
                "profit_margin": 26.79,
                "tracking_number": "TRK102",
                "tracking_status": "in_transit",
                "status": "booked",
            },
            {
                "id": 103,
                "shipment_number": "SHP-103",
                "customer_name": "Nova Manufacturing",
                "weight": 620.0,
                "origin_city": "Riyadh",
                "destination_city": "Jeddah",
                "pickup_date": "2026-03-26T06:00:00+00:00",
                "assigned_carrier_id": None,
                "carrier_quote": 0.0,
                "our_price": 1450.0,
                "profit_margin": 0.0,
                "tracking_number": "TRK103",
                "tracking_status": "pending",
                "status": "open",
            },
        ]
        self.rate_requests: List[Dict[str, Any]] = []

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        context = payload.get("context", {}) or {}
        action = (
            payload.get("action")
            or context.get("action")
            or payload.get("meta", {}).get("action")
            or "status"
        )

        if action == "status":
            return await self.status()
        if action == "config":
            return await self.config()
        if action == "dashboard":
            return await self.get_dashboard()
        if action == "compare_rates":
            return await self.compare_rates(
                context.get("origin") or payload.get("origin"),
                context.get("destination") or payload.get("destination"),
                float(context.get("weight") or payload.get("weight") or 0),
            )
        if action == "assign_carrier":
            return await self.assign_carrier(
                int(context.get("shipment_id") or payload.get("shipment_id") or 0),
                int(context.get("carrier_id") or payload.get("carrier_id") or 0),
                float(context.get("quoted_price") or payload.get("quoted_price") or 0),
            )
        if action == "get_carriers":
            return {"ok": True, "carriers": deepcopy(self.carriers)}
        if action == "get_shipment":
            return await self.get_shipment(int(context.get("shipment_id") or payload.get("shipment_id") or 0))
        return {"ok": False, "error": f"Unknown action: {action}"}

    async def process_message(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        context = context or {}
        if context.get("action"):
            return await self.run({"context": context})
        message_lower = (message or "").lower()
        if "dashboard" in message_lower:
            return await self.get_dashboard()
        if "carrier" in message_lower:
            return {"ok": True, "carriers": deepcopy(self.carriers)}
        if "rate" in message_lower or "quote" in message_lower:
            return await self.compare_rates("Riyadh", "Jeddah", 500)
        return await self.status()

    async def status(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "bot": self.name,
            "display_name": self.display_name,
            "version": self.version,
            "mode": self.mode,
            "is_active": self.is_active,
            "carriers_active": len([carrier for carrier in self.carriers if carrier["status"] == "active"]),
            "shipments_open": len([shipment for shipment in self.shipments if shipment["status"] != "completed"]),
        }

    async def config(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "actions": ["dashboard", "compare_rates", "assign_carrier", "get_carriers", "get_shipment"],
        }

    async def get_dashboard(self) -> Dict[str, Any]:
        open_shipments = [shipment for shipment in self.shipments if shipment["status"] == "open"]
        booked_shipments = [shipment for shipment in self.shipments if shipment["status"] == "booked"]
        top_carriers = sorted(self.carriers, key=lambda carrier: carrier["rating"], reverse=True)[:3]
        return {
            "ok": True,
            "overview": {
                "active_carriers": len([carrier for carrier in self.carriers if carrier["status"] == "active"]),
                "open_shipments": len(open_shipments),
                "booked_shipments": len(booked_shipments),
                "rate_requests": len(self.rate_requests),
            },
            "shipments": deepcopy(self.shipments),
            "top_carriers": deepcopy(top_carriers),
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    async def get_shipment(self, shipment_id: int) -> Dict[str, Any]:
        shipment = next((item for item in self.shipments if item["id"] == shipment_id), None)
        if not shipment:
            return {"ok": False, "error": "Shipment not found"}
        return {"ok": True, "shipment": deepcopy(shipment)}

    async def compare_rates(self, origin: Optional[str], destination: Optional[str], weight: float) -> Dict[str, Any]:
        if not origin or not destination or weight <= 0:
            return {"ok": False, "error": "Origin, destination, and weight are required"}

        offers: List[Dict[str, Any]] = []
        for carrier in self.carriers:
            if carrier["status"] != "active":
                continue
            rate = carrier["base_rate"] + (weight * carrier["rate_per_km"])
            offers.append(
                {
                    "carrier_id": carrier["id"],
                    "carrier_name": carrier["carrier_name"],
                    "price": round(rate, 2),
                    "rating": carrier["rating"],
                    "transit_days": 1 if origin == destination else 2,
                }
            )
        offers.sort(key=lambda offer: offer["price"])
        return {
            "ok": True,
            "origin": origin,
            "destination": destination,
            "weight": weight,
            "offers": offers,
            "best_by_price": offers[0] if offers else None,
        }

    async def assign_carrier(self, shipment_id: int, carrier_id: int, quoted_price: float) -> Dict[str, Any]:
        shipment = next((item for item in self.shipments if item["id"] == shipment_id), None)
        carrier = next((item for item in self.carriers if item["id"] == carrier_id), None)
        if not shipment:
            return {"ok": False, "error": "Shipment not found"}
        if not carrier:
            return {"ok": False, "error": "Carrier not found"}

        shipment["assigned_carrier_id"] = carrier_id
        shipment["carrier_quote"] = quoted_price
        shipment["tracking_status"] = "booked"
        shipment["status"] = "booked"
        shipment["profit_margin"] = round(
            ((shipment["our_price"] - quoted_price) / quoted_price) * 100,
            2,
        ) if quoted_price else 0.0
        return {"ok": True, "shipment": deepcopy(shipment), "carrier": deepcopy(carrier)}

