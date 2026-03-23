from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, Optional

from backend.services.notification_service import notification_service

logger = logging.getLogger(__name__)


class IVRBot:
    """Minimal IVR flow manager. Real telephony prompts/DTMF remain provider-driven."""

    def __init__(self) -> None:
        self.active_calls: Dict[str, Dict[str, Any]] = {}

    async def handle_incoming_call(self, call_id: str, from_number: str, to_number: str) -> Dict[str, Any]:
        self.active_calls[call_id] = {
            "from": from_number,
            "to": to_number,
            "step": "menu",
        }
        logger.info("Incoming IVR call %s from=%s to=%s", call_id, from_number, to_number)
        await self._notify_ops(
            "operations_manager",
            f"Incoming call received from {from_number} to {to_number}. Call ID: {call_id}",
        )
        return {
            "status": "menu",
            "call_id": call_id,
            "message": "Welcome to GTS Logistics. Press 1 for shipments, 2 for billing, 3 for support, 0 for operator.",
        }

    async def route_choice(self, call_id: str, choice: str, from_number: Optional[str] = None) -> Dict[str, Any]:
        state = self.active_calls.setdefault(call_id, {"step": "menu", "from": from_number or "", "to": ""})
        choice = str(choice or "").strip()
        if choice == "1":
            state["step"] = "shipments"
            return {"status": "shipments", "message": "Please enter your shipment number."}
        if choice == "2":
            state["step"] = "billing"
            await self._notify_ops("finance_bot", f"Billing transfer requested from {state.get('from')}. Call ID: {call_id}")
            return {"status": "billing", "message": "Your billing request has been forwarded to finance."}
        if choice == "3":
            state["step"] = "support"
            await self._notify_ops("customer_service", f"Support transfer requested from {state.get('from')}. Call ID: {call_id}")
            return {"status": "support", "message": "Your support request has been forwarded to customer service."}
        if choice == "0":
            state["step"] = "operator"
            await self._notify_ops("operations_manager", f"Human operator requested from {state.get('from')}. Call ID: {call_id}")
            return {"status": "operator", "message": "A human operator has been requested."}
        return {"status": "invalid", "message": "Invalid option. Press 1 for shipments, 2 for billing, 3 for support, 0 for operator."}

    async def _notify_ops(self, bot_name: str, message: str) -> None:
        try:
            await notification_service.send_bot_notification(
                bot_name=bot_name,
                template_key="system_alert",
                context={"user_name": "IVR System", "message": message},
            )
        except Exception as exc:
            logger.warning("IVR notification failed for %s: %s", bot_name, exc)
        await asyncio.sleep(0)


ivr_bot = IVRBot()
