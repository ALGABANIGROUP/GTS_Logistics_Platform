from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Boolean,
    Index,
)
from backend.database.base import Base


class MessageLog(Base):
    __tablename__ = "message_logs"  # type: ignore[assignment]

    id = Column(Integer, primary_key=True, index=True)

    # Who sent the message (email or system identifier)
    sender = Column(String(255), nullable=True)

    # Who received the message (email, user id, etc.)
    recipient = Column(String(255), nullable=True)

    # Optional subject/title (for emails, notifications, etc.)
    subject = Column(String(255), nullable=True)

    # Main body/content of the message
    body = Column(Text, nullable=True)

    # Channel: email, sms, in_app, webhook, etc.
    channel = Column(String(50), nullable=True)

    # Status: sent, failed, queued, etc.
    status = Column(String(50), nullable=False, default="sent")

    # Optional error message if status == failed
    error_message = Column(Text, nullable=True)

    # Optional correlation or external id
    correlation_id = Column(String(255), nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
    )

    __table_args__ = (
        Index("ix_message_logs_recipient", "recipient"),
        Index("ix_message_logs_channel", "channel"),
        Index("ix_message_logs_status", "status"),
    )

    def __repr__(self) -> str:
        return (
            f"<MessageLog id={self.id} channel={self.channel} "
            f"recipient={self.recipient} status={self.status}>"
        )

