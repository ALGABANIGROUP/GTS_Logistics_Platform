from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import select

from backend.database.config import get_sessionmaker
from backend.models.invoices import Invoice
from backend.models.shipment import Shipment
from backend.models.user import User
from backend.services.chatgpt_service import chatgpt_service
from backend.services.notification_service import notification_service
from backend.services.sms_service import sms_service

logger = logging.getLogger(__name__)


class CallBot:
    def __init__(self) -> None:
        self.active_calls: Dict[str, Dict[str, Any]] = {}

    async def handle_call(self, call_id: str, from_number: str, to_number: str) -> None:
        logger.info("CallBot handling call %s from=%s", call_id, from_number)
        self.active_calls[call_id] = {
            "from": from_number,
            "to": to_number,
            "started_at": datetime.utcnow().isoformat(),
            "step": "welcome",
            "context": {},
            "history": [],
        }
        await self._say(call_id, "Hello, this is GTS virtual assistant.")
        await self._identify_caller(call_id, from_number)
        purpose = await self._get_call_purpose(call_id)
        if purpose == "shipment":
            await self._handle_shipment_call(call_id)
        elif purpose == "billing":
            await self._handle_billing_call(call_id)
        elif purpose == "support":
            await self._handle_support_call(call_id)
        elif purpose == "safety":
            await self._handle_safety_call(call_id)
        elif purpose == "security":
            await self._handle_security_call(call_id)
        else:
            await self._handle_general_call(call_id)

    async def _identify_caller(self, call_id: str, phone: str) -> None:
        maker = get_sessionmaker()
        async with maker() as session:
            result = await session.execute(select(User).where(User.phone_number == phone).limit(1))
            user = result.scalars().first()
            if user:
                self.active_calls[call_id]["context"].update({"type": "user", "id": user.id, "name": user.full_name or user.email})
                await self._say(call_id, f"Welcome back, {user.full_name or user.email}.")
                return
        self.active_calls[call_id]["context"]["type"] = "guest"
        await self._say(call_id, "I do not have your information yet.")

    async def _get_call_purpose(self, call_id: str) -> str:
        await self._say(call_id, "How can I help you today?")
        response = await self._listen(call_id, timeout=10)
        lowered = (response or "").lower()
        if any(word in lowered for word in ["shipment", "track", "deliver", "package"]):
            return "shipment"
        if any(word in lowered for word in ["bill", "invoice", "pay", "money"]):
            return "billing"
        if any(word in lowered for word in ["help", "support", "issue", "problem"]):
            return "support"
        if any(word in lowered for word in ["accident", "incident", "safety", "unsafe"]):
            return "safety"
        if any(word in lowered for word in ["security", "hack", "breach", "password"]):
            return "security"
        return "general"

    async def _handle_shipment_call(self, call_id: str) -> None:
        self.active_calls[call_id]["step"] = "shipment"
        await self._say(call_id, "Please say or enter your shipment number.")
        shipment_number = await self._listen(call_id, timeout=15)
        if not shipment_number:
            await self._say(call_id, "No shipment number received.")
            return
        maker = get_sessionmaker()
        async with maker() as session:
            result = await session.execute(select(Shipment).where(Shipment.shipment_number == shipment_number).limit(1))
            shipment = result.scalars().first()
            if shipment:
                eta = shipment.delivery_scheduled.isoformat() if shipment.delivery_scheduled else "unknown"
                location = shipment.current_location_description or "unknown"
                await self._say(call_id, f"Shipment {shipment_number} is {shipment.status}. Current location: {location}. Estimated delivery: {eta}.")
                await self._say(call_id, "Would you like SMS updates? Say yes or no.")
                response = await self._listen(call_id, timeout=5)
                if response and "yes" in response.lower():
                    await sms_service.send_sms(self.active_calls[call_id]["from"], f"GTS: Shipment {shipment_number} is {shipment.status}.", bot_name="freight_broker")
                    await self._say(call_id, "SMS updates enabled.")
            else:
                await self._say(call_id, f"Shipment {shipment_number} not found.")

    async def _handle_billing_call(self, call_id: str) -> None:
        self.active_calls[call_id]["step"] = "billing"
        await self._say(call_id, "Please say your invoice number.")
        invoice_number = await self._listen(call_id, timeout=10)
        if invoice_number:
            maker = get_sessionmaker()
            async with maker() as session:
                result = await session.execute(select(Invoice).where(Invoice.number == invoice_number).limit(1))
                invoice = result.scalars().first()
                if invoice:
                    await self._say(call_id, f"Invoice {invoice.number} is {invoice.status}. Amount: {invoice.amount_usd} US dollars.")
                    return
        await self._transfer_to_bot(call_id, "finance_bot")

    async def _handle_support_call(self, call_id: str) -> None:
        self.active_calls[call_id]["step"] = "support"
        await self._say(call_id, "Please describe the issue you are experiencing.")
        issue = await self._listen(call_id, timeout=20)
        if issue:
            analysis = await self._analyze_issue(issue)
            if analysis.get("can_help"):
                await self._say(call_id, str(analysis.get("solution") or "I can help with that."))
                return
        await self._transfer_to_human(call_id, "customer_service")

    async def _handle_safety_call(self, call_id: str) -> None:
        self.active_calls[call_id]["step"] = "safety"
        await self._say(call_id, "Please describe the safety incident.")
        incident = await self._listen(call_id, timeout=30)
        if incident:
            analysis = await self._analyze_incident(incident)
            if analysis.get("urgent"):
                await self._say(call_id, "This sounds urgent. Connecting you immediately.")
                await self._transfer_to_human(call_id, "safety_manager")
                return
            await notification_service.send_bot_notification(
                bot_name="safety_manager",
                template_key="system_alert",
                context={"user_name": self.active_calls[call_id]["context"].get("name", "Customer"), "message": f"Safety incident reported by call {call_id}: {incident[:400]}"},
            )
        await self._say(call_id, "A safety specialist will contact you.")

    async def _handle_security_call(self, call_id: str) -> None:
        self.active_calls[call_id]["step"] = "security"
        await self._say(call_id, "Please describe the security issue.")
        issue = await self._listen(call_id, timeout=20)
        if issue and any(word in issue.lower() for word in ["hack", "breach", "unauthorized"]):
            await self._transfer_to_human(call_id, "security_manager")
            return
        await self._say(call_id, "A security specialist will review this.")

    async def _handle_general_call(self, call_id: str) -> None:
        self.active_calls[call_id]["step"] = "general"
        await self._say(call_id, "Let me connect you with an operator.")
        await self._transfer_to_human(call_id, "operations_manager")

    async def _analyze_issue(self, issue: str) -> Dict[str, Any]:
        try:
            response = await chatgpt_service.chat(
                user_message=f"Return compact JSON only with keys: can_help, solution, category, urgency.\n\nIssue:\n{issue[:500]}",
                conversation_id=f"issue_analysis_{datetime.utcnow().timestamp()}",
            )
            return self._coerce_json(response.get("response", ""))
        except Exception:
            return {"can_help": False, "category": "unknown", "urgency": "medium"}

    async def _analyze_incident(self, incident: str) -> Dict[str, Any]:
        try:
            response = await chatgpt_service.chat(
                user_message=f"Return compact JSON only with keys: urgent, severity, category, recommended_action.\n\nIncident:\n{incident[:500]}",
                conversation_id=f"incident_analysis_{datetime.utcnow().timestamp()}",
            )
            return self._coerce_json(response.get("response", ""))
        except Exception:
            return {"urgent": False, "severity": "medium", "category": "unknown"}

    async def _transfer_to_bot(self, call_id: str, bot_name: str) -> None:
        await self._say(call_id, f"Transferring you to {bot_name.replace('_', ' ')}.")
        await notification_service.send_bot_notification(
            bot_name=bot_name,
            template_key="system_alert",
            context={"user_name": self.active_calls.get(call_id, {}).get("context", {}).get("name", "Customer"), "message": f"Call {call_id} transferred to bot {bot_name}."},
        )

    async def _transfer_to_human(self, call_id: str, department: str) -> None:
        await self._say(call_id, "Connecting you to a human operator. Please hold.")
        await notification_service.send_bot_notification(
            bot_name=department,
            template_key="system_alert",
            context={"user_name": "Operator", "message": f"Human transfer requested for call {call_id} from {self.active_calls.get(call_id, {}).get('from', 'unknown')}."},
        )

    async def _say(self, call_id: str, text: str) -> None:
        logger.info("[Call %s] BOT: %s", call_id, text)
        if call_id in self.active_calls:
            self.active_calls[call_id]["history"].append({"role": "bot", "text": text, "timestamp": datetime.utcnow().isoformat()})
        await asyncio.sleep(min(len(text) * 0.01, 1.5))

    async def _listen(self, call_id: str, timeout: int = 10) -> Optional[str]:
        logger.info("[Call %s] Listening timeout=%ss", call_id, timeout)
        await asyncio.sleep(min(timeout, 2))
        response = "shipment"
        if call_id in self.active_calls:
            self.active_calls[call_id]["history"].append({"role": "user", "text": response, "timestamp": datetime.utcnow().isoformat()})
        return response

    def _coerce_json(self, text: str) -> Dict[str, Any]:
        raw = text.strip()
        if raw.startswith("```"):
            raw = raw.strip("`")
            raw = raw.split("\n", 1)[1] if "\n" in raw else raw
        try:
            value = json.loads(raw)
            return value if isinstance(value, dict) else {}
        except Exception:
            return {}


call_bot = CallBot()
