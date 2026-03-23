from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.ai.sales_team import sales_team_bot

router = APIRouter(prefix="/api/v1/sales-team", tags=["Sales Team Learning"])


class LeadQualifyRequest(BaseModel):
    lead_id: Optional[str] = None
    score: Optional[int] = 75
    source: Optional[str] = "website"


class SalesAnalysisRequest(BaseModel):
    period: Optional[str] = "monthly"
    amount: Optional[float] = 0


class FeedbackRequest(BaseModel):
    session_id: str
    rating: int
    feedback: Optional[str] = None
    user_id: Optional[str] = None


@router.post("/qualify-lead")
async def qualify_lead(request: LeadQualifyRequest) -> Dict[str, Any]:
    return await sales_team_bot.qualify_lead(request.model_dump())


@router.post("/analyze")
async def analyze_sales(request: SalesAnalysisRequest) -> Dict[str, Any]:
    return await sales_team_bot.analyze_sales_performance(request.model_dump())


@router.post("/feedback")
async def submit_feedback(request: FeedbackRequest) -> Dict[str, Any]:
    if request.rating < 1 or request.rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    return sales_team_bot.submit_feedback(
        session_id=request.session_id,
        rating=request.rating,
        comment=request.feedback,
        user_id=request.user_id,
        feedback_type="sales_team",
    )


@router.get("/stats")
async def get_stats() -> Dict[str, Any]:
    return sales_team_bot.get_stats()

