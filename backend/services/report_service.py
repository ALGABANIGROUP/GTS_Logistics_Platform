# backend/services/report_service.py
from __future__ import annotations

from typing import Optional, Dict, Any, Tuple
from datetime import date, datetime, timedelta
import os

try:
    import httpx
except Exception:  # pragma: no cover
    httpx = None

# Optional DB access (safe fallback if not available)
try:
    from sqlalchemy import text
    from sqlalchemy.ext.asyncio import AsyncSession
    from backend.database.session import get_async_session as _get_session  # type: ignore
    from backend.database.session import wrap_session_factory
except Exception:  # pragma: no cover
    text = None  # type: ignore
    AsyncSession = None  # type: ignore
    _get_session = None  # type: ignore
    wrap_session_factory = None  # type: ignore


# ---------------------------- Date helpers ----------------------------

def _period_range(
    period: str = "week",
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> Tuple[datetime, datetime, str]:
    today = date.today()
    if period == "today":
        start = datetime.combine(today, datetime.min.time())
        end = datetime.combine(today, datetime.max.time())
        label = "today"
    elif period == "month":
        first = today.replace(day=1)
        start = datetime.combine(first, datetime.min.time())
        end = datetime.combine(today, datetime.max.time())
        label = "month"
    elif period == "custom" and start_date and end_date:
        start = datetime.combine(start_date, datetime.min.time())
        end = datetime.combine(end_date, datetime.max.time())
        label = "custom"
    else:  # default "week"
        start = datetime.combine(today - timedelta(days=6), datetime.min.time())
        end = datetime.combine(today, datetime.max.time())
        label = "week"
    return start, end, label


def _iso(dt: datetime) -> str:
    return dt.replace(microsecond=0).isoformat() + "Z"


# ---------------------------- HTTP helpers ----------------------------

async def _safe_http_get_json(url: str) -> Optional[Dict[str, Any]]:
    if not httpx:
        return None
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            r = await client.get(url)
            if r.status_code // 100 == 2:
                return r.json()
    except Exception:
        return None
    return None


# ---------------------------- Finance ----------------------------

async def _fetch_finance_summary(base_url: str) -> Tuple[Dict[str, Any], str]:
    """
    Tries to pull /finance/summary.
    Returns (data, source), where source is 'live' or 'fallback'.
    """
    url = base_url.rstrip("/") + "/finance/summary"
    data = await _safe_http_get_json(url)
    if isinstance(data, dict) and data:
        # Normalize a few likely keys
        rev = data.get("revenue") or data.get("revenue_total") or data.get("total_revenue")
        exp = data.get("expenses") or data.get("expenses_total") or data.get("total_expenses")
        paid = data.get("paid") if "paid" in data else None
        pending = data.get("pending") if "pending" in data else None
        return {
            "revenue_total": rev if isinstance(rev, (int, float)) else None,
            "expenses_total": exp if isinstance(exp, (int, float)) else (paid + pending if isinstance(paid, (int, float)) and isinstance(pending, (int, float)) else None),
            "paid": paid,
            "pending": pending,
        }, "live"

    # Fallback if finance API not available
    return {
        "revenue_total": None,  # may not be tracked yet
        "expenses_total": None,
        "paid": None,
        "pending": None,
    }, "fallback"


# ---------------------------- Shipments ----------------------------

async def _fetch_shipments_counts_from_db(
    start_dt: datetime,
    end_dt: datetime,
) -> Optional[Dict[str, int]]:
    """
    Best-effort DB query. Works if:
    - SQLAlchemy + async session are available
    - There's a 'shipments' table with 'status' and 'created_at' (common pattern)
    Falls back to None if not available or schema differs.
    """
    if not (text and _get_session and AsyncSession):
        return None

    # Try a generic query that tolerates varying status casing
    sql = text(
        """
        SELECT
            COUNT(*)                                                              AS total,
            SUM(CASE WHEN LOWER(status) LIKE 'in-%' OR status='IN_TRANSIT' THEN 1 ELSE 0 END) AS in_transit,
            SUM(CASE WHEN LOWER(status) LIKE 'deliver%'                            THEN 1 ELSE 0 END) AS delivered,
            SUM(CASE WHEN LOWER(status) LIKE 'delay%'                              THEN 1 ELSE 0 END) AS delayed
        FROM shipments
        WHERE
            (created_at BETWEEN :start AND :end)
            OR (pickup_date BETWEEN :start AND :end)
            OR (updated_at BETWEEN :start AND :end)
        """
    )

    try:
        async with wrap_session_factory(_get_session) as session:  # type: ignore
            assert isinstance(session, AsyncSession)  # for type-checkers
            res = await session.execute(sql, {"start": start_dt, "end": end_dt})
            row = res.fetchone()
            if not row:
                return None
            total, in_transit, delivered, delayed = [int(x or 0) for x in row]
            return {
                "total": total,
                "in_transit": in_transit,
                "delivered": delivered,
                "delayed": delayed,
            }
    except Exception:
        return None


# ---------------------------- Markdown ----------------------------

def _render_markdown(report: Dict[str, Any]) -> str:
    kpis = report.get("kpis") or {}
    s = report.get("shipments") or {}
    f = report.get("finance") or {}

    lines = []
    lines.append(f"# GTS Weekly Report")
    when = report.get("period_label", "week")
    lines.append(f"_Period:_ **{when}**  \n_Generated at:_ {report.get('generated_at')}")
    lines.append("")
    lines.append("## KPIs")
    lines.append(f"- Shipments: **{kpis.get('shipments_total', 'N/A')}**")
    if kpis.get("on_time_rate") is not None:
        lines.append(f"- On-time rate: **{round(100.0 * kpis['on_time_rate'], 2)}%**")
    if kpis.get("profit") is not None:
        lines.append(f"- Profit: **{kpis['profit']}**")
    lines.append("")
    lines.append("## Shipments")
    lines.append(f"- In-Transit: **{s.get('in_transit', 'N/A')}**")
    lines.append(f"- Delivered: **{s.get('delivered', 'N/A')}**")
    lines.append(f"- Delayed: **{s.get('delayed', 'N/A')}**")
    lines.append("")
    lines.append("## Finance")
    lines.append(f"- Revenue: **{f.get('revenue_total', 'N/A')}**")
    lines.append(f"- Expenses: **{f.get('expenses_total', 'N/A')}**")
    if f.get("paid") is not None or f.get("pending") is not None:
        lines.append(f"- Paid: **{f.get('paid', 'N/A')}** | Pending: **{f.get('pending', 'N/A')}**")
    return "\n".join(lines)


# ---------------------------- Main API ----------------------------

async def compile_system_report(
    period: str = "week",
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    fmt: Optional[str] = None,           # support both fmt and format
    format: str = "json",
    include_kpis: bool = True,
) -> Any:
    """
    Builds an executive report from available live sources with safe fallbacks.
    - period: today|week|month|custom
    - start_date/end_date: used when period=custom
    - format/fmt: 'json' (default) or 'markdown'
    - include_kpis: include KPI rollups
    """
    start_dt, end_dt, label = _period_range(period, start_date, end_date)
    out_format = (fmt or format or "json").lower()
    base_url = os.getenv("INTERNAL_BASE_URL", "http://localhost:8000")

    # Finance
    finance, finance_source = await _fetch_finance_summary(base_url)

    # Shipments
    shipments_counts = await _fetch_shipments_counts_from_db(start_dt, end_dt)
    if shipments_counts is None:
        shipments_counts = {"total": None, "in_transit": None, "delivered": None, "delayed": None}
        shipments_source = "fallback"
    else:
        shipments_source = "live"

    # KPIs
    kpis: Dict[str, Any] = {}
    if include_kpis:
        shipments_total = shipments_counts.get("total") or 0
        delivered = shipments_counts.get("delivered") or 0
        delayed = shipments_counts.get("delayed") or 0

        # Naive on-time rate if we have delivered+delayed
        on_time_rate = None
        denom = delivered + delayed
        if denom > 0:
            on_time_rate = delivered / float(denom)

        revenue = finance.get("revenue_total")
        expenses = finance.get("expenses_total")
        profit = None
        if isinstance(revenue, (int, float)) and isinstance(expenses, (int, float)):
            profit = float(revenue) - float(expenses)

        kpis.update(
            {
                "shipments_total": shipments_total or 0,
                "on_time_rate": on_time_rate,
                "profit": profit,
            }
        )

    # Assemble report
    report: Dict[str, Any] = {
        "generated_at": _iso(datetime.utcnow()),
        "period_label": label,
        "period": {"start": _iso(start_dt), "end": _iso(end_dt)},
        "sources": {"finance": finance_source, "shipments": shipments_source},
        "shipments": {
            "total": shipments_counts.get("total"),
            "in_transit": shipments_counts.get("in_transit"),
            "delivered": shipments_counts.get("delivered"),
            "delayed": shipments_counts.get("delayed"),
        },
        "finance": {
            "revenue_total": finance.get("revenue_total"),
            "expenses_total": finance.get("expenses_total"),
            "paid": finance.get("paid"),
            "pending": finance.get("pending"),
        },
    }
    if include_kpis:
        report["kpis"] = kpis

    # Output format
    if out_format == "markdown":
        return _render_markdown(report)
    return report


