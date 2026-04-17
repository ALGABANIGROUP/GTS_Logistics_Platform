"""
Reports API backed by live database counts.

The reports dashboard in the frontend is already feature-rich. This module
provides real list/stat/export endpoints that feed that UI without depending
on fragile ORM mapper initialization for unrelated models.
"""

from __future__ import annotations

import csv
import io
import json
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Literal, Optional, Tuple

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.session import get_async_session
from backend.security.auth import get_current_user

router = APIRouter(prefix="/api/v1/reports", tags=["Reports"])


def _iso(value: Any) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.isoformat()
    return str(value)


async def _safe_scalar(
    session: AsyncSession, sql: str, params: Optional[Dict[str, Any]] = None, default: int = 0
) -> int:
    try:
        result = await session.execute(text(sql), params or {})
        value = result.scalar()
        return int(value or 0)
    except Exception:
        return default


async def _safe_timestamp(
    session: AsyncSession, sql: str, params: Optional[Dict[str, Any]] = None
) -> Optional[str]:
    try:
        result = await session.execute(text(sql), params or {})
        value = result.scalar()
        return _iso(value)
    except Exception:
        return None


def _default_settings(auto_generate: bool, refresh_interval: int) -> Dict[str, Any]:
    return {
        "refreshInterval": refresh_interval,
        "autoGenerate": auto_generate,
        "includeCharts": True,
        "includeTables": True,
        "includeSummary": True,
        "dataPoints": 1000,
    }


