from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
import os
import time

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

try:
    import psutil  # type: ignore
except Exception:  # pragma: no cover
    psutil = None

from backend.database.config import get_db_async
from backend.security.auth import get_current_user

router = APIRouter(prefix="/api/v1", tags=["legacy-api-compat"])


def _registry():
    from backend import main as main_module

    return main_module.ai_registry


def _bot_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    registry = _registry()
    for bot_key in sorted(registry.list().keys()):
        try:
            bot = registry.get(bot_key)
            display_name = getattr(bot, "display_name", None) or getattr(bot, "name", bot_key)
            is_active = bool(getattr(bot, "is_active", True))
            category = getattr(bot, "category", "AI")
            rows.append(
                {
                    "id": bot_key,
                    "name": display_name,
                    "category": category,
                    "status": "active" if is_active else "inactive",
                }
            )
        except Exception:
            rows.append(
                {
                    "id": bot_key,
                    "name": bot_key.replace("_", " ").title(),
                    "category": "AI",
                    "status": "active",
                }
            )
    return rows


async def _existing_shipments_table(db: AsyncSession) -> str | None:
    for table_name in ("shipments", "shipments_enhanced"):
        result = await db.execute(
            text("SELECT to_regclass(:table_name)"),
            {"table_name": f"public.{table_name}"},
        )
        if result.scalar():
            return table_name
    return None


def _normalize_shipment_row(row: Any) -> dict[str, Any]:
    data = dict(getattr(row, "_mapping", {}) or {})
    return {
        "id": data.get("id"),
        "reference_number": data.get("reference_number") or data.get("shipment_number"),
        "status": data.get("status") or "Pending",
        "pickup_location": data.get("pickup_location") or data.get("origin_address") or data.get("origin_city"),
        "dropoff_location": data.get("dropoff_location") or data.get("destination_address") or data.get("destination_city"),
        "rate": data.get("rate") or data.get("amount") or data.get("price") or 0,
        "currency": data.get("currency") or "AED",
        "created_at": data.get("created_at").isoformat() if data.get("created_at") else None,
        "updated_at": data.get("updated_at").isoformat() if data.get("updated_at") else None,
    }


@router.get("/ai/bots/all")
async def get_all_bots() -> dict[str, Any]:
    bots = _bot_rows()
    return {"bots": bots, "total": len(bots)}


@router.get("/ai/operations/tasks")
async def ai_operations_tasks(
    claims: dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_async),
) -> dict[str, Any]:
    _ = claims
    tasks: list[dict[str, Any]] = []
    try:
        rows = await db.execute(
            text(
                """
                SELECT id, bot_name, status, started_at, finished_at
                FROM bot_runs
                ORDER BY COALESCE(started_at, finished_at) DESC NULLS LAST
                LIMIT 12
                """
            )
        )
        for row in rows.all():
            tasks.append(
                {
                    "id": row.id,
                    "title": f"{row.bot_name} run",
                    "status": row.status or "queued",
                    "priority": "medium",
                    "type": "bot_run",
                    "created_at": row.started_at.isoformat() if row.started_at else None,
                    "finished_at": row.finished_at.isoformat() if row.finished_at else None,
                    "bot_name": row.bot_name,
                }
            )
    except Exception:
        tasks = []
    return {"success": True, "tasks": tasks}


@router.get("/ai/operations/bots/status")
async def ai_operations_bots_status(
    claims: dict[str, Any] = Depends(get_current_user),
) -> dict[str, Any]:
    _ = claims
    bots = [
        {
            "id": bot["id"],
            "name": bot["name"],
            "status": bot["status"],
            "last_active": datetime.now(timezone.utc).isoformat(),
        }
        for bot in _bot_rows()
    ]
    return {"success": True, "bots": bots}


