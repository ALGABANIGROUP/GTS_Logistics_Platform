from __future__ import annotations

import json
import logging
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database.session import get_async_session, wrap_session_factory

logger = logging.getLogger(__name__)

_schema_initialized = False
_portal_table = "portal_access_requests"


def _normalize_status(value: Optional[str]) -> Optional[str]:
    if value == "denied":
        return "rejected"
    return value


async def _ensure_schema(session) -> None:
    global _schema_initialized
    if _schema_initialized:
        return
    if not hasattr(session, "execute"):
        return
    try:
        await session.execute(text("SELECT 1 FROM portal_access_requests LIMIT 1"))
        await session.execute(text("SELECT 1 FROM email_verifications LIMIT 1"))
        _schema_initialized = True
        return
    except SQLAlchemyError as exc:
        msg = str(exc).lower()
        if "does not exist" not in msg and "undefinedtable" not in msg:
            raise
    await session.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS portal_access_requests (
                id BIGSERIAL PRIMARY KEY,
                request_id TEXT UNIQUE,
                tenant_id TEXT,
                email_normalized TEXT,
                full_name TEXT,
                company TEXT,
                company_name TEXT,
                email TEXT,
                mobile TEXT,
                comment TEXT,
                country TEXT,
                user_type TEXT,
                system TEXT DEFAULT 'standard',
                requested_systems TEXT,
                us_state TEXT,
                dot_number TEXT,
                mc_number TEXT,
                us_business_address TEXT,
                ca_province TEXT,
                ca_registered_address TEXT,
                ca_company_number TEXT,
                document_name TEXT,
                status TEXT DEFAULT 'pending',
                rejection_code TEXT,
                rejection_message TEXT,
                attempts_count INT DEFAULT 0,
                last_attempt_at TIMESTAMPTZ,
                decided_at TIMESTAMPTZ,
                decided_by TEXT,
                email_verified BOOLEAN DEFAULT FALSE,
                verification_token TEXT,
                verification_sent_at TIMESTAMPTZ,
                ip_address TEXT,
                created_at TIMESTAMPTZ DEFAULT NOW()
            );
            """
        )
    )
    await session.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS email_verifications (
                id BIGSERIAL PRIMARY KEY,
                email TEXT NOT NULL,
                token TEXT NOT NULL UNIQUE,
                expires_at TIMESTAMPTZ NOT NULL,
                verified_at TIMESTAMPTZ,
                created_at TIMESTAMPTZ DEFAULT NOW()
            );
            """
        )
    )
    _schema_initialized = True


@asynccontextmanager
async def get_portal_session():
    async with wrap_session_factory(get_async_session)() as session:
        await _ensure_schema(session)
        yield session


async def create_portal_request(
    tenant_id: str,
    email: str,
    full_name: str,
    company: str,
    company_name: Optional[str] = None,
    mobile: Optional[str] = None,
    comment: Optional[str] = None,
    country: Optional[str] = None,
    user_type: Optional[str] = None,
    system: str = "standard",
    requested_systems: Optional[str] = None,
    us_state: Optional[str] = None,
    dot_number: Optional[str] = None,
    mc_number: Optional[str] = None,
    us_business_address: Optional[str] = None,
    ca_province: Optional[str] = None,
    ca_registered_address: Optional[str] = None,
    ca_company_number: Optional[str] = None,
    document_name: Optional[str] = None,
    ip_address: Optional[str] = None,
) -> str:
    request_id = str(uuid.uuid4())
    email_normalized = email.lower().strip()

    async with get_portal_session() as session:
        await session.execute(
            text(
                """
                INSERT INTO portal_access_requests (
                    request_id, tenant_id, email_normalized, full_name, company,
                    company_name, email, mobile, comment, country, user_type,
                    system, requested_systems, us_state, dot_number, mc_number,
                    us_business_address, ca_province, ca_registered_address,
                    ca_company_number, document_name, ip_address
                ) VALUES (
                    :request_id, :tenant_id, :email_normalized, :full_name, :company,
                    :company_name, :email, :mobile, :comment, :country, :user_type,
                    :system, :requested_systems, :us_state, :dot_number, :mc_number,
                    :us_business_address, :ca_province, :ca_registered_address,
                    :ca_company_number, :document_name, :ip_address
                )
                """
            ),
            {
                "request_id": request_id,
                "tenant_id": tenant_id,
                "email_normalized": email_normalized,
                "full_name": full_name,
                "company": company,
                "company_name": company_name,
                "email": email,
                "mobile": mobile,
                "comment": comment,
                "country": country,
                "user_type": user_type,
                "system": system,
                "requested_systems": requested_systems,
                "us_state": us_state,
                "dot_number": dot_number,
                "mc_number": mc_number,
                "us_business_address": us_business_address,
                "ca_province": ca_province,
                "ca_registered_address": ca_registered_address,
                "ca_company_number": ca_company_number,
                "document_name": document_name,
                "ip_address": ip_address,
            },
        )
        await session.commit()

    return request_id


