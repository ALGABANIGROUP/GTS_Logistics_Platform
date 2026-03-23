from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple

from pydantic import BaseModel, Field

from backend.database.session import async_session

try:
    from models.financial import Expense  # type: ignore
except Exception:
    Expense = None

try:
    from sqlalchemy import text, select, func
except Exception:
    text = None  # type: ignore
    select = None  # type: ignore
    func = None  # type: ignore


class PeriodWindow(BaseModel):
    start: Optional[str] = None
    end: Optional[str] = None
    label: Optional[str] = None


class ShipmentsSnapshot(BaseModel):
    total: Optional[int] = None
    in_transit: Optional[int] = None
    delivered: Optional[int] = None
    delayed: Optional[int] = None


class FinanceSnapshot(BaseModel):
    revenue_total: Optional[float] = None
    expenses_total: Optional[float] = None
    paid: Optional[float] = None
    pending: Optional[float] = None


class KPISnapshot(BaseModel):
    shipments_total: Optional[int] = None
    on_time_rate: Optional[float] = None
    profit: Optional[float] = None


class SourcesSnapshot(BaseModel):
    shipments: Optional[str] = None
    finance: Optional[str] = None


class COOSnapshot(BaseModel):
    period: PeriodWindow = Field(default_factory=PeriodWindow)
    shipments: ShipmentsSnapshot = Field(default_factory=ShipmentsSnapshot)
    finance: FinanceSnapshot = Field(default_factory=FinanceSnapshot)
    kpis: KPISnapshot = Field(default_factory=KPISnapshot)
    sources: SourcesSnapshot = Field(default_factory=SourcesSnapshot)
    generated_at: str
    trace_id: Optional[str] = None


def _period_window(period: str, start_date: Optional[str], end_date: Optional[str]) -> PeriodWindow:
    now = datetime.now(timezone.utc)
    label = (period or "custom").strip().lower()
    if start_date or end_date:
        return PeriodWindow(start=start_date, end=end_date, label=label)
    if label == "day":
        start = now - timedelta(days=1)
    elif label == "month":
        start = now - timedelta(days=30)
    else:
        start = now - timedelta(days=7)
        label = "week"
    return PeriodWindow(start=start.isoformat(), end=now.isoformat(), label=label)


async def _load_shipments(session) -> Tuple[ShipmentsSnapshot, str]:
    if text is None:
        return ShipmentsSnapshot(), "fallback"
    try:
        total = await session.execute(text("SELECT COUNT(*) FROM shipments"))
        total_count = int(total.scalar() or 0)
        status_rows = await session.execute(
            text("SELECT status, COUNT(*) FROM shipments GROUP BY status")
        )
        in_transit = delivered = delayed = 0
        for status, count in status_rows.all():
            label = str(status or "").strip().lower()
            if label in {"in_transit", "in-progress", "in_progress", "on_the_way"}:
                in_transit += int(count or 0)
            elif label in {"delivered", "complete", "completed"}:
                delivered += int(count or 0)
            elif label in {"delayed", "late"}:
                delayed += int(count or 0)
        return (
            ShipmentsSnapshot(
                total=total_count,
                in_transit=in_transit,
                delivered=delivered,
                delayed=delayed,
            ),
            "db",
        )
    except Exception:
        return ShipmentsSnapshot(), "fallback"


async def _load_finance(session) -> Tuple[FinanceSnapshot, str]:
    if Expense is None or select is None or func is None:
        return FinanceSnapshot(), "fallback"
    try:
        total_q = await session.execute(select(func.coalesce(func.sum(Expense.amount), 0.0)))
        total_expenses = float(total_q.scalar() or 0.0)

        by_status_q = await session.execute(
            select(Expense.status, func.coalesce(func.sum(Expense.amount), 0.0)).group_by(Expense.status)
        )
        paid = pending = 0.0
        for status, amount in by_status_q.all():
            label = str(status or "").upper()
            if label == "PAID":
                paid = float(amount or 0.0)
            elif label == "PENDING":
                pending = float(amount or 0.0)

        return (
            FinanceSnapshot(
                revenue_total=None,
                expenses_total=round(total_expenses, 2),
                paid=round(paid, 2),
                pending=round(pending, 2),
            ),
            "db",
        )
    except Exception:
        return FinanceSnapshot(), "fallback"


def _build_kpis(shipments: ShipmentsSnapshot, finance: FinanceSnapshot) -> KPISnapshot:
    shipments_total = shipments.total
    on_time_rate = None
    if shipments_total is not None and shipments_total > 0 and shipments.delivered is not None:
        on_time_rate = round(float(shipments.delivered) / float(shipments_total), 4)

    profit = None
    if finance.revenue_total is not None and finance.expenses_total is not None:
        profit = round(finance.revenue_total - finance.expenses_total, 2)

    return KPISnapshot(
        shipments_total=shipments_total,
        on_time_rate=on_time_rate,
        profit=profit,
    )


async def build_coo_snapshot(
    period: str = "week",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    trace_id: Optional[str] = None,
) -> COOSnapshot:
    trace_id = trace_id or uuid.uuid4().hex
    window = _period_window(period, start_date, end_date)
    shipments = ShipmentsSnapshot()
    finance = FinanceSnapshot()
    sources = SourcesSnapshot(shipments="fallback", finance="fallback")

    if async_session is not None:
        async with async_session() as session:
            shipments, shipments_source = await _load_shipments(session)
            finance, finance_source = await _load_finance(session)
            sources = SourcesSnapshot(shipments=shipments_source, finance=finance_source)

    kpis = _build_kpis(shipments, finance)
    return COOSnapshot(
        period=window,
        shipments=shipments,
        finance=finance,
        kpis=kpis,
        sources=sources,
        generated_at=datetime.now(timezone.utc).isoformat(),
        trace_id=trace_id,
    )