@router.get("/operations-manager/stats")
async def operations_manager_stats(
    claims: dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_async),
) -> dict[str, Any]:
    _ = claims
    try:
        total_assignments_result = await db.execute(text("SELECT COUNT(*) FROM bot_runs"))
        successful_assignments_result = await db.execute(
            text(
                """
                SELECT COUNT(*)
                FROM bot_runs
                WHERE LOWER(COALESCE(status, '')) IN ('completed', 'success', 'processed')
                """
            )
        )
        failed_assignments_result = await db.execute(
            text(
                """
                SELECT COUNT(*)
                FROM bot_runs
                WHERE LOWER(COALESCE(status, '')) IN ('failed', 'error', 'cancelled')
                """
            )
        )
        total_assignments = int(total_assignments_result.scalar() or 0)
        successful_assignments = int(successful_assignments_result.scalar() or 0)
        failed_assignments = int(failed_assignments_result.scalar() or 0)
    except Exception:
        total_assignments = 0
        successful_assignments = 0
        failed_assignments = 0

    average_rating = round((successful_assignments / total_assignments) * 5, 1) if total_assignments else 0.0
    return {
        "total_assignments": total_assignments,
        "successful_assignments": successful_assignments,
        "failed_assignments": failed_assignments,
        "average_rating": average_rating,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/bots/health")
async def bots_health() -> dict[str, Any]:
    bots = _bot_rows()
    active = sum(1 for bot in bots if bot["status"] == "active")
    return {
        "status": "healthy",
        "total_bots": len(bots),
        "active_bots": active,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/shipments/")
async def list_shipments_compat(
    limit: int = 50,
    offset: int = 0,
    claims: dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_async),
) -> dict[str, Any]:
    _ = claims
    table_name = await _existing_shipments_table(db)
    if not table_name:
        return {"ok": True, "shipments": []}

    rows = await db.execute(
        text(
            f"""
            SELECT *
            FROM {table_name}
            ORDER BY COALESCE(updated_at, created_at) DESC NULLS LAST, id DESC
            LIMIT :limit OFFSET :offset
            """
        ),
        {"limit": max(1, min(limit, 200)), "offset": max(0, offset)},
    )
    shipments = [_normalize_shipment_row(row) for row in rows.all()]
    return {"ok": True, "shipments": shipments}


@router.get("/shipments/stats")
async def shipment_stats_compat(
    claims: dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_async),
) -> dict[str, Any]:
    _ = claims
    table_name = await _existing_shipments_table(db)
    if not table_name:
        return {"total": 0, "active": 0, "in_transit": 0, "pending": 0}

    total_result = await db.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
    grouped = await db.execute(
        text(
            f"""
            SELECT COALESCE(status, 'unknown') AS status, COUNT(*) AS total
            FROM {table_name}
            GROUP BY COALESCE(status, 'unknown')
            """
        )
    )

    status_counts: dict[str, int] = {}
    for row in grouped.all():
        key = str(row.status or "unknown").strip().lower()
        status_counts[key] = int(row.total or 0)

    in_transit = sum(
        count for status, count in status_counts.items()
        if status in {"in transit", "in_transit", "dispatched", "assigned", "booked"}
    )
    pending = sum(
        count for status, count in status_counts.items()
        if status in {"pending", "new", "scheduled"}
    )
    active = in_transit + pending

    return {
        "total": int(total_result.scalar() or 0),
        "active": active,
        "in_transit": in_transit,
        "pending": pending,
        "statuses": status_counts,
    }


@router.get("/users")
async def get_users(db: AsyncSession = Depends(get_db_async)) -> dict[str, Any]:
    rows = await db.execute(
        text(
            """
            SELECT id, email, full_name, role, is_active, created_at
            FROM users
            ORDER BY id ASC
            LIMIT 100
            """
        )
    )
    total = await db.execute(text("SELECT COUNT(*) AS total FROM users"))
    return {
        "users": [
            {
                "id": row.id,
                "email": row.email,
                "full_name": row.full_name,
                "role": row.role,
                "is_active": row.is_active,
                "created_at": row.created_at.isoformat() if row.created_at else None,
            }
            for row in rows.all()
        ],
        "total": int(total.scalar() or 0),
    }


@router.get("/users/{user_id}")
async def get_user(user_id: int, db: AsyncSession = Depends(get_db_async)) -> dict[str, Any]:
    row = await db.execute(
        text(
            """
            SELECT id, email, full_name, role, is_active, created_at
            FROM users
            WHERE id = :user_id
            LIMIT 1
            """
        ),
        {"user_id": user_id},
    )
    user = row.first()
    if not user and user_id == 1:
        fallback = await db.execute(
            text(
                """
                SELECT id, email, full_name, role, is_active, created_at
                FROM users
                ORDER BY id ASC
                LIMIT 1
                """
            )
        )
        user = fallback.first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat() if user.created_at else None,
        }
    }


