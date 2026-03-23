from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.ai.operations_manager import operations_manager_bot

router = APIRouter(prefix="/api/v1/operations-manager", tags=["Operations Manager Learning"])


class TaskAssignRequest(BaseModel):
    task_type: str
    priority: Optional[str] = "normal"
    preferred_resource: Optional[str] = None


class FeedbackRequest(BaseModel):
    session_id: str
    rating: int
    feedback: Optional[str] = None
    user_id: Optional[str] = None


@router.post("/assign-task")
async def assign_task(request: TaskAssignRequest) -> Dict[str, Any]:
    return await operations_manager_bot.assign_task(request.model_dump())


@router.post("/feedback")
async def submit_feedback(request: FeedbackRequest) -> Dict[str, Any]:
    if request.rating < 1 or request.rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    return operations_manager_bot.submit_feedback(
        session_id=request.session_id,
        rating=request.rating,
        comment=request.feedback,
        user_id=request.user_id,
        feedback_type="operations_manager",
    )


@router.get("/stats")
async def get_stats() -> Dict[str, Any]:
    return operations_manager_bot.get_stats()

