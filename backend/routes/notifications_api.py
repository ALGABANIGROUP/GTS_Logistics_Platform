"""
Notifications API - Send alerts to drivers and users
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.services.notification_service import notification_service

router = APIRouter(prefix="/api/v1/notifications", tags=["Notifications"])


class NotificationCreate(BaseModel):
    recipient_id: int
    type: str  # weather_alert, shipment_update, system_notification
    severity: str  # low, medium, high, critical
    title: str
    message: str
    shipment_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class NotificationOut(BaseModel):
    id: str
    recipient_id: int
    type: str
    severity: str
    title: str
    message: str
    sent_at: datetime
    delivered: bool
    read: bool


@router.get("/", response_model=List[NotificationOut])
async def get_notifications(
    limit: int = 50,
    unread_only: bool = False
) -> List[NotificationOut]:
    """Get notifications for the current user"""
    # Mock response - in production this would query the database
    return []


@router.post("", response_model=NotificationOut)
async def create_notification(notification: NotificationCreate) -> NotificationOut:
    """Create a new notification"""
    notification_id = f"NOTIF-{int(datetime.utcnow().timestamp())}"
    
    return NotificationOut(
        id=notification_id,
        recipient_id=notification.recipient_id,
        type=notification.type,
        severity=notification.severity,
        title=notification.title,
        message=notification.message,
        sent_at=datetime.utcnow(),
        delivered=True,
        read=False,
    )


@router.post("/send", response_model=NotificationOut)
async def send_notification(notification: NotificationCreate) -> NotificationOut:
    """
    Send notification to driver/user

    Supports multiple channels:
    - Email (via EmailService)
    - SMS (via QUO API - TODO)
    - Push notification (TODO)
    - In-app notification
    """
    try:
        # Map severity to priority
        priority_map = {
            "low": "low",
            "medium": "medium",
            "high": "high",
            "critical": "critical"
        }

        # Send notification using the service
        result = await notification_service.send_notification(
            recipient_id=notification.recipient_id,
            notification_type=notification.type,
            template_key="system_alert",  # Use system alert template for custom notifications
            template_data={"message": notification.message},
            priority=priority_map.get(notification.severity, "medium"),
            channels=["email"]  # Default to email for now
        )

        return NotificationOut(
            id=result["notification_id"],
            recipient_id=notification.recipient_id,
            type=notification.type,
            severity=notification.severity,
            title=notification.title,
            message=notification.message,
            sent_at=datetime.utcnow(),
            delivered=True,  # Assume delivered for now
            read=False,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send notification: {str(e)}")


@router.post("/schedule")
async def schedule_notification(data: Dict[str, Any]) -> Dict[str, Any]:
    """Schedule a notification for later delivery"""
    return {
        "success": True,
        "scheduled_for": data.get("scheduled_for"),
        "notification_id": f"NOTIF-SCHED-{int(datetime.utcnow().timestamp())}"
    }


@router.get("/user/{user_id}", response_model=List[NotificationOut])
async def get_user_notifications(user_id: int, unread_only: bool = False) -> List[NotificationOut]:
    """Get all notifications for a user"""
    # Mock response
    return [
        NotificationOut(
            id=f"NOTIF-{user_id}-1",
            recipient_id=user_id,
            type="weather_alert",
            severity="high",
            title="Weather Alert - Vancouver",
            message="Heavy rain expected on your route. Drive with caution.",
            sent_at=datetime.utcnow(),
            delivered=True,
            read=False,
        )
    ]


@router.post("/mark-read/{notification_id}")
async def mark_notification_read(notification_id: str) -> Dict[str, Any]:
    """Mark notification as read"""
    return {
        "success": True,
        "notification_id": notification_id,
        "read_at": datetime.utcnow().isoformat(),
    }


@router.get("/shipment/{shipment_id}/alerts", response_model=List[NotificationOut])
async def get_shipment_alerts(shipment_id: str) -> List[NotificationOut]:
    """Get all alerts for a specific shipment"""
    # Mock response
    return [
        NotificationOut(
            id=f"NOTIF-{shipment_id}-weather",
            recipient_id=1,
            type="weather_alert",
            severity="medium",
            title=f"Weather Alert - Shipment {shipment_id}",
            message="Weather conditions may affect delivery time.",
            sent_at=datetime.utcnow(),
            delivered=True,
            read=False,
        )
    ]
