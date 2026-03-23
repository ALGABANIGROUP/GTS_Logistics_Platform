from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    Index,
)
from database.base import Base  # type: ignore[import]


class MonthlyReport(Base):
    __tablename__: str = "monthly_reports"

    id = Column(Integer, primary_key=True, index=True)

    # Year-month key, e.g. "2025-01"
    period = Column(String(7), nullable=False, index=True)

    # Optional label, e.g. "January 2025"
    label = Column(String(50), nullable=True)

    total_revenue = Column(Float, nullable=False, default=0.0)
    total_expenses = Column(Float, nullable=False, default=0.0)
    net_profit = Column(Float, nullable=False, default=0.0)

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

    notes = Column(String(512), nullable=True)

    __table_args__ = (
        Index("ix_monthly_reports_period", "period"),
    )

    def __repr__(self) -> str:
        return (
            f"<MonthlyReport id={self.id} period={self.period} "
            f"net_profit={self.net_profit}>"
        )

