from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.ai.partner_manager import partner_manager_bot

router = APIRouter(prefix="/api/v1/partner-manager", tags=["Partner Manager Learning"])


class PartnerEvaluationRequest(BaseModel):
    name: Optional[str] = None
    industry: Optional[str] = "logistics"
    size: Optional[str] = "medium"


class CollaborationRequest(BaseModel):
    project: Optional[str] = "joint_venture"
    partner_id: Optional[str] = None


class FeedbackRequest(BaseModel):
    session_id: str
    rating: int
    feedback: Optional[str] = None
    user_id: Optional[str] = None


@router.post("/evaluate")
async def evaluate_partner(request: PartnerEvaluationRequest) -> Dict[str, Any]:
    return await partner_manager_bot.evaluate_partner(request.model_dump())


@router.post("/manage-collaboration")
async def manage_collaboration(request: CollaborationRequest) -> Dict[str, Any]:
    return await partner_manager_bot.manage_collaboration(request.model_dump())


@router.post("/feedback")
async def submit_feedback(request: FeedbackRequest) -> Dict[str, Any]:
    if request.rating < 1 or request.rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    return partner_manager_bot.submit_feedback(
        session_id=request.session_id,
        rating=request.rating,
        comment=request.feedback,
        user_id=request.user_id,
        feedback_type="partner_manager",
    )


@router.get("/stats")
async def get_stats() -> Dict[str, Any]:
    return partner_manager_bot.get_stats()

