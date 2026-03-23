from __future__ import annotations

import enum

from datetime import datetime
from typing import Optional

from sqlalchemy import Enum, String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from database.base import Base


class IssueSeverity(str, enum.Enum):
    critical = "critical"
    high = "high"
    medium = "medium"
    low = "low"


class IssueStatus(str, enum.Enum):
    open = "open"
    in_progress = "in_progress"
    resolved = "resolved"
    closed = "closed"


class AIBotIssue(Base):
    __tablename__ = "ai_bot_issues"
    __table_args__ = {"extend_existing": True}

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    bot_name: Mapped[str] = mapped_column(String, nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[IssueSeverity] = mapped_column(
        Enum(IssueSeverity, native_enum=False),
        nullable=False,
        default=IssueSeverity.low,
        server_default=IssueSeverity.low.value,
    )
    status: Mapped[IssueStatus] = mapped_column(
        Enum(IssueStatus, native_enum=False),
        nullable=False,
        default=IssueStatus.open,
        server_default=IssueStatus.open.value,
    )
    reported_by: Mapped[str] = mapped_column(String(255), nullable=False, default="system", server_default="system")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

