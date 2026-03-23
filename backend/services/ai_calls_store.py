from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from sqlalchemy import text
from backend.database.session import get_async_session, wrap_session_factory

logger = logging.getLogger(__name__)

_schema_initialized = False


async def _ensure_schema(session) -> None:
    global _schema_initialized
    if _schema_initialized:
        return
    await session.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS ai_calls (
                call_id TEXT PRIMARY KEY,
                direction TEXT,
                from_number TEXT,
                to_number TEXT,
                status TEXT,
                bot_name TEXT,
                purpose TEXT,
                customer_name TEXT,
                provider TEXT,
                metadata JSONB,
                created_at TIMESTAMPTZ DEFAULT NOW(),
                updated_at TIMESTAMPTZ DEFAULT NOW(),
                last_event TEXT,
                last_event_ts TIMESTAMPTZ
            );
            """
        )
    )
    await session.execute(
        text(
            """
            CREATE INDEX IF NOT EXISTS idx_ai_calls_status ON ai_calls(status);
            """
        )
    )
    await session.execute(
        text(
            """
            CREATE INDEX IF NOT EXISTS idx_ai_calls_updated_at ON ai_calls(updated_at DESC);
            """
        )
    )
    await session.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS ai_call_events (
                id BIGSERIAL PRIMARY KEY,
                call_id TEXT REFERENCES ai_calls(call_id) ON DELETE CASCADE,
                event_type TEXT,
                payload JSONB,
                ts TIMESTAMPTZ DEFAULT NOW()
            );
            """
        )
    )
    await session.execute(
        text(
            """
            CREATE INDEX IF NOT EXISTS idx_ai_call_events_call_ts ON ai_call_events(call_id, ts DESC);
            """
        )
    )
    await session.commit()
    _schema_initialized = True


async def record_call(
    *,
    call_id: str,
    direction: str,
    from_number: Optional[str],
    to_number: Optional[str],
    status: str,
    bot_name: Optional[str] = None,
    purpose: Optional[str] = None,
    customer_name: Optional[str] = None,
    provider: str = "quo",
    metadata: Optional[Dict[str, Any]] = None,
    last_event: Optional[str] = None,
) -> None:
    async with wrap_session_factory(get_async_session) as session:
        await _ensure_schema(session)
        await session.execute(
            text(
                """
                INSERT INTO ai_calls (
                    call_id, direction, from_number, to_number, status, bot_name,
                    purpose, customer_name, provider, metadata, created_at,
                    updated_at, last_event, last_event_ts
                )
                VALUES (:call_id, :direction, :from_number, :to_number, :status, :bot_name,
                        :purpose, :customer_name, :provider, :metadata, NOW(), NOW(),
                        :last_event, NOW())
                ON CONFLICT (call_id) DO UPDATE SET
                    direction = EXCLUDED.direction,
                    from_number = COALESCE(EXCLUDED.from_number, ai_calls.from_number),
                    to_number = COALESCE(EXCLUDED.to_number, ai_calls.to_number),
                    status = EXCLUDED.status,
                    bot_name = COALESCE(EXCLUDED.bot_name, ai_calls.bot_name),
                    purpose = COALESCE(EXCLUDED.purpose, ai_calls.purpose),
                    customer_name = COALESCE(EXCLUDED.customer_name, ai_calls.customer_name),
                    provider = COALESCE(EXCLUDED.provider, ai_calls.provider),
                    metadata = COALESCE(EXCLUDED.metadata, ai_calls.metadata),
                    updated_at = NOW(),
                    last_event = COALESCE(EXCLUDED.last_event, ai_calls.last_event),
                    last_event_ts = COALESCE(EXCLUDED.last_event_ts, ai_calls.last_event_ts)
                ;
                """
            ),
            {
                "call_id": call_id,
                "direction": direction,
                "from_number": from_number,
                "to_number": to_number,
                "status": status,
                "bot_name": bot_name,
                "purpose": purpose,
                "customer_name": customer_name,
                "provider": provider,
                "metadata": metadata,
                "last_event": last_event or status,
            },
        )
        await session.commit()


async def record_event(
    *, call_id: str, event_type: str, payload: Optional[Dict[str, Any]] = None
) -> None:
    async with wrap_session_factory(get_async_session) as session:
        await _ensure_schema(session)
        await session.execute(
            text(
                """
                INSERT INTO ai_call_events (call_id, event_type, payload)
                VALUES (:call_id, :event_type, :payload);
                """
            ),
            {"call_id": call_id, "event_type": event_type, "payload": payload},
        )
        await session.commit()


async def list_recent_calls(limit: int = 50) -> List[Dict[str, Any]]:
    async with wrap_session_factory(get_async_session) as session:
        await _ensure_schema(session)
        rows = await session.execute(
            text(
                """
                SELECT call_id, direction, from_number, to_number, status, bot_name,
                       purpose, customer_name, provider, metadata, created_at,
                       updated_at, last_event, last_event_ts
                FROM ai_calls
                ORDER BY updated_at DESC
                LIMIT :limit;
                """
            ),
            {"limit": limit},
        )
        return [dict(row) for row in rows.mappings().all()]


async def list_events(call_id: str, limit: int = 50) -> List[Dict[str, Any]]:
    async with wrap_session_factory(get_async_session) as session:
        await _ensure_schema(session)
        rows = await session.execute(
            text(
                """
                SELECT id, call_id, event_type, payload, ts
                FROM ai_call_events
                WHERE call_id = :call_id
                ORDER BY ts DESC
                LIMIT :limit;
                """
            ),
            {"call_id": call_id, "limit": limit},
        )
        return [dict(row) for row in rows.mappings().all()]

