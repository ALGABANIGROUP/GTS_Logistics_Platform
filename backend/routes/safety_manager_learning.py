from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.ai.safety_manager import safety_manager_bot

router = APIRouter(prefix="/api/v1/safety-manager", tags=["Safety Manager Learning"])


class ComplianceCheckRequest(BaseModel):
    vehicle_id: Optional[str] = None
    inspection_date: Optional[str] = None


class IncidentReportRequest(BaseModel):
    incident_id: Optional[str] = None
    severity: str = "medium"
    description: Optional[str] = None


class FeedbackRequest(BaseModel):
    session_id: str
    rating: int
    feedback: Optional[str] = None
    user_id: Optional[str] = None


@router.post("/check-compliance")
async def check_compliance(request: ComplianceCheckRequest) -> Dict[str, Any]:
    return await safety_manager_bot.check_compliance(request.model_dump())


@router.post("/report-incident")
async def report_incident(request: IncidentReportRequest) -> Dict[str, Any]:
    return await safety_manager_bot.report_incident(request.model_dump())


@router.post("/feedback")
async def submit_feedback(request: FeedbackRequest) -> Dict[str, Any]:
    if request.rating < 1 or request.rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    return safety_manager_bot.submit_feedback(
        session_id=request.session_id,
        rating=request.rating,
        comment=request.feedback,
        user_id=request.user_id,
        feedback_type="safety_manager",
    )


@router.get("/stats")
async def get_stats() -> Dict[str, Any]:
    return safety_manager_bot.get_stats()

