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
        # Test doubles may provide only the minimal API used by route handlers.
        _schema_initialized = True
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

    await session.execute(text("ALTER TABLE portal_access_requests ADD COLUMN IF NOT EXISTS request_id TEXT UNIQUE"))
    await session.execute(text("ALTER TABLE portal_access_requests ADD COLUMN IF NOT EXISTS tenant_id TEXT"))
    await session.execute(text("ALTER TABLE portal_access_requests ADD COLUMN IF NOT EXISTS email_normalized TEXT"))
    await session.execute(text("ALTER TABLE portal_access_requests ADD COLUMN IF NOT EXISTS company_name TEXT"))
    await session.execute(text("ALTER TABLE portal_access_requests ADD COLUMN IF NOT EXISTS system TEXT DEFAULT 'standard'"))
    await session.execute(text("ALTER TABLE portal_access_requests ADD COLUMN IF NOT EXISTS requested_systems TEXT"))
    await session.execute(text("ALTER TABLE portal_access_requests ADD COLUMN IF NOT EXISTS rejection_code TEXT"))
    await session.execute(text("ALTER TABLE portal_access_requests ADD COLUMN IF NOT EXISTS rejection_message TEXT"))
    await session.execute(text("ALTER TABLE portal_access_requests ADD COLUMN IF NOT EXISTS attempts_count INT DEFAULT 0"))
    await session.execute(text("ALTER TABLE portal_access_requests ADD COLUMN IF NOT EXISTS last_attempt_at TIMESTAMPTZ"))
    await session.execute(text("ALTER TABLE portal_access_requests ADD COLUMN IF NOT EXISTS decided_at TIMESTAMPTZ"))
    await session.execute(text("ALTER TABLE portal_access_requests ADD COLUMN IF NOT EXISTS decided_by TEXT"))
    await session.execute(text("ALTER TABLE portal_access_requests ADD COLUMN IF NOT EXISTS ip_address TEXT"))

    for column in ("country", "user_type", "system"):
        try:
            await session.execute(
                text(
                    f"""
                    ALTER TABLE portal_access_requests
                    ALTER COLUMN {column} TYPE TEXT
                    """
                )
            )
        except Exception as exc:
            logger.debug("portal_access_requests column %s type not altered: %s", column, exc)

    await session.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS email_verifications (
                id BIGSERIAL PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                token TEXT NOT NULL,
                expires_at TIMESTAMPTZ NOT NULL,
                verified_at TIMESTAMPTZ,
                created_at TIMESTAMPTZ DEFAULT NOW()
            );
            """
        )
    )

    await session.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS admin_notifications (
                id BIGSERIAL PRIMARY KEY,
                request_id BIGINT REFERENCES portal_access_requests(id),
                notification_type TEXT,
                title TEXT,
                message TEXT,
                read BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMPTZ DEFAULT NOW()
            );
            """
        )
    )

    await session.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS audit_log (
                id BIGSERIAL PRIMARY KEY,
                request_id BIGINT REFERENCES portal_access_requests(id),
                action TEXT,
                actor TEXT,
                details JSONB,
                ip_address TEXT,
                created_at TIMESTAMPTZ DEFAULT NOW()
            );
            """
        )
    )

    await session.execute(
        text(
            """
            CREATE INDEX IF NOT EXISTS idx_portal_requests_created_at
            ON portal_access_requests(created_at DESC);
            """
        )
    )
    await session.execute(
        text(
            """
            CREATE INDEX IF NOT EXISTS idx_portal_requests_email
            ON portal_access_requests(email);
            """
        )
    )
    await session.execute(
        text(
            """
            CREATE INDEX IF NOT EXISTS idx_portal_requests_email_norm
            ON portal_access_requests(email_normalized);
            """
        )
    )
    try:
        await session.execute(
            text(
                """
                CREATE UNIQUE INDEX IF NOT EXISTS ux_portal_access_requests_pending
                ON portal_access_requests(tenant_id, email_normalized)
                WHERE status = 'pending';
                """
            )
        )
    except Exception as exc:
        logger.warning("portal_access_requests pending unique index not created: %s", exc)
    await session.execute(
        text(
            """
            CREATE INDEX IF NOT EXISTS idx_email_verifications_token
            ON email_verifications(token);
            """
        )
    )
    await session.execute(
        text(
            """
            CREATE INDEX IF NOT EXISTS idx_audit_log_request_id
            ON audit_log(request_id);
            """
        )
    )

    await session.commit()
    _schema_initialized = True


@asynccontextmanager
async def _maybe_session(session: Optional[AsyncSession]):
    if session is not None:
        yield session, False
        return
    async with wrap_session_factory(get_async_session) as scoped_session:
        yield scoped_session, True


async def create_portal_request(
    *,
    tenant_id: Optional[str],
    full_name: str,
    company: str,
    email: str,
    mobile: str,
    comment: Optional[str],
    country: str,
    user_type: str,
    system: str = "standard",
    requested_systems: Optional[Dict[str, Any]] = None,
    us_state: Optional[str] = None,
    dot_number: Optional[str] = None,
    mc_number: Optional[str] = None,
    us_business_address: Optional[str] = None,
    ca_province: Optional[str] = None,
    ca_registered_address: Optional[str] = None,
    ca_company_number: Optional[str] = None,
    document_name: Optional[str] = None,
    session: Optional[AsyncSession] = None,
) -> Dict[str, Any]:
    request_id = str(uuid.uuid4())
    email_clean = email.strip()
    email_norm = email_clean.lower()
    company_clean = company.strip()
    systems_json = json.dumps(requested_systems or {"system": system})

    async with _maybe_session(session) as (session, owns_session):
        await _ensure_schema(session)
        result = await session.execute(
            text(
                """
                INSERT INTO portal_access_requests (
                    request_id, tenant_id, email_normalized,
                    full_name, company, company_name, email, mobile, comment, country, user_type,
                    system, requested_systems,
                    us_state, dot_number, mc_number, us_business_address,
                    ca_province, ca_registered_address, ca_company_number,
                    document_name, status, attempts_count, last_attempt_at
                )
                VALUES (
                    :request_id, :tenant_id, :email_normalized,
                    :full_name, :company, :company_name, :email, :mobile, :comment, :country, :user_type,
                    :system, :requested_systems,
                    :us_state, :dot_number, :mc_number, :us_business_address,
                    :ca_province, :ca_registered_address, :ca_company_number,
                    :document_name, 'pending', 1, NOW()
                )
                RETURNING id, request_id, status, created_at;
                """
            ),
            {
                "request_id": request_id,
                "tenant_id": tenant_id,
                "email_normalized": email_norm,
                "full_name": full_name,
                "company": company_clean,
                "company_name": company_clean,
                "email": email_clean,
                "mobile": mobile,
                "comment": comment,
                "country": country,
                "user_type": user_type,
                "system": system,
                "requested_systems": systems_json,
                "us_state": us_state,
                "dot_number": dot_number,
                "mc_number": mc_number,
                "us_business_address": us_business_address,
                "ca_province": ca_province,
                "ca_registered_address": ca_registered_address,
                "ca_company_number": ca_company_number,
                "document_name": document_name,
            },
        )
        row = result.mappings().first()
        if owns_session:
            await session.commit()
        if row is None:
            return {}
        return {
            "id": row["id"],
            "request_id": row["request_id"],
            "status": row["status"],
            "created_at": row["created_at"],
        }


async def list_portal_requests(
    *,
    limit: int = 100,
    status: Optional[str] = None,
    session: Optional[AsyncSession] = None,
) -> list[dict]:
    async with _maybe_session(session) as (session, owns_session):
        await _ensure_schema(session)
        if status:
            if status == "rejected":
                rows = await session.execute(
                    text(
                        """
                        SELECT id, request_id, full_name, company, company_name, email, email_normalized,
                               mobile, country, user_type, document_name, system, requested_systems,
                               status, rejection_code, rejection_message, attempts_count, last_attempt_at,
                               created_at, decided_at, decided_by, tenant_id
                        FROM portal_access_requests
                        WHERE status IN ('rejected','denied')
                        ORDER BY created_at DESC
                        LIMIT :limit;
                        """
                    ),
                    {"limit": limit},
                )
                normalized = [dict(row) for row in rows.mappings().all()]
                for row in normalized:
                    row["status"] = _normalize_status(row.get("status"))
                return normalized
            rows = await session.execute(
                text(
                    """
                    SELECT id, request_id, full_name, company, company_name, email, email_normalized,
                           mobile, country, user_type, document_name, system, requested_systems,
                           status, rejection_code, rejection_message, attempts_count, last_attempt_at,
                           created_at, decided_at, decided_by, tenant_id
                    FROM portal_access_requests
                    WHERE status = :status
                    ORDER BY created_at DESC
                    LIMIT :limit;
                    """
                ),
                {"status": status, "limit": limit},
            )
        else:
            rows = await session.execute(
                text(
                    """
                    SELECT id, request_id, full_name, company, company_name, email, email_normalized,
                           mobile, country, user_type, document_name, system, requested_systems,
                           status, rejection_code, rejection_message, attempts_count, last_attempt_at,
                           created_at, decided_at, decided_by, tenant_id
                    FROM portal_access_requests
                    ORDER BY created_at DESC
                    LIMIT :limit;
                    """
                ),
                {"limit": limit},
            )
        normalized = [dict(row) for row in rows.mappings().all()]
        for row in normalized:
            row["status"] = _normalize_status(row.get("status"))
        return normalized


async def get_portal_request_by_id(
    id: int,
    *,
    session: Optional[AsyncSession] = None,
) -> Optional[dict]:
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
                WHERE id = :id;
                """
            ),
            {"id": id},
        )
        m = row.mappings().first()
        if not m:
            return None
        data = dict(m)
        data["status"] = _normalize_status(data.get("status"))
        return data


