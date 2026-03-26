from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, Optional

from backend.config import settings
from backend.services.chatgpt_service import ChatServiceUnavailableError, chatgpt_service
from backend.services.notification_service import notification_service

logger = logging.getLogger(__name__)

try:
    from twilio.base.exceptions import TwilioRestException  # type: ignore
    from twilio.rest import Client  # type: ignore
except Exception:  # pragma: no cover
    Client = None  # type: ignore

    class TwilioRestException(Exception):
        pass


class WhatsAppService:
    """WhatsApp channel support via Twilio with safe fallback when SDK/creds are missing."""

    def __init__(self) -> None:
        self.account_sid = settings.TWILIO_ACCOUNT_SID
        self.auth_token = settings.TWILIO_AUTH_TOKEN
        self.whatsapp_number = settings.TWILIO_WHATSAPP_NUMBER
        self.enabled = bool(Client and self.account_sid and self.auth_token and self.whatsapp_number)
        self.client = Client(self.account_sid, self.auth_token) if self.enabled else None
        if self.enabled:
            logger.info("WhatsApp service initialized")
        else:
            logger.info("WhatsApp service disabled: missing SDK or credentials")

    async def send_message(
        self,
        to: str,
        message: str,
        bot_name: str = "customer_service",
        media_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        if not self.enabled or self.client is None:
            return {"success": False, "error": "service_disabled"}
        to_number = self._to_whatsapp_number(to)
        params: Dict[str, Any] = {
            "body": message,
            "from_": self._to_whatsapp_number(self.whatsapp_number),
            "to": to_number,
        }
        if media_url:
            params["media_url"] = [media_url]
        try:
            response = await asyncio.to_thread(self.client.messages.create, **params)
            await self._notify(
                bot_name,
                f"WhatsApp sent to {to}. SID: {getattr(response, 'sid', 'unknown')}.",
            )
            return {
                "success": True,
                "message_sid": getattr(response, "sid", None),
                "status": getattr(response, "status", None),
                "timestamp": datetime.utcnow().isoformat(),
            }
        except TwilioRestException as exc:
            logger.error("WhatsApp send failed: %s", exc)
            return {"success": False, "error": str(exc)}

    async def send_template_message(
        self,
        to: str,
        template_name: str,
        template_data: Dict[str, str],
        bot_name: str = "customer_service",
    ) -> Dict[str, Any]:
        templates = {
            "shipment_created": "Your shipment #{shipment_id} has been created and will be picked up soon.",
            "shipment_delivered": "Your shipment #{shipment_id} has been delivered successfully.",
            "payment_reminder": "Reminder: Payment of {amount} is due for shipment #{shipment_id}.",
            "driver_assigned": "Driver {driver_name} has been assigned to your shipment #{shipment_id}.",
            "safety_alert": "Safety alert: {message}",
            "welcome": "Welcome to GTS Logistics. How can we help you today?",
        }
        text = templates.get(template_name, template_name).format(**template_data)
        return await self.send_message(to, text, bot_name)

    async def handle_incoming(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        from_number = str(payload.get("From") or "").replace("whatsapp:", "")
        body = str(payload.get("Body") or "").strip()
        bot_name = self._detect_bot(body)
        analysis = await self._analyze_message(body)
        auto_reply = await self._generate_reply(body, analysis, bot_name)
        await self._notify(
            bot_name,
            f"WhatsApp received from {from_number}. Intent: {analysis.get('intent', 'unknown')}.",
        )
        if auto_reply:
            await self.send_message(from_number, auto_reply, bot_name)
        return {
            "success": True,
            "from": from_number,
            "bot_name": bot_name,
            "analysis": analysis,
            "auto_replied": bool(auto_reply),
        }

    def _detect_bot(self, message: str) -> str:
        msg_lower = message.lower()
        keywords = {
            "freight_broker": ["shipment", "track", "delivery", "pickup", "load"],
            "finance_bot": ["invoice", "payment", "bill", "cost", "price"],
            "customer_service": ["help", "support", "problem", "issue", "question"],
            "safety_manager": ["accident", "incident", "unsafe", "hazard", "injury"],
            "security_manager": ["hack", "breach", "unauthorized", "suspicious"],
        }
        for bot_name, words in keywords.items():
            if any(word in msg_lower for word in words):
                return bot_name
        return "customer_service"

    async def _analyze_message(self, message: str) -> Dict[str, Any]:
        if not message:
            return {"intent": "other", "urgency": "low", "sentiment": "neutral", "needs_human": False}
        try:
            response = await chatgpt_service.chat(
                user_message=(
                    "Return compact JSON only with keys: intent, urgency, sentiment, needs_human, suggested_reply.\n\n"
                    f"Message:\n{message[:500]}"
                ),
                conversation_id=f"whatsapp_analysis_{datetime.utcnow().timestamp()}",
            )
            return self._coerce_json(response.get("response", ""))
        except ChatServiceUnavailableError:
            return self._fallback_analysis(message)
        except Exception as exc:
            logger.warning("WhatsApp analysis failed: %s", exc)
            return self._fallback_analysis(message)

    async def _generate_reply(self, message: str, analysis: Dict[str, Any], bot_name: str) -> Optional[str]:
        if analysis.get("needs_human"):
            return None
        try:
            response = await chatgpt_service.chat(
                user_message=(
                    f"As {bot_name} at GTS Logistics, reply in under 200 characters.\n"
                    f"Intent: {analysis.get('intent', 'unknown')}\n"
                    f"Urgency: {analysis.get('urgency', 'medium')}\n"
                    f"Message: {message[:500]}"
                ),
                conversation_id=f"whatsapp_reply_{datetime.utcnow().timestamp()}",
            )
            return str(response.get("response") or "").strip() or "Thank you for your message. Our team will respond shortly."
        except ChatServiceUnavailableError:
            return analysis.get("suggested_reply") or "Thank you for your message. Our team will respond shortly."
        except Exception:
            return analysis.get("suggested_reply") or "Thank you for your message. Our team will respond shortly."

    def _fallback_analysis(self, message: str) -> Dict[str, Any]:
        lowered = message.lower()
        if any(token in lowered for token in ["urgent", "asap", "immediately"]):
            urgency = "high"
        else:
            urgency = "medium"
        if any(token in lowered for token in ["invoice", "payment", "bill"]):
            intent = "billing"
        elif any(token in lowered for token in ["shipment", "track", "delivery"]):
            intent = "shipment"
        elif any(token in lowered for token in ["accident", "unsafe", "hazard"]):
            intent = "safety"
        else:
            intent = "support"
        return {
            "intent": intent,
            "urgency": urgency,
            "sentiment": "neutral",
            "needs_human": urgency == "high",
            "suggested_reply": "Thank you for your message. Our team will respond shortly.",
        }

    def _coerce_json(self, text: str) -> Dict[str, Any]:
        raw = text.strip()
        if raw.startswith("```"):
            raw = raw.strip("`")
            raw = raw.split("\n", 1)[1] if "\n" in raw else raw
        try:
            value = json.loads(raw)
            return value if isinstance(value, dict) else self._fallback_analysis(text)
        except Exception:
            return self._fallback_analysis(text)

    def _to_whatsapp_number(self, value: str) -> str:
        value = value.strip()
        return value if value.startswith("whatsapp:") else f"whatsapp:{value}"

    async def _notify(self, bot_name: str, message: str) -> None:
        try:
            await notification_service.send_bot_notification(
                bot_name=bot_name,
                template_key="system_alert",
                context={"user_name": "Channels", "message": message},
            )
        except Exception as exc:
            logger.debug("WhatsApp channel notification skipped: %s", exc)


whatsapp_service = WhatsAppService()
