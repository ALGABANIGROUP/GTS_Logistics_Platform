from __future__ import annotations

from backend.services import crud
from backend.database.base import Base
from backend.database.config import get_db, get_db_async
from backend.database.session import async_session, get_async_session, wrap_session_factory


async def get_async_db():
    async for session in get_db_async():
        yield session


__all__ = [
    "crud",
    "Base",
    "get_db",
    "get_db_async",
    "get_async_db",
    "get_async_session",
    "async_session",
    "wrap_session_factory",
]
