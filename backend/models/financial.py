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
from backend.models.invoices import Invoice
from backend.models.payment import Payment


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


# Use the canonical billing models to avoid duplicate SQLAlchemy registry entries
# for Invoice/Payment when this module is imported by finance routes.