async def get_portal_request_by_email(email: str) -> Optional[Dict[str, Any]]:
    email_normalized = email.lower().strip()

    async with get_portal_session() as session:
        result = await session.execute(
            text(
                """
                SELECT * FROM portal_access_requests
                WHERE email_normalized = :email_normalized
                ORDER BY created_at DESC
                LIMIT 1
                """
            ),
            {"email_normalized": email_normalized},
        )
        row = result.fetchone()
        if row:
            return dict(row)
        return None


async def get_portal_request_by_id(request_id: str) -> Optional[Dict[str, Any]]:
    async with get_portal_session() as session:
        result = await session.execute(
            text(
                """
                SELECT * FROM portal_access_requests
                WHERE request_id = :request_id
                """
            ),
            {"request_id": request_id},
        )
        row = result.fetchone()
        if row:
            return dict(row)
        return None


async def update_portal_request_status(
    request_id: str,
    status: str,
    decided_by: Optional[str] = None,
    rejection_code: Optional[str] = None,
    rejection_message: Optional[str] = None,
) -> bool:
    status = _normalize_status(status)

    async with get_portal_session() as session:
        result = await session.execute(
            text(
                """
                UPDATE portal_access_requests
                SET status = :status,
                    decided_at = NOW(),
                    decided_by = :decided_by,
                    rejection_code = :rejection_code,
                    rejection_message = :rejection_message
                WHERE request_id = :request_id
                """
            ),
            {
                "request_id": request_id,
                "status": status,
                "decided_by": decided_by,
                "rejection_code": rejection_code,
                "rejection_message": rejection_message,
            },
        )
        await session.commit()
        return result.rowcount > 0


async def increment_request_attempts(request_id: str) -> bool:
    async with get_portal_session() as session:
        result = await session.execute(
            text(
                """
                UPDATE portal_access_requests
                SET attempts_count = attempts_count + 1,
                    last_attempt_at = NOW()
                WHERE request_id = :request_id
                """
            ),
            {"request_id": request_id},
        )
        await session.commit()
        return result.rowcount > 0


async def create_email_verification(email: str, token: str, expires_at: datetime) -> None:
    async with get_portal_session() as session:
        await session.execute(
            text(
                """
                INSERT INTO email_verifications (email, token, expires_at)
                VALUES (:email, :token, :expires_at)
                ON CONFLICT (token) DO NOTHING
                """
            ),
            {"email": email, "token": token, "expires_at": expires_at},
        )
        await session.commit()


async def verify_email_token(token: str) -> Optional[str]:
    async with get_portal_session() as session:
        result = await session.execute(
            text(
                """
                SELECT email FROM email_verifications
                WHERE token = :token AND expires_at > NOW()
                """
            ),
            {"token": token},
        )
        row = result.fetchone()
        if row:
            # Delete the token after successful verification
            await session.execute(
                text("DELETE FROM email_verifications WHERE token = :token"),
                {"token": token},
            )
            await session.commit()
            return row[0]
        return None


async def update_email_verification_status(request_id: str, verified: bool) -> bool:
    async with get_portal_session() as session:
        result = await session.execute(
            text(
                """
                UPDATE portal_access_requests
                SET email_verified = :verified,
                    verification_sent_at = CASE WHEN :verified THEN verification_sent_at ELSE NOW() END
                WHERE request_id = :request_id
                """
            ),
            {"request_id": request_id, "verified": verified},
        )
        await session.commit()
        return result.rowcount > 0


async def get_pending_requests(limit: int = 50) -> list[Dict[str, Any]]:
    async with get_portal_session() as session:
        result = await session.execute(
            text(
                """
                SELECT * FROM portal_access_requests
                WHERE status = 'pending'
                ORDER BY created_at ASC
                LIMIT :limit
                """
            ),
            {"limit": limit},
        )
        return [dict(row) for row in result.fetchall()]


async def get_requests_by_status(status: str, limit: int = 100) -> list[Dict[str, Any]]:
    status = _normalize_status(status)

    async with get_portal_session() as session:
        result = await session.execute(
            text(
                """
                SELECT * FROM portal_access_requests
                WHERE status = :status
                ORDER BY created_at DESC
                LIMIT :limit
                """
            ),
            {"status": status, "limit": limit},
        )
        return [dict(row) for row in result.fetchall()]


async def get_all_requests(limit: int = 1000) -> list[Dict[str, Any]]:
    async with get_portal_session() as session:
        result = await session.execute(
            text(
                """
                SELECT * FROM portal_access_requests
                ORDER BY created_at DESC
                LIMIT :limit
                """
            ),
            {"limit": limit},
        )
        return [dict(row) for row in result.fetchall()]