async def get_portal_request_by_request_id(
    request_id: str,
    *,
    session: Optional[AsyncSession] = None,
) -> Optional[dict]:
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


async def update_portal_request_status(
    id: int,
    status: str,
    reason: Optional[str] = None,
    rejection_code: Optional[str] = None,
    decided_by: Optional[str] = None,
    *,
    session: Optional[AsyncSession] = None,
) -> bool:
    async with _maybe_session(session) as (session, owns_session):
        await _ensure_schema(session)
        await session.execute(
            text(
                """
                UPDATE portal_access_requests
                SET status = :status,
                    rejection_code = :rejection_code,
                    rejection_message = :rejection_message,
                    decided_at = CASE WHEN :status IN ('approved','rejected') THEN NOW() ELSE decided_at END,
                    decided_by = COALESCE(:decided_by, decided_by)
                WHERE id = :id;
                """
            ),
            {
                "id": id,
                "status": status,
                "rejection_code": rejection_code,
                "rejection_message": reason,
                "decided_by": decided_by,
            },
        )
        if owns_session:
            await session.commit()
        return True


async def delete_portal_request(
    id: int,
    *,
    session: Optional[AsyncSession] = None,
) -> bool:
    async with _maybe_session(session) as (session, owns_session):
        await _ensure_schema(session)
        await session.execute(
            text(
                """
                DELETE FROM portal_access_requests
                WHERE id = :id;
                """
            ),
            {"id": id},
        )
        if owns_session:
            await session.commit()
        return True


