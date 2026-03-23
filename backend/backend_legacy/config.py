# backend/database/config.py
"""
Thin compatibility layer for database access.

This module exposes:
- get_db_async: the standard FastAPI async dependency for DB sessions.
- get_db: a legacy sync-style dependency placeholder (not supported).
- engine
- AsyncSessionLocal
- Base

It re-uses the core database configuration from backend.core.db_config.
"""

from __future__ import annotations

from typing import AsyncGenerator, Generator

from sqlalchemy.ext.asyncio import AsyncSession

from core.db_config import (
    engine,
    AsyncSessionLocal,
    Base,
    get_async_db,
    get_db_async as _core_get_db_async,
)


async def get_db_async() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI async DB session dependency.

    Typical usage in routers:
from database.config import get_db_async

        async def some_endpoint(db: AsyncSession = Depends(get_db_async)):
            ...
    """
    async for session in _core_get_db_async():
        yield session


def get_db() -> Generator[AsyncSession, None, None]:
    """
    Legacy sync-style dependency placeholder.

    This project is fully async; using this function is not supported in the
    current setup. It is kept only for backwards compatibility with older code
    paths that may still import `get_db`.
    """
    raise RuntimeError("get_db (sync) is not supported in this setup.")


__all__ = [
    "engine",
    "AsyncSessionLocal",
    "Base",
    "get_db_async",
    "get_db",
]





