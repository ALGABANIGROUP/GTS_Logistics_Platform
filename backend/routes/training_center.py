from __future__ import annotations

import logging
from typing import Any, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from backend.training_center.core.trainer_bot import TrainerBot

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/training-center", tags=["training-center"])
_trainer = TrainerBot()


class RegisterBotRequest(BaseModel):
    bot_key: str
    level: Optional[str] = "beginner"
    version: Optional[str] = "1.0"


class AssessBotRequest(BaseModel):
    bot_key: str


class CreatePlanRequest(BaseModel):
    bot_key: str
    goal: Optional[str] = None


class StartSessionRequest(BaseModel):
    plan_id: str


def _normalize_bot_key(bot_key: Optional[str]) -> Optional[str]:
    if not bot_key:
        return None
    return _trainer.bot_connector.normalize_bot_key(bot_key)


def _bad_request(exc: Exception) -> HTTPException:
    return HTTPException(status_code=400, detail=str(exc))


@router.get("/bots")
async def list_trainable_bots() -> dict[str, Any]:
    return {"success": True, "bots": _trainer.list_trainable_bots()}


@router.post("/bots/register")
async def register_bot(payload: RegisterBotRequest) -> dict[str, Any]:
    try:
        profile = await _trainer.register_bot(
            payload.bot_key,
            level=payload.level,
            version=payload.version,
        )
    except ValueError as exc:
        raise _bad_request(exc) from exc
    return {"success": True, "profile": profile}


@router.post("/assess")
async def assess_bot(payload: AssessBotRequest) -> dict[str, Any]:
    try:
        assessment = await _trainer.assess_bot_capabilities(payload.bot_key)
    except ValueError as exc:
        raise _bad_request(exc) from exc
    return {"success": True, "assessment": assessment}


@router.post("/plans")
async def create_training_plan(payload: CreatePlanRequest) -> dict[str, Any]:
    try:
        plan = await _trainer.create_training_plan(payload.bot_key, payload.goal)
    except ValueError as exc:
        raise _bad_request(exc) from exc
    return {"success": True, "plan": plan}


@router.get("/courses")
async def list_courses(
    specialization: Optional[str] = Query(default=None),
) -> dict[str, Any]:
    courses = await _trainer.list_available_courses()
    if specialization:
        courses = [course for course in courses if course.get("specialization") == specialization]
    return {"success": True, "courses": courses}


@router.post("/sessions/start")
async def start_training_session(payload: StartSessionRequest) -> dict[str, Any]:
    try:
        result = await _trainer.start_training_session(payload.plan_id)
    except ValueError as exc:
        raise _bad_request(exc) from exc
    return {"success": True, **result}


@router.get("/sessions/{session_id}")
async def get_training_session(session_id: str) -> dict[str, Any]:
    session = _trainer.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Training session not found")
    return {"success": True, "session": session}


@router.get("/reports/{session_id}")
async def get_training_report(session_id: str) -> dict[str, Any]:
    report = _trainer.get_report(session_id)
    if not report:
        raise HTTPException(status_code=404, detail="Training report not found")
    return {"success": True, "report": report}


@router.get("/reports")
async def list_training_reports(
    bot_key: Optional[str] = Query(default=None),
) -> dict[str, Any]:
    normalized_bot_key = _normalize_bot_key(bot_key)
    reports = _trainer.list_reports()
    if normalized_bot_key:
        reports = [report for report in reports if report.get("bot_key") == normalized_bot_key]
    return {"success": True, "reports": reports}


@router.get("/stats")
async def get_training_stats() -> dict[str, Any]:
    return {"success": True, "stats": _trainer.get_stats()}
