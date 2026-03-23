from __future__ import annotations

from datetime import datetime
from typing import ClassVar, Optional

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
)
from database.base import Base  # type: ignore[import]


class Notification(Base):
    __tablename__: ClassVar[str] = "notifications"

    id = Column(Integer, primary_key=True, index=True)

    # Optional user id (if the notification is tied to a specific user)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Short title or subject of the notification
    title = Column(String(255), nullable=False)

    # Detailed message body
    message = Column(String(1024), nullable=False)

    # Optional channel: email, in_app, sms, etc.
    channel = Column(String(50), nullable=True)

    # Read/unread flag
    is_read = Column(
        Boolean,
        nullable=False,
        default=False,
        server_default="0",
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
    )

    read_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    __table_args__ = (
        Index("ix_notifications_user_id", "user_id"),
        Index("ix_notifications_is_read", "is_read"),
    )

    def __repr__(self) -> str:
        return (
            f"<Notification id={self.id} user_id={self.user_id} "
            f"is_read={self.is_read}>"
        )

