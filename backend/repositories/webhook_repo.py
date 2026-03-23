from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from backend.models.tracking_webhook import WebhookLog


class WebhookRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def is_duplicate_idempotency_key(self, key: str) -> bool:
        result = await self.session.execute(
            select(WebhookLog.id).where(WebhookLog.idempotency_key == key)
        )
        return result.scalar_one_or_none() is not None

    async def log_webhook(
        self,
        *,
        client_id: str,
        endpoint: str,
        payload: Dict[str, Any],
        headers: Dict[str, Any],
        idempotency_key: str,
        signature: Optional[str] = None,
    ) -> WebhookLog:
        entry = WebhookLog(
            client_id=client_id,
            endpoint=endpoint,
            payload=payload,
            headers=headers,
            idempotency_key=idempotency_key,
            signature=signature,
        )
        self.session.add(entry)
        await self.session.flush()
        return entry

    async def mark_processed(self, webhook_id: str, status_code: int = 202) -> None:
        await self.session.execute(
            update(WebhookLog)
            .where(WebhookLog.id == webhook_id)
            .values(processed=True, processed_at=datetime.utcnow(), response_status=status_code)
        )

    async def mark_failed(self, webhook_id: str, error: str, status_code: int = 500) -> None:
        await self.session.execute(
            update(WebhookLog)
            .where(WebhookLog.id == webhook_id)
            .values(processed=False, processed_at=datetime.utcnow(), error=error[:2000], response_status=status_code)
        )

