from __future__ import annotations

import re
from datetime import date, datetime, timezone
from typing import Any, Optional

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_async_session

router = APIRouter(prefix="/coordinator")
_TABLE_NAME_RE = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")


async def _table_exists(db: AsyncSession, table_name: str) -> bool:
    if not _TABLE_NAME_RE.match(table_name):
        return False
    result = await db.execute(
        text(
            """
            SELECT EXISTS (
                SELECT 1
                FROM information_schema.tables
                WHERE table_schema = 'public' AND table_name = :table_name
            )
            """
        ),
        {"table_name": table_name},
    )
    return bool(result.scalar())


async def _column_exists(db: AsyncSession, table_name: str, column_name: str) -> bool:
    if not _TABLE_NAME_RE.match(table_name):
        return False
    result = await db.execute(
        text(
            """
            SELECT EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_schema = 'public'
                  AND table_name = :table_name
                  AND column_name = :column_name
            )
            """
        ),
        {"table_name": table_name, "column_name": column_name},
    )
    return bool(result.scalar())


async def _count_rows(db: AsyncSession, table_name: str, where_sql: str = "", params: Optional[dict[str, Any]] = None) -> int:
    if not await _table_exists(db, table_name):
        return 0
    query = f"SELECT COUNT(*) FROM {table_name}"
    if where_sql:
        query += f" WHERE {where_sql}"
    result = await db.execute(text(query), params or {})
    return int(result.scalar() or 0)


@router.get("/dashboard/metrics")
async def get_dashboard_metrics(db: AsyncSession = Depends(get_async_session)):
    today = date.today()
    shipments_total = await _count_rows(db, "shipments")

    completed_today = 0
    if await _column_exists(db, "shipments", "completed_at"):
        completed_today = await _count_rows(
            db,
            "shipments",
            "DATE(completed_at) = :today",
            {"today": today},
        )

    monthly_revenue = 0.0
    daily_revenue = 0.0
    if await _table_exists(db, "payments") and await _column_exists(db, "payments", "amount"):
        if await _column_exists(db, "payments", "created_at"):
            month_start = today.replace(day=1)
            daily_revenue_result = await db.execute(
                text("SELECT COALESCE(SUM(amount), 0) FROM payments WHERE DATE(created_at) = :today"),
                {"today": today},
            )
            monthly_revenue_result = await db.execute(
                text("SELECT COALESCE(SUM(amount), 0) FROM payments WHERE DATE(created_at) >= :month_start"),
                {"month_start": month_start},
            )
            daily_revenue = float(daily_revenue_result.scalar() or 0)
            monthly_revenue = float(monthly_revenue_result.scalar() or 0)

    return {
        "metrics": {
            "shipments": {
                "completed_today": completed_today,
                "delayed_shipments": 0,
                "total_active": shipments_total,
            },
            "financial": {
                "daily_revenue": daily_revenue,
                "monthly_revenue": monthly_revenue,
                "overdue_amount": 0,
            },
            "inventory": {
                "total_items": await _count_rows(db, "inventory_items"),
                "low_stock_count": 0,
                "total_inventory_value": 0,
            },
            "customers": {
                "total_customers": await _count_rows(db, "users"),
                "active_customers": await _count_rows(db, "users"),
                "new_customers_month": 0,
            },
        },
        "timestamp": today.isoformat(),
    }


@router.get("/analytics/trends")
async def get_analytics_trends(db: AsyncSession = Depends(get_async_session)):
    current_shipments = await _count_rows(db, "shipments")
    current_customers = await _count_rows(db, "users")
    revenue = 0.0
    if await _table_exists(db, "payments") and await _column_exists(db, "payments", "amount"):
        result = await db.execute(text("SELECT COALESCE(SUM(amount), 0) FROM payments"))
        revenue = float(result.scalar() or 0)

    return {
        "trends": [
            {"metric": "shipments", "trend": "stable", "value": current_shipments},
            {"metric": "revenue", "trend": "stable", "value": revenue},
            {"metric": "customers", "trend": "stable", "value": current_customers},
        ],
        "timestamp": date.today().isoformat(),
    }


@router.get("/sync/status")
async def get_sync_status(db: AsyncSession = Depends(get_async_session)):
    await db.execute(text("SELECT 1"))
    return {
        "status": "ok",
        "last_sync": datetime.now(timezone.utc).isoformat(),
        "message": "Database connectivity check passed.",
    }


