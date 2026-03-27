from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from backend.database.base import Base


class HealthSnapshot(Base):
    __tablename__ = "health_snapshots"  # type: ignore
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, nullable=True)  # For multi-tenant
    timestamp = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    # System metrics
    cpu_percent = Column(Float, nullable=True)
    memory_percent = Column(Float, nullable=True)
    disk_percent = Column(Float, nullable=True)
    load_average = Column(Float, nullable=True)

    # Database metrics
    db_connections = Column(Integer, nullable=True)
    db_latency_ms = Column(Float, nullable=True)

    # Application metrics
    active_users = Column(Integer, nullable=True)
    active_sessions = Column(Integer, nullable=True)

    # Bot metrics (JSON)
    bot_metrics = Column(JSON, nullable=True)  # {"bot_name": {"latency": 100, "errors": 0, "status": "healthy"}}

    # Overall status
    overall_status = Column(String(32), nullable=False, default="unknown")  # healthy, degraded, critical

    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)


class Incident(Base):
    __tablename__ = "incidents"  # type: ignore
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, nullable=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    severity = Column(String(32), nullable=False, default="warning")  # info, warning, error, critical
    status = Column(String(32), nullable=False, default="open")  # open, investigating, resolved, closed

    # What triggered it
    component = Column(String(100), nullable=False)  # bot, db, system, api
    component_id = Column(String(100), nullable=True)  # bot name, endpoint, etc.


    # Metrics at time of incident
    metrics_snapshot = Column(JSON, nullable=True)

    # Enterprise observability fields
    root_cause = Column(String(50), nullable=True)
    last_remediation = Column(String(100), nullable=True)

    # Confidence in root cause (0-1)
    root_cause_confidence = Column(Float, default=0.5)

    # Resolution
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    resolution_notes = Column(Text, nullable=True)

    # Auto-remediation
    auto_remediated = Column(Boolean, nullable=False, default=False)

    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    remediation_actions = relationship(
        lambda: RemediationAction,
        back_populates="incident",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class RemediationAction(Base):
    __tablename__ = "remediation_actions"  # type: ignore
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, nullable=True)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=True)

    # Action details
    action_type = Column(String(100), nullable=False)  # restart_bot, clear_cache, rotate_logs, etc.
    action_params = Column(JSON, nullable=True)  # {"bot_name": "finance_bot", "reason": "high_latency"}

    # Execution
    status = Column(String(32), nullable=False, default="pending")  # pending, running, completed, failed
    executed_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Results
    success = Column(Boolean, nullable=True)
    output = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)

    # Runbook reference
    runbook_id = Column(String(100), nullable=True)  # Reference to predefined runbook

    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    incident = relationship(
        lambda: Incident,
        back_populates="remediation_actions",
        passive_deletes=True,
    )


class MaintenanceAuditLog(Base):
    __tablename__ = "maintenance_audit_log"  # type: ignore
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, nullable=True)
    user_id = Column(Integer, nullable=True)  # Who triggered the action
    action = Column(String(100), nullable=False)  # snapshot_created, incident_opened, remediation_executed, etc.
    resource_type = Column(String(50), nullable=True)  # bot, system, db, etc.
    resource_id = Column(String(100), nullable=True)  # bot name, component id

    # Details
    details = Column(JSON, nullable=True)  # Additional context
    old_value = Column(JSON, nullable=True)  # For changes
    new_value = Column(JSON, nullable=True)  # For changes

    # Metadata
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)


class AlertRule(Base):
    __tablename__ = "maintenance_alert_rules"  # type: ignore
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, nullable=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    enabled = Column(Boolean, nullable=False, default=True)

    # Rule conditions
    metric_name = Column(String(100), nullable=False)  # cpu_percent, bot_latency, etc.
    operator = Column(String(10), nullable=False)  # >, <, >=, <=, ==
    threshold = Column(Float, nullable=False)

    # Time window
    time_window_minutes = Column(Integer, nullable=False, default=5)

    # Actions
    severity = Column(String(32), nullable=False, default="warning")
    auto_remediate = Column(Boolean, nullable=False, default=False)
    remediation_runbook = Column(String(100), nullable=True)

    # Notification channels
    notify_operations_manager = Column(Boolean, nullable=False, default=True)
    notify_email = Column(String(255), nullable=True)  # Email addresses

    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
