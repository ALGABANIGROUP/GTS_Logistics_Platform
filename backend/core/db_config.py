from __future__ import annotations

try:
    from backend.core.settings import Settings, settings
except Exception:  # pragma: no cover
    Settings = None  # type: ignore[assignment]
    settings = None  # type: ignore[assignment]

from backend.database.base import Base
from backend.database.config import AsyncSessionLocal, get_db, get_db_async, init_engines

init_engines()

try:
    from backend.database import config as _modern_config
    engine = getattr(_modern_config, "_async_engine", None)
except Exception:  # pragma: no cover
    engine = None


async def get_async_db():
    async for session in get_db_async():
        yield session


__all__ = [
    "Base",
    "Settings",
    "AsyncSessionLocal",
    "engine",
    "get_async_db",
    "get_db",
    "get_db_async",
    "settings",
]
