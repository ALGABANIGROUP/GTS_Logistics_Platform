from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import String, Boolean, DateTime, UniqueConstraint, Index, Enum, JSON
import enum

class TenantPlan(str, enum.Enum):
    """Subscription plans"""
    FREE_TRIAL = "free_trial"
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class TenantStatus(str, enum.Enum):
    """Tenant operational status"""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    TRIAL_EXPIRED = "trial_expired"
    PENDING_VERIFICATION = "pending_verification"


class BillingStatus(str, enum.Enum):
    """Billing status"""
    NOT_REQUIRED = "not_required"
    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELLED = "cancelled"

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from backend.database.base import Base


class Tenant(Base):
    """Multi-tenant organization record.

    - `id`: stable string identifier (UUID or slug) up to 64 chars
    - `subdomain`: unique subdomain used for routing (e.g., company-a)
    - `name`: display name for the tenant
    - `status`: operational status (active, suspended, etc.)
    - `plan`: subscription plan (free_trial, basic, professional, enterprise)
    - `billing_status`: payment status (not_required for free trial)
    """

    __tablename__ = "tenants"
    __table_args__ = (
        UniqueConstraint("subdomain", name="uq_tenants_subdomain"),
        Index("ix_tenants_is_default", "is_default"),
        UniqueConstraint("owner_email", name="uq_tenants_owner_email"),
        Index("ix_tenants_status", "status"),
        Index("ix_tenants_subdomain", "subdomain"),
        {"extend_existing": True},
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    subdomain: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_default: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Status & Plan
    status: Mapped[str] = mapped_column(
        Enum(TenantStatus, native_enum=False, length=50),
        nullable=False,
        default=TenantStatus.ACTIVE
    )

    # Subscription & Billing
    plan: Mapped[str] = mapped_column(
        Enum(TenantPlan, native_enum=False, length=50),
        nullable=False,
        default=TenantPlan.FREE_TRIAL
    )
    trial_ends_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    billing_status: Mapped[str] = mapped_column(
        Enum(BillingStatus, native_enum=False, length=50),
        nullable=False,
        default=BillingStatus.NOT_REQUIRED
    )

    # Owner info (for signup)
    owner_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    owner_user_id: Mapped[Optional[int]] = mapped_column(nullable=True)

    # Quotas (JSON field for flexibility)
    quotas: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, default=dict)

    # Metadata
    settings_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True, default=dict)
    email_verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

