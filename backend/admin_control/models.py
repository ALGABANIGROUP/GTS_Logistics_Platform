from __future__ import annotations

from datetime import datetime, date
from typing import Optional

from sqlalchemy import (
    String,
    DateTime,
    Text,
    ForeignKey,
    Integer,
    Boolean,
    Date,
    JSON,
)
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from database.base import Base


class OrgUnit(Base):
    __tablename__ = "org_units"  # type: ignore[assignment]

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    parent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("org_units.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    metadata_json: Mapped[Optional[dict]] = mapped_column("metadata", JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)


class OrgMembership(Base):
    __tablename__ = "org_memberships"  # type: ignore[assignment]

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    org_unit_id: Mapped[int] = mapped_column(ForeignKey("org_units.id", ondelete="CASCADE"), primary_key=True)
    title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    level: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    start_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)


class Role(Base):
    """DEPRECATED: This role model is deprecated. Use backend.models.subscription.Role instead."""
    __tablename__ = "roles_deprecated"  # type: ignore[assignment]

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    priority: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    parent_role_id: Mapped[Optional[int]] = mapped_column(ForeignKey("roles_deprecated.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)


class Permission(Base):
    __tablename__ = "permissions"  # type: ignore[assignment]

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    scope_type: Mapped[str] = mapped_column(String(20), nullable=False)
    scope_key: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class RolePermission(Base):
    """DEPRECATED: Use the role system in backend.models.subscription instead."""
    __tablename__ = "role_permissions"  # type: ignore[assignment]

    role_id: Mapped[int] = mapped_column(ForeignKey("roles_deprecated.id", ondelete="CASCADE"), primary_key=True)
    permission_id: Mapped[int] = mapped_column(ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True)


class PermissionTemplate(Base):
    __tablename__ = "permission_templates"  # type: ignore[assignment]

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class TemplatePermission(Base):
    __tablename__ = "template_permissions"  # type: ignore[assignment]

    template_id: Mapped[int] = mapped_column(
        ForeignKey("permission_templates.id", ondelete="CASCADE"), primary_key=True
    )
    permission_id: Mapped[int] = mapped_column(ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True)


class UserRole(Base):
    """DEPRECATED: Use the role system in backend.models.subscription instead."""
    __tablename__ = "user_roles"  # type: ignore[assignment]

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles_deprecated.id", ondelete="CASCADE"), primary_key=True)
    org_unit_id: Mapped[Optional[int]] = mapped_column(ForeignKey("org_units.id"), nullable=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class Session(Base):
    __tablename__ = "sessions"  # type: ignore[assignment]

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_seen_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    ip: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    revoked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)


class AuditLog(Base):
    __tablename__ = "audit_logs"  # type: ignore[assignment]

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    actor_user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    target_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    target_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    diff_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    ip: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    severity: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)


class AlertRule(Base):
    __tablename__ = "alert_rules"  # type: ignore[assignment]

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    severity: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    condition_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    channels_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

