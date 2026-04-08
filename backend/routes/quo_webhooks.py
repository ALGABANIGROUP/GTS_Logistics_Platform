from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse

from backend.bots.ws_manager import broadcast_event
from backend.security.webhook_signatures import build_timestamped_message, verify_hmac_sha256_signature
from backend.services.ai_calls_store import record_call, record_event
from backend.services.ai_calls_dispatch import dispatch_to_marketing_bot

router = APIRouter(tags=["Quo Webhooks"])  # mounted with prefix from backend.routes.registry


def _get_secret() -> str:
    return (os.getenv("QUO_WEBHOOK_SECRET") or "").strip()


def _verify_signature(*, body: bytes, signature: Optional[str], timestamp: Optional[str]) -> bool:
    secret = _get_secret()
    if not timestamp:
        return False
    return verify_hmac_sha256_signature(
        secret=secret,
        payload=build_timestamped_message(timestamp, body),
        signature_header=signature,
        app_env=os.getenv("ENVIRONMENT"),
        preferred_signature_keys=("v1",),
    )


async def _broadcast(event_type: str, data: Dict[str, Any]) -> None:
    await broadcast_event(channel=f"quo.{event_type}", payload={
        "event": event_type,
        "data": data,
        "ts": datetime.utcnow().isoformat() + "Z",
    })


@router.post("/calls")
async def webhook_calls(request: Request):
    body = await request.body()
    sig = request.headers.get("X-Quo-Signature") or request.headers.get("X-Signature")
    ts = request.headers.get("X-Quo-Timestamp") or request.headers.get("X-Timestamp")
    if not _verify_signature(body=body, signature=sig, timestamp=ts):
        raise HTTPException(status_code=401, detail="Invalid signature")

    try:
        payload = json.loads(body.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    event_type = str(payload.get("event") or payload.get("type") or "call.event")
    data = payload.get("data") or payload

    payload = data if isinstance(data, dict) else {"raw": data}
    await _broadcast(event_type, payload)

    call_id = str(payload.get("id") or payload.get("call_id") or payload.get("callId") or "")
    from_number = payload.get("from") or payload.get("caller")
    to_number = payload.get("to") or payload.get("callee")
    if call_id:
        await record_call(
            call_id=call_id,
            direction="inbound",
            from_number=from_number,
            to_number=to_number,
            status=event_type,
            purpose=str(payload.get("purpose") or "call"),
            customer_name=str(payload.get("customer") or payload.get("contact", {}).get("name", "")) or None,
            last_event=event_type,
        )
        await record_event(call_id=call_id, event_type=event_type, payload=payload)
        await dispatch_to_marketing_bot(
            task_type="call_webhook",
            params={"event": event_type, "call_id": call_id, "data": payload},
        )

    return JSONResponse(content={"status": "ok"})


@router.post("/messages")
async def webhook_messages(request: Request):
    body = await request.body()
    sig = request.headers.get("X-Quo-Signature") or request.headers.get("X-Signature")
    ts = request.headers.get("X-Quo-Timestamp") or request.headers.get("X-Timestamp")
    if not _verify_signature(body=body, signature=sig, timestamp=ts):
        raise HTTPException(status_code=401, detail="Invalid signature")

    try:
        payload = json.loads(body.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    event_type = str(payload.get("event") or payload.get("type") or "message.event")
    data = payload.get("data") or payload
    payload = data if isinstance(data, dict) else {"raw": data}
    await _broadcast(event_type, payload)
    call_id = str(payload.get("id") or payload.get("call_id") or payload.get("callId") or "")
    if call_id:
        await record_event(call_id=call_id, event_type=event_type, payload=payload)
    return {"status": "ok"}


@router.post("/voicemails")
async def webhook_voicemails(request: Request):
    body = await request.body()
    sig = request.headers.get("X-Quo-Signature") or request.headers.get("X-Signature")
    ts = request.headers.get("X-Quo-Timestamp") or request.headers.get("X-Timestamp")
    if not _verify_signature(body=body, signature=sig, timestamp=ts):
        raise HTTPException(status_code=401, detail="Invalid signature")

    try:
        payload = json.loads(body.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    event_type = str(payload.get("event") or payload.get("type") or "voicemail.event")
    data = payload.get("data") or payload
    payload = data if isinstance(data, dict) else {"raw": data}
    await _broadcast(event_type, payload)
    call_id = str(payload.get("id") or payload.get("call_id") or payload.get("callId") or "")
    if call_id:
        await record_event(call_id=call_id, event_type=event_type, payload=payload)
    return {"status": "ok"}


@router.get("/verify")
async def verify(challenge: Optional[str] = None, mode: Optional[str] = None, token: Optional[str] = None):
    # Simple verification echo endpoint
    if mode == "subscribe" and challenge:
        return JSONResponse(content={"challenge": challenge})
    return {"status": "active"}
