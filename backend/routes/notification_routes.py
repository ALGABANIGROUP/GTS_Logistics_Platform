from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database.config import get_db_async  # type: ignore[import]
from backend.models.notification import Notification  # type: ignore[import]

router = APIRouter(prefix="/notifications", tags=["notifications"])


class NotificationOut(BaseModel):
    id: int
    user_id: int
    message: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


@router.get("/", response_model=List[NotificationOut])
async def list_notifications(
    user_id: int = Query(..., description="User ID to filter notifications"),
    only_unread: bool = Query(False, description="Return only unread notifications"),
    db: AsyncSession = Depends(get_db_async),
):
    """
    List notifications for a given user.

    - If only_unread is True, returns only unread notifications.
    """

    stmt = select(Notification).where(Notification.user_id == user_id)

    if only_unread:
        stmt = stmt.where(Notification.is_read.is_(False))  # type: ignore[attr-defined]

    result = await db.execute(stmt)
    notifications = result.scalars().all()

    return notifications


@router.post("/{notification_id}/read", response_model=NotificationOut)
async def mark_notification_as_read(
    notification_id: int,
    db: AsyncSession = Depends(get_db_async),
):
    """
    Mark a single notification as read.
    """

    stmt = select(Notification).where(Notification.id == notification_id)
    result = await db.execute(stmt)
    notification: Optional[Notification] = result.scalar_one_or_none()

    if notification is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )

    # Use setattr to avoid Pylance complaining about Column[bool] type
    setattr(notification, "is_read", True)
    await db.commit()
    await db.refresh(notification)

    return notification


@router.post("/read-all", response_model=int)
async def mark_all_notifications_as_read(
    user_id: int = Query(..., description="User ID to mark notifications as read"),
    db: AsyncSession = Depends(get_db_async),
):
    """
    Mark all notifications for a given user as read.

    Returns the number of notifications affected.
    """

    stmt = select(Notification).where(
        Notification.user_id == user_id,  # type: ignore[attr-defined]
        Notification.is_read.is_(False),  # type: ignore[attr-defined]
    )
    result = await db.execute(stmt)
    notifications = result.scalars().all()

    count = 0
    for n in notifications:
        setattr(n, "is_read", True)
        count += 1

    if count > 0:
        await db.commit()

    return count

