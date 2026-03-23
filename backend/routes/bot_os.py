from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from backend.bots import get_bot_os
from backend.bots.command_parser import parse_command
from backend.bots.rate_limit import RoleRateLimiter
from backend.bots.ws_manager import broadcast_event
from backend.models.bot_os import HumanCommand
from backend.security.auth import get_current_user
from backend.security.scope_dependency import require_scope
from backend.database.session import wrap_session_factory

logger = logging.getLogger("bots.os.routes")

router = APIRouter(prefix="/api/v1", tags=["Bot OS"])
_rate_limiter = RoleRateLimiter()


class HumanCommandPayload(BaseModel):
    command: str = Field(..., min_length=1)
    bot_name: Optional[str] = None
    task_type: Optional[str] = None
    params: Dict[str, Any] = Field(default_factory=dict)


def _get_role(user: Dict[str, Any]) -> str:
    if not isinstance(user, dict):
        return "user"
    return (
        user.get("effective_role")
        or user.get("role")
        or user.get("db_role")
        or user.get("token_role")
        or user.get("user_type")
        or "user"
    ).lower()



@router.get("/bots", dependencies=[Depends(require_scope("bot:read"))])
async def list_bots(user: Dict[str, Any] = Depends(get_current_user)):
    bot_os = get_bot_os()
    return {"bots": await bot_os.list_bots()}


@router.get("/bots/history")
async def list_bot_history(limit: int = 50, user: Dict[str, Any] = Depends(get_current_user)):
    bot_os = get_bot_os()
    return {"runs": await bot_os.list_runs(limit=limit)}


@router.get("/bots/stats")
async def bot_stats(user: Dict[str, Any] = Depends(get_current_user)):
    bot_os = get_bot_os()
    return await bot_os.stats()


@router.post("/commands/human")
async def run_human_command(payload: HumanCommandPayload, user: Dict[str, Any] = Depends(get_current_user)):
    bot_os = get_bot_os()
    role = _get_role(user)
    user_id = user.get("id")
    user_email = user.get("email") or user.get("username")
    rate_key = str(user_id or user_email or "anonymous")

    decision = _rate_limiter.check(role, rate_key)
    if not decision.allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={"error": "rate_limited", "retry_in": decision.reset_in},
        )

    parsed = parse_command(payload.command)
    bot_name = payload.bot_name or parsed.get("bot_name")
    task_type = payload.task_type or parsed.get("task_type") or "run"
    params = payload.params or parsed.get("params") or {}

    if not bot_name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="bot_name_required")
    if not bot_os.has_bot(bot_name):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="bot_not_found")

    try:
        async with wrap_session_factory(bot_os.session_factory) as session:
            command = HumanCommand(
                user_id=user_id,
                user_email=user_email,
                natural_command=payload.command,
                parsed_json=parsed,
                technical_json={"bot_name": bot_name, "task_type": task_type, "params": params},
                status="running",
            )
            session.add(command)
            await session.commit()
            await session.refresh(command)
            command_id = command.id

        paused = await bot_os.pause_bot(bot_name)
        result = None
        error = None
        status_value = "completed"
        try:
            result = await bot_os.execute_bot(
                bot_name, task_type=task_type, params=params, allow_paused=True
            )
        except Exception as exc:
            status_value = "failed"
            error = str(exc)
        finally:
            if paused:
                await bot_os.resume_bot(bot_name)

        async with wrap_session_factory(bot_os.session_factory) as session:
            command_row = await session.get(HumanCommand, command_id)
            if command_row:
                command_row.status = status_value
                command_row.result_json = {
                    "run_id": result.run_id if result else None,
                    "status": result.status if result else "failed",
                    "error": error or (result.error if result else None),
                }
                await session.commit()

        await broadcast_event(
            channel="commands.executed",
            payload={
                "command_id": command_id,
                "bot_name": bot_name,
                "task_type": task_type,
                "status": status_value,
            },
        )

        return {
            "ok": status_value == "completed",
            "command_id": command_id,
            "bot_name": bot_name,
            "task_type": task_type,
            "result": result.result if result else None,
            "error": error or (result.error if result else None),
        }
    except Exception as exc:
        logger.exception("run_human_command failed: %s", exc)
        return {
            "ok": False,
            "command_id": None,
            "bot_name": bot_name,
            "task_type": task_type,
            "result": None,
            "error": str(exc),
        }

