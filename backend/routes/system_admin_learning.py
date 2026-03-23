from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.ai.system_admin import system_admin_bot

router = APIRouter(prefix="/api/v1/system-admin", tags=["System Admin Learning"])


class UserManagementRequest(BaseModel):
    action: str = "add"
    user_id: Optional[str] = None
    role: Optional[str] = "viewer"


class SystemPerformanceRequest(BaseModel):
    component: Optional[str] = "all"


class FeedbackRequest(BaseModel):
    session_id: str
    rating: int
    feedback: Optional[str] = None
    user_id: Optional[str] = None


@router.post("/manage-users")
async def manage_users(request: UserManagementRequest) -> Dict[str, Any]:
    return await system_admin_bot.manage_users(request.model_dump())


@router.post("/check-performance")
async def check_performance(request: SystemPerformanceRequest) -> Dict[str, Any]:
    return await system_admin_bot.check_system_performance(request.model_dump())


@router.post("/feedback")
async def submit_feedback(request: FeedbackRequest) -> Dict[str, Any]:
    if request.rating < 1 or request.rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    return system_admin_bot.submit_feedback(
        session_id=request.session_id,
        rating=request.rating,
        comment=request.feedback,
        user_id=request.user_id,
        feedback_type="system_admin",
    )


@router.get("/stats")
async def get_stats() -> Dict[str, Any]:
    return system_admin_bot.get_stats()

