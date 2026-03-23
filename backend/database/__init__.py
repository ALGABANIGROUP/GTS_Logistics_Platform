from __future__ import annotations

from backend.services import crud
from backend.database.base import Base
from backend.database.config import get_db_async


async def get_async_db():
    async for session in get_db_async():
        yield session


__all__ = ["crud", "Base", "get_db_async", "get_async_db"]
