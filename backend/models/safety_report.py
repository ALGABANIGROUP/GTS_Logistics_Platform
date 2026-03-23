from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Text,
    Boolean,
    Index,
)
from backend.database.base import Base


class SafetyReport(Base):
    __tablename__ = "safety_reports"  # type: ignore[assignment]

    id = Column(Integer, primary_key=True, index=True)

    # Optional: related vehicle, driver, or asset identifiers
    vehicle_id = Column(String(64), nullable=True, index=True)
    driver_name = Column(String(255), nullable=True)

    # Type of safety incident: "near_miss", "accident", "inspection", etc.
    incident_type = Column(String(100), nullable=False, default="general")

    # Severity: "low", "medium", "high", "critical"
    severity = Column(String(50), nullable=False, default="low")

    # Short title and detailed description
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)

    # Location or route information (optional)
    location = Column(String(255), nullable=True)
    route_reference = Column(String(255), nullable=True)

    # Time of occurrence and when it was reported
    occurred_at = Column(DateTime(timezone=True), nullable=True)
    reported_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
    )

    # Status: "open", "in_review", "closed"
    status = Column(String(50), nullable=False, default="open")

    # Whether corrective actions have been taken
    corrective_action_taken = Column(Boolean, nullable=False, default=False)

    corrective_action_notes = Column(Text, nullable=True)

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
        Index("ix_safety_reports_vehicle_id", "vehicle_id"),
        Index("ix_safety_reports_severity", "severity"),
        Index("ix_safety_reports_status", "status"),
        Index("ix_safety_reports_incident_type", "incident_type"),
    )

    def __repr__(self) -> str:
        return (
            f"<SafetyReport id={self.id} incident_type={self.incident_type} "
            f"severity={self.severity} status={self.status}>"
        )

