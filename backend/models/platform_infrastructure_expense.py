"""Platform Infrastructure Expenses Model"""
from __future__ import annotations

import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    Index,
    Boolean,
)
from backend.database.base import Base


class ExpenseCategory(enum.Enum):
    """Platform expense categories"""
    DATABASE = "database"
    HOSTING = "hosting"
    DOMAIN = "domain"
    PHONE = "phone"
    VIRTUAL_OFFICE = "virtual_office"
    API_SERVICES = "api_services"
    CLOUD_STORAGE = "cloud_storage"
    EMAIL_SERVICE = "email_service"
    SMS_SERVICE = "sms_service"
    PAYMENT_GATEWAY = "payment_gateway"
    MONITORING = "monitoring"
    SECURITY = "security"
    BACKUP = "backup"
    CDN = "cdn"
    OTHER = "other"


class BillingFrequency(enum.Enum):
    """Billing frequency for recurring expenses"""
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    ONE_TIME = "one_time"


class PlatformInfrastructureExpense(Base):
    """Model for platform infrastructure expenses"""
    __tablename__ = "platform_infrastructure_expenses"

    id = Column(Integer, primary_key=True, index=True)
    
    # Expense details
    category = Column(String, nullable=False, index=True)
    service_name = Column(String, nullable=False)
    vendor = Column(String, nullable=False)
    description = Column(String, nullable=True)
    
    # Financial details
    amount = Column(Float, nullable=False)
    currency = Column(String, nullable=False, default="USD")
    
    # Billing details
    billing_frequency = Column(String, nullable=False, default="monthly")
    is_recurring = Column(Boolean, default=True)
    
    # Invoice/Reference
    invoice_number = Column(String, nullable=True)
    invoice_url = Column(String, nullable=True)
    attachment_path = Column(String, nullable=True)  # Uploaded file path
    
    # Dates
    billing_date = Column(DateTime(timezone=True), nullable=False)
    due_date = Column(DateTime(timezone=True), nullable=True)
    paid_date = Column(DateTime(timezone=True), nullable=True)
    
    # Status
    is_paid = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)  # For recurring services
    
    # Metadata
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Notes
    notes = Column(String, nullable=True)
    
    __table_args__ = (
        Index("ix_platform_infra_exp_category", "category"),
        Index("ix_platform_infra_exp_vendor", "vendor"),
        Index("ix_platform_infra_exp_billing_date", "billing_date"),
        Index("ix_platform_infra_exp_is_paid", "is_paid"),
        Index("ix_platform_infra_exp_is_active", "is_active"),
    )

    def __repr__(self) -> str:
        return f"<PlatformInfrastructureExpense id={self.id} service={self.service_name} amount={self.amount}>"

