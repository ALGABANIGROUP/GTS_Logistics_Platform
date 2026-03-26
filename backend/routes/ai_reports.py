from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict

from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.session import get_async_session
from backend.security.auth import get_current_user

router = APIRouter(prefix="/ai/reports", tags=["AI Reports"])


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _period_start(period: str) -> datetime:
    now = _utcnow()
    mapping = {
        "weekly": timedelta(days=7),
        "monthly": timedelta(days=30),
        "quarterly": timedelta(days=90),
        "yearly": timedelta(days=365),
    }
    return now - mapping.get(period, timedelta(days=30))


async def _sum_completed_payments(session: AsyncSession, start_at: datetime) -> float:
    query = text(
        """
        SELECT COALESCE(SUM(amount), 0)
        FROM payments
        WHERE LOWER(CAST(status AS TEXT)) = 'completed'
          AND created_at >= :start_at
        """
    )
    result = await session.execute(query, {"start_at": start_at})
    return float(result.scalar() or 0.0)


async def _shipment_stats(session: AsyncSession, start_at: datetime) -> Dict[str, int]:
    query = text(
        """
        SELECT
          COUNT(*) AS total,
          SUM(CASE WHEN LOWER(COALESCE(status, '')) IN ('completed', 'delivered') THEN 1 ELSE 0 END) AS completed,
          SUM(CASE WHEN LOWER(COALESCE(status, '')) IN ('pending', 'assigned', 'in_transit', 'delayed') THEN 1 ELSE 0 END) AS active,
          SUM(CASE WHEN LOWER(COALESCE(status, '')) IN ('failed', 'cancelled') THEN 1 ELSE 0 END) AS failed
        FROM shipments_enhanced
        WHERE created_at >= :start_at
        """
    )
    try:
        row = (await session.execute(query, {"start_at": start_at})).mappings().one()
    except Exception:
        return {
            "total": 0,
            "completed": 0,
            "active": 0,
            "failed": 0,
        }
    return {
        "total": int(row["total"] or 0),
        "completed": int(row["completed"] or 0),
        "active": int(row["active"] or 0),
        "failed": int(row["failed"] or 0),
    }


async def _bot_metrics(session: AsyncSession, start_at: datetime) -> Dict[str, Any]:
    query = text(
        """
        SELECT
          COUNT(*) AS total_runs,
          SUM(CASE WHEN LOWER(COALESCE(status, '')) = 'completed' THEN 1 ELSE 0 END) AS completed_runs,
          SUM(CASE WHEN LOWER(COALESCE(status, '')) IN ('failed', 'error', 'cancelled') THEN 1 ELSE 0 END) AS failed_runs
        FROM bot_runs
        WHERE started_at >= :start_at
        """
    )
    try:
        row = (await session.execute(query, {"start_at": start_at})).mappings().one()
    except Exception:
        row = {"total_runs": 0, "completed_runs": 0, "failed_runs": 0}
    try:
        active_bots = await session.execute(text("SELECT COUNT(*) FROM bot_registry WHERE enabled = true"))
        active_bots_count = int(active_bots.scalar() or 0)
    except Exception:
        active_bots_count = 0
    total_runs = int(row["total_runs"] or 0)
    completed_runs = int(row["completed_runs"] or 0)
    failed_runs = int(row["failed_runs"] or 0)
    success_rate = round((completed_runs / total_runs) * 100.0, 1) if total_runs else 0.0
    return {
        "active_bots": active_bots_count,
        "total_runs": total_runs,
        "failed_runs": failed_runs,
        "success_rate": f"{success_rate:.1f}%",
        "average_response_time": "-",
    }


@router.get("/general")
async def general_analysis(
    period: str = Query("monthly"),
    from_month: str | None = Query(None),
    to_month: str | None = Query(None),
    session: AsyncSession = Depends(get_async_session),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    del from_month, to_month, current_user
    start_at = _period_start(period)

    revenue = await _sum_completed_payments(session, start_at)
    shipment_stats = await _shipment_stats(session, start_at)
    bot_stats = await _bot_metrics(session, start_at)

    completed = shipment_stats["completed"]
    total = shipment_stats["total"]
    on_time_rate = round((completed / total) * 100.0, 1) if total else 0.0
    expenses_estimate = 0.0
    profit = revenue - expenses_estimate
    profit_margin = round((profit / revenue) * 100.0, 1) if revenue else 0.0

    return {
        "financial_analysis": {
            "total_income": round(revenue, 2),
            "total_revenue": round(revenue, 2),
            "total_expenses": round(expenses_estimate, 2),
            "profit": round(profit, 2),
            "profit_margin": f"{profit_margin:.1f}%",
        },
        "operational_metrics": {
            "total_shipments": total,
            "completed_shipments": completed,
            "active_shipments": shipment_stats["active"],
            "failed_shipments": shipment_stats["failed"],
            "on_time_rate": f"{on_time_rate:.1f}%",
        },
        "ai_bots_performance": bot_stats,
        "generated_at": _utcnow().isoformat(),
        "period": period,
    }


@router.get("/weekly")
async def weekly_reports(
    since_days: int = Query(7, ge=1, le=90),
    session: AsyncSession = Depends(get_async_session),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    del current_user
    now = _utcnow()
    start_at = now - timedelta(days=since_days)

    revenue = await _sum_completed_payments(session, start_at)
    shipment_stats = await _shipment_stats(session, start_at)
    previous_start = start_at - timedelta(days=since_days)
    previous_revenue = await _sum_completed_payments(session, previous_start)
    previous_shipments = await _shipment_stats(session, previous_start)

    def _growth(current: float, previous: float) -> str:
        if not previous:
            return "0.0%"
        return f"{(((current - previous) / previous) * 100.0):.1f}%"

    return {
        "period": f"Last {since_days} days",
        "summary": {
            "new_shipments": shipment_stats["total"],
            "completed_shipments": shipment_stats["completed"],
            "revenue": round(revenue, 2),
            "expenses": 0.0,
        },
        "trends": {
            "shipment_growth": _growth(float(shipment_stats["total"]), float(previous_shipments["total"])),
            "revenue_growth": _growth(revenue, previous_revenue),
            "efficiency_improvement": _growth(
                float(shipment_stats["completed"]),
                float(previous_shipments["completed"]),
            ),
        },
        "generated_at": now.isoformat(),
    }


__all__ = ["router"]
