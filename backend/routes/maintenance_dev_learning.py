from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.ai.maintenance_dev import maintenance_dev_bot

router = APIRouter(prefix="/api/v1/maintenance-dev", tags=["Maintenance Dev Learning"])


class HealthCheckRequest(BaseModel):
    component: str = "all"


class UpgradesRequest(BaseModel):
    priority: str = "medium"
    metrics: Optional[Dict[str, Any]] = None


class FeedbackRequest(BaseModel):
    session_id: str
    rating: int
    feedback: Optional[str] = None
    user_id: Optional[str] = None


@router.post("/check-health")
async def check_system_health(request: HealthCheckRequest) -> Dict[str, Any]:
    return await maintenance_dev_bot.check_system_health(request.model_dump())


@router.post("/suggest-upgrades")
async def suggest_upgrades(request: UpgradesRequest) -> Dict[str, Any]:
    return await maintenance_dev_bot.suggest_upgrades(request.model_dump())


@router.post("/feedback")
async def submit_feedback(request: FeedbackRequest) -> Dict[str, Any]:
    if request.rating < 1 or request.rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    return maintenance_dev_bot.submit_feedback(
        session_id=request.session_id,
        rating=request.rating,
        comment=request.feedback,
        user_id=request.user_id,
        feedback_type="maintenance_dev",
    )


@router.get("/stats")
async def get_stats() -> Dict[str, Any]:
    return maintenance_dev_bot.get_stats()

