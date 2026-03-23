from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.ai.information_coordinator import information_coordinator_bot

router = APIRouter(prefix="/api/v1/information-coordinator", tags=["Information Coordinator Learning"])


class RouteInfoRequest(BaseModel):
    source: Optional[str] = None
    destination: Optional[str] = None
    data_type: Optional[str] = "general"


class ConnectDataRequest(BaseModel):
    source: str
    target: str
    connection_type: Optional[str] = "api"


class FeedbackRequest(BaseModel):
    session_id: str
    rating: int
    feedback: Optional[str] = None
    user_id: Optional[str] = None


@router.post("/route")
async def route_information(request: RouteInfoRequest) -> Dict[str, Any]:
    return await information_coordinator_bot.route_information(request.model_dump())


@router.post("/connect")
async def connect_data(request: ConnectDataRequest) -> Dict[str, Any]:
    return await information_coordinator_bot.connect_data(
        source=request.source,
        target=request.target,
    )


@router.post("/feedback")
async def submit_feedback(request: FeedbackRequest) -> Dict[str, Any]:
    if request.rating < 1 or request.rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    return information_coordinator_bot.submit_feedback(
        session_id=request.session_id,
        rating=request.rating,
        comment=request.feedback,
        user_id=request.user_id,
        feedback_type="information_coordinator",
    )


@router.get("/stats")
async def get_stats() -> Dict[str, Any]:
    return information_coordinator_bot.get_stats()

