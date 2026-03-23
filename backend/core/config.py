# backend/core/db_config.py

from __future__ import annotations

import os
from typing import AsyncGenerator

try:
    from backend.config import Settings as AppSettings, settings as app_settings
except Exception:  # pragma: no cover - safe fallback
    AppSettings = None
    app_settings = None

Settings = AppSettings
settings = app_settings

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from database.base import Base


def _sanitize_async_url(raw_url: str) -> str:
    """
    Normalize ASYNC_DATABASE_URL for asyncpg.

    - Logs the original value.
    - Drops unsupported query parameters like `sslmode=` if present.
    """
    print(f"[db.sanitize] ASYNC_DATABASE_URL -> {raw_url}")

    if not raw_url:
        return raw_url

    # If url contains sslmode, drop the query string completely.
    if "sslmode=" in raw_url:
        base, *_ = raw_url.split("?", 1)
        cleaned = base
    else:
        cleaned = raw_url

    print(f"[db] DSN -> {cleaned}")
    return cleaned


# =====================================================================
# Read ASYNC_DATABASE_URL from environment and sanitize it
# =====================================================================

_raw_async_url = os.getenv("ASYNC_DATABASE_URL", "").strip()
ASYNC_DATABASE_URL: str = _sanitize_async_url(_raw_async_url)

if not ASYNC_DATABASE_URL:
    raise RuntimeError(
        "ASYNC_DATABASE_URL is not set. "
        "Please configure it in your .env file."
    )

# =====================================================================
# Async engine and session factory
# =====================================================================

engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=False,          # Set to True if you want SQL logs
    future=True,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Low-level async session generator.

    Typical usage (not directly in routes):
        async for session in get_async_db():
            ...
    """
    async with AsyncSessionLocal() as session:
        yield session


async def get_db_async() -> AsyncGenerator[AsyncSession, None]:
    """
    Standard FastAPI dependency for async DB sessions.

    Usage in routes:
from backend.database.config import get_db_async

        @router.get("/items")
        async def list_items(db: AsyncSession = Depends(get_db_async)):
            ...
    """
    async for session in get_async_db():
        yield session


__all__ = [
    "engine",
    "AsyncSessionLocal",
    "Base",
    "get_async_db",
    "get_db_async",
    "Settings",
    "settings",
]
