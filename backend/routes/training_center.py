from __future__ import annotations

from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from backend.training_center import TrainerBot


router = APIRouter(prefix="/api/v1/training-center", tags=["Training Center"])

_trainer = TrainerBot(
    data_dir=Path(__file__).resolve().parents[1] / "training_center" / "data",
    reports_dir=Path(__file__).resolve().parents[1] / "training_center" / "reports",
)


class RegisterBotRequest(BaseModel):
    bot_key: str = Field(..., min_length=1)
    level: str = "beginner"
    version: str = "1.0"


class AssessBotRequest(BaseModel):
    bot_key: str = Field(..., min_length=1)


class CreatePlanRequest(BaseModel):
    bot_key: str = Field(..., min_length=1)
    goal: Optional[str] = None


class StartSessionRequest(BaseModel):
    plan_id: str = Field(..., min_length=1)


@router.get("/bots")
async def list_trainable_bots():
    return {"success": True, "bots": _trainer.list_trainable_bots()}


@router.post("/bots/register")
async def register_bot(request: RegisterBotRequest):
    try:
        profile = await _trainer.register_bot(request.bot_key, level=request.level, version=request.version)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"success": True, "profile": profile}


@router.get("/courses")
async def list_courses(specialization: str | None = Query(default=None)):
    return {"success": True, "courses": _trainer.course_manager.list_courses(specialization)}


@router.post("/assess")
async def assess_bot(request: AssessBotRequest):
    try:
        assessment = await _trainer.assess_bot_capabilities(request.bot_key)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"success": True, "assessment": assessment}


@router.post("/plans")
async def create_plan(request: CreatePlanRequest):
    try:
        plan = await _trainer.create_training_plan(request.bot_key, request.goal)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"success": True, "plan": plan}


@router.post("/sessions/start")
async def start_session(request: StartSessionRequest):
    try:
        result = await _trainer.start_training_session(request.plan_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"success": True, **result}


@router.get("/sessions/{session_id}")
async def get_session(session_id: str):
    session = _trainer.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"success": True, "session": session}


@router.get("/reports")
async def list_reports(bot_key: str | None = Query(default=None)):
    reports = _trainer.list_reports()
    if bot_key:
        reports = [report for report in reports if report.get("bot_key") == _trainer.bot_connector.normalize_bot_key(bot_key)]
    return {"success": True, "reports": reports}


@router.get("/reports/{session_id}")
async def get_report(session_id: str):
    report = _trainer.get_report(session_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return {"success": True, "report": report}


@router.get("/stats")
async def get_stats():
    return {"success": True, "stats": _trainer.get_stats()}
