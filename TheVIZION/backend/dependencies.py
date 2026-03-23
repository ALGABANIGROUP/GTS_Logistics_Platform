# dependencies.py
import os
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from .models import Base


# Use main database unless a separate database is explicitly required
DATABASE_URL = os.getenv("VIZION_DATABASE_URL") or os.getenv("ASYNC_DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError(
        "[Vizion] Missing environment variable: ASYNC_DATABASE_URL or VIZION_DATABASE_URL"
    )

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True,
    pool_pre_ping=True,
)

SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@asynccontextmanager
async def get_db():
    session: AsyncSession = SessionLocal()
    try:
        yield session


async def init_db() -> None:
    """
    Initialize Vizion DB tables inside the main PostgreSQL database.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
