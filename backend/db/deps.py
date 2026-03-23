from __future__ import annotations

from typing import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.session import async_session_maker


async def get_db() -> AsyncIterator[AsyncSession]:
    """
    FastAPI-compatible dependency returning a usable async session.
    """
    SessionLocal = async_session_maker()
    async with SessionLocal() as session:
        yield session
