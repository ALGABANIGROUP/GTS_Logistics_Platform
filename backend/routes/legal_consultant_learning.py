from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.ai.legal_consultant import legal_consultant_bot

router = APIRouter(prefix="/api/v1/legal-consultant", tags=["Legal Consultant Learning"])


class ContractReviewRequest(BaseModel):
    contract_id: Optional[str] = None
    contract_type: Optional[str] = "service"
    content: Optional[str] = None


class ComplianceCheckRequest(BaseModel):
    document_id: Optional[str] = None
    doc_type: Optional[str] = "general"
    content: Optional[str] = None


class FeedbackRequest(BaseModel):
    session_id: str
    rating: int
    feedback: Optional[str] = None
    user_id: Optional[str] = None


@router.post("/review-contract")
async def review_contract(request: ContractReviewRequest) -> Dict[str, Any]:
    return await legal_consultant_bot.review_contract(request.model_dump())


@router.post("/check-compliance")
async def check_compliance(request: ComplianceCheckRequest) -> Dict[str, Any]:
    return await legal_consultant_bot.check_compliance(request.model_dump())


@router.post("/feedback")
async def submit_feedback(request: FeedbackRequest) -> Dict[str, Any]:
    if request.rating < 1 or request.rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    return legal_consultant_bot.submit_feedback(
        session_id=request.session_id,
        rating=request.rating,
        comment=request.feedback,
        user_id=request.user_id,
        feedback_type="legal_consultant",
    )


@router.get("/stats")
async def get_stats() -> Dict[str, Any]:
    return legal_consultant_bot.get_stats()

