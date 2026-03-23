from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict
from backend.database.session import wrap_session_factory
from backend.database.config import get_db_async
from backend.schemas.webhook import TrackingEventData
from backend.services.tracking_service import TrackingService
from backend.services.webhook_service import WebhookService

logger = logging.getLogger(__name__)


async def process_tracking_webhook(webhook_id: str, payload: Dict[str, Any], client_info: Dict[str, str]) -> None:
    max_retries = 3
    delay_seconds = 2

    for attempt in range(max_retries):
        try:
            async with wrap_session_factory(get_db_async) as session:
                tracking_service = TrackingService(session)
                webhook_service = WebhookService(session)
                event_data = TrackingEventData(**payload.get("event", {}))

                await tracking_service.process_tracking_event(event_data)
                await webhook_service.mark_webhook_processed(webhook_id, status_code=202)
            return
        except Exception as exc:  # noqa: BLE001
            logger.error("Webhook %s attempt %s failed: %s", webhook_id, attempt + 1, exc)
            if attempt == max_retries - 1:
                async with wrap_session_factory(get_db_async) as session:
                    await WebhookService(session).mark_webhook_failed(webhook_id, error=str(exc))
                await send_to_dlq(webhook_id, payload, str(exc))
                raise
            await asyncio.sleep(delay_seconds * (2**attempt))


async def send_to_dlq(webhook_id: str, payload: Dict[str, Any], error: str) -> None:
    """Placeholder DLQ hook (wired to log for now)."""
    logger.error("Webhook %s sent to DLQ: %s", webhook_id, error)
    # Integration point: push to Redis/RabbitMQ/SQS as needed.

