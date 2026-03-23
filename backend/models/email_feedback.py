from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from backend.database.base import Base


class EmailFeedback(Base):
    __tablename__ = "email_feedback"
    __table_args__ = (
        Index("ix_email_feedback_message_id", "message_id"),
        Index("ix_email_feedback_bot_key", "bot_key"),
        Index("ix_email_feedback_was_correct", "was_correct"),
        Index("ix_email_feedback_routing_source", "routing_source"),
        Index("ix_email_feedback_created_at", "created_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    message_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("email_messages.id", ondelete="CASCADE"),
        nullable=False,
    )
    bot_key: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    was_correct: Mapped[bool] = mapped_column(Boolean, nullable=False)
    user_comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    routing_source: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    routing_confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    created_by: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
