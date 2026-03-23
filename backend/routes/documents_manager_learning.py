from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.ai.documents_manager import documents_manager_bot

router = APIRouter(prefix="/api/v1/documents-manager", tags=["Documents Manager Learning"])


class DocumentProcessRequest(BaseModel):
    document_id: Optional[str] = None
    document_type: Optional[str] = "general"
    file_name: Optional[str] = None


class FeedbackRequest(BaseModel):
    session_id: str
    rating: int
    feedback: Optional[str] = None
    user_id: Optional[str] = None


@router.post("/process-document")
async def process_document(request: DocumentProcessRequest) -> Dict[str, Any]:
    return await documents_manager_bot.process_document(request.model_dump())


@router.post("/feedback")
async def submit_feedback(request: FeedbackRequest) -> Dict[str, Any]:
    if request.rating < 1 or request.rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    return documents_manager_bot.submit_feedback(
        session_id=request.session_id,
        rating=request.rating,
        comment=request.feedback,
        user_id=request.user_id,
        feedback_type="documents_manager",
    )


@router.get("/stats")
async def get_stats() -> Dict[str, Any]:
    return documents_manager_bot.get_stats()

