from __future__ import annotations

import hashlib
import hmac
import os
import secrets
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from typing import Any, Optional

from fastapi import HTTPException, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.security.auth import JWT_SECRET

PASSWORD_RESET_EXPIRE_MINUTES = int(os.getenv("PASSWORD_RESET_EXPIRE_MINUTES", "5"))
PASSWORD_RESET_TOKEN_SECRET = os.getenv("PASSWORD_RESET_TOKEN_SECRET") or JWT_SECRET
FRONTEND_RESET_URL = (
    os.getenv("FRONTEND_RESET_URL")
    or os.getenv("FRONTEND_URL")
    or "https://gtsdispatcher.com/#token={token}"
)

_reset_table_initialized = False


async def _ensure_reset_table(db: AsyncSession) -> None:
    global _reset_table_initialized
    if _reset_table_initialized:
        return

    dialect = db.bind.dialect.name if db.bind is not None else ""
    if dialect == "sqlite":
        create_table_sql = """
            CREATE TABLE IF NOT EXISTS password_reset_tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                token_hash TEXT NOT NULL UNIQUE,
                expires_at TEXT NOT NULL,
                used_at TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            );
        """
    else:
        create_table_sql = """
            CREATE TABLE IF NOT EXISTS password_reset_tokens (
                id BIGSERIAL PRIMARY KEY,
                user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                token_hash TEXT NOT NULL UNIQUE,
                expires_at TIMESTAMPTZ NOT NULL,
                used_at TIMESTAMPTZ,
                created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
            );
        """

    await db.execute(text(create_table_sql))
    await db.execute(
        text(
            """
            CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_user
            ON password_reset_tokens(user_id);
            """
        )
    )
    await db.commit()
    _reset_table_initialized = True


def _hash_reset_token(token: str) -> str:
    return hmac.new(
        PASSWORD_RESET_TOKEN_SECRET.encode("utf-8"),
        token.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def _user_value(user: Any, field: str) -> Any:
    if isinstance(user, dict):
        return user.get(field)
    return getattr(user, field, None)


def _normalize_db_datetime(value: Any) -> datetime:
    if isinstance(value, datetime):
        return value if value.tzinfo is not None else value.replace(tzinfo=timezone.utc)
    if isinstance(value, str):
        normalized = value.strip().replace("Z", "+00:00")
        return datetime.fromisoformat(normalized)
    raise ValueError("Unsupported datetime value")


async def _load_reset_user_by_email(email: str, db: AsyncSession) -> Optional[Any]:
    result = await db.execute(
        text(
            """
            SELECT id, email, hashed_password, role, is_active
            FROM users
            WHERE lower(email) = lower(:email)
            LIMIT 1
            """
        ),
        {"email": str(email or "").strip().lower()},
    )
    row = result.mappings().first()
    if not row:
        return None
    return SimpleNamespace(
        id=int(row["id"]),
        email=row["email"],
        hashed_password=row.get("hashed_password"),
        role=row.get("role"),
        is_active=row.get("is_active"),
    )


async def _load_reset_user_by_id(user_id: int, db: AsyncSession) -> Optional[Any]:
    result = await db.execute(
        text(
            """
            SELECT id, email, hashed_password, role, is_active
            FROM users
            WHERE id = :user_id
            LIMIT 1
            """
        ),
        {"user_id": int(user_id)},
    )
    row = result.mappings().first()
    if not row:
        return None
    return SimpleNamespace(
        id=int(row["id"]),
        email=row["email"],
        hashed_password=row.get("hashed_password"),
        role=row.get("role"),
        is_active=row.get("is_active"),
    )


async def _create_password_reset_token(user: Any, db: AsyncSession) -> str:
    await _ensure_reset_table(db)

    token = secrets.token_urlsafe(16)
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=PASSWORD_RESET_EXPIRE_MINUTES)

    await db.execute(
        text(
            """
            UPDATE password_reset_tokens
            SET used_at = CURRENT_TIMESTAMP
            WHERE user_id = :user_id AND used_at IS NULL
            """
        ),
        {"user_id": int(_user_value(user, "id"))},
    )
    await db.execute(
        text(
            """
            INSERT INTO password_reset_tokens (user_id, token_hash, expires_at)
            VALUES (:user_id, :token_hash, :expires_at)
            """
        ),
        {
            "user_id": int(_user_value(user, "id")),
            "token_hash": _hash_reset_token(token),
            "expires_at": expires_at,
        },
    )
    await db.commit()
    return token


async def _get_user_from_reset_token(token: str, db: AsyncSession) -> Any:
    error = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Invalid or expired reset token",
    )
    await _ensure_reset_table(db)

    result = await db.execute(
        text(
            """
            SELECT user_id, expires_at, used_at
            FROM password_reset_tokens
            WHERE token_hash = :token_hash
            LIMIT 1
            """
        ),
        {"token_hash": _hash_reset_token(token)},
    )
    row = result.mappings().first()
    if not row or row["used_at"] is not None:
        raise error

    expires_at = _normalize_db_datetime(row["expires_at"])
    if expires_at <= datetime.now(timezone.utc):
        raise error

    user = await _load_reset_user_by_id(int(row["user_id"]), db)
    if not user:
        raise error

    return user


def _build_reset_link(token: str) -> str:
    if "{token}" in FRONTEND_RESET_URL:
        return FRONTEND_RESET_URL.replace("{token}", token)
    if "?" in FRONTEND_RESET_URL:
        return f"{FRONTEND_RESET_URL}&token={token}"
    return f"{FRONTEND_RESET_URL}?token={token}"
