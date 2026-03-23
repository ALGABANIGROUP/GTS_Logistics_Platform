from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from backend.services.ivr_bot import ivr_bot
from backend.services.quo_service_enhanced import quo_service

router = APIRouter(prefix="/api/v1/calls", tags=["AI Calls Enhanced"])
logger = logging.getLogger(__name__)


class SmartCallRequest(BaseModel):
    to: str = Field(..., description="Destination phone number")
    bot_name: str = Field(..., description="Bot initiating the call")
    purpose: str = Field(..., description="Purpose label")
    from_number: Optional[str] = Field(None, description="Optional origin number override")
    user_id: Optional[str] = Field(None, description="Provider user ID")
    context: Dict[str, Any] = Field(default_factory=dict)


class IVRChoiceRequest(BaseModel):
    choice: str = Field(..., description="DTMF/menu selection")
    from_number: Optional[str] = None


@router.post("/smart")
async def create_smart_call(request: SmartCallRequest) -> Dict[str, Any]:
    result = await quo_service.make_smart_call(
        to=request.to,
        bot_name=request.bot_name,
        purpose=request.purpose,
        context=request.context,
        from_number=request.from_number,
        user_id=request.user_id,
    )
    if not result.get("success"):
        raise HTTPException(status_code=502, detail=result)
    return result


@router.get("/history")
async def get_call_history(bot_name: Optional[str] = None, days: int = 7) -> Dict[str, Any]:
    return {"items": await quo_service.get_call_history(bot_name=bot_name, days=days)}


@router.get("/{call_id}/transcript")
async def get_call_transcript(call_id: str) -> Dict[str, Any]:
    transcript = await quo_service.get_call_transcript(call_id)
    if transcript is None:
        raise HTTPException(status_code=404, detail="Transcript not found")
    return {"call_id": call_id, "transcript": transcript}


@router.post("/webhooks/{call_id}")
async def call_webhook(call_id: str, request: Request) -> Dict[str, Any]:
    try:
        payload = await request.json()
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Invalid JSON payload: {exc}") from exc
    logger.info("Enhanced call webhook received call_id=%s event=%s", call_id, payload.get("event") or payload.get("type"))
    return await quo_service.handle_call_webhook(call_id, payload)


@router.post("/incoming")
async def incoming_call(request: Request) -> Dict[str, Any]:
    try:
        payload = await request.json()
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Invalid JSON payload: {exc}") from exc

    call_id = str(payload.get("id") or payload.get("call_id") or payload.get("callId") or "")
    from_number = str(payload.get("from") or payload.get("caller") or "")
    to_number = str(payload.get("to") or payload.get("callee") or "")
    if not call_id:
        raise HTTPException(status_code=400, detail="Missing call ID")
    return await ivr_bot.handle_incoming_call(call_id, from_number, to_number)


@router.post("/incoming/{call_id}/choice")
async def incoming_call_choice(call_id: str, request: IVRChoiceRequest) -> Dict[str, Any]:
    return await ivr_bot.route_choice(call_id, request.choice, request.from_number)
