from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from backend.config import settings
from backend.services.notification_service import notification_service

logger = logging.getLogger(__name__)

try:
    from twilio.base.exceptions import TwilioRestException  # type: ignore
    from twilio.rest import Client  # type: ignore
except Exception:  # pragma: no cover
    Client = None  # type: ignore

    class TwilioRestException(Exception):
        pass


class SMSService:
    def __init__(self) -> None:
        self.account_sid = settings.TWILIO_ACCOUNT_SID
        self.auth_token = settings.TWILIO_AUTH_TOKEN
        self.sms_number = settings.TWILIO_SMS_NUMBER
        self.enabled = bool(Client and self.account_sid and self.auth_token and self.sms_number)
        self.client = Client(self.account_sid, self.auth_token) if self.enabled else None
        if self.enabled:
            logger.info("SMS service initialized")
        else:
            logger.warning("SMS service disabled: missing SDK or credentials")

    async def send_sms(
        self,
        to: str,
        message: str,
        bot_name: str = "customer_service",
        priority: str = "normal",
    ) -> Dict[str, Any]:
        if not self.enabled or self.client is None:
            return {"success": False, "error": "service_disabled"}
        if len(message) > 160 and priority != "urgent":
            message = message[:157] + "..."
        if len(message) > 160 and priority == "urgent":
            chunks = [message[i:i + 154] for i in range(0, len(message), 154)]
            results = []
            for idx, chunk in enumerate(chunks, start=1):
                prefix = f"({idx}/{len(chunks)}) " if len(chunks) > 1 else ""
                results.append(await self._send_single(to, prefix + chunk, bot_name))
            return {"success": all(r.get("success") for r in results), "parts": len(results), "results": results}
        return await self._send_single(to, message, bot_name)

    async def send_verification_code(self, to: str, code: str) -> Dict[str, Any]:
        return await self.send_sms(to, f"Your GTS verification code is: {code}. Valid for 10 minutes.", "security_manager")

    async def send_shipment_alert(
        self,
        driver_phone: str,
        customer_phone: Optional[str],
        shipment_id: int,
        alert_type: str,
        details: Dict[str, Any],
    ) -> Dict[str, Any]:
        alerts = {
            "pickup": f"Pickup scheduled for shipment #{shipment_id} at {details.get('time', 'scheduled time')}.",
            "delay": f"Shipment #{shipment_id} delayed. New ETA: {details.get('new_eta', 'unknown')}.",
            "delivery": f"Shipment #{shipment_id} delivered at {details.get('time', 'delivery time')}.",
            "issue": f"Issue with shipment #{shipment_id}: {details.get('issue', 'unknown issue')}.",
        }
        message = alerts.get(alert_type, f"Shipment #{shipment_id} update.")
        driver_result = await self.send_sms(driver_phone, message, bot_name="freight_broker")
        customer_result = await self.send_sms(customer_phone, message, bot_name="customer_service") if customer_phone else None
        return {"success": driver_result.get("success", False), "driver": driver_result, "customer": customer_result}

    async def send_bulk_sms(self, numbers: List[str], message: str, bot_name: str = "customer_service") -> List[Dict[str, Any]]:
        return [await self.send_sms(number, message, bot_name) for number in numbers]

    async def handle_incoming(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        from_number = str(payload.get("From") or "")
        body = str(payload.get("Body") or "").strip()
        await self._notify("customer_service", f"SMS received from {from_number}.")
        if "STOP" in body.upper():
            auto_reply = "You have been unsubscribed from GTS notifications."
        elif "HELP" in body.upper():
            auto_reply = "Reply with SHIPMENT <number> for tracking, or contact GTS support."
        else:
            auto_reply = "Thank you for your message. A representative will contact you shortly."
        if from_number:
            await self.send_sms(from_number, auto_reply, "customer_service")
        return {"success": True, "from": from_number, "auto_replied": True}

    async def _send_single(self, to: str, message: str, bot_name: str) -> Dict[str, Any]:
        try:
            response = await asyncio.to_thread(
                self.client.messages.create,
                body=message,
                from_=self.sms_number,
                to=to,
            )
            await self._notify(bot_name, f"SMS sent to {to}. SID: {getattr(response, 'sid', 'unknown')}.")
            return {
                "success": True,
                "message_sid": getattr(response, "sid", None),
                "status": getattr(response, "status", None),
                "timestamp": datetime.utcnow().isoformat(),
            }
        except TwilioRestException as exc:
            logger.error("SMS send failed: %s", exc)
            return {"success": False, "error": str(exc)}

    async def _notify(self, bot_name: str, message: str) -> None:
        try:
            await notification_service.send_bot_notification(
                bot_name=bot_name,
                template_key="system_alert",
                context={"user_name": "SMS Channel", "message": message},
            )
        except Exception as exc:
            logger.debug("SMS channel notification skipped: %s", exc)


sms_service = SMSService()