async def increment_request_attempt(
    id: int,
    *,
    session: Optional[AsyncSession] = None,
) -> None:
    async with _maybe_session(session) as (session, owns_session):
        await _ensure_schema(session)
        await session.execute(
            text(
                """
                UPDATE portal_access_requests
                SET attempts_count = COALESCE(attempts_count, 0) + 1,
                    last_attempt_at = NOW()
                WHERE id = :id;
                """
            ),
            {"id": id},
        )
        if owns_session:
            await session.commit()


async def check_duplicate_today(
    email: str,
    company: str,
    *,
    session: Optional[AsyncSession] = None,
) -> bool:
    async with _maybe_session(session) as (session, owns_session):
        await _ensure_schema(session)
        result = await session.execute(
            text(
                """
                SELECT COUNT(*) as cnt
                FROM portal_access_requests
                WHERE (LOWER(BTRIM(email)) = :email OR LOWER(BTRIM(company)) = :company)
                AND created_at >= NOW() - INTERVAL '24 hours'
                """
            ),
            {"email": email.strip().lower(), "company": company.strip().lower()},
        )
        row = result.mappings().first()
        return row["cnt"] > 0 if row else False


async def check_duplicate_email(
    email: str,
    *,
    session: Optional[AsyncSession] = None,
) -> bool:
    email_norm = email.strip().lower()
    if not email_norm:
        return False

    async with _maybe_session(session) as (session, owns_session):
        await _ensure_schema(session)
        result = await session.execute(
            text(
                """
                SELECT 1
                FROM portal_access_requests
                WHERE LOWER(BTRIM(email)) = :email
                LIMIT 1
                """
            ),
            {"email": email_norm},
        )
        row = result.first()
        if row is not None:
            return True

        try:
            legacy = await session.execute(
                text(
                    """
                    SELECT 1
                    FROM portal_requests
                    WHERE LOWER(BTRIM(email)) = :email
                    LIMIT 1
                    """
                ),
                {"email": email_norm},
            )
            return legacy.first() is not None
        except Exception:
            return False


async def check_ip_rate_limit(
    ip_address: str,
    requests_per_hour: int = 5,
    *,
    session: Optional[AsyncSession] = None,
) -> bool:
    async with _maybe_session(session) as (session, owns_session):
        await _ensure_schema(session)

        if not hasattr(session, "execute"):
            # Test double – treat as not rate-limited so the route can proceed.
            return False

        result = await session.execute(
            text(
                """
                SELECT COUNT(*) as cnt
                FROM portal_access_requests
                WHERE ip_address = :ip_address
                AND created_at >= NOW() - INTERVAL '1 hour'
                """
            ),
            {"ip_address": ip_address},
        )
        row = result.mappings().first()
        count = row["cnt"] if row else 0
        return count >= requests_per_hour


