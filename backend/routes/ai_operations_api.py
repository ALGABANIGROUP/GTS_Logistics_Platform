from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.session import get_async_session
from backend.models.bot_os import BotRegistry, BotRun
from backend.models.shipment import Shipment
from backend.security.auth import get_current_user

router = APIRouter(tags=["AI Operations"])


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _is_admin(user: Dict[str, Any] | None) -> bool:
    if not isinstance(user, dict):
        return False
    role = str(
        user.get("effective_role")
        or user.get("role")
        or user.get("db_role")
        or user.get("token_role")
        or ""
    ).strip().lower()
    return role in {"admin", "super_admin", "owner", "system_admin"}


def _to_iso(value: Any) -> str | None:
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).isoformat()
    return None


async def _build_status(session: AsyncSession) -> Dict[str, Any]:
    now = _utcnow()
    day_start = now - timedelta(hours=24)

    try:
        registry_rows = (
            await session.execute(select(BotRegistry).order_by(BotRegistry.bot_name.asc()))
        ).scalars().all()
    except Exception:
        registry_rows = []
    try:
        recent_runs = (
            await session.execute(
                select(BotRun)
                .where(BotRun.started_at >= day_start)
                .order_by(desc(BotRun.started_at))
            )
        ).scalars().all()
    except Exception:
        recent_runs = []

    latest_by_bot: Dict[str, BotRun] = {}
    by_status: Dict[str, int] = {}
    for run in recent_runs:
        by_status[run.status] = by_status.get(run.status, 0) + 1
        if run.bot_name not in latest_by_bot:
            latest_by_bot[run.bot_name] = run

    try:
        active_shipments = (
            await session.execute(
                select(func.count(Shipment.id)).where(
                    func.lower(func.coalesce(Shipment.status, "")).in_(
                        ["pending", "assigned", "in_transit", "delayed"]
                    )
                )
            )
        ).scalar()
    except Exception:
        active_shipments = 0

    bots = []
    for entry in registry_rows:
        last_run = latest_by_bot.get(entry.bot_name)
        derived_status = "inactive"
        if entry.enabled:
            derived_status = "idle"
            if last_run is not None:
                if str(last_run.status).lower() in {"failed", "error", "cancelled"}:
                    derived_status = "error"
                elif str(last_run.status).lower() == "running":
                    derived_status = "running"

        bots.append(
            {
                "bot_name": entry.bot_name,
                "enabled": bool(entry.enabled),
                "automation_level": entry.automation_level,
                "schedule_cron": entry.schedule_cron,
                "status": derived_status,
                "last_run": {
                    "id": last_run.id,
                    "status": last_run.status,
                    "started_at": _to_iso(last_run.started_at),
                    "finished_at": _to_iso(last_run.finished_at),
                    "error": last_run.error,
                }
                if last_run is not None
                else None,
            }
        )

    return {
        "timestamp": now.isoformat(),
        "registry": {
            "total_bots": len(registry_rows),
            "enabled_bots": sum(1 for entry in registry_rows if entry.enabled),
            "paused_bots": sum(
                1 for entry in registry_rows if str(entry.automation_level or "").lower() == "paused"
            ),
        },
        "runs": {
            "last_24h": len(recent_runs),
            "by_status": by_status,
        },
        "shipments": {
            "active": int(active_shipments or 0),
        },
        "bots": bots,
    }


@router.get("/ai/operations/status")
async def get_ai_operations_status(
    session: AsyncSession = Depends(get_async_session),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    return {"success": True, "status": await _build_status(session)}


@router.get("/ai/operations/metrics")
async def get_ai_operations_metrics(
    period: str = "24h",
    session: AsyncSession = Depends(get_async_session),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    if not _is_admin(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    period_map = {
        "24h": timedelta(hours=24),
        "7d": timedelta(days=7),
        "30d": timedelta(days=30),
    }
    window = period_map.get(period, timedelta(hours=24))
    started_after = _utcnow() - window

    try:
        total_runs = (
            await session.execute(
                select(func.count(BotRun.id)).where(BotRun.started_at >= started_after)
            )
        ).scalar()
        successful_runs = (
            await session.execute(
                select(func.count(BotRun.id)).where(
                    BotRun.started_at >= started_after,
                    func.lower(func.coalesce(BotRun.status, "")) == "completed",
                )
            )
        ).scalar()
        failed_runs = (
            await session.execute(
                select(func.count(BotRun.id)).where(
                    BotRun.started_at >= started_after,
                    func.lower(func.coalesce(BotRun.status, "")).in_(["failed", "error", "cancelled"]),
                )
            )
        ).scalar()

        by_bot_rows = (
            await session.execute(
                select(BotRun.bot_name, func.count(BotRun.id))
                .where(BotRun.started_at >= started_after)
                .group_by(BotRun.bot_name)
                .order_by(desc(func.count(BotRun.id)))
            )
        ).all()
    except Exception:
        total_runs = 0
        successful_runs = 0
        failed_runs = 0
        by_bot_rows = []

    return {
        "success": True,
        "metrics": {
            "period": period,
            "window_start": started_after.isoformat(),
            "total_runs": int(total_runs or 0),
            "successful_runs": int(successful_runs or 0),
            "failed_runs": int(failed_runs or 0),
            "success_rate": round((int(successful_runs or 0) / int(total_runs or 1)) * 100.0, 1)
            if int(total_runs or 0) > 0
            else 0.0,
            "by_bot": [
                {"bot_name": bot_name, "runs": int(count or 0)}
                for bot_name, count in by_bot_rows
            ],
        },
    }


@router.post("/ai/operations/optimize")
async def trigger_ai_optimization(
    payload: Dict[str, Any] | None = None,
    session: AsyncSession = Depends(get_async_session),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    if not _is_admin(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    status_snapshot = await _build_status(session)
    suggested_actions = []
    for bot in status_snapshot["bots"]:
        if bot["enabled"] and bot["status"] == "error":
            suggested_actions.append(
                {
                    "bot_name": bot["bot_name"],
                    "action": "investigate_last_failure",
                    "reason": "Bot has a failed or error status in the most recent run.",
                }
            )
        if bot["enabled"] and not bot["schedule_cron"]:
            suggested_actions.append(
                {
                    "bot_name": bot["bot_name"],
                    "action": "review_schedule",
                    "reason": "Enabled bot has no schedule configured.",
                }
            )

    return {
        "success": True,
        "result": {
            "triggered_at": _utcnow().isoformat(),
            "requested_by": current_user.get("email") or current_user.get("id"),
            "mode": (payload or {}).get("mode", "analysis"),
            "actions_recommended": suggested_actions,
            "status_snapshot": status_snapshot,
        },
    }


@router.post("/ai/ops/load-import/trigger")
async def trigger_load_import(
    session: AsyncSession = Depends(get_async_session),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    if not _is_admin(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    status_snapshot = await _build_status(session)
    return {
        "status": "disabled",
        "message": "Legacy offline load import has been removed. Use the live AI operations endpoints instead.",
        "status_snapshot": status_snapshot,
    }
