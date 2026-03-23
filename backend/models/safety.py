from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    Text,
    ForeignKey,
    Index,
)
from sqlalchemy.orm import relationship
from backend.database.base import Base


class SafetyEvent(Base):
    __tablename__: str = "safety_events"

    id = Column(Integer, primary_key=True, index=True)

    # Optional link to a driver or user
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Optional link to vehicle/asset identifier
    vehicle_id = Column(String(64), nullable=True, index=True)

    # Category of safety event: "inspection", "violation", "incident", etc.
    category = Column(String(100), nullable=False, default="general")

    # Severity level: "low", "medium", "high", "critical"
    severity = Column(String(50), nullable=False, default="low")

    # Short title and detailed description
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)

    # Optional location / route information
    location = Column(String(255), nullable=True)
    route_reference = Column(String(255), nullable=True)

    # When the event occurred and when it was logged
    occurred_at = Column(DateTime(timezone=True), nullable=True)
    logged_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
    )

    # Status: "open", "in_review", "resolved"
    status = Column(String(50), nullable=False, default="open")

    # Acknowledgement workflow
    acknowledged = Column(Boolean, nullable=False, default=False)
    acknowledged_by = Column(String(255), nullable=True)
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
    )

    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
    )

    __table_args__ = (
        Index("ix_safety_events_user_id", "user_id"),
        Index("ix_safety_events_vehicle_id", "vehicle_id"),
        Index("ix_safety_events_category", "category"),
        Index("ix_safety_events_severity", "severity"),
        Index("ix_safety_events_status", "status"),
    )

    def __repr__(self) -> str:
        return (
            f"<SafetyEvent id={self.id} category={self.category} "
            f"severity={self.severity} status={self.status}>"
        )

