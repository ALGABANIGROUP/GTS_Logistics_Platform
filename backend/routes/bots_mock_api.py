from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from backend.bots import get_bot_os
from backend.bots import BOTS_REGISTRY, get_active_bots
from backend.bots.command_parser import parse_command
from backend.database.session import get_async_session
from backend.security.auth import get_current_user

router = APIRouter(prefix="/api/v1/bots", tags=["Bots"])


class BotStatsResponse(BaseModel):
    total_runs: int
    by_status: Dict[str, int]
    human_commands: int
    active_bots: int


def _slug(value: str) -> str:
    return str(value or "").strip().lower().replace(" ", "_")


async def _list_bots() -> list[Dict[str, Any]]:
    try:
        bot_os = get_bot_os()
        return await bot_os.list_bots()
    except RuntimeError:
        active = set(get_active_bots())
        return [
            {
                "bot_name": bot_name,
                "enabled": bot_name in active,
                "automation_level": "manual",
                "schedule_cron": None,
                "status": "idle" if bot_name in active else "inactive",
                "last_run": None,
            }
            for bot_name in sorted(BOTS_REGISTRY.keys())
        ]


def _bot_os_or_none():
    try:
        return get_bot_os()
    except RuntimeError:
        return None


async def _resolve_bot_name(bot_name: str) -> str | None:
    normalized = _slug(bot_name)
    for item in await _list_bots():
        candidate = str(item.get("bot_name") or "")
        if candidate == bot_name or _slug(candidate) == normalized:
            return candidate
    return None


@router.get("/mock", response_model=Dict[str, Any])
async def get_bots(
    session: AsyncSession = Depends(get_async_session),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    del session, current_user
    bots = await _list_bots()
    return {"ok": True, "bots": bots}


@router.get("/mock/stats", response_model=BotStatsResponse)
async def get_bot_stats(
    session: AsyncSession = Depends(get_async_session),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> BotStatsResponse:
    del session, current_user
    bot_os = _bot_os_or_none()
    if bot_os is None:
      bots = await _list_bots()
      by_status = {
        "completed": 0,
        "failed": 0,
        "running": 0,
        "pending": 0,
      }
      active_bots = sum(1 for bot in bots if bot.get("enabled"))
      return BotStatsResponse(
          total_runs=0,
          by_status=by_status,
          human_commands=0,
          active_bots=active_bots,
      )
    stats = await bot_os.stats()
    bots = await bot_os.list_bots()
    active_bots = sum(1 for bot in bots if bot.get("enabled"))
    return BotStatsResponse(
        total_runs=int(stats.get("total_runs", 0)),
        by_status={str(key): int(value or 0) for key, value in (stats.get("by_status") or {}).items()},
        human_commands=int(stats.get("human_commands", 0)),
        active_bots=active_bots,
    )


@router.get("/mock/history", response_model=Dict[str, Any])
async def get_bot_history(
    limit: int = 20,
    session: AsyncSession = Depends(get_async_session),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    del session, current_user
    bot_os = _bot_os_or_none()
    if bot_os is None:
        return {"ok": True, "runs": []}
    return {"ok": True, "runs": await bot_os.list_runs(limit=limit)}


@router.post("/commands/human", response_model=Dict[str, Any])
async def execute_human_command(
    data: Dict[str, str],
    session: AsyncSession = Depends(get_async_session),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    del session
    command = str(data.get("command") or "").strip()
    if not command:
        raise HTTPException(status_code=400, detail="Command cannot be empty")

    parsed = parse_command(command)
    bot_name = parsed.get("bot_name")
    task_type = parsed.get("task_type") or "run"
    params = parsed.get("params") or {}

    if not bot_name:
        raise HTTPException(status_code=400, detail="Unable to determine target bot")

    resolved_bot_name = await _resolve_bot_name(str(bot_name))
    if not resolved_bot_name:
        raise HTTPException(status_code=404, detail=f"Bot '{bot_name}' not found")

    bot_os = _bot_os_or_none()
    if bot_os is None:
        raise HTTPException(status_code=503, detail="Bot operating system is not initialized")
    result = await bot_os.execute_bot(
        resolved_bot_name,
        task_type=str(task_type),
        params={
            **params,
            "requested_by": current_user.get("email") or current_user.get("id"),
            "natural_command": command,
        },
        allow_paused=True,
    )
    return {
        "ok": result.status == "completed",
        "message": f"Command executed for {resolved_bot_name}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "bot_name": resolved_bot_name,
        "task_type": result.task_type,
        "run_id": result.run_id,
        "result": result.result,
        "error": result.error,
    }


@router.post("/{bot_name}/pause", response_model=Dict[str, Any])
async def pause_bot(
    bot_name: str,
    session: AsyncSession = Depends(get_async_session),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    del session, current_user
    resolved_bot_name = await _resolve_bot_name(bot_name)
    if not resolved_bot_name:
        raise HTTPException(status_code=404, detail=f"Bot '{bot_name}' not found")
    bot_os = _bot_os_or_none()
    if bot_os is None:
        raise HTTPException(status_code=503, detail="Bot operating system is not initialized")
    changed = await bot_os.pause_bot(resolved_bot_name)
    return {"ok": True, "message": f"Bot '{resolved_bot_name}' paused", "changed": changed}


@router.post("/{bot_name}/resume", response_model=Dict[str, Any])
async def resume_bot(
    bot_name: str,
    session: AsyncSession = Depends(get_async_session),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    del session, current_user
    resolved_bot_name = await _resolve_bot_name(bot_name)
    if not resolved_bot_name:
        raise HTTPException(status_code=404, detail=f"Bot '{bot_name}' not found")
    bot_os = _bot_os_or_none()
    if bot_os is None:
        raise HTTPException(status_code=503, detail="Bot operating system is not initialized")
    changed = await bot_os.resume_bot(resolved_bot_name)
    return {"ok": True, "message": f"Bot '{resolved_bot_name}' resumed", "changed": changed}


@router.post("/{bot_name}/restart", response_model=Dict[str, Any])
async def restart_bot(
    bot_name: str,
    session: AsyncSession = Depends(get_async_session),
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    del session, current_user
    resolved_bot_name = await _resolve_bot_name(bot_name)
    if not resolved_bot_name:
        raise HTTPException(status_code=404, detail=f"Bot '{bot_name}' not found")
    bot_os = _bot_os_or_none()
    if bot_os is None:
        raise HTTPException(status_code=503, detail="Bot operating system is not initialized")
    await bot_os.resume_bot(resolved_bot_name)
    run = await bot_os.execute_bot(
        resolved_bot_name,
        task_type="healthcheck",
        params={"source": "restart_route"},
        allow_paused=True,
    )
    return {
        "ok": run.status == "completed",
        "message": f"Bot '{resolved_bot_name}' restarted",
        "run_id": run.run_id,
        "status": run.status,
        "error": run.error,
    }


__all__ = ["router"]
