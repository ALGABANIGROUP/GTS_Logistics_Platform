from __future__ import annotations

from typing import Any, Dict

from sqlalchemy.ext.asyncio import AsyncSession

from backend.repositories.webhook_repo import WebhookRepository


class WebhookService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = WebhookRepository(session)

    async def is_duplicate_idempotency_key(self, key: str) -> bool:
        return await self.repo.is_duplicate_idempotency_key(key)

    async def log_webhook(
        self,
        *,
        client_id: str,
        endpoint: str,
        payload: Dict[str, Any],
        headers: Dict[str, Any],
        idempotency_key: str,
        signature: str | None,
    ) -> str:
        entry = await self.repo.log_webhook(
            client_id=client_id,
            endpoint=endpoint,
            payload=payload,
            headers=headers,
            idempotency_key=idempotency_key,
            signature=signature,
        )
        return str(entry.id)

    async def mark_webhook_processed(self, webhook_id: str, status_code: int = 202) -> None:
        await self.repo.mark_processed(webhook_id, status_code=status_code)
        await self.session.commit()

    async def mark_webhook_failed(self, webhook_id: str, error: str, status_code: int = 500) -> None:
        await self.repo.mark_failed(webhook_id, error=error, status_code=status_code)
        await self.session.commit()
