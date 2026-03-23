from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.ai.security_manager import security_manager_bot

router = APIRouter(prefix="/api/v1/security-manager", tags=["Security Manager Learning"])


class ThreatScanRequest(BaseModel):
    target: Optional[str] = "system"
    depth: Optional[str] = "standard"


class AccessMonitorRequest(BaseModel):
    user: Optional[str] = None
    resource: Optional[str] = None
    action: Optional[str] = "view"


class FeedbackRequest(BaseModel):
    session_id: str
    rating: int
    feedback: Optional[str] = None
    user_id: Optional[str] = None


@router.post("/scan-threats")
async def scan_for_threats(request: ThreatScanRequest) -> Dict[str, Any]:
    return await security_manager_bot.scan_for_threats(request.model_dump())


@router.post("/monitor-access")
async def monitor_access(request: AccessMonitorRequest) -> Dict[str, Any]:
    return await security_manager_bot.monitor_access(request.model_dump())


@router.post("/feedback")
async def submit_feedback(request: FeedbackRequest) -> Dict[str, Any]:
    if request.rating < 1 or request.rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    return security_manager_bot.submit_feedback(
        session_id=request.session_id,
        rating=request.rating,
        comment=request.feedback,
        user_id=request.user_id,
        feedback_type="security_manager",
    )


@router.get("/stats")
async def get_stats() -> Dict[str, Any]:
    return security_manager_bot.get_stats()

