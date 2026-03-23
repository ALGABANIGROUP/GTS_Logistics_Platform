from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.ai.finance_bot import finance_bot

router = APIRouter(prefix="/api/v1/finance-bot", tags=["Finance Bot Learning"])


class InvoiceProcessRequest(BaseModel):
    invoice_number: Optional[str] = None
    amount: float
    currency: Optional[str] = "CAD"


class FeedbackRequest(BaseModel):
    session_id: str
    rating: int
    feedback: Optional[str] = None
    user_id: Optional[str] = None


@router.post("/process-invoice")
async def process_invoice(request: InvoiceProcessRequest) -> Dict[str, Any]:
    return await finance_bot.process_invoice(request.model_dump())


@router.post("/feedback")
async def submit_feedback(request: FeedbackRequest) -> Dict[str, Any]:
    if request.rating < 1 or request.rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    return finance_bot.submit_feedback(
        session_id=request.session_id,
        rating=request.rating,
        comment=request.feedback,
        user_id=request.user_id,
        feedback_type="finance_bot",
    )


@router.get("/stats")
async def get_stats() -> Dict[str, Any]:
    return finance_bot.get_stats()

