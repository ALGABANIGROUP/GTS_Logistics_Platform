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
    # Store TMS access grants per user
    await session.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS tms_access (
                id BIGSERIAL PRIMARY KEY,
                user_id INTEGER,
                email TEXT,
                tms_enabled BOOLEAN DEFAULT true,
                granted_at TIMESTAMPTZ DEFAULT NOW(),
                granted_by TEXT,
                notes TEXT,
                UNIQUE(email)
            );
            """
        )
    )
    await session.execute(
        text(
            """
            CREATE INDEX IF NOT EXISTS idx_tms_access_email ON tms_access(email);
            """
        )
    )
    await session.commit()
    _schema_initialized = True


async def grant_tms_access(
    *,
    email: str,
    granted_by: str = "admin",
    notes: Optional[str] = None,
) -> Dict[str, Any]:
    """Grant TMS access to a user by email."""

    async with wrap_session_factory(get_async_session) as session:
        await _ensure_schema(session)
        result = await session.execute(
            text(
                """
                INSERT INTO tms_access (email, tms_enabled, granted_by, notes, granted_at)
                VALUES (:email, true, :granted_by, :notes, NOW())
                ON CONFLICT (email) DO UPDATE SET
                    tms_enabled = true,
                    granted_by = EXCLUDED.granted_by,
                    notes = EXCLUDED.notes
                RETURNING id, email, tms_enabled, granted_at;
                """
            ),
            {"email": email, "granted_by": granted_by, "notes": notes},
        )
        row = result.mappings().first()
        await session.commit()
        return dict(row) if row else {}


async def revoke_tms_access(email: str) -> bool:
    """Revoke TMS access from a user by email."""

    async with wrap_session_factory(get_async_session) as session:
        await _ensure_schema(session)
        await session.execute(
            text(
                """
                UPDATE tms_access SET tms_enabled = false WHERE email = :email;
                """
            ),
            {"email": email},
        )
        await session.commit()
        return True


async def check_tms_access(email: str) -> bool:
    """Check if a user has TMS access."""

    async with wrap_session_factory(get_async_session) as session:
        await _ensure_schema(session)
        row = await session.execute(
            text(
                """
                SELECT tms_enabled FROM tms_access WHERE email = :email;
                """
            ),
            {"email": email},
        )
        result = row.scalar()
        return result is True


async def list_tms_access(limit: int = 100) -> List[Dict[str, Any]]:
    """List all TMS access grants."""

    async with wrap_session_factory(get_async_session) as session:
        await _ensure_schema(session)
        rows = await session.execute(
            text(
                """
                SELECT id, email, tms_enabled, granted_by, notes, granted_at
                FROM tms_access
                ORDER BY granted_at DESC
                LIMIT :limit;
                """
            ),
            {"limit": limit},
        )
        return [dict(row) for row in rows.mappings().all()]

