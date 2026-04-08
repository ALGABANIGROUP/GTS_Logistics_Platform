from __future__ import annotations

import os
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.config import get_db
from backend.security.webhook_signatures import verify_hmac_sha256_signature
from backend.services.truckerpath_service import TruckerPathService

# Optional: WebSocket broadcast (best-effort)
async def _noop_broadcast(*args, **kwargs) -> None:
    return None

broadcast_event = _noop_broadcast
try:
    from backend.routes.ws_routes import broadcast_event as _broadcast_event  # type: ignore
    broadcast_event = _broadcast_event
except Exception:
    try:
        from backend.routes.ws_routes import broadcast_event as _broadcast_event  # type: ignore
        broadcast_event = _broadcast_event
    except Exception:
        pass

router = APIRouter(prefix="/truckerpath/webhook", tags=["TruckerPath Webhook"])

def _verify_signature(secret: Optional[str], raw_body: bytes, signature: Optional[str]) -> bool:
    return verify_hmac_sha256_signature(
        secret=secret,
        payload=raw_body,
        signature_header=signature,
        app_env=os.getenv("ENVIRONMENT"),
        allow_missing_secret=True,
    )

@router.post("/events")
async def receive_event(
    request: Request,
    x_truckerpath_signature: Optional[str] = Header(default=None, convert_underscores=False),
    db: AsyncSession = Depends(get_db),
):
    raw = await request.body()
    secret = (
        request.app.state.__dict__.get("TRUCKERPATH_WEBHOOK_SECRET")
        or os.getenv("TRUCKERPATH_WEBHOOK_SECRET")
        or None
    )
    if not _verify_signature(secret, raw, x_truckerpath_signature):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")

    try:
        payload: Dict[str, Any] = await request.json()
    except Exception:
        payload = {"raw": raw.decode("utf-8", errors="ignore")}

    # Broadcast for live UI
    try:
        await broadcast_event(channel="events.truckerpath.webhook", payload=payload)
    except Exception:
        pass

    handled = await TruckerPathService.handle_webhook(db, payload)

    return {"ok": True, "received": True, "handled": handled}