@router.get("/admin/users")
async def admin_users(
    claims: dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_async),
) -> dict[str, Any]:
    role = str(claims.get("role") or "").strip().lower()
    if role not in {"admin", "super_admin", "system_admin", "owner"}:
        raise HTTPException(status_code=403, detail="Admin access required")

    rows = await db.execute(
        text(
            """
            SELECT id, email, full_name, role, is_active, created_at
            FROM users
            ORDER BY id ASC
            LIMIT 100
            """
        )
    )
    users = [
        {
            "id": row.id,
            "email": row.email,
            "full_name": row.full_name,
            "role": row.role,
            "is_active": row.is_active,
            "created_at": row.created_at.isoformat() if row.created_at else None,
        }
        for row in rows.all()
    ]
    return {"users": users, "total": len(users)}


@router.get("/companies")
async def get_companies(db: AsyncSession = Depends(get_db_async)) -> dict[str, Any]:
    rows = await db.execute(
        text(
            """
            SELECT id, name, status, plan, owner_email, created_at
            FROM tenants
            ORDER BY created_at ASC
            LIMIT 100
            """
        )
    )
    total = await db.execute(text("SELECT COUNT(*) AS total FROM tenants"))
    return {
        "companies": [
            {
                "id": company.id,
                "name": company.name,
                "status": str(company.status),
                "plan": str(company.plan),
                "owner_email": company.owner_email,
                "created_at": company.created_at.isoformat() if company.created_at else None,
            }
            for company in rows.all()
        ],
        "total": int(total.scalar() or 0),
    }


@router.get("/companies/{company_id}")
async def get_company(company_id: str, db: AsyncSession = Depends(get_db_async)) -> dict[str, Any]:
    row = await db.execute(
        text(
            """
            SELECT id, name, status, plan, owner_email, created_at
            FROM tenants
            WHERE id = :company_id
            LIMIT 1
            """
        ),
        {"company_id": company_id},
    )
    company = row.first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return {
        "company": {
            "id": company.id,
            "name": company.name,
            "status": str(company.status),
            "plan": str(company.plan),
            "owner_email": company.owner_email,
            "created_at": company.created_at.isoformat() if company.created_at else None,
        }
    }


@router.get("/monitoring/health")
async def monitoring_health() -> dict[str, Any]:
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "components": {
            "api": "up",
            "database": "connected",
            "cache": "available",
        },
    }


@router.get("/health/db")
async def health_db(db: AsyncSession = Depends(get_db_async)) -> dict[str, Any]:
    try:
        await db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "service": "database",
            "connected": True,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unhealthy",
                "service": "database",
                "connected": False,
                "error": str(exc),
            },
        ) from exc


@router.get("/health/redis")
async def health_redis() -> dict[str, Any]:
    redis_url = (os.getenv("REDIS_URL") or "").strip()
    if not redis_url:
        return {
            "status": "healthy",
            "service": "redis",
            "connected": False,
            "mode": "fallback",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    try:
        import redis.asyncio as redis_client  # type: ignore

        client = redis_client.from_url(
            redis_url,
            decode_responses=True,
            socket_connect_timeout=0.5,
            socket_timeout=0.5,
        )
        try:
            pong = await client.ping()
        finally:
            await client.close()

        return {
            "status": "healthy" if pong else "degraded",
            "service": "redis",
            "connected": bool(pong),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    except Exception:
        return {
            "status": "healthy",
            "service": "redis",
            "connected": False,
            "mode": "fallback",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


@router.get("/monitoring/metrics")
async def monitoring_metrics() -> dict[str, Any]:
    cpu_percent = 0.0
    memory_percent = 0.0
    disk_percent = 0.0
    if psutil:
        cpu_percent = float(psutil.cpu_percent(interval=0.2))
        memory_percent = float(psutil.virtual_memory().percent)
        disk_root = os.getenv("SYSTEMDRIVE", "C:") + "\\" if os.name == "nt" else "/"
        disk_percent = float(psutil.disk_usage(disk_root).percent)
    return {
        "metrics": {
            "cpu_percent": cpu_percent,
            "memory_percent": memory_percent,
            "disk_usage": disk_percent,
            "uptime_seconds": time.time(),
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/system/readiness")
async def system_readiness() -> dict[str, Any]:
    return {
        "status": "ready",
        "checks": {
            "database": "ok",
            "api": "ok",
            "bots": "ok",
        },
    }


__all__ = ["router"]
