from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from backend.config import settings
from backend.database.config import get_sessionmaker
from backend.models.user import User
from backend.notifications.templates import NOTIFICATION_TEMPLATES
from backend.utils.email_utils import send_bot_email

logger = logging.getLogger(__name__)


class NotificationType(str, Enum):
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    WHATSAPP = "whatsapp"
    SYSTEM = "system"


class NotificationPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class NotificationService:
    """Central notification service with bot-specific email templates."""

    def __init__(self) -> None:
        self.default_recipient = settings.ADMIN_EMAIL or settings.SUPPORT_EMAIL or settings.SMTP_FROM or settings.SMTP_USER
        self.legacy_templates = {
            "shipment_created": {
                "title": "New Shipment Created",
                "message": "Shipment #{shipment_id} has been created.",
                "email_subject": "Shipment #{shipment_id} Created - GTS Logistics",
            },
            "shipment_delivered": {
                "title": "Shipment Delivered",
                "message": "Shipment #{shipment_id} has been delivered.",
                "email_subject": "Shipment #{shipment_id} Delivered - GTS Logistics",
            },
            "payment_reminder": {
                "title": "Payment Reminder",
                "message": "Payment of ${amount} is due for shipment #{shipment_id}.",
                "email_subject": "Payment Reminder - Shipment #{shipment_id}",
            },
            "driver_assigned": {
                "title": "Driver Assigned",
                "message": "Driver {driver_name} has been assigned to shipment #{shipment_id}.",
                "email_subject": "Driver Assigned - Shipment #{shipment_id}",
            },
            "system_alert": {
                "title": "System Alert",
                "message": "{message}",
                "email_subject": "GTS System Alert",
            },
        }

    async def render_template(self, template_key: str, context: Dict[str, Any]) -> Dict[str, str]:
        template_info = NOTIFICATION_TEMPLATES.get(template_key)
        if not template_info:
            raise KeyError(f"Unknown notification template: {template_key}")

        subject = str(template_info["subject"]).format(**context)
        text_body = str(template_info["template"]).format(**context)
        html_template = template_info.get("html_template")
        html_body = str(html_template).format(**context) if html_template else ""
        return {
            "subject": subject,
            "body": html_body or text_body,
            "text_body": text_body,
            "html_body": html_body,
        }

    async def send_bot_notification(
        self,
        *,
        bot_name: str,
        template_key: str,
        context: Dict[str, Any],
        recipient_email: Optional[str] = None,
    ) -> bool:
        try:
            rendered = await self.render_template(template_key, context)
        except Exception as exc:
            logger.error("Notification template render failed for %s: %s", template_key, exc)
            return False

        to_email = recipient_email or str(context.get("user_email") or "").strip() or self.default_recipient
        if not to_email:
            logger.warning("Notification skipped for %s because no recipient was resolved", template_key)
            return False

        result = await asyncio.to_thread(
            send_bot_email,
            bot_name,
            rendered["subject"],
            rendered["body"],
            [to_email],
            bool(rendered["html_body"]),
            rendered["text_body"],
        )
        logger.info(
            "Bot notification %s sent=%s bot=%s to=%s",
            template_key,
            result,
            bot_name,
            to_email,
        )
        return bool(result)

    async def send_security_notification(
        self,
        *,
        event_type: str,
        user_email: str,
        user_name: str,
        ip_address: str,
        device: str = "Unknown",
        attempt_count: int = 1,
        reason: str = "",
    ) -> bool:
        template_map = {
            "login_success": "security_login_success",
            "login_failed": "security_login_failed",
            "password_changed": "security_password_changed",
            "logout": "security_logout",
        }
        template_key = template_map.get(event_type)
        if not template_key:
            logger.warning("Unknown security notification event: %s", event_type)
            return False

        return await self.send_bot_notification(
            bot_name="security_manager",
            template_key=template_key,
            recipient_email=user_email,
            context={
                "user_name": user_name,
                "user_email": user_email,
                "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
                "ip_address": ip_address,
                "device": device,
                "attempt_count": attempt_count,
                "reason": reason or "User logout",
            },
        )

    async def send_finance_notification(
        self,
        *,
        event_type: str,
        user_email: Optional[str],
        user_name: str,
        invoice_data: Dict[str, Any],
    ) -> bool:
        template_map = {
            "invoice_created": "finance_invoice_created",
            "invoice_paid": "finance_invoice_paid",
            "invoice_overdue": "finance_invoice_overdue",
        }
        template_key = template_map.get(event_type)
        if not template_key:
            logger.warning("Unknown finance notification event: %s", event_type)
            return False

        payload = {
            "user_name": user_name,
            "user_email": user_email or self.default_recipient,
            "invoice_number": invoice_data.get("invoice_number", "N/A"),
            "amount": invoice_data.get("amount", 0),
            "currency": invoice_data.get("currency", "USD"),
            "due_date": invoice_data.get("due_date", "N/A"),
            "customer_name": invoice_data.get("customer_name", user_name),
            "invoice_url": invoice_data.get("invoice_url", settings.FRONTEND_URL),
            "payment_date": invoice_data.get("payment_date", "N/A"),
            "payment_method": invoice_data.get("payment_method", "Recorded in platform"),
            "receipt_url": invoice_data.get("receipt_url", settings.FRONTEND_URL),
            "days_overdue": invoice_data.get("days_overdue", 0),
        }
        return await self.send_bot_notification(
            bot_name="finance_bot",
            template_key=template_key,
            recipient_email=user_email,
            context=payload,
        )

    async def send_document_notification(
        self,
        *,
        event_type: str,
        user_email: Optional[str],
        user_name: str,
        document_data: Dict[str, Any],
    ) -> bool:
        template_map = {
            "uploaded": "document_uploaded",
            "expiring": "document_expiring_soon",
            "signed": "document_signed",
        }
        template_key = template_map.get(event_type)
        if not template_key:
            logger.warning("Unknown document notification event: %s", event_type)
            return False
        return await self.send_bot_notification(
            bot_name="documents_manager",
            template_key=template_key,
            recipient_email=user_email,
            context={"user_name": user_name, "user_email": user_email or self.default_recipient, **document_data},
        )

    async def send_shipment_notification(
        self,
        *,
        event_type: str,
        user_email: Optional[str],
        user_name: str,
        shipment_data: Dict[str, Any],
    ) -> bool:
        template_map = {
            "created": "shipment_created",
            "driver_assigned": "shipment_driver_assigned",
            "status_changed": "shipment_status_changed",
            "delayed": "shipment_delayed",
            "delivered": "shipment_delivered",
        }
        template_key = template_map.get(event_type)
        if not template_key:
            logger.warning("Unknown shipment notification event: %s", event_type)
            return False

        payload = {
            "user_name": user_name,
            "user_email": user_email or self.default_recipient,
            "shipment_id": shipment_data.get("shipment_id", "N/A"),
            "origin": shipment_data.get("origin", "Unknown"),
            "destination": shipment_data.get("destination", "Unknown"),
            "estimated_delivery": shipment_data.get("estimated_delivery", "Pending"),
            "tracking_url": shipment_data.get("tracking_url", settings.FRONTEND_URL),
            "driver_name": shipment_data.get("driver_name", "Unassigned"),
            "driver_phone": shipment_data.get("driver_phone", "N/A"),
            "vehicle_plate": shipment_data.get("vehicle_plate", "N/A"),
            "new_status": shipment_data.get("new_status", shipment_data.get("status", "Updated")),
            "current_location": shipment_data.get("current_location", "Unknown"),
            "delay_reason": shipment_data.get("delay_reason", "Operational delay"),
            "new_eta": shipment_data.get("new_eta", shipment_data.get("estimated_delivery", "Pending")),
            "delivery_time": shipment_data.get("delivery_time", datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")),
            "recipient_name": shipment_data.get("recipient_name", "Recipient"),
            "confirmation_url": shipment_data.get("confirmation_url", settings.FRONTEND_URL),
        }
        return await self.send_bot_notification(
            bot_name="freight_broker",
            template_key=template_key,
            recipient_email=user_email,
            context=payload,
        )

    async def send_safety_notification(
        self,
        *,
        event_type: str,
        user_email: Optional[str],
        user_name: str,
        safety_data: Dict[str, Any],
    ) -> bool:
        template_map = {
            "incident": "safety_incident_reported",
            "violation": "safety_violation_detected",
            "maintenance": "safety_maintenance_reminder",
        }
        template_key = template_map.get(event_type)
        if not template_key:
            logger.warning("Unknown safety notification event: %s", event_type)
            return False
        return await self.send_bot_notification(
            bot_name="safety_manager",
            template_key=template_key,
            recipient_email=user_email,
            context={"user_name": user_name, "user_email": user_email or self.default_recipient, **safety_data},
        )

    async def send_notification(
        self,
        recipient_id: int,
        notification_type: NotificationType | str,
        template_key: str,
        template_data: Optional[Dict[str, Any]] = None,
        priority: NotificationPriority | str = NotificationPriority.MEDIUM,
        channels: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        user_email = await self._get_user_email(recipient_id)
        channels = channels or ["email"]
        template_data = template_data or {}

        if template_key in NOTIFICATION_TEMPLATES:
            rendered = await self.render_template(
                template_key,
                {"user_name": template_data.get("user_name", f"User {recipient_id}"), **template_data},
            )
            sent = False
            if "email" in channels and user_email:
                sent = await asyncio.to_thread(
                    send_bot_email,
                    "system_admin",
                    rendered["subject"],
                    rendered["body"],
                    [user_email],
                    False,
                )
            results = {"email": {"status": "sent" if sent else "failed", "recipient": user_email}}
            payload_title = rendered["subject"]
            payload_message = rendered["body"]
        else:
            legacy_template = self.legacy_templates.get(template_key, self.legacy_templates["system_alert"])
            payload_title = legacy_template["title"].format(**template_data)
            payload_message = legacy_template["message"].format(**template_data)
            subject = legacy_template.get("email_subject", payload_title).format(**template_data)
            sent = False
            if "email" in channels and user_email:
                sent = await asyncio.to_thread(send_bot_email, "system_admin", subject, payload_message, [user_email], False)
            results = {"email": {"status": "sent" if sent else "failed", "recipient": user_email}}

        await self._log_notification(
            recipient_id=recipient_id,
            type=str(notification_type),
            title=payload_title,
            message=payload_message,
            priority=str(priority),
            channels=channels,
            results=results,
        )
        return {
            "notification_id": f"notif_{int(datetime.utcnow().timestamp())}_{recipient_id}",
            "recipient_id": recipient_id,
            "type": str(notification_type),
            "title": payload_title,
            "message": payload_message,
            "channels": channels,
            "results": results,
            "sent_at": datetime.utcnow().isoformat(),
        }

    async def send_bulk_notification(
        self,
        recipient_ids: List[int],
        notification_type: NotificationType | str,
        template_key: str,
        template_data: Optional[Dict[str, Any]] = None,
        priority: NotificationPriority | str = NotificationPriority.MEDIUM,
        channels: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        results = []
        for recipient_id in recipient_ids:
            try:
                results.append(
                    await self.send_notification(
                        recipient_id=recipient_id,
                        notification_type=notification_type,
                        template_key=template_key,
                        template_data=template_data,
                        priority=priority,
                        channels=channels,
                    )
                )
            except Exception as exc:
                results.append({"recipient_id": recipient_id, "status": "failed", "error": str(exc)})
        return {
            "total_recipients": len(recipient_ids),
            "successful": len([item for item in results if "error" not in item]),
            "failed": len([item for item in results if "error" in item]),
            "results": results,
        }

    async def send_system_alert(
        self,
        *,
        title: str,
        message: str,
        recipient_ids: Optional[List[int]] = None,
        priority: NotificationPriority = NotificationPriority.HIGH,
    ) -> Dict[str, Any]:
        recipient_ids = recipient_ids or await self._get_admin_user_ids()
        return await self.send_bulk_notification(
            recipient_ids=recipient_ids,
            notification_type=NotificationType.SYSTEM,
            template_key="system_alert",
            template_data={"user_name": "Administrator", "message": message, "title": title},
            priority=priority,
            channels=["email"],
        )

    async def _get_user_email(self, user_id: int) -> Optional[str]:
        maker = get_sessionmaker()
        async with maker() as session:
            user = await session.get(User, user_id)
            return str(getattr(user, "email", "") or "").strip() or None

    async def _get_admin_user_ids(self) -> List[int]:
        maker = get_sessionmaker()
        async with maker() as session:
            result = await session.execute(
                User.__table__.select().with_only_columns(User.id).where(User.role.in_(["admin", "super_admin"]))
            )
            return [int(row[0]) for row in result.fetchall() if row and row[0] is not None]

    async def _log_notification(
        self,
        *,
        recipient_id: int,
        type: str,
        title: str,
        message: str,
        priority: str,
        channels: List[str],
        results: Dict[str, Any],
    ) -> None:
        logger.info(
            "notification recipient_id=%s type=%s priority=%s channels=%s results=%s title=%s",
            recipient_id,
            type,
            priority,
            channels,
            results,
            title,
        )


notification_service = NotificationService()