@router.get("/integrations/status")
async def get_integrations_status(db: AsyncSession = Depends(get_async_session)):
    await db.execute(text("SELECT 1"))
    return {
        "status": "ok",
        "integrations": [],
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/status")
async def get_coordinator_status(db: AsyncSession = Depends(get_async_session)):
    await db.execute(text("SELECT 1"))
    return {
        "status": "ok",
        "last_restart": None,
        "message": "Coordinator service is running.",
    }


@router.get("/dashboard/operational")
async def get_operational_dashboard(db: AsyncSession = Depends(get_async_session)):
    metrics = await get_dashboard_metrics(db)
    return {
        "status": "ok",
        "timestamp": date.today().isoformat(),
        "metrics": metrics["metrics"],
        "insights": [],
        "alerts": [],
    }


@router.get("/dashboard/alerts")
async def get_system_alerts(limit: int = 20, db: AsyncSession = Depends(get_async_session)):
    _ = limit
    total_alerts = await _count_rows(db, "alerts")
    unresolved = 0
    if await _table_exists(db, "alerts") and await _column_exists(db, "alerts", "resolved"):
        unresolved = await _count_rows(db, "alerts", "resolved = false")
    return {
        "total_alerts": total_alerts,
        "unresolved": unresolved,
        "alerts": [],
    }


@router.get("/dashboard/kpis")
async def get_kpis(db: AsyncSession = Depends(get_async_session)):
    shipments_total = await _count_rows(db, "shipments")
    customers_total = await _count_rows(db, "users")
    return {
        "timestamp": date.today().isoformat(),
        "kpis": {
            "operational": {"shipments": {"value": shipments_total, "unit": "count", "trend": "stable"}},
            "customer": {"customers": {"value": customers_total, "unit": "count", "trend": "stable"}},
        },
    }


@router.get("/analytics/shipments")
async def get_shipments_analytics(start_date: Optional[str] = None, end_date: Optional[str] = None, db: AsyncSession = Depends(get_async_session)):
    return {
        "total_shipments": await _count_rows(db, "shipments"),
        "delayed": 0,
        "on_time": 0,
        "status": "ok",
        "details": [{"start_date": start_date, "end_date": end_date}],
    }


@router.get("/analytics/financial")
async def get_financial_analytics(start_date: Optional[str] = None, end_date: Optional[str] = None, db: AsyncSession = Depends(get_async_session)):
    _ = (start_date, end_date)
    total_revenue = 0.0
    if await _table_exists(db, "payments") and await _column_exists(db, "payments", "amount"):
        result = await db.execute(text("SELECT COALESCE(SUM(amount), 0) FROM payments"))
        total_revenue = float(result.scalar() or 0)
    return {
        "total_revenue": total_revenue,
        "total_expenses": 0,
        "net_profit": total_revenue,
        "status": "ok",
        "details": [],
    }


@router.get("/analytics/inventory")
async def get_inventory_analytics(db: AsyncSession = Depends(get_async_session)):
    return {
        "total_items": await _count_rows(db, "inventory_items"),
        "low_stock": 0,
        "status": "ok",
        "details": [],
    }


@router.get("/analytics/customers")
async def get_customer_analytics(start_date: Optional[str] = None, end_date: Optional[str] = None, db: AsyncSession = Depends(get_async_session)):
    _ = (start_date, end_date)
    return {
        "total_customers": await _count_rows(db, "users"),
        "new_customers": 0,
        "churned": 0,
        "status": "ok",
        "details": [],
    }


@router.post("/analytics/predict")
async def predict(type: str, period: Optional[str] = None):
    return {
        "status": "not_implemented",
        "message": "Predictive analytics requires a configured ML pipeline.",
        "type": type,
        "period": period,
    }


@router.post("/reports/generate")
async def generate_custom_report(type: str, start_date: str, end_date: str, filters: dict | None = None, format: str = "json"):
    return {
        "status": "accepted",
        "message": "Report generation request received.",
        "requested": {
            "type": type,
            "start_date": start_date,
            "end_date": end_date,
            "filters": filters or {},
            "format": format,
        },
    }


@router.get("/reports/list")
async def list_reports(limit: int = 50):
    return {"reports": [], "total": 0, "limit": limit}


@router.get("/reports/{report_id}")
async def get_report_details(report_id: int):
    return {"id": report_id, "status": "not_found"}


@router.get("/reports/{report_id}/download")
async def download_report(report_id: int, format: str = "pdf"):
    return {
        "status": "not_available",
        "message": "Report download is not available for this report.",
        "report_id": report_id,
        "format": format,
    }
