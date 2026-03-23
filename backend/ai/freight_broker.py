from __future__ import annotations

from typing import Any, Dict

from backend.ai.learning_bot_base import ReusableLearningBot


class FreightBrokerLearningBot(ReusableLearningBot):
    name = "freight_broker"
    description = "Freight brokerage with learning"
    learning_frequency = "hourly"
    learning_intensity = "high"

    async def match_shipment(self, shipment_data: Dict[str, Any]) -> Dict[str, Any]:
        return await self.process_action("match_shipment", shipment=shipment_data)

    async def _execute_action(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        shipment = params.get("shipment", {})
        origin = shipment.get("origin") or shipment.get("pickup_location") or "Unknown"
        destination = shipment.get("destination") or shipment.get("dropoff_location") or "Unknown"
        weight = float(shipment.get("weight") or 0)
        return {
            "status": "matched",
            "carrier_id": "carrier_demo_123",
            "lane": f"{origin} -> {destination}",
            "priority": "high" if weight > 20000 else "standard",
            "accuracy": 0.94,
        }


freight_broker_bot = FreightBrokerLearningBot()

