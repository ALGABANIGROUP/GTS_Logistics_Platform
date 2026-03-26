from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.ai.general_manager import GeneralManagerBot

router = APIRouter(prefix="/api/v1/general-manager", tags=["General Manager Learning"])
general_manager_bot = GeneralManagerBot()


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
    return await general_manager_bot.generate_strategic_report(request.period)


@router.post("/analyze-performance")
async def analyze_performance(request: PerformanceRequest) -> Dict[str, Any]:
    return await general_manager_bot._analyze_performance()


@router.post("/feedback")
async def submit_feedback(request: FeedbackRequest) -> Dict[str, Any]:
    if request.rating < 1 or request.rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    return {
        "success": True,
        "session_id": request.session_id,
        "rating": request.rating,
        "feedback": request.feedback,
        "user_id": request.user_id,
    }


@router.get("/stats")
async def get_stats() -> Dict[str, Any]:
    return {
        "bot": general_manager_bot.name,
        "display_name": general_manager_bot.display_name,
        "status": "active",
    }