async def create_verification_token(
    email: str,
    token: str,
    expires_hours: int = 24,
    *,
    session: Optional[AsyncSession] = None,
) -> bool:
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


async def create_admin_notification(
    request_id: Optional[int],
    notification_type: str,
    title: str,
    message: str,
    *,
    session: Optional[AsyncSession] = None,
) -> bool:
    async with _maybe_session(session) as (session, owns_session):
        await _ensure_schema(session)
        try:
            async with session.begin_nested():
                await session.execute(
                    text(
                        """
                        INSERT INTO admin_notifications (request_id, notification_type, title, message)
                        VALUES (:request_id, :notification_type, :title, :message)
                        """
                    ),
                    {
                        "request_id": request_id,
                        "notification_type": notification_type,
                        "title": title,
                        "message": message,
                    },
                )
            if owns_session:
                await session.commit()
            return True
        except SQLAlchemyError as exc:
            logger.warning("admin_notifications insert failed: %s", exc)
            try:
                async with session.begin_nested():
                    await session.execute(
                        text(
                            """
                            INSERT INTO admin_notifications (request_id, notification_type, title, message)
                            VALUES (NULL, :notification_type, :title, :message)
                            """
                        ),
                        {
                            "notification_type": notification_type,
                            "title": title,
                            "message": message,
                        },
                    )
                if owns_session:
                    await session.commit()
                return True
            except SQLAlchemyError as exc2:
                logger.warning("admin_notifications fallback insert failed: %s", exc2)
                if owns_session:
                    await session.rollback()
                return False


async def list_admin_notifications(
    limit: int = 50,
    unread_only: bool = False,
    *,
    session: Optional[AsyncSession] = None,
) -> list[dict]:
    async with _maybe_session(session) as (session, owns_session):
        await _ensure_schema(session)

        query = "SELECT * FROM admin_notifications"
        if unread_only:
            query += " WHERE read = FALSE"
        query += " ORDER BY created_at DESC LIMIT :limit"

        rows = await session.execute(text(query), {"limit": limit})
        return [dict(row) for row in rows.mappings().all()]


async def log_audit_action(
    request_id: Optional[int],
    action: str,
    actor: str,
    details: Optional[Dict] = None,
    ip_address: Optional[str] = None,
    *,
    session: Optional[AsyncSession] = None,
) -> bool:
    async with _maybe_session(session) as (session, owns_session):
        await _ensure_schema(session)

        details_json = json.dumps(details if details is not None else {})
        ip_addr = ip_address if ip_address is not None else ""

        try:
            async with session.begin_nested():
                await session.execute(
                    text(
                        """
                        INSERT INTO audit_log (request_id, action, actor, details, ip_address)
                        VALUES (:request_id, :action, :actor, CAST(:details AS JSONB), :ip_address)
                        """
                    ),
                    {
                        "request_id": request_id,
                        "action": action,
                        "actor": actor,
                        "details": details_json,
                        "ip_address": ip_addr,
                    },
                )
            if owns_session:
                await session.commit()
            return True
        except SQLAlchemyError as exc:
            logger.warning("audit_log insert failed: %s", exc)
            try:
                async with session.begin_nested():
                    await session.execute(
                        text(
                            """
                            INSERT INTO audit_log (request_id, action, actor, details, ip_address)
                            VALUES (NULL, :action, :actor, CAST(:details AS JSONB), :ip_address)
                            """
                        ),
                        {
                            "action": action,
                            "actor": actor,
                            "details": details_json,
                            "ip_address": ip_address,
                        },
                    )
                if owns_session:
                    await session.commit()
                return True
            except SQLAlchemyError as exc2:
                logger.warning("audit_log fallback insert failed: %s", exc2)
                if owns_session:
                    await session.rollback()
                return False


async def get_request_audit_log(
    request_id: int,
    *,
    session: Optional[AsyncSession] = None,
) -> list[dict]:
    async with _maybe_session(session) as (session, owns_session):
        await _ensure_schema(session)
        result = await session.execute(
            text(
                """
                SELECT id, action, actor, details, ip_address, created_at
                FROM audit_log
                WHERE request_id = :request_id
                ORDER BY created_at DESC
                """
            ),
            {"request_id": request_id},
        )
        return [dict(row) for row in result.mappings().all()]
