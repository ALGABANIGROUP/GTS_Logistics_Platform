from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.ai.strategy_advisor import strategy_advisor_bot

router = APIRouter(prefix="/api/v1/strategy-advisor", tags=["Strategy Advisor Learning"])


class MarketAnalysisRequest(BaseModel):
    region: str = "global"
    sector: Optional[str] = None


class RecommendationsRequest(BaseModel):
    context: Optional[Dict[str, Any]] = None
    priority: str = "medium"


class FeedbackRequest(BaseModel):
    session_id: str
    rating: int
    feedback: Optional[str] = None
    user_id: Optional[str] = None


@router.post("/analyze-market")
async def analyze_market(request: MarketAnalysisRequest) -> Dict[str, Any]:
    return await strategy_advisor_bot.analyze_market(request.model_dump())


@router.post("/recommendations")
async def provide_recommendations(request: RecommendationsRequest) -> Dict[str, Any]:
    return await strategy_advisor_bot.provide_recommendations(request.model_dump())


@router.post("/feedback")
async def submit_feedback(request: FeedbackRequest) -> Dict[str, Any]:
    if request.rating < 1 or request.rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    return strategy_advisor_bot.submit_feedback(
        session_id=request.session_id,
        rating=request.rating,
        comment=request.feedback,
        user_id=request.user_id,
        feedback_type="strategy_advisor",
    )


@router.get("/stats")
async def get_stats() -> Dict[str, Any]:
    return strategy_advisor_bot.get_stats()

