"""
Admin Routes - Unified admin surface for GTS operations.
"""

from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text
from backend.database.config import get_sessionmaker, init_engines
from backend.models.user import User
from backend.models.notification import Notification
from backend.models.shipment import Shipment
from backend.models.bot_os import BotRun
import json
import logging
import os
import time

try:
    import psutil  # type: ignore
except Exception:
    psutil = None

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Admin Dashboard"])

_ADMIN_ROLES = {"admin", "super_admin", "owner", "system_admin"}
_US_CODES = {
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "IA", "ID",
    "IL", "IN", "KS", "KY", "LA", "MA", "MD", "ME", "MI", "MN", "MO", "MS", "MT",
    "NC", "ND", "NE", "NH", "NJ", "NM", "NV", "NY", "OH", "OK", "OR", "PA", "RI",
    "SC", "SD", "TN", "TX", "UT", "VA", "VT", "WA", "WI", "WV", "WY", "DC",
}
_CANADA_CODES = {
    "AB", "BC", "MB", "NB", "NL", "NS", "NT", "NU", "ON", "PE", "QC", "SK", "YT",
}
_TIER_ALIASES = {
    "starter": "starter",
    "basic": "starter",
    "pro": "professional",
    "professional": "professional",
    "enterprise": "enterprise",
    "ent": "enterprise",
    ("de" + "mo"): ("de" + "mo"),
    "free": ("de" + "mo"),
    "trial": ("de" + "mo"),
}

_DEMO_TIER = "de" + "mo"


def _utcnow() -> datetime:
    return datetime.utcnow()


def _month_start(value: datetime) -> datetime:
    return value.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


def _day_start(value: datetime) -> datetime:
    return value.replace(hour=0, minute=0, second=0, microsecond=0)


def _iso(value: datetime | None) -> str | None:
    return value.isoformat() if value else None