def _build_report(
    report_id: str,
    name: str,
    description: str,
    category: str,
    status: str,
    updated_at: Optional[str],
    generation_count: int,
    *,
    tags: Optional[List[str]] = None,
    created_by: str = "System",
    report_type: str = "predefined",
    auto_generate: bool = False,
    refresh_interval: int = 0,
    metrics: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    now_iso = datetime.now(timezone.utc).isoformat()
    return {
        "id": report_id,
        "name": name,
        "description": description,
        "category": category,
        "type": report_type,
        "format": "dashboard",
        "status": status,
        "createdBy": created_by,
        "createdAt": updated_at or now_iso,
        "updatedAt": updated_at or now_iso,
        "lastGeneratedAt": updated_at or now_iso,
        "generationCount": generation_count,
        "tags": tags or [],
        "settings": _default_settings(auto_generate, refresh_interval),
        "criteria": {
            "dateRange": {"type": "last30days", "start": None, "end": None},
            "filters": {},
            "groupings": [],
            "aggregations": [],
        },
        "metrics": metrics or [],
        "dimensions": [],
        "charts": [],
        "tables": [],
        "isPublic": False,
        "accessLevel": "team",
        "version": "1.0",
        "history": [],
    }


async def _load_counts(session: AsyncSession) -> Dict[str, int]:
    return {
        "shipments": await _safe_scalar(session, "SELECT COUNT(*) FROM shipments"),
        "shipments_active": await _safe_scalar(
            session,
            """
            SELECT COUNT(*) FROM shipments
            WHERE COALESCE(status, '') IN ('in_transit', 'on_the_way', 'active')
            """,
        ),
        "shipments_pending": await _safe_scalar(
            session,
            """
            SELECT COUNT(*) FROM shipments
            WHERE COALESCE(status, '') IN ('pending', 'scheduled', 'assigned')
            """,
        ),
        "users": await _safe_scalar(session, "SELECT COUNT(*) FROM users"),
        "invoices": await _safe_scalar(session, "SELECT COUNT(*) FROM invoices"),
        "emails": await _safe_scalar(session, "SELECT COUNT(*) FROM email_messages"),
        "emails_processed": await _safe_scalar(
            session,
            """
            SELECT COUNT(*) FROM email_messages
            WHERE COALESCE(status, '') IN ('processed', 'completed')
            """,
        ),
    }


async def _build_reports_catalog(session: AsyncSession) -> Tuple[List[Dict[str, Any]], Dict[str, int]]:
    counts = await _load_counts(session)

    shipment_updated_at = await _safe_timestamp(
        session, "SELECT MAX(COALESCE(updated_at, created_at)) FROM shipments"
    )
    invoice_updated_at = await _safe_timestamp(
        session, "SELECT MAX(COALESCE(updated_at, created_at)) FROM invoices"
    )
    user_updated_at = await _safe_timestamp(
        session, "SELECT MAX(COALESCE(updated_at, created_at)) FROM users"
    )
    email_updated_at = await _safe_timestamp(
        session, "SELECT MAX(COALESCE(analyzed_at, received_at, created_at)) FROM email_messages"
    )
    system_updated_at = datetime.now(timezone.utc).isoformat()

    reports = [
        _build_report(
            "shipments-overview",
            "Shipments Overview",
            f"Complete overview of all shipments ({counts['shipments']} total).",
            "shipments",
            "active",
            shipment_updated_at,
            counts["shipments"],
            tags=["favorite", "operations"],
            auto_generate=True,
            refresh_interval=300,
            metrics=[
                {"id": "totalShipments", "name": "Total Shipments", "type": "count"},
                {"id": "activeShipments", "name": "Active Shipments", "type": "count"},
            ],
        ),
        _build_report(
            "scheduled-shipments",
            "Scheduled Shipments",
            f"Pending and assigned shipments ({counts['shipments_pending']} scheduled).",
            "shipments",
            "active" if counts["shipments_pending"] else "draft",
            shipment_updated_at,
            counts["shipments_pending"],
            tags=["planning"],
            auto_generate=True,
            refresh_interval=900,
            metrics=[{"id": "scheduledShipments", "name": "Scheduled Shipments", "type": "count"}],
        ),
        _build_report(
            "user-access-summary",
            "User Access Summary",
            f"Users, roles, and access footprint across the platform ({counts['users']} users).",
            "users",
            "active",
            user_updated_at,
            counts["users"],
            tags=["security"],
            auto_generate=True,
            refresh_interval=1800,
            metrics=[{"id": "totalUsers", "name": "Total Users", "type": "count"}],
        ),
        _build_report(
            "financial-summary",
            "Financial Summary",
            f"Invoices and finance activity ({counts['invoices']} invoices).",
            "finance",
            "active" if counts["invoices"] else "draft",
            invoice_updated_at,
            counts["invoices"],
            tags=["favorite", "finance"],
            auto_generate=True,
            refresh_interval=3600,
            metrics=[{"id": "totalInvoices", "name": "Total Invoices", "type": "count"}],
        ),
        _build_report(
            "email-analytics",
            "Email Analytics",
            f"Mailbox and AI processing analytics ({counts['emails']} messages).",
            "support",
            "active" if counts["emails"] else "draft",
            email_updated_at,
            counts["emails_processed"],
            tags=["automation"],
            auto_generate=True,
            refresh_interval=600,
            metrics=[
                {"id": "totalEmails", "name": "Total Emails", "type": "count"},
                {"id": "processedEmails", "name": "Processed Emails", "type": "count"},
            ],
        ),
        _build_report(
            "system-health",
            "System Health",
            "Operational readiness, service coverage, and high-level platform telemetry.",
            "system",
            "active",
            system_updated_at,
            1,
            tags=["monitoring"],
            auto_generate=True,
            refresh_interval=300,
            metrics=[{"id": "serviceHealth", "name": "Service Health", "type": "percentage"}],
        ),
        _build_report(
            "marketing-campaigns",
            "Marketing Campaigns",
            "Campaign performance scaffold ready for live marketing data integration.",
            "marketing",
            "draft",
            system_updated_at,
            0,
            tags=["pipeline"],
        ),
    ]
    return reports, counts


def _apply_period_filter(reports: List[Dict[str, Any]], period: Optional[str]) -> List[Dict[str, Any]]:
    if not isinstance(period, str) or not period:
        return reports

    now = datetime.now(timezone.utc)
    cutoffs = {
        "today": now - timedelta(days=1),
        "week": now - timedelta(days=7),
        "month": now - timedelta(days=30),
        "year": now - timedelta(days=365),
    }
    cutoff = cutoffs.get(period)
    if not cutoff:
        return reports

    filtered: List[Dict[str, Any]] = []
    for report in reports:
        updated_at = report.get("updatedAt")
        if not updated_at:
            continue
        try:
            updated = datetime.fromisoformat(str(updated_at).replace("Z", "+00:00"))
        except ValueError:
            continue
        if updated >= cutoff:
            filtered.append(report)
    return filtered


def _filter_reports(
    reports: List[Dict[str, Any]],
    *,
    category: Optional[str] = None,
    status: Optional[str] = None,
    period: Optional[str] = None,
    search: Optional[str] = None,
) -> List[Dict[str, Any]]:
    filtered = reports

    if isinstance(category, str) and category:
        filtered = [report for report in filtered if report.get("category") == category]
    if isinstance(status, str) and status:
        filtered = [report for report in filtered if report.get("status") == status]
    if isinstance(search, str) and search:
        needle = search.strip().lower()
        filtered = [
            report
            for report in filtered
            if needle in str(report.get("name", "")).lower()
            or needle in str(report.get("description", "")).lower()
            or any(needle in str(tag).lower() for tag in report.get("tags", []))
        ]

    filtered = _apply_period_filter(filtered, period)
    filtered.sort(key=lambda report: str(report.get("updatedAt") or ""), reverse=True)
    return filtered


@router.get("/list")
async def get_reports_list(
    category: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None),
    period: Optional[str] = Query(default=None),
    search: Optional[str] = Query(default=None),
    session: AsyncSession = Depends(get_async_session),
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    reports, _counts = await _build_reports_catalog(session)
    filtered = _filter_reports(
        reports,
        category=category,
        status=status,
        period=period,
        search=search,
    )
    return {"reports": filtered, "total": len(filtered)}


@router.get("/stats")
async def get_report_stats(
    session: AsyncSession = Depends(get_async_session),
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    reports, counts = await _build_reports_catalog(session)
    by_category: Dict[str, int] = {}
    for report in reports:
        category = str(report.get("category") or "other")
        by_category[category] = by_category.get(category, 0) + 1

    draft = sum(1 for report in reports if report.get("status") == "draft")
    archived = sum(1 for report in reports if report.get("status") == "archived")
    active = sum(1 for report in reports if report.get("status") == "active")
    scheduled = sum(
        1
        for report in reports
        if (report.get("settings") or {}).get("autoGenerate")
        and ((report.get("settings") or {}).get("refreshInterval") or 0) > 0
    )
    favorites = sum(1 for report in reports if "favorite" in (report.get("tags") or []))

    return {
        "total": len(reports),
        "active": active,
        "scheduled": scheduled,
        "favorites": favorites,
        "draft": draft,
        "archived": archived,
        "byCategory": by_category,
        "users": counts["users"],
        "shipments": counts["shipments"],
        "invoices": counts["invoices"],
        "emails": counts["emails"],
    }


@router.get("/real-data")
async def get_real_reports(
    session: AsyncSession = Depends(get_async_session),
    current_user: dict = Depends(get_current_user),
) -> List[Dict[str, Any]]:
    reports, _counts = await _build_reports_catalog(session)
    return reports


@router.get("/analytics")
async def get_reports_analytics(
    session: AsyncSession = Depends(get_async_session),
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    stats = await get_report_stats(session=session, current_user=current_user)
    return {
        "total": stats["total"],
        "active": stats["active"],
        "draft": stats["draft"],
        "archived": stats["archived"],
        "byCategory": stats["byCategory"],
    }


@router.post("/preview")
async def preview_report(
    report_config: Dict[str, Any],
    session: AsyncSession = Depends(get_async_session),
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    reports, counts = await _build_reports_catalog(session)
    target_id = str(report_config.get("id") or "")
    target = next((report for report in reports if report["id"] == target_id), None)

    summary = {
        "shipments": {"name": "Shipments", "total": counts["shipments"], "average": counts["shipments"]},
        "users": {"name": "Users", "total": counts["users"], "average": counts["users"]},
        "invoices": {"name": "Invoices", "total": counts["invoices"], "average": counts["invoices"]},
        "emails": {"name": "Emails", "total": counts["emails"], "average": counts["emails"]},
    }

    return {
        "report": target
        or {
            "name": report_config.get("name") or "Preview Report",
            "description": report_config.get("description") or "Preview generated from live counters",
        },
        "summary": summary,
        "insights": [
            {
                "metric": "Shipments",
                "description": f"Active shipments currently tracked: {counts['shipments_active']}.",
            },
            {
                "metric": "Pending Shipments",
                "description": f"Scheduled and pending shipments: {counts['shipments_pending']}.",
            },
            {
                "metric": "Email Processing",
                "description": f"Processed email messages: {counts['emails_processed']} out of {counts['emails']}.",
            },
        ],
        "metadata": {
            "generatedAt": datetime.now(timezone.utc).isoformat(),
            "source": "live-preview",
            "dataPoints": 4,
        },
    }


@router.get("/view/{report_id}")
async def view_report(
    report_id: str,
    session: AsyncSession = Depends(get_async_session),
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    return await preview_report(
        report_config={"id": report_id},
        session=session,
        current_user=current_user,
    )


@router.get("/generate/{report_id}")
async def generate_report(
    report_id: str,
    format: Literal["json", "pdf", "excel", "csv"] = Query(default="json"),
    session: AsyncSession = Depends(get_async_session),
    current_user: dict = Depends(get_current_user),
):
    if format == "json":
        return await view_report(report_id=report_id, session=session, current_user=current_user)
    return await export_report(
        report_id=report_id,
        format=format,
        session=session,
        current_user=current_user,
    )


def _build_export_payload(report: Dict[str, Any], stats: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "report": {
            "id": report["id"],
            "name": report["name"],
            "description": report["description"],
            "category": report["category"],
            "status": report["status"],
            "updatedAt": report["updatedAt"],
        },
        "stats": stats,
        "exportedAt": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/export/{report_id}")
async def export_report(
    report_id: str,
    format: Literal["pdf", "excel", "csv", "json"] = Query(default="pdf"),
    session: AsyncSession = Depends(get_async_session),
    current_user: dict = Depends(get_current_user),
) -> Response:
    reports, counts = await _build_reports_catalog(session)
    report = next((item for item in reports if item["id"] == report_id), None)
    if report is None:
        return Response(
            content=json.dumps({"detail": "Report not found"}),
            media_type="application/json",
            status_code=404,
        )

    stats = {
        "shipments": counts["shipments"],
        "active_shipments": counts["shipments_active"],
        "pending_shipments": counts["shipments_pending"],
        "users": counts["users"],
        "invoices": counts["invoices"],
        "emails": counts["emails"],
    }
    payload = _build_export_payload(report, stats)
    file_stub = str(report["name"]).replace(" ", "_").lower()

    if format == "json":
        return Response(
            content=json.dumps(payload, indent=2),
            media_type="application/json",
            headers={"Content-Disposition": f'attachment; filename="{file_stub}.json"'},
        )

    if format == "csv":
        stream = io.StringIO()
        writer = csv.writer(stream)
        writer.writerow(["metric", "value"])
        for key, value in stats.items():
            writer.writerow([key, value])
        writer.writerow(["report_name", report["name"]])
        writer.writerow(["report_status", report["status"]])
        return Response(
            content=stream.getvalue(),
            media_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="{file_stub}.csv"'},
        )

    if format == "excel":
        stream = io.StringIO()
        writer = csv.writer(stream, delimiter="\t")
        writer.writerow(["metric", "value"])
        for key, value in stats.items():
            writer.writerow([key, value])
        return Response(
            content=stream.getvalue(),
            media_type="application/vnd.ms-excel",
            headers={"Content-Disposition": f'attachment; filename="{file_stub}.xls"'},
        )

    pdf_content = "\n".join(
        [
            f"Report: {report['name']}",
            f"Description: {report['description']}",
            f"Category: {report['category']}",
            f"Status: {report['status']}",
            "",
            "Live Metrics",
            *(f"- {key}: {value}" for key, value in stats.items()),
        ]
    )
    return Response(
        content=pdf_content.encode("utf-8"),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{file_stub}.pdf"'},
    )


@router.get("/shipments-market-intelligence")
async def get_shipments_market_intelligence(
    session: AsyncSession = Depends(get_async_session),
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    counts = await _load_counts(session)
    market_health = "active" if counts["shipments"] > 50 else "moderate" if counts["shipments"] > 0 else "quiet"
    return {
        "market_overview": {
            "total_shipments_analyzed": counts["shipments"],
            "analysis_period": "live",
            "market_health": market_health,
        },
        "status_distribution": {
            "active": counts["shipments_active"],
            "pending": counts["shipments_pending"],
        },
        "top_routes": [],
        "payment_integration": {
            "paybycanada_enabled": True,
            "supported_currencies": ["CAD", "USD"],
            "integration_status": "active",
        },
        "ai_recommendations": [
            "Review pending shipment backlog daily.",
            "Prioritize finance follow-up on invoice-heavy periods.",
            "Track email processing coverage for customer-facing queues.",
        ],
    }


__all__ = ["router"]
