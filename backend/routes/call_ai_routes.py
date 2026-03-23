from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from backend.ai.call_bot import call_bot
from backend.ai.call_ner import info_extractor
from backend.ai.call_sentiment import sentiment_analyzer
from backend.services.quo_service_enhanced import quo_service

router = APIRouter(prefix="/api/v1/call-ai", tags=["Call AI"])


class CallAnalysisRequest(BaseModel):
    transcript: str
    speaker_labels: Optional[list[str]] = None


class CallExtractionRequest(BaseModel):
    transcript: str


class CallBotRequest(BaseModel):
    call_id: str
    from_number: str
    to_number: str


@router.post("/analyze-sentiment")
async def analyze_call_sentiment(request: CallAnalysisRequest):
    return {"success": True, "analysis": await sentiment_analyzer.analyze_transcript(request.transcript, request.speaker_labels)}


@router.post("/extract-info")
async def extract_call_info(request: CallExtractionRequest):
    return {"success": True, "extraction": await info_extractor.extract_info(request.transcript)}


@router.post("/bot/handle")
async def handle_call_with_bot(request: CallBotRequest):
    await call_bot.handle_call(request.call_id, request.from_number, request.to_number)
    return {"success": True, "message": "Call being processed by bot"}


@router.get("/bot/status/{call_id}")
async def get_call_bot_status(call_id: str):
    call_data = call_bot.active_calls.get(call_id)
    if not call_data:
        raise HTTPException(status_code=404, detail="Call not found")
    return {"success": True, "call": call_data}


@router.post("/transfer")
async def transfer_call(call_id: str, target: str = Query(..., description="bot_name or human department")):
    bot_targets = {"freight_broker", "finance_bot", "customer_service", "safety_manager", "security_manager", "operations_manager"}
    if target in bot_targets:
        await call_bot._transfer_to_bot(call_id, target)
        message = f"Transferred to bot {target}"
    else:
        await call_bot._transfer_to_human(call_id, target)
        message = f"Transferred to human in {target}"
    return {"success": True, "message": message}


@router.get("/history")
async def get_call_history(limit: int = 10):
    history = await quo_service.get_call_history(days=7)
    return {"success": True, "history": history[:limit]}


@router.get("/transcript/{call_id}")
async def get_call_transcript(call_id: str):
    transcript = await quo_service.get_call_transcript(call_id)
    if not transcript:
        raise HTTPException(status_code=404, detail="Transcript not found")
    return {"success": True, "call_id": call_id, "transcript": transcript}