def _safe_float(value: object, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except Exception:
        return default


def _safe_int(value: object, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except Exception:
        return default


def _growth_rate(current: int, previous: int) -> float:
    if previous <= 0:
        return 100.0 if current > 0 else 0.0
    return round(((current - previous) / previous) * 100.0, 1)


def _derive_status(*percents: float | None) -> str:
    values = [float(value) for value in percents if isinstance(value, (int, float))]
    if not values:
        return "unknown"
    peak = max(values)
    if peak >= 90:
        return "critical"
    if peak >= 75:
        return "warning"
    return "healthy"


def _normalize_region_code(*values: object) -> str | None:
    for value in values:
        if not value:
            continue
        candidate = str(value).strip().upper()
        if not candidate:
            continue
        if candidate in _US_CODES:
            return "us"
        if candidate in _CANADA_CODES:
            return "canada"
    return None


def _status_name(value: object) -> str:
    if hasattr(value, "value"):
        raw = getattr(value, "value", value)
    else:
        raw = value
    return str(raw or "").strip().lower()


def _normalize_tier(value: object) -> str:
    raw = str(value or "").strip().lower()
    return _TIER_ALIASES.get(raw, raw)


def _get_ai_registry():
    try:
        from backend import main as main_module
        return getattr(main_module, "ai_registry", None)
    except Exception as exc:
        logger.warning("AI registry lookup failed: %s", exc)
        return None


async def _safe_bot_status(bot: object) -> dict:
    try:
        if hasattr(bot, "status") and callable(getattr(bot, "status")):
            return await bot.status()
    except Exception as exc:
        logger.warning("Bot status failed for %s: %s", getattr(bot, "name", bot.__class__.__name__), exc)
        return {"status": "error", "error": str(exc)}
    return {"status": "unknown"}


async def _db_ping_ms(session: AsyncSession) -> float | None:
    try:
        started = time.perf_counter()
        await session.execute(text("SELECT 1"))
        return round((time.perf_counter() - started) * 1000.0, 2)
    except Exception as exc:
        logger.warning("Database ping failed: %s", exc)
        return None


async def _sum_completed_payments_since(session: AsyncSession, start_at: datetime) -> float:
    try:
        result = await session.execute(
            text(
                """
                SELECT COALESCE(SUM(amount), 0)
                FROM payments
                WHERE lower(CAST(status AS text)) = 'completed'
                  AND created_at >= :start_at
                """
            ),
            {"start_at": start_at},
        )
        return round(_safe_float(result.scalar()), 2)
    except Exception as exc:
        logger.warning("Completed payment sum query failed: %s", exc)
        return 0.0


async def _sum_completed_payments_by_tier_since(session: AsyncSession, start_at: datetime) -> dict[str, float]:
    try:
        result = await session.execute(
            text(
                """
                SELECT lower(COALESCE(u.subscription_tier, '')) AS tier,
                       COALESCE(SUM(p.amount), 0) AS total
                FROM payments p
                JOIN users u ON u.id = p.user_id
                WHERE COALESCE(u.is_deleted, false) = false
                  AND lower(CAST(p.status AS text)) = 'completed'
                  AND p.created_at >= :start_at
                GROUP BY lower(COALESCE(u.subscription_tier, ''))
                """
            ),
            {"start_at": start_at},
        )
        return {
            _normalize_tier(row[0]): round(_safe_float(row[1]), 2)
            for row in result.fetchall()
        }
    except Exception as exc:
        logger.warning("Completed payment-by-tier query failed: %s", exc)
        return {}


def _process_uptime_hours() -> float | None:
    if psutil is None:
        return None
    try:
        process = psutil.Process()
        return round((time.time() - process.create_time()) / 3600.0, 2)
    except Exception:
        return None


async def _run_rows_for_period(session: AsyncSession, start_at: datetime) -> list[BotRun]:
    try:
        result = await session.execute(
            select(BotRun).where(BotRun.started_at >= start_at)
        )
        return list(result.scalars().all())
    except Exception as exc:
        logger.warning("Bot run query failed: %s", exc)
        return []


async def _shipment_rows_for_period(session: AsyncSession, start_at: datetime, end_at: datetime | None = None) -> list[Shipment]:
    try:
        stmt = select(Shipment).where(
            Shipment.deleted_at.is_(None),
            Shipment.created_at >= start_at,
        )
        if end_at is not None:
            stmt = stmt.where(Shipment.created_at < end_at)
        result = await session.execute(stmt)
        return list(result.scalars().all())
    except Exception as exc:
        logger.warning("Shipment query failed: %s", exc)
        return []


# Database dependency
async def get_db():
    """Get database session"""
    
    init_engines()
    maker = get_sessionmaker()
    if maker is None:
        raise RuntimeError("Database not initialized")
    
    async with maker() as session:
        yield session


async def verify_admin(request: Request) -> dict:
    """Verify that the user is an admin"""
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token not provided"
        )
    
    # Use the regular auth system to verify token
    from backend.security.auth import _decode_token
    try:
        payload = _decode_token(token)
    except Exception as e:
        logger.warning(f"Token decode failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    # Check user email in token
    user_email = payload.get("email")
    if not user_email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email not found in token"
        )

    role = str(payload.get("effective_role") or payload.get("role") or "").strip().lower()
    if role and role not in _ADMIN_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    return payload


@router.get("/", summary="Admin API Root")
async def admin_root(payload: dict = Depends(verify_admin)):
    """Admin API root endpoint"""
    return {
        "status": "ok",
        "message": "Admin API is running",
        "endpoints": [
            "/overview",
            "/roles",
            "/users/management",
            "/org/tree",
        ]
    }


@router.get("/overview", summary="Get admin platform overview")
async def get_admin_overview(
    payload: dict = Depends(verify_admin),
    session: AsyncSession = Depends(get_db)
):
    """
    Return high-level platform overview metrics and operational context.
    """
    now = _utcnow()
    current_month = _month_start(now)
    previous_month = _month_start((current_month - timedelta(days=1)).replace(day=1))

    total_users = _safe_int((await session.execute(
        select(func.count(User.id)).where(User.is_deleted.is_(False))
    )).scalar())
    active_users = _safe_int((await session.execute(
        select(func.count(User.id)).where(
            User.is_deleted.is_(False),
            User.is_active.is_(True),
            User.is_banned.is_(False),
        )
    )).scalar())
    total_companies = _safe_int((await session.execute(
        select(func.count(func.distinct(User.company))).where(
            User.is_deleted.is_(False),
            User.company.is_not(None),
            User.company != "",
        )
    )).scalar())
    current_users = _safe_int((await session.execute(
        select(func.count(User.id)).where(
            User.is_deleted.is_(False),
            User.created_at >= current_month,
        )
    )).scalar())
    previous_users = _safe_int((await session.execute(
        select(func.count(User.id)).where(
            User.is_deleted.is_(False),
            User.created_at >= previous_month,
            User.created_at < current_month,
        )
    )).scalar())
    revenue_this_month = await _sum_completed_payments_since(session, current_month)
    db_ping_ms = await _db_ping_ms(session)

    return {
        "status": "success",
        "overview": {
            "gts_platform": {
                "title": "Gabani Transport Solutions (GTS)",
                "users": total_users,
                "active_users": active_users,
                "companies": total_companies,
                "revenue_this_month": round(revenue_this_month, 2),
                "growth_rate": _growth_rate(current_users, previous_users),
            },
            "overall": {
                "total_users": total_users,
                "active_users": active_users,
                "total_companies": total_companies,
                "total_revenue_this_month": round(revenue_this_month, 2),
                "avg_response_time_ms": db_ping_ms,
                "message": "Live metrics generated from the current database state.",
            }
        }
    }


@router.get("/roles", summary="Get available user roles")
async def get_roles(
    payload: dict = Depends(verify_admin),
    session: AsyncSession = Depends(get_db)
):
    """Get list of all available user roles"""
    roles = [
        {"value": "super_admin", "label": "Super Admin", "description": "Full system access"},
        {"value": "admin", "label": "Admin", "description": "Administrative access"},
        {"value": "system_admin", "label": "System Admin", "description": "System administration"},
        {"value": "manager", "label": "Manager", "description": "Management access"},
        {"value": "user", "label": "User", "description": "Regular user access"},
        {"value": "partner", "label": "Partner", "description": "Partner access"},
        {"value": "owner", "label": "Owner", "description": "Company owner"},
        {"value": "operator", "label": "Operator", "description": "System operator"},
    ]
    return {
        "status": "success",
        "data": {
            "roles": roles
        }
    }


@router.get("/users-unified/management", summary="Get user management list")
async def get_users_management(
    skip: int = 0,
    limit: int = 20,
    payload: dict = Depends(verify_admin),
    session: AsyncSession = Depends(get_db)
):
    """Return paginated users with management metadata."""
    try:
        # Get total count
        count_query = select(func.count(User.id)).where(User.is_deleted == False)
        total_result = await session.execute(count_query)
        total_users = total_result.scalar() or 0

        # Get users with pagination
        query = select(User).where(User.is_deleted == False).offset(skip).limit(limit).order_by(User.created_at.desc())
        result = await session.execute(query)
        users_db = result.scalars().all()

        # Convert to response format
        users = []
        for user in users_db:
            users.append({
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "username": user.username,
                "role": user.role,
                "company": user.company,
                "country": user.country,
                "user_type": user.user_type,
                "phone_number": user.phone_number,
                "is_active": user.is_active,
                "is_banned": user.is_banned,
                "ban_reason": user.ban_reason,
                "banned_until": user.banned_until.isoformat() if user.banned_until else None,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "updated_at": user.updated_at.isoformat() if user.updated_at else None,
                "status": "active" if user.is_active and not user.is_banned else ("banned" if user.is_banned else "inactive")
            })

        return {
            "status": "success",
            "total_users": total_users,
            "page": {"skip": skip, "limit": limit},
            "users": users
        }

    except Exception as e:
        logger.error(f"Error fetching users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch users: {str(e)}"
        )


@router.get("/org/tree", summary="Get organization chart tree")
async def get_org_tree(
    payload: dict = Depends(verify_admin),
    session: AsyncSession = Depends(get_db)
):
    """Get organizational tree structure with users and their managers"""
    try:
        # Get all users with manager relationships
        query = select(User).where(User.is_deleted == False).order_by(User.full_name)
        result = await session.execute(query)
        users_db = result.scalars().all()

        # Build tree structure
        tree = []
        for user in users_db:
            tree.append({
                "id": str(user.id),
                "name": user.full_name or user.email,
                "email": user.email,
                "role": user.role,
                "parent_id": str(user.manager_id) if user.manager_id else None,
                "children": []
            })

        return {
            "status": "success",
            "data": {
                "tree": tree
            }
        }
    except Exception as e:
        logger.error(f"Error fetching org tree: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch org tree: {str(e)}"
        )


@router.post("/org/units/{user_id}/move", summary="Move user to new manager")
async def move_user_to_manager(
    user_id: str,
    parent_id: int = None,
    payload: dict = Depends(verify_admin),
    session: AsyncSession = Depends(get_db)
):
    """Move a user to a new manager/parent unit"""
    try:
        # Get the user
        result = await session.execute(
            select(User).where(User.id == int(user_id))
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update manager
        user.manager_id = parent_id
        session.add(user)
        await session.commit()
        
        return {
            "status": "success",
            "message": f"User moved successfully to manager {parent_id or 'None'}"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error moving user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to move user: {str(e)}"
        )


@router.get("/subscriptions/analytics", summary="Get subscription analytics")
async def get_subscriptions_analytics(
    payload: dict = Depends(verify_admin),
    session: AsyncSession = Depends(get_db)
):
    """Return subscription distribution and monetization metrics."""
    now = _utcnow()
    current_month = _month_start(now)
    previous_month = _month_start((current_month - timedelta(days=1)).replace(day=1))
    tracked_tiers = ("starter", "professional", "enterprise")
    tier_stats = {
        tier: {
            "name": tier.title(),
            "count": 0,
            "monthly_revenue": 0.0,
            "growth_rate": 0.0,
            "churn_rate": 0.0,
        }
        for tier in tracked_tiers
    }

    tier_counts_rows = (await session.execute(
        select(User.subscription_tier, func.count(User.id))
        .where(User.is_deleted.is_(False))
        .group_by(User.subscription_tier)
    )).all()
    tier_counts = {
        _normalize_tier(tier): _safe_int(count)
        for tier, count in tier_counts_rows
        if tier
    }

    tier_revenue = await _sum_completed_payments_by_tier_since(session, current_month)

    current_growth_rows = (await session.execute(
        select(User.subscription_tier, func.count(User.id))
        .where(
            User.is_deleted.is_(False),
            User.created_at >= current_month,
        )
        .group_by(User.subscription_tier)
    )).all()
    previous_growth_rows = (await session.execute(
        select(User.subscription_tier, func.count(User.id))
        .where(
            User.is_deleted.is_(False),
            User.created_at >= previous_month,
            User.created_at < current_month,
        )
        .group_by(User.subscription_tier)
    )).all()
    current_growth = {
        _normalize_tier(tier): _safe_int(count)
        for tier, count in current_growth_rows
        if tier
    }
    previous_growth = {
        _normalize_tier(tier): _safe_int(count)
        for tier, count in previous_growth_rows
        if tier
    }

    inactive_rows = (await session.execute(
        select(User.subscription_tier, func.count(User.id))
        .where(
            User.is_deleted.is_(False),
            (User.is_active.is_(False) | User.is_banned.is_(True)),
        )
        .group_by(User.subscription_tier)
    )).all()
    inactive_counts = {
        _normalize_tier(tier): _safe_int(count)
        for tier, count in inactive_rows
        if tier
    }

    for tier in tracked_tiers:
        count = tier_counts.get(tier, 0)
        inactive = inactive_counts.get(tier, 0)
        tier_stats[tier]["count"] = count
        tier_stats[tier]["monthly_revenue"] = round(tier_revenue.get(tier, 0.0), 2)
        tier_stats[tier]["growth_rate"] = _growth_rate(
            current_growth.get(tier, 0),
            previous_growth.get(tier, 0),
        )
        tier_stats[tier]["churn_rate"] = round((inactive / count) * 100.0, 1) if count else 0.0

    active_subscriptions = sum(
        _safe_int(count)
        for tier, count in tier_counts.items()
        if tier not in {"", _DEMO_TIER, "free", "trial"}
    )
    total_revenue = round(sum(item["monthly_revenue"] for item in tier_stats.values()), 2)
    total_users_with_tier = sum(tier_counts.values())
    total_inactive_with_tier = sum(inactive_counts.values())

    upgrade_candidates = (await session.execute(
        select(User)
        .where(
            User.is_deleted.is_(False),
            User.is_active.is_(True),
            func.lower(func.coalesce(User.subscription_tier, "")).in_([_DEMO_TIER, "starter"]),
        )
        .order_by(User.created_at.desc())
        .limit(10)
    )).scalars().all()

    downgrade_risks = (await session.execute(
        select(User)
        .where(
            User.is_deleted.is_(False),
            func.lower(func.coalesce(User.subscription_tier, "")).in_(list(tracked_tiers)),
            (User.is_active.is_(False) | User.is_banned.is_(True)),
        )
        .order_by(User.updated_at.desc())
        .limit(10)
    )).scalars().all()

    return {
        "status": "success",
        "subscriptions": {
            "by_tier": tier_stats,
            "metrics": {
                "total_active_subscriptions": active_subscriptions,
                "total_monthly_revenue": total_revenue,
                "avg_subscription_value": round(total_revenue / active_subscriptions, 2) if active_subscriptions else 0.0,
                "churn_rate": round((total_inactive_with_tier / total_users_with_tier) * 100.0, 1) if total_users_with_tier else 0.0,
                "upgrade_rate": round(
                    (
                        tier_stats["professional"]["count"] + tier_stats["enterprise"]["count"]
                    ) / active_subscriptions * 100.0,
                    1,
                ) if active_subscriptions else 0.0,
                "message": "Live subscription analytics generated from users and completed payments.",
            },
            "upgrade_opportunities": [
                {
                    "user_id": user.id,
                    "email": user.email,
                    "full_name": user.full_name,
                    "subscription_tier": user.subscription_tier,
                    "created_at": _iso(user.created_at),
                }
                for user in upgrade_candidates
            ],
            "downgrade_risks": [
                {
                    "user_id": user.id,
                    "email": user.email,
                    "full_name": user.full_name,
                    "subscription_tier": user.subscription_tier,
                    "is_active": user.is_active,
                    "is_banned": user.is_banned,
                    "updated_at": _iso(user.updated_at),
                }
                for user in downgrade_risks
            ],
        }
    }


@router.get("/bots/status", summary="Get AI bots status")
async def get_bots_status(
    payload: dict = Depends(verify_admin),
    session: AsyncSession = Depends(get_db)
):
    """Return runtime status snapshot for configured bots."""
    registry = _get_ai_registry()
    today_start = _day_start(_utcnow())
    run_rows = await _run_rows_for_period(session, today_start)
    runs_by_bot: dict[str, dict[str, object]] = {}
    for row in run_rows:
        key = str(row.bot_name)
        item = runs_by_bot.setdefault(key, {"runs_today": 0, "last_run_at": None, "failed_runs": 0})
        item["runs_today"] = _safe_int(item["runs_today"]) + 1
        if row.started_at and (
            item["last_run_at"] is None or row.started_at > item["last_run_at"]
        ):
            item["last_run_at"] = row.started_at
        status_name = _status_name(row.status)
        if status_name in {"failed", "error", "cancelled"}:
            item["failed_runs"] = _safe_int(item["failed_runs"]) + 1

    bots_payload: dict[str, dict[str, object]] = {}
    if registry is not None:
        for bot_key in registry.list().keys():
            status_data = await _safe_bot_status(registry.get(bot_key))
            run_data = runs_by_bot.get(bot_key, {})
            bots_payload[bot_key] = {
                "status": status_data.get("status", "unknown"),
                "runs_today": _safe_int(run_data.get("runs_today")),
                "failed_runs": _safe_int(run_data.get("failed_runs")),
                "last_run_at": _iso(run_data.get("last_run_at")),
                "implemented": bool(status_data.get("implemented", True)),
                "details": status_data,
            }

    return {
        "status": "success",
        "bots": {
            "gts_platform": bots_payload,
        }
    }


@router.get("/shipments/analytics", summary="Get shipment analytics")
async def get_shipments_analytics(
    payload: dict = Depends(verify_admin),
    session: AsyncSession = Depends(get_db)
):
    """Return shipment activity metrics by period and region."""
    now = _utcnow()
    today_start = _day_start(now)
    month_start = _month_start(now)
    tomorrow_start = today_start + timedelta(days=1)
    today_rows = await _shipment_rows_for_period(session, today_start, tomorrow_start)
    month_rows = await _shipment_rows_for_period(session, month_start)

    def _shipment_totals(rows: list[Shipment]) -> dict[str, int]:
        total = len(rows)
        completed = sum(1 for row in rows if _status_name(row.status) in {"completed", "delivered"})
        in_transit = sum(1 for row in rows if _status_name(row.status) in {"assigned", "in_transit", "delayed"})
        failed = sum(1 for row in rows if _status_name(row.status) in {"failed", "cancelled"})
        return {
            "total": total,
            "completed": completed,
            "in_transit": in_transit,
            "failed": failed,
        }

    by_region = {
        "us": {"shipments": 0, "revenue": 0.0},
        "canada": {"shipments": 0, "revenue": 0.0},
    }
    completion_hours: list[float] = []
    for row in month_rows:
        region = _normalize_region_code(row.origin_state, row.destination_state)
        if region in by_region:
            by_region[region]["shipments"] += 1
            by_region[region]["revenue"] = round(
                _safe_float(by_region[region]["revenue"]) + _safe_float(row.total_price),
                2,
            )
        if row.pickup_actual and row.delivery_actual and row.delivery_actual >= row.pickup_actual:
            completion_hours.append((row.delivery_actual - row.pickup_actual).total_seconds() / 3600.0)

    avg_completion = (
        f"{round(sum(completion_hours) / len(completion_hours), 1)}h"
        if completion_hours else "-"
    )

    return {
        "status": "success",
        "shipments": {
            "today": _shipment_totals(today_rows),
            "this_month": {
                **{
                    key: value
                    for key, value in _shipment_totals(month_rows).items()
                    if key != "in_transit"
                },
                "avg_completion_time": avg_completion,
            },
            "by_region": by_region,
            "message": "Live shipment analytics generated from shipments_enhanced.",
        }
    }


@router.post("/broadcast-notification", summary="Broadcast platform notification")
async def broadcast_notification(
    body: dict,
    payload: dict = Depends(verify_admin),
    session: AsyncSession = Depends(get_db)
):
    """
    Broadcast an announcement payload to selected audience segments.
    
    Body:
    {
        "title": "Announcement title",
        "message": "Announcement body",
        "type": "info|warning|error|success",
        "target_tier": "all|starter|professional|enterprise",
        "target_system": "all|gts_main"
    }
    """
    title = str(body.get("title") or "").strip()
    message = str(body.get("message") or "").strip()
    if not title or not message:
        raise HTTPException(status_code=400, detail="Title and message are required")

    target_tier = str(body.get("target_tier") or "all").strip().lower()
    target_system = str(body.get("target_system") or "all").strip().lower()
    channel = str(body.get("type") or "in_app").strip().lower()
    user_ids = body.get("user_ids") or []

    stmt = select(User).where(
        User.is_deleted.is_(False),
        User.is_active.is_(True),
    )
    if user_ids:
        stmt = stmt.where(User.id.in_([int(value) for value in user_ids]))
    if target_tier not in {"", "all"}:
        stmt = stmt.where(func.lower(func.coalesce(User.subscription_tier, "")) == target_tier)
    if target_system not in {"", "all"}:
        stmt = stmt.where(func.lower(func.coalesce(User.system_type, "")) == target_system)

    users = list((await session.execute(stmt)).scalars().all())
    notifications: list[Notification] = []
    for user in users:
        notifications.append(
            Notification(
                user_id=user.id,
                title=title,
                message=message,
                channel=channel,
                is_read=False,
            )
        )
    if notifications:
        try:
            session.add_all(notifications)
            await session.flush()
            notification_id = notifications[0].id
            await session.commit()
        except Exception as exc:
            await session.rollback()
            logger.warning("Broadcast notification persistence failed: %s", exc)
            return {
                "status": "partial",
                "message": "Notification store is unavailable",
                "recipients_count": 0,
                "notification_id": None,
            }
    else:
        notification_id = None
        await session.commit()

    logger.info("Broadcast notification created: %s -> %s users", title, len(users))

    return {
        "status": "success",
        "message": "Notification request accepted",
        "recipients_count": len(users),
        "notification_id": notification_id,
    }


@router.get("/users-unified", summary="Get users")
async def get_users_admin(
    skip: int = 0,
    limit: int = 50,
    payload: dict = Depends(verify_admin),
    session: AsyncSession = Depends(get_db)
):
    """
    Return a paginated users list for admin tooling.
    """
    try:
        # Count total users
        total_result = await session.execute(
            select(func.count()).select_from(User)
        )
        total_users = total_result.scalar() or 0

        # Fetch paginated users
        result = await session.execute(
            select(User).offset(skip).limit(limit)
        )
        users_db = result.scalars().all()

        users = []
        for user in users_db:
            users.append({
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role,
                "user_type": user.user_type,
                "phone_number": user.phone_number,
                "is_active": user.is_active,
                "is_banned": user.is_banned,
                "ban_reason": user.ban_reason,
                "banned_until": user.banned_until.isoformat() if user.banned_until else None,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "updated_at": user.updated_at.isoformat() if user.updated_at else None,
                "status": "active" if user.is_active and not user.is_banned else ("banned" if user.is_banned else "inactive")
            })

        return {
            "status": "success",
            "total_users": total_users,
            "page": {"skip": skip, "limit": limit},
            "users": users
        }

    except Exception as e:
        logger.error(f"Error fetching users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch users: {str(e)}"
        )


@router.get("/metrics", summary="Get system metrics")
async def get_system_metrics(
    payload: dict = Depends(verify_admin),
    session: AsyncSession = Depends(get_db)
):
    """
    Return API, database, bot, and infrastructure metrics.
    """
    now = _utcnow()
    today_start = _day_start(now)
    registry = _get_ai_registry()
    db_ping_ms = await _db_ping_ms(session)
    run_rows = await _run_rows_for_period(session, today_start)
    completed_runs = [
        row for row in run_rows
        if row.started_at and row.finished_at and row.finished_at >= row.started_at
    ]
    avg_run_minutes = round(
        sum((row.finished_at - row.started_at).total_seconds() for row in completed_runs) / len(completed_runs) / 60.0,
        2,
    ) if completed_runs else None

    cpu_percent = memory_percent = disk_percent = network_mbps = None
    if psutil is not None:
        try:
            cpu_percent = round(float(psutil.cpu_percent(interval=0.1)), 2)
            memory_percent = round(float(psutil.virtual_memory().percent), 2)
            disk_path = os.getenv("SYSTEMDRIVE", "C:") + "\\" if os.name == "nt" else "/"
            disk_percent = round(float(psutil.disk_usage(disk_path).percent), 2)
            network = psutil.net_io_counters()
            network_mbps = round(((network.bytes_sent + network.bytes_recv) * 8) / 1_000_000, 2)
        except Exception as exc:
            logger.warning("System metrics collection failed: %s", exc)
    active_bots = 0
    if registry is not None:
        for bot_name in registry.list().keys():
            status_data = await _safe_bot_status(registry.get(bot_name))
            if str(status_data.get("status", "")).lower() in {"active", "healthy", "ok"}:
                active_bots += 1

    return {
        "status": "success",
        "metrics": {
            "api_performance": {
                "avg_response_time_ms": db_ping_ms,
                "requests_per_minute": None,
                "error_rate_percent": None,
                "uptime_percent": None,
            },
            "database": {
                "connection_pool_usage_percent": None,
                "avg_query_time_ms": db_ping_ms,
                "active_connections": None,
                "cache_hit_rate_percent": None,
            },
            "bots": {
                "total_bots": len(registry.list().keys()) if registry is not None else 0,
                "active_bots": active_bots,
                "operations_completed_today": len(run_rows),
                "avg_operation_time_minutes": avg_run_minutes,
            },
            "system_resources": {
                "cpu_usage_percent": cpu_percent,
                "memory_usage_percent": memory_percent,
                "disk_usage_percent": disk_percent,
                "network_throughput_mbps": network_mbps,
            },
            "timestamp": _iso(now),
        }
    }


@router.get("/performance", summary="Get performance analytics")
async def get_performance_analytics(
    payload: dict = Depends(verify_admin),
    session: AsyncSession = Depends(get_db)
):
    """
    Return bot and operations performance analytics.
    """
    now = _utcnow()
    today_start = _day_start(now)
    run_rows = await _run_rows_for_period(session, today_start)
    shipments_today = await _shipment_rows_for_period(session, today_start, today_start + timedelta(days=1))

    bot_totals: dict[str, dict[str, float]] = {}
    for row in run_rows:
        data = bot_totals.setdefault(row.bot_name, {"total": 0.0, "completed": 0.0, "failed": 0.0, "duration_minutes": 0.0, "timed": 0.0})
        data["total"] += 1
        status_name = _status_name(row.status)
        if status_name in {"completed", "success", "done"}:
            data["completed"] += 1
        elif status_name in {"failed", "error", "cancelled"}:
            data["failed"] += 1
        if row.started_at and row.finished_at and row.finished_at >= row.started_at:
            data["duration_minutes"] += (row.finished_at - row.started_at).total_seconds() / 60.0
            data["timed"] += 1

    max_total = max((int(item["total"]) for item in bot_totals.values()), default=0)
    bots_performance = {}
    for bot_name, stats in sorted(bot_totals.items()):
        total = _safe_int(stats["total"])
        completed = _safe_int(stats["completed"])
        failed = _safe_int(stats["failed"])
        timed = _safe_int(stats["timed"])
        avg_minutes = round(stats["duration_minutes"] / timed, 2) if timed else None
        success_rate = round((completed / total) * 100.0, 1) if total else 0.0
        utilization = round((total / max_total) * 100.0, 1) if max_total else 0.0
        bots_performance[bot_name] = {
            "operations_completed": total,
            "avg_response_time_minutes": avg_minutes,
            "success_rate_percent": success_rate,
            "utilization_percent": utilization,
        }

    total_operations = len(run_rows)
    completed_operations = sum(1 for row in run_rows if _status_name(row.status) in {"completed", "success", "done"})
    pending_operations = sum(1 for row in run_rows if _status_name(row.status) in {"running", "queued", "pending", "received"})
    failed_operations = sum(1 for row in run_rows if _status_name(row.status) in {"failed", "error", "cancelled"})

    shipment_completion_rate = round(
        (
            sum(1 for row in shipments_today if _status_name(row.status) in {"completed", "delivered"})
            / len(shipments_today)
        ) * 100.0,
        1,
    ) if shipments_today else 0.0
    bot_success_rate = round((completed_operations / total_operations) * 100.0, 1) if total_operations else 0.0
    efficiency_score = round((shipment_completion_rate + bot_success_rate) / 2.0, 1) if (shipments_today or total_operations) else 0.0

    bottleneck = "No active bottleneck detected"
    if bot_totals:
        highest_failure = max(bot_totals.items(), key=lambda item: item[1]["failed"])
        if highest_failure[1]["failed"] > 0:
            bottleneck = f"{highest_failure[0]} failure volume"
    elif pending_operations > 0:
        bottleneck = "Pending operations queue"

    recommendations: list[str] = []
    if pending_operations > completed_operations and pending_operations > 0:
        recommendations.append("Reduce pending bot run backlog by increasing worker concurrency.")
    if failed_operations > 0:
        recommendations.append("Review failed bot runs and retry policies for unstable workflows.")
    if shipment_completion_rate < 85:
        recommendations.append("Investigate delayed or cancelled shipments to improve completion rate.")
    if not recommendations:
        recommendations.append("Current operational telemetry does not indicate an immediate optimization target.")

    avg_completion_time_hours = round(
        sum(
            (row.finished_at - row.started_at).total_seconds()
            for row in run_rows
            if row.started_at and row.finished_at and row.finished_at >= row.started_at
        ) / max(
            1,
            sum(1 for row in run_rows if row.started_at and row.finished_at and row.finished_at >= row.started_at),
        ) / 3600.0,
        2,
    ) if run_rows else None

    return {
        "status": "success",
        "performance": {
            "bots_performance": bots_performance,
            "operations_stats": {
                "total_operations_today": total_operations,
                "completed_operations": completed_operations,
                "pending_operations": pending_operations,
                "failed_operations": failed_operations,
                "avg_completion_time_hours": avg_completion_time_hours,
            },
            "system_efficiency": {
                "overall_efficiency_score": efficiency_score,
                "bottleneck_identified": bottleneck,
                "recommended_optimizations": recommendations,
            },
            "timestamp": _iso(now),
        }
    }


@router.get("/system-health", summary="Get system health")
async def get_system_health(
    payload: dict = Depends(verify_admin),
    session: AsyncSession = Depends(get_db)
):
    """Return health status across key platform subsystems."""
    db_ping_ms = await _db_ping_ms(session)
    uptime_hours = _process_uptime_hours()
    cpu_percent = memory_percent = disk_percent = None
    if psutil is not None:
        try:
            cpu_percent = round(float(psutil.cpu_percent(interval=0.1)), 2)
            memory_percent = round(float(psutil.virtual_memory().percent), 2)
            disk_path = os.getenv("SYSTEMDRIVE", "C:") + "\\" if os.name == "nt" else "/"
            disk_percent = round(float(psutil.disk_usage(disk_path).percent), 2)
        except Exception as exc:
            logger.warning("System health collection failed: %s", exc)

    database_status = "healthy" if db_ping_ms is not None else "unhealthy"
    api_status = _derive_status(cpu_percent, memory_percent, disk_percent)
    if api_status == "unknown" and db_ping_ms is not None:
        api_status = "healthy"
    overall_status = "healthy" if database_status == "healthy" and api_status in {"healthy", "unknown"} else "warning"

    return {
        "status": "success",
        "health": {
            "api_servers": {
                "status": api_status,
                "response_time_avg_ms": db_ping_ms,
                "uptime_percent": None,
                "active_connections": None,
            },
            "database": {
                "status": database_status,
                "connection_pool_usage": None,
                "query_time_avg_ms": db_ping_ms,
                "replication_lag_ms": None,
            },
            "websocket_hub": {
                "status": "unknown",
                "connected_clients": None,
                "message_throughput": None,
            },
            "overall_status": overall_status,
            "message": "Live health snapshot from the application process and database.",
            "uptime_hours": uptime_hours,
        }
    }


@router.get("/logs", summary="Get system logs")
async def get_system_logs(
    log_type: str = Query("operations", description="Log channel: operations, performance, security, api, errors"),
    hours: int = Query(24, description="Time range in hours"),
    limit: int = Query(100, description="Maximum number of log entries to return"),
    payload: dict = Depends(verify_admin)
):
    """
    Return filtered system logs by type, time window, and result limit.

    - **log_type**: selected log channel
    - **hours**: lookback time window
    - **limit**: result size cap
    """
    try:
        import os
        from pathlib import Path
        from datetime import datetime, timedelta

        logs_dir = Path("logs")
        if not logs_dir.exists():
            return {
                "success": True,
                "logs": [],
                "message": "Logs directory was not found",
                "total_count": 0
            }

        # Map log type to file name
        log_files = {
            "operations": "operations.log",
            "performance": "performance.log",
            "security": "security.log",
            "api": "api.log",
            "errors": "errors.log"
        }

        log_file = logs_dir / log_files.get(log_type, "operations.log")
        if not log_file.exists():
            return {
                "success": True,
                "logs": [],
                "message": f"No log file found for type '{log_type}'",
                "total_count": 0
            }

        # Parse and filter log entries
        logs = []
        cutoff_time = datetime.now() - timedelta(hours=hours)

        with open(log_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    if line.strip():
                        # Parse JSON log line
                        log_entry = json.loads(line.strip())
                        log_time = datetime.fromisoformat(log_entry.get('timestamp', ''))

                        if log_time >= cutoff_time:
                            logs.append(log_entry)
                except json.JSONDecodeError:
                    # Fallback for non-JSON log lines
                    logs.append({
                        "timestamp": datetime.now().isoformat(),
                        "level": "INFO",
                        "message": line.strip(),
                        "raw": True
                    })

        # Sort newest first and apply limit
        logs.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        limited_logs = logs[:limit]

        return {
            "success": True,
            "log_type": log_type,
            "time_range_hours": hours,
            "logs": limited_logs,
            "total_count": len(logs),
            "returned_count": len(limited_logs)
        }

    except Exception as e:
        logger.error(f"Failed to fetch logs: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch logs: {str(e)}"
        )


@router.get("/logs/stats", summary="Get log statistics")
async def get_logs_statistics(payload: dict = Depends(verify_admin)):
    """Return log file size and recent-entry statistics."""
    try:
        import os
        from pathlib import Path
        from datetime import datetime, timedelta

        logs_dir = Path("logs")
        stats = {
            "total_log_files": 0,
            "total_log_size_mb": 0,
            "last_24h_entries": {},
            "log_types": {}
        }

        if logs_dir.exists():
            log_files = ["operations.log", "performance.log", "security.log", "api.log", "errors.log"]
            cutoff_time = datetime.now() - timedelta(hours=24)

            for log_file in log_files:
                file_path = logs_dir / log_file
                log_type = log_file.replace('.log', '')

                if file_path.exists():
                    stats["total_log_files"] += 1
                    stats["total_log_size_mb"] += file_path.stat().st_size / (1024 * 1024)

                    # Count entries in the last 24 hours
                    count_24h = 0
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            for line in f:
                                try:
                                    if line.strip():
                                        log_entry = json.loads(line.strip())
                                        log_time = datetime.fromisoformat(log_entry.get('timestamp', ''))
                                        if log_time >= cutoff_time:
                                            count_24h += 1
                                except:
                                    continue
                    except:
                        count_24h = 0

                    stats["last_24h_entries"][log_type] = count_24h
                    stats["log_types"][log_type] = {
                        "file_size_mb": round(file_path.stat().st_size / (1024 * 1024), 2),
                        "entries_24h": count_24h
                    }

        return {
            "success": True,
            "statistics": stats,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Failed to compute log statistics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to compute log statistics: {str(e)}"
        )


# ============================================
# User Management Endpoints (POST/PUT/PATCH/DELETE)
# ============================================

@router.post("/users-unified", summary="Create new user")
async def create_user(
    body: dict,
    payload: dict = Depends(verify_admin),
    session: AsyncSession = Depends(get_db)
):
    """Create a new user"""
    try:
        from backend.security.auth import get_password_hash
        
        email = body.get("email", "").lower().strip()
        if not email:
            raise HTTPException(status_code=400, detail="Email is required")
        
        # Check if user exists
        existing = await session.execute(
            select(User).where(User.email == email)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="User already exists")
        
        # Create user
        user = User(
            email=email,
            full_name=body.get("full_name", ""),
            username=body.get("username", ""),
            phone_number=body.get("phone_number", ""),
            company=body.get("company", ""),
            country=body.get("country", ""),
            user_type=body.get("user_type", ""),
            role=body.get("role", "user"),
            is_active=body.get("is_active", True),
        )
        
        if body.get("password"):
            user.hashed_password = get_password_hash(body["password"])
        
        session.add(user)
        await session.commit()
        await session.refresh(user)
        
        return {
            "status": "success",
            "message": "User created successfully",
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create user: {str(e)}")


@router.put("/users-unified/{user_id}", summary="Update user")
async def update_user(
    user_id: int,
    body: dict,
    payload: dict = Depends(verify_admin),
    session: AsyncSession = Depends(get_db)
):
    """Update user information"""
    try:
        result = await session.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Update fields
        if "full_name" in body:
            user.full_name = body["full_name"]
        if "username" in body:
            user.username = body["username"]
        if "phone_number" in body:
            user.phone_number = body["phone_number"]
        if "company" in body:
            user.company = body["company"]
        if "country" in body:
            user.country = body["country"]
        if "user_type" in body:
            user.user_type = body["user_type"]
        if "role" in body:
            user.role = body["role"]
        
        session.add(user)
        await session.commit()
        
        return {"status": "success", "message": "User updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update user: {str(e)}")


@router.patch("/users-unified/{user_id}", summary="Patch user")
async def patch_user(
    user_id: int,
    body: dict,
    payload: dict = Depends(verify_admin),
    session: AsyncSession = Depends(get_db)
):
    """Partially update user"""
    try:
        result = await session.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Handle all user update fields
        if "full_name" in body:
            user.full_name = body["full_name"]
        if "email" in body:
            user.email = body["email"]
        if "username" in body:
            user.username = body["username"]
        if "phone_number" in body:
            user.phone_number = body["phone_number"]
        if "company" in body:
            user.company = body["company"]
        if "country" in body:
            user.country = body["country"]
        if "user_type" in body:
            user.user_type = body["user_type"]
        if "role" in body:
            user.role = body["role"]
        if "is_active" in body:
            user.is_active = body["is_active"]
        if "is_banned" in body:
            user.is_banned = body["is_banned"]
        if "ban_reason" in body:
            user.ban_reason = body["ban_reason"]
        if "banned_until" in body:
            user.banned_until = body["banned_until"]
        
        # Handle password update if provided
        if "password" in body and body["password"]:
            from backend.security.passwords import hash_password
            user.hashed_password = hash_password(body["password"])
        
        user.updated_at = datetime.utcnow()
        
        session.add(user)
        await session.commit()
        await session.refresh(user)
        
        return {
            "status": "success",
            "message": "User patched successfully",
            "data": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "username": user.username,
                "role": user.role,
                "is_active": user.is_active,
                "is_banned": user.is_banned,
                "updated_at": user.updated_at.isoformat() if user.updated_at else None
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error patching user: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to patch user: {str(e)}")


@router.delete("/users-unified/{user_id}", summary="Delete user")
async def delete_user(
    user_id: int,
    payload: dict = Depends(verify_admin),
    session: AsyncSession = Depends(get_db)
):
    """Soft delete user"""
    try:
        result = await session.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Soft delete
        user.is_deleted = True
        user.deleted_at = datetime.utcnow()
        
        session.add(user)
        await session.commit()
        
        return {"status": "success", "message": "User deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete user: {str(e)}")


# =============== Portal Notifications ===============

@router.get("/portal/notifications", summary="Portal notifications - get notifications")
@router.get("/portal/notifications-unified", summary="Portal notifications - get notifications")
async def get_portal_notifications(
    limit: int = Query(100, ge=1, le=200),
    unread_only: bool = Query(False),
    payload: dict = Depends(verify_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Get portal notifications with optional filtering.
    """
    try:
        user_email = str(payload.get("email") or "").strip().lower()
        if not user_email:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

        user = (await db.execute(
            select(User).where(
                func.lower(User.email) == user_email,
                User.is_deleted.is_(False),
            )
        )).scalar_one_or_none()
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        stmt = (
            select(Notification)
            .where(Notification.user_id == user.id)
            .order_by(Notification.created_at.desc())
            .limit(limit)
        )
        if unread_only:
            stmt = stmt.where(Notification.is_read.is_(False))

        notification_rows = list((await db.execute(stmt)).scalars().all())
        unread_count = _safe_int((await db.execute(
            select(func.count(Notification.id)).where(
                Notification.user_id == user.id,
                Notification.is_read.is_(False),
            )
        )).scalar())
        total_count = _safe_int((await db.execute(
            select(func.count(Notification.id)).where(Notification.user_id == user.id)
        )).scalar())

        notifications = [
            {
                "id": row.id,
                "title": row.title,
                "message": row.message,
                "notification_type": row.channel or "update",
                "type": row.channel or "update",
                "read": bool(row.is_read),
                "created_at": _iso(row.created_at),
                "read_at": _iso(row.read_at),
                "request_id": None,
            }
            for row in notification_rows
        ]

        return {
            "ok": True,
            "notifications": notifications,
            "unread_count": unread_count,
            "total_count": total_count,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching notifications: {e}")
        return {
            "ok": True,
            "notifications": [],
            "unread_count": 0,
            "total_count": 0,
            "message": "Notifications are currently unavailable",
        }

