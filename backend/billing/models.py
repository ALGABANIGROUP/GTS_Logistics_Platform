from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from backend.database.base import Base


class Plan(Base):
    __tablename__ = "plans" # type: ignore

    key = Column(String(50), primary_key=True)
    name_ar = Column(String(120), nullable=False)
    name_en = Column(String(120), nullable=False)
    description = Column(Text, nullable=True)
    price_monthly = Column(Numeric(12, 2), nullable=False, default=0)
    price_yearly = Column(Numeric(12, 2), nullable=False, default=0)
    features = Column(JSON, nullable=True)
    limits = Column(JSON, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    entitlements = relationship(
        "PlanEntitlement",
        back_populates="plan",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class PlanEntitlement(Base):
    __tablename__ = "plan_entitlements" # type: ignore
    __table_args__ = (UniqueConstraint("plan_id", "key", name="uq_plan_entitlements_plan_key"),)

    id = Column(Integer, primary_key=True)
    plan_id = Column(String(50), ForeignKey("plans.key", ondelete="CASCADE"), nullable=False)
    key = Column(String(120), nullable=False)
    value_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    plan = relationship("Plan", back_populates="entitlements")


class Subscription(Base):
    __tablename__ = "subscriptions" # type: ignore

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=True)
    partner_id = Column(Integer, nullable=True)
    plan_id = Column(String(50), ForeignKey("plans.key"), nullable=False)
    status = Column(String(32), nullable=False, default="active")
    source = Column(String(32), nullable=True)
    start_at = Column(DateTime(timezone=True), nullable=True)
    end_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    plan = relationship("Plan", lazy="selectin")
    addons = relationship(
        "SubscriptionAddon",
        back_populates="subscription",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class SubscriptionAddon(Base):
    __tablename__ = "subscription_addons" # type: ignore
    __table_args__ = (UniqueConstraint("subscription_id", "addon_code", name="uq_subscription_addons_code"),)

    id = Column(Integer, primary_key=True)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id", ondelete="CASCADE"), nullable=False)
    addon_code = Column(String(64), nullable=False)
    enabled = Column(Boolean, nullable=False, default=True)

    # ✅ Fix: "metadata" is reserved in SQLAlchemy Declarative models
    # Keep the DB column name as "metadata"
    extra_data = Column("metadata", JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    subscription = relationship("Subscription", back_populates="addons")

