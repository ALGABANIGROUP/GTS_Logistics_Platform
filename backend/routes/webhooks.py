from __future__ import annotations

import uuid
from datetime import datetime
from typing import Dict

from fastapi import APIRouter, BackgroundTasks, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_202_ACCEPTED
from backend.database.config import get_db_async
from backend.schemas.webhook import WebhookPayload, WebhookResponse
from backend.security.webhook_hmac import verify_webhook_hmac
from backend.services.webhook_service import WebhookService
from backend.services.webhook_tasks import process_tracking_webhook

router = APIRouter(prefix="/api/v1/webhooks", tags=["Webhooks"])


@router.post("/tracking", response_model=WebhookResponse, status_code=HTTP_202_ACCEPTED)
async def handle_tracking_webhook(
    request: Request,
    payload: WebhookPayload,
    background_tasks: BackgroundTasks,
    client_info: Dict[str, str] = Depends(verify_webhook_hmac),
    db: AsyncSession = Depends(get_db_async),
):
    webhook_service = WebhookService(db)

    if await webhook_service.is_duplicate_idempotency_key(payload.idempotency_key):
        return JSONResponse(
            status_code=HTTP_202_ACCEPTED,
            content={
                "status": "accepted",
                "message": "Duplicate webhook ignored (idempotency)",
                "webhook_id": str(uuid.uuid4()),
                "received_at": datetime.utcnow().isoformat(),
            },
        )

    webhook_entry_id = await webhook_service.log_webhook(
        client_id=client_info.get("client_id", ""),
        endpoint=request.url.path,
        payload=payload.model_dump(),
        headers=dict(request.headers),
        idempotency_key=payload.idempotency_key,
        signature=client_info.get("signature"),
    )

    background_tasks.add_task(
        process_tracking_webhook,
        webhook_id=webhook_entry_id,
        payload=payload.model_dump(),
        client_info=client_info,
    )

    return WebhookResponse(
        status="accepted",
        message="Webhook processing started",
        webhook_id=webhook_entry_id,
        received_at=datetime.utcnow(),
    )

