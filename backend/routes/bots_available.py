from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from backend.ai.access_engine import build_available_bots, evaluate_bot_access
from backend.database.config import get_db_async
from backend.security.access_context import build_auth_me_payload
from backend.security.auth import get_current_user

router = APIRouter(prefix="/api/v1/bots", tags=["Bots"])
compat_router = APIRouter(prefix="/api/v1/ai/bots/available", tags=["AI Bots Compat"])


class BotRunPayload(BaseModel):
    message: str = ""
    context: Optional[Dict[str, Any]] = None
    meta: Optional[Dict[str, Any]] = None


def _registry():
    from backend import main as main_module

    return main_module.ai_registry


def _get_bot_or_404(bot_key: str):
    registry = _registry()
    try:
        return registry.get(bot_key)
    except Exception:
        raise HTTPException(status_code=404, detail=f"Bot '{bot_key}' not found")


async def _maybe_await(value: Any) -> Any:
    if hasattr(value, "__await__"):
        return await value
    return value


async def _bot_config(bot: Any) -> Dict[str, Any]:
    if hasattr(bot, "config") and callable(getattr(bot, "config")):
        return await _maybe_await(bot.config())
    return {"bot": getattr(bot, "name", "unknown"), "mode": "default"}


async def _bot_status_payload(bot: Any) -> Dict[str, Any]:
    if hasattr(bot, "status") and callable(getattr(bot, "status")):
        return await _maybe_await(bot.status())
    if hasattr(bot, "get_status") and callable(getattr(bot, "get_status")):
        return await _maybe_await(bot.get_status())
    return {"status": "running", "available": True}


@router.get("/available")
async def list_available_bots(
    request: Request,
    db: AsyncSession = Depends(get_db_async),
    claims: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    payload = await build_auth_me_payload(request, db, claims)
    role = payload.get("user", {}).get("role", "user")
    features = set(payload.get("features") or [])
    permissions = set(payload.get("user", {}).get("permissions") or [])
    plan_key = payload.get("tenant", {}).get("plan_key") or "tms"
    modules = payload.get("modules") or {}

    registry = _registry()
    data = build_available_bots(
        registry=registry,
        role=role,
        features=features,
        permissions=permissions,
        plan_key=plan_key,
        modules=modules,
    )

    return {
        "ok": True,
        "bots": data["bots"],
        "aliases": data["aliases"],
        "count": data["count"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@compat_router.post("/{bot_key}/run")
@router.post("/{bot_key}/run")
async def run_bot(
    bot_key: str,
    payload: BotRunPayload,
    request: Request,
    db: AsyncSession = Depends(get_db_async),
    claims: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    auth_payload = await build_auth_me_payload(request, db, claims)
    role = auth_payload.get("user", {}).get("role", "user")
    features = set(auth_payload.get("features") or [])
    permissions = set(auth_payload.get("user", {}).get("permissions") or [])
    plan_key = auth_payload.get("tenant", {}).get("plan_key") or "tms"

    registry = _registry()
    from backend.ai.access_engine import _bot_status  # type: ignore

    status_value = _bot_status(registry, bot_key)
    decision = evaluate_bot_access(
        bot_key,
        role=role,
        features=features,
        permissions=permissions,
        plan_key=plan_key,
        status=status_value,
    )

    if not decision.get("can_run"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "forbidden",
                "reason_codes": decision.get("reason_codes", []),
            },
        )

    try:
        from backend.bots.rate_limit import RoleRateLimiter  # type: ignore

        limiter = RoleRateLimiter()
        rate_key = f"bots.run:{bot_key}"
        limit_decision = limiter.check(role, rate_key)
        if not limit_decision.allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={"error": "rate_limited", "retry_in": limit_decision.reset_in},
            )
    except HTTPException:
        raise
    except Exception:
        pass

    bot = _get_bot_or_404(bot_key)
    trace_id = uuid.uuid4().hex
    ts = datetime.now(timezone.utc).isoformat()

    run_payload = {
        "message": payload.message,
        "context": payload.context or {},
        "meta": payload.meta or {},
        "trace_id": trace_id,
        "ts": ts,
    }

    if hasattr(bot, "process_message") and callable(getattr(bot, "process_message")):
        result = await bot.process_message(payload.message, payload.context or {})
    else:
        result = await bot.run(run_payload)

    return {
        "ok": True,
        "bot_key": bot_key,
        "result": result,
        "trace_id": trace_id,
        "timestamp": ts,
    }


@compat_router.get("/{bot_key}/status")
@router.get("/{bot_key}/status")
async def bot_status(
    bot_key: str,
    request: Request,
    db: AsyncSession = Depends(get_db_async),
    claims: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """Get the status of a specific bot"""
    bot = _get_bot_or_404(bot_key)
    
    try:
        status_data = await _bot_status_payload(bot)
    except Exception as e:
        status_data = {"status": "error", "error": str(e), "available": False}

    return {
        "ok": True,
        "bot_key": bot_key,
        "status": status_data,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@compat_router.get("/{bot_key}/health")
@router.get("/{bot_key}/health")
async def bot_health(
    bot_key: str,
    request: Request,
    db: AsyncSession = Depends(get_db_async),
    claims: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    return await bot_status(bot_key=bot_key, request=request, db=db, claims=claims)


@compat_router.get("/{bot_key}/config")
@router.get("/{bot_key}/config")
async def bot_config(
    bot_key: str,
    request: Request,
    db: AsyncSession = Depends(get_db_async),
    claims: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    bot = _get_bot_or_404(bot_key)
    try:
        config_data = await _bot_config(bot)
    except Exception as e:
        config_data = {"error": str(e), "available": False}
    return {
        "ok": True,
        "bot_key": bot_key,
        "config": config_data,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


__all__ = ["compat_router", "router"]

