# backend/init_db.py
from __future__ import annotations

import asyncio

from sqlalchemy.ext.asyncio import AsyncEngine
from database.base import Base
from backend.database.connection import get_async_engine_from_env

# Import models so that they are registered with Base.metadata
# (Side-effect imports – we don't use the names directly here.)
from backend.models import models as _models  # noqa: F401
import backend.models.accounting_models  # noqa: F401


async def init_db() -> None:
    """
    Create all database tables defined on Base.metadata.
    """
    engine: AsyncEngine = get_async_engine_from_env()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(init_db())

