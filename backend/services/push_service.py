from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from backend.config import settings
from backend.services.notification_service import notification_service

logger = logging.getLogger(__name__)

try:
    import firebase_admin  # type: ignore
    from firebase_admin import credentials, messaging  # type: ignore
    from firebase_admin.exceptions import FirebaseError  # type: ignore
except Exception:  # pragma: no cover
    firebase_admin = None  # type: ignore
    credentials = None  # type: ignore
    messaging = None  # type: ignore

    class FirebaseError(Exception):
        pass


class PushNotificationService:
    def __init__(self) -> None:
        self.device_tokens: Dict[int, List[str]] = {}
        self.enabled = False
        if firebase_admin and credentials and messaging and settings.FIREBASE_CREDENTIALS_PATH:
            try:
                if not firebase_admin._apps:  # type: ignore[attr-defined]
                    cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
                    firebase_admin.initialize_app(cred)
                self.enabled = True
                logger.info("Firebase push initialized")
            except Exception as exc:
                logger.error("Firebase init failed: %s", exc)

    async def register_device(self, user_id: int, device_token: str, device_type: str = "android") -> bool:
        tokens = self.device_tokens.setdefault(user_id, [])
        if device_token not in tokens:
            tokens.append(device_token)
            logger.info("Push device registered user_id=%s type=%s", user_id, device_type)
        return True

    async def unregister_device(self, user_id: int, device_token: str) -> bool:
        tokens = self.device_tokens.get(user_id, [])
        if device_token in tokens:
            tokens.remove(device_token)
        return True

    async def send_to_user(
        self,
        user_id: int,
        title: str,
        body: str,
        data: Optional[Dict[str, str]] = None,
        bot_name: str = "system_admin",
    ) -> Dict[str, Any]:
        if not self.enabled or messaging is None:
            return {"success": False, "error": "service_disabled"}
        tokens = self.device_tokens.get(user_id, [])
        if not tokens:
            return {"success": False, "error": "no_devices_registered"}
        message = messaging.MulticastMessage(
            notification=messaging.Notification(title=title, body=body),
            data=data or {},
            tokens=tokens,
        )
        try:
            response = messaging.send_each_for_multicast(message)
            await self._notify(bot_name, f"Push sent to user {user_id}. Success: {response.success_count}, Failed: {response.failure_count}.")
            return {
                "success": True,
                "success_count": response.success_count,
                "failure_count": response.failure_count,
                "timestamp": datetime.utcnow().isoformat(),
            }
        except FirebaseError as exc:
            logger.error("Push send failed: %s", exc)
            return {"success": False, "error": str(exc)}

    async def send_to_driver(
        self,
        driver_id: int,
        title: str,
        body: str,
        shipment_id: Optional[int] = None,
        data: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        payload = dict(data or {})
        if shipment_id is not None:
            payload["shipment_id"] = str(shipment_id)
            payload["click_action"] = "OPEN_SHIPMENT"
        return await self.send_to_user(driver_id, title, body, payload, bot_name="freight_broker")

    async def send_to_customer(
        self,
        customer_id: int,
        title: str,
        body: str,
        shipment_id: Optional[int] = None,
        data: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        payload = dict(data or {})
        if shipment_id is not None:
            payload["shipment_id"] = str(shipment_id)
            payload["click_action"] = "TRACK_SHIPMENT"
        return await self.send_to_user(customer_id, title, body, payload, bot_name="customer_service")

    async def broadcast_to_role(
        self,
        role: str,
        title: str,
        body: str,
        data: Optional[Dict[str, str]] = None,
        exclude_user_ids: Optional[List[int]] = None,
    ) -> Dict[str, Any]:
        exclude = set(exclude_user_ids or [])
        user_ids = [user_id for user_id in self.device_tokens if user_id not in exclude]
        results = [await self.send_to_user(user_id, title, body, data) for user_id in user_ids]
        return {
            "success": True,
            "role": role,
            "total": len(user_ids),
            "sent": sum(1 for item in results if item.get("success")),
            "failed": sum(1 for item in results if not item.get("success")),
        }

    async def send_shipment_update(
        self,
        customer_id: int,
        driver_id: int,
        shipment_id: int,
        status: str,
        location: Optional[str] = None,
    ) -> Dict[str, Any]:
        title = f"Shipment #{shipment_id} Update"
        body = f"Shipment status updated to {status}"
        if location:
            body = f"{body} near {location}"
        data = {"shipment_id": str(shipment_id), "status": status}
        if location:
            data["location"] = location
        customer_result = await self.send_to_customer(customer_id, title, body, shipment_id, data)
        driver_result = await self.send_to_driver(driver_id, title, body, shipment_id, data)
        return {
            "success": customer_result.get("success") or driver_result.get("success"),
            "customer": customer_result,
            "driver": driver_result,
        }

    async def send_safety_alert(
        self,
        driver_id: int,
        alert_type: str,
        message: str,
        severity: str = "warning",
    ) -> Dict[str, Any]:
        return await self.send_to_driver(
            driver_id,
            title=f"Safety Alert: {alert_type}",
            body=message,
            data={"alert_type": alert_type, "severity": severity, "click_action": "OPEN_SAFETY"},
        )

    async def _notify(self, bot_name: str, message: str) -> None:
        try:
            await notification_service.send_bot_notification(
                bot_name=bot_name,
                template_key="system_alert",
                context={"user_name": "Push Channel", "message": message},
            )
        except Exception as exc:
            logger.debug("Push channel notification skipped: %s", exc)


push_service = PushNotificationService()
