from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel, Field

from backend.bots.ws_manager import broadcast_event
from backend.services.quo_api import get_quo_client
from backend.services.ai_calls_store import list_events, list_recent_calls, record_call, record_event
from backend.services.ai_calls_dispatch import dispatch_to_marketing_bot

router = APIRouter(tags=["AI Calls"])  # mounted with prefix in main.py


class OutboundCallRequest(BaseModel):
    from_number: str = Field(..., description="Originating phone number")
    to_number: str = Field(..., description="Destination phone number")
    user_id: Optional[str] = Field(None, description="Quo/OpenPhone user ID")
    purpose: str = Field("sales", description="Call purpose label")
    notes: Optional[str] = Field(None, description="Optional note for internal tracking")


class CallResponse(BaseModel):
    call_id: str
    status: str
    message: str
    timestamp: datetime
    details: Optional[Dict[str, Any]] = None


class SMSRequest(BaseModel):
    from_number: str
    to_numbers: List[str]
    content: str
    user_id: Optional[str] = None
    related_call_id: Optional[str] = None


@router.post("/outbound", response_model=CallResponse)
async def create_outbound_call(request: OutboundCallRequest, background_tasks: BackgroundTasks) -> CallResponse:
    client = get_quo_client()
    result = await client.make_outbound_call(
        from_number=request.from_number,
        to_number=request.to_number,
        user_id=request.user_id,
        call_flow={"type": "ai_assisted"},
    )
    if "error" in result:
        raise HTTPException(status_code=502, detail=f"Quo API error: {result['error']}")

    call_id = str(result.get("id") or result.get("callId") or "unknown")
    await record_call(
        call_id=call_id,
        direction="outbound",
        from_number=request.from_number,
        to_number=request.to_number,
        status="initiated",
        purpose=request.purpose,
        provider="quo",
        last_event="initiated",
    )
    await record_event(call_id=call_id, event_type="initiated", payload={"request": request.model_dump(), "provider": result})

    dispatched_bot = await dispatch_to_marketing_bot(
        task_type="call_outbound_initiated",
        params={"call_id": call_id, "from": request.from_number, "to": request.to_number, "purpose": request.purpose},
    )
    if dispatched_bot:
        await record_call(
            call_id=call_id,
            direction="outbound",
            from_number=request.from_number,
            to_number=request.to_number,
            status="initiated",
            purpose=request.purpose,
            provider="quo",
            bot_name=dispatched_bot,
            last_event="initiated",
        )
    await broadcast_event(
        channel="ai.calls.outbound",
        payload={
            "event": "outbound_initiated",
            "call_id": call_id,
            "from": request.from_number,
            "to": request.to_number,
            "purpose": request.purpose,
            "ts": datetime.utcnow().isoformat() + "Z",
        },
    )

    # Optionally monitor the call in the background
    background_tasks.add_task(_monitor_call_once, call_id)

    return CallResponse(
        call_id=call_id,
        status="initiated",
        message="Outbound call initiated",
        timestamp=datetime.utcnow(),
        details={"provider": result},
    )


@router.post("/send-sms", response_model=Dict[str, Any])
async def send_followup_sms(request: SMSRequest) -> Dict[str, Any]:
    client = get_quo_client()
    result = await client.send_sms(
        from_number=request.from_number,
        to_numbers=request.to_numbers,
        content=request.content,
        user_id=request.user_id,
    )
    if "error" in result:
        raise HTTPException(status_code=502, detail=f"Quo API error: {result['error']}")

    await broadcast_event(
        channel="ai.calls.sms",
        payload={
            "event": "sms_sent",
            "message_id": result.get("id"),
            "to": request.to_numbers,
            "related_call_id": request.related_call_id,
            "ts": datetime.utcnow().isoformat() + "Z",
        },
    )
    return {"status": "ok", "message_id": result.get("id")}


@router.get("/recent", response_model=List[Dict[str, Any]])
async def recent_calls(limit: int = 50) -> List[Dict[str, Any]]:
    return await list_recent_calls(limit=limit)


@router.get("/{call_id}/events", response_model=List[Dict[str, Any]])
async def call_events(call_id: str, limit: int = 50) -> List[Dict[str, Any]]:
    return await list_events(call_id=call_id, limit=limit)


async def _monitor_call_once(call_id: str) -> None:
    client = get_quo_client()
    details = await client.get_call_by_id(call_id)
    await record_event(call_id=call_id, event_type="status_check", payload=details if isinstance(details, dict) else {"raw": details})
    await broadcast_event(
        channel="ai.calls.status",
        payload={
            "event": "status_check",
            "call_id": call_id,
            "details": details,
            "ts": datetime.utcnow().isoformat() + "Z",
        },
    )
