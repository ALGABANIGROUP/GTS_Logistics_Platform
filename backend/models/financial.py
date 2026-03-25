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
    UniqueConstraint,
    ForeignKey,
    Text,
    JSON,
)
from sqlalchemy.sql import func
from backend.database.base import Base


class ExpenseStatus(enum.Enum):
    PENDING = "PENDING"
    PAID = "PAID"


class Expense(Base):
    __tablename__: str = "expenses"

    id = Column(Integer, primary_key=True, index=True)

    category = Column(String, nullable=False)
    description = Column(String, nullable=True)
    vendor = Column(String, nullable=True)

    amount = Column(Float, nullable=False, default=0.0)

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

    date = Column(DateTime(timezone=True), nullable=True)

    status = Column(
        String,
        nullable=False,
        default="PENDING",
        server_default="PENDING",
    )

    dedupe_key = Column(String, nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "dedupe_key",
            name="uq_expenses_dedupe_key",
        ),
        Index("ix_expenses_status", "status"),
        Index("ix_expenses_vendor", "vendor"),
        {"extend_existing": True},  # Fix table conflict
    )

    @staticmethod
    def make_dedupe_key(
        *,
        category: str,
        amount: float,
        description: Optional[str],
        vendor: Optional[str],
        created_at_iso: str,
    ) -> str:
        import hashlib
        import json

        payload = {
            "category": category or "",
            "amount": round(float(amount), 4),
            "description": description or "",
            "vendor": vendor or "",
            "created_at": created_at_iso,
        }
        raw = json.dumps(payload, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def __repr__(self) -> str:
        return f"<Expense id={self.id} category={self.category} amount={self.amount}>"


class Invoice(Base):
    """Invoice model for billing"""
    __tablename__ = "invoices"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    invoice_number = Column(String(50), unique=True, nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="USD")
    status = Column(String(20), default="pending")  # pending, paid, overdue, cancelled
    due_date = Column(DateTime(timezone=True))
    paid_date = Column(DateTime(timezone=True))
    items = Column(JSON, default=[])  # List of invoice items
    invoice_metadata = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Payment(Base):
    """Payment model for transactions"""
    __tablename__ = "payments"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    invoice_id = Column(Integer, ForeignKey("invoices.id"))
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="USD")
    gateway = Column(String(50))  # stripe, wise, sudapay, bank
    gateway_transaction_id = Column(String(200))
    status = Column(String(20), default="pending")  # pending, completed, failed, refunded
    payment_method = Column(String(50))
    payment_metadata = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))

