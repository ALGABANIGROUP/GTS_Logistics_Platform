from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.ai.mapleload_canada import mapleload_canada_bot

router = APIRouter(prefix="/api/v1/mapleload-canada", tags=["MapleLoad Canada Learning"])


class MarketAnalysisRequest(BaseModel):
    region: Optional[str] = "Ontario"
    sector: Optional[str] = "freight"


class CarrierDiscoveryRequest(BaseModel):
    province: str = "ON"
    type: Optional[str] = "all"


class FeedbackRequest(BaseModel):
    session_id: str
    rating: int
    feedback: Optional[str] = None
    user_id: Optional[str] = None


@router.post("/analyze-market")
async def analyze_canadian_market(request: MarketAnalysisRequest) -> Dict[str, Any]:
    return await mapleload_canada_bot.analyze_canadian_market(request.model_dump())


@router.post("/discover-carriers")
async def discover_carriers(request: CarrierDiscoveryRequest) -> Dict[str, Any]:
    return await mapleload_canada_bot.discover_carriers(request.province)


@router.post("/feedback")
async def submit_feedback(request: FeedbackRequest) -> Dict[str, Any]:
    if request.rating < 1 or request.rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    return mapleload_canada_bot.submit_feedback(
        session_id=request.session_id,
        rating=request.rating,
        comment=request.feedback,
        user_id=request.user_id,
        feedback_type="mapleload_canada",
    )


@router.get("/stats")
async def get_stats() -> Dict[str, Any]:
    return mapleload_canada_bot.get_stats()

