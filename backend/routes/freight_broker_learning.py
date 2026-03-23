from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.ai.freight_broker import freight_broker_bot

router = APIRouter(prefix="/api/v1/freight-broker", tags=["Freight Broker Learning"])


class ShipmentMatchRequest(BaseModel):
    origin: str
    destination: str
    weight: float
    shipment_id: Optional[str] = None


class FeedbackRequest(BaseModel):
    session_id: str
    rating: int
    feedback: Optional[str] = None
    user_id: Optional[str] = None


@router.post("/match")
async def match_shipment(request: ShipmentMatchRequest) -> Dict[str, Any]:
    return await freight_broker_bot.match_shipment(request.model_dump())


@router.post("/feedback")
async def submit_feedback(request: FeedbackRequest) -> Dict[str, Any]:
    if request.rating < 1 or request.rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    return freight_broker_bot.submit_feedback(
        session_id=request.session_id,
        rating=request.rating,
        comment=request.feedback,
        user_id=request.user_id,
        feedback_type="freight_broker",
    )


@router.get("/stats")
async def get_stats() -> Dict[str, Any]:
    return freight_broker_bot.get_stats()