async def search_requests(
    query: str, status_filter: Optional[str] = None, limit: int = 50
) -> list[Dict[str, Any]]:
    query = f"%{query}%"
    status_filter = _normalize_status(status_filter) if status_filter else None

    async with get_portal_session() as session:
        if status_filter:
            result = await session.execute(
                text(
                    """
                    SELECT * FROM portal_access_requests
                    WHERE (full_name ILIKE :query OR email ILIKE :query OR company ILIKE :query)
                    AND status = :status
                    ORDER BY created_at DESC
                    LIMIT :limit
                    """
                ),
                {"query": query, "status": status_filter, "limit": limit},
            )
        else:
            result = await session.execute(
                text(
                    """
                    SELECT * FROM portal_access_requests
                    WHERE full_name ILIKE :query OR email ILIKE :query OR company ILIKE :query
                    ORDER BY created_at DESC
                    LIMIT :limit
                    """
                ),
                {"query": query, "limit": limit},
            )
        return [dict(row) for row in result.fetchall()]


async def get_request_stats() -> Dict[str, int]:
    async with get_portal_session() as session:
        result = await session.execute(
            text(
                """
                SELECT status, COUNT(*) as count
                FROM portal_access_requests
                GROUP BY status
                """
            )
        )
        stats = {"total": 0, "pending": 0, "approved": 0, "rejected": 0}
        for row in result.fetchall():
            status = _normalize_status(row[0])
            count = row[1]
            stats[status] = count
            stats["total"] += count
        return stats


@asynccontextmanager
async def _maybe_session(session: Optional[AsyncSession] = None):
    """Context manager that provides a session, creating one if needed."""
    if session is not None:
        yield session, False
        return

    async with get_portal_session() as sess:
        yield sess, True


async def get_portal_request_by_request_id(
    request_id: str,
    *,
    session: Optional[AsyncSession] = None,
) -> Optional[dict]:
    """Get portal request by request_id"""
    async with _maybe_session(session) as (session, owns_session):
        await _ensure_schema(session)
        row = await session.execute(
            text(
                """
                SELECT id, request_id, tenant_id, email_normalized,
                       full_name, company, company_name, email, mobile, country, user_type,
                       comment, document_name, system, requested_systems,
                       status, rejection_code, rejection_message, attempts_count,
                       last_attempt_at, created_at, decided_at, decided_by
                FROM portal_access_requests
                WHERE request_id = :request_id;
                """
            ),
            {"request_id": request_id},
        )
        m = row.mappings().first()
        if not m:
            return None
        data = dict(m)
        data["status"] = _normalize_status(data.get("status"))
        return data


async def get_portal_request_by_email(
    email_normalized: str,
    *,
    tenant_id: Optional[str],
    session: Optional[AsyncSession] = None,
) -> Optional[dict]:
    """Get portal request by email"""
    async with _maybe_session(session) as (session, owns_session):
        await _ensure_schema(session)
        query = """
            SELECT id, request_id, status, created_at, decided_at,
                   rejection_code, rejection_message, attempts_count, last_attempt_at
            FROM portal_access_requests
            WHERE (email_normalized = :email OR LOWER(BTRIM(email)) = :email)
        """
        params = {"email": email_normalized}
        if tenant_id:
            query += " AND tenant_id = :tenant_id"
            params["tenant_id"] = tenant_id
        query += """
            ORDER BY created_at DESC
            LIMIT 1;
        """
        row = await session.execute(text(query), params)
        m = row.mappings().first()
        if not m:
            return None
        data = dict(m)
        data["status"] = _normalize_status(data.get("status"))
        return data


async def create_verification_token(
    email: str,
    token: str,
    expires_hours: int = 24,
    *,
    session: Optional[AsyncSession] = None,
) -> bool:
    """Create email verification token"""
    async with _maybe_session(session) as (session, owns_session):
        await _ensure_schema(session)
        await session.execute(
            text(
                """
                INSERT INTO email_verifications (email, token, expires_at)
                VALUES (:email, :token, NOW() + make_interval(hours => :hours))
                ON CONFLICT (email) DO UPDATE SET
                    token = :token,
                    expires_at = NOW() + make_interval(hours => :hours),
                    verified_at = NULL
                """
            ),
            {"email": email, "token": token, "hours": expires_hours},
        )
        if owns_session:
            await session.commit()
        return True


async def verify_email(
    token: str,
    *,
    session: Optional[AsyncSession] = None,
) -> Optional[str]:
    """Verify email token"""
    async with _maybe_session(session) as (session, owns_session):
        await _ensure_schema(session)
        result = await session.execute(
            text(
                """
                SELECT email FROM email_verifications
                WHERE token = :token
                AND expires_at > NOW()
                AND verified_at IS NULL
                """
            ),
            {"token": token},
        )
        row = result.mappings().first()
        if not row:
            return None

        email = row["email"]
        await session.execute(
            text(
                """
                UPDATE email_verifications
                SET verified_at = NOW()
                WHERE email = :email
                """
            ),
            {"email": email},
        )
        if owns_session:
            await session.commit()
        return email
