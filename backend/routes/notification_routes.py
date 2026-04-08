from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from fastapi import APIRouter, HTTPException, Query, status

from backend.routes import notifications_api

router = APIRouter(prefix="/notifications", tags=["notifications"])


def _to_legacy_payload(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": item.get("id"),
        "user_id": item.get("recipient_id"),
        "message": item.get("message"),
        "is_read": bool(item.get("read")),
        "created_at": (
            item.get("sent_at").isoformat()
            if isinstance(item.get("sent_at"), datetime)
            else item.get("sent_at")
        ),
    }


def _find_notification(notification_id: str) -> dict[str, Any] | None:
    for item in notifications_api._notification_store:
        if str(item.get("id")) == str(notification_id):
            return item
    return None


@router.get("/")
async def list_notifications(
    user_id: Optional[int] = Query(None, description="User ID to filter notifications"),
    only_unread: bool = Query(False, description="Return only unread notifications"),
) -> dict[str, list[dict[str, Any]]]:
    items = [
        _to_legacy_payload(item)
        for item in reversed(notifications_api._notification_store)
        if user_id is None or item.get("recipient_id") == user_id
    ]
    if only_unread:
        items = [item for item in items if not item.get("is_read")]
    return {"notifications": items}


@router.post("/{notification_id}/read")
async def mark_notification_as_read(notification_id: str) -> dict[str, Any]:
    item = _find_notification(notification_id)
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )

    item["read"] = True
    return _to_legacy_payload(item)


@router.post("/read-all")
async def mark_all_notifications_as_read(
    user_id: int = Query(..., description="User ID to mark notifications as read"),
) -> int:
    count = 0
    for item in notifications_api._notification_store:
        if item.get("recipient_id") == user_id and not item.get("read"):
            item["read"] = True
            count += 1
    return count
