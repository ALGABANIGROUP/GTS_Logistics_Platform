from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.ai.general_manager import general_manager_bot

router = APIRouter(prefix="/api/v1/general-manager", tags=["General Manager Learning"])


class ReportRequest(BaseModel):
    period: str = "monthly"
    format: str = "summary"


class PerformanceRequest(BaseModel):
    score: Optional[int] = None
    metrics: Optional[Dict[str, Any]] = None


class FeedbackRequest(BaseModel):
    session_id: str
    rating: int
    feedback: Optional[str] = None
    user_id: Optional[str] = None


@router.post("/generate-report")
async def generate_report(request: ReportRequest) -> Dict[str, Any]:
    return await general_manager_bot.generate_report(request.model_dump())


@router.post("/analyze-performance")
async def analyze_performance(request: PerformanceRequest) -> Dict[str, Any]:
    return await general_manager_bot.analyze_performance(request.model_dump())


@router.post("/feedback")
async def submit_feedback(request: FeedbackRequest) -> Dict[str, Any]:
    if request.rating < 1 or request.rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    return general_manager_bot.submit_feedback(
        session_id=request.session_id,
        rating=request.rating,
        comment=request.feedback,
        user_id=request.user_id,
        feedback_type="general_manager",
    )


@router.get("/stats")
async def get_stats() -> Dict[str, Any]:
    return general_manager_bot.get_stats()

