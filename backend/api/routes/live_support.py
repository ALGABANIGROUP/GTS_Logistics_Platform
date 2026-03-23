from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
import logging

from backend.services.live_support_service import LiveSupportService
from backend.security.auth import get_current_user

router = APIRouter(prefix="/api/v1/support", tags=["Live Support"])
support_service = LiveSupportService()

class MessageRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class MessageResponse(BaseModel):
    success: bool
    response: str
    intent: str
    session_id: str
    timestamp: str

@router.post("/chat", response_model=MessageResponse)
async def chat(
    request: MessageRequest,
    current_user = Depends(get_current_user)
):
    """
    Send message to live support and get intelligent response
    """
    result = await support_service.process_message(
        user_id=str(current_user.get("id")),
        message=request.message,
        session_id=request.session_id
    )

    return MessageResponse(**result)

@router.get("/health")
async def support_health():
    """
    Check live support service health
    """
    return {
        "status": "online",
        "service": "Live Support Assistant",
        "version": "2.0",
        "features": ["system_health", "error_analysis", "security", "weather", "finance"]
    }

@router.get("/conversation/{session_id}")
async def get_conversation(
    session_id: str,
    current_user = Depends(get_current_user)
):
    """
    Get conversation history
    """
    history = support_service.get_conversation_history(session_id)
    return {
        "session_id": session_id,
        "history": history,
        "total": len(history)
    }