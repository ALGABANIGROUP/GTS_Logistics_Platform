# backend/core/config.py
from __future__ import annotations

import os
from typing import Optional, AsyncGenerator
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy import event
from sqlalchemy.orm import with_loader_criteria
from sqlalchemy.pool import NullPool
from backend.database.base import Base
from backend.database.tenant_write_guard import install_tenant_write_guard
from sqlalchemy.orm import Session

# ---------------------------------------------------------------------
# Env bootstrap (root .env wins)
# ---------------------------------------------------------------------
try:
    import backend.env_bootstrap  # noqa: F401
except Exception:
    try:
        import env_bootstrap  # type: ignore  # noqa: F401
    except Exception:
        pass


def _mask_pw(dsn: str) -> str:
    if not dsn:
        return dsn
    try:
        parts = urlsplit(dsn)
        if parts.password:
            masked_netloc = parts.netloc.replace(parts.password, "****")
            return urlunsplit(
                (parts.scheme, masked_netloc, parts.path, parts.query, parts.fragment)
            )
    except Exception:
        pass
    return dsn


def _sanitize_async_url(raw_url: str) -> str:
    if not raw_url:
        return raw_url

    # SQLite URLs don't need sanitization
    if raw_url.startswith("sqlite"):
        return raw_url

    if raw_url.startswith("postgresql+psycopg://"):
        raw_url = raw_url.replace("postgresql+psycopg://", "postgresql+asyncpg://", 1)
    elif raw_url.startswith("postgresql://"):
        raw_url = raw_url.replace("postgresql://", "postgresql+asyncpg://", 1)

    parts = urlsplit(raw_url)
    query = dict(parse_qsl(parts.query))

    # asyncpg does not support sslmode; convert sslmode=require -> ssl=require
    if "sslmode" in query:
        query.pop("sslmode", None)
        query.setdefault("ssl", "require")

    cleaned = urlencode(query)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, cleaned, parts.fragment))


def _get_async_dsn() -> str:
    raw = os.getenv("ASYNC_DATABASE_URL", "").strip()
    if not raw:
        raw = os.getenv("DATABASE_URL", "").strip()
    return _sanitize_async_url(raw)


_async_engine: Optional[AsyncEngine] = None
_async_maker: Optional[async_sessionmaker[AsyncSession]] = None


def init_engines() -> None:
    global _async_engine, _async_maker

    if _async_engine is not None and _async_maker is not None:
        return

    dsn = _get_async_dsn()
    if not dsn:
        print("[db] WARN: No database DSN configured - running in offline mode")
        return

    # Safe log (masked)
    print(f"[db] DSN -> {_mask_pw(dsn)}")


    try:
        # Phase 3 Optimization: Increase pool size from default (5/10) to handle 100+ concurrent users
        # Separate config for tests vs production (NullPool doesn't accept pool parameters)
        if os.getenv("PYTEST_CURRENT_TEST"):
            # Test environment: NullPool without pool parameters
            _async_engine = create_async_engine(
                dsn,
                echo=False,
                future=True,
                poolclass=NullPool,
                pool_pre_ping=False
            )
            print(f"[db] Test mode: NullPool configured")
        else:
            # Production: QueuePool with optimizations (tunable via env vars)
            POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "20"))
            MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "30"))
            POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", "30"))
            POOL_PRE_PING = os.getenv("DB_POOL_PRE_PING", "true").lower() in ("1", "true", "yes")
            POOL_RECYCLE = int(os.getenv("DB_POOL_RECYCLE", "3600"))
            CONNECT_ARGS = {}
            if os.getenv("DB_CONNECT_COMMAND_TIMEOUT"):
                CONNECT_ARGS["command_timeout"] = int(os.getenv("DB_CONNECT_COMMAND_TIMEOUT"))
            if os.getenv("DB_CONNECT_TIMEOUT"):
                CONNECT_ARGS["timeout"] = int(os.getenv("DB_CONNECT_TIMEOUT"))

            # allow custom pool settings via env vars without editing code
            _async_engine = create_async_engine(
                dsn,
                echo=False,
                future=True,
                pool_size=POOL_SIZE,
                max_overflow=MAX_OVERFLOW,
                pool_timeout=POOL_TIMEOUT,
                pool_pre_ping=POOL_PRE_PING,
                pool_recycle=POOL_RECYCLE,  # Recycle connections
                **({"connect_args": CONNECT_ARGS} if CONNECT_ARGS else {}),
            )
            print(
                f"[db] Production mode: Pool configured "
                f"(size={POOL_SIZE}, max_overflow={MAX_OVERFLOW}, timeout={POOL_TIMEOUT}s, "
                f"pre_ping={POOL_PRE_PING}, recycle={POOL_RECYCLE}s, connect_args={CONNECT_ARGS})"
            )

        # Activate Tenant Write Guard (covers all Session types)
        install_tenant_write_guard(Session)

        # (Tenant filter removed from config.py — now handled in request/middleware layer)

        _async_maker = async_sessionmaker(
            bind=_async_engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
            autocommit=False,
        )
    except Exception as e:
        print(f"[db] ERROR: Failed to initialize database engine: {e}")
        print("[db] WARN: Running in offline mode - database features disabled")
        return


def get_sessionmaker() -> async_sessionmaker[AsyncSession]:
    if _async_maker is None:
        init_engines()
    assert _async_maker is not None
    return _async_maker


AsyncSessionLocal = get_sessionmaker()


# ---------------------------------------------------------------------
# Backward compatible exports
# ---------------------------------------------------------------------
async def get_db_async() -> AsyncGenerator[AsyncSession, None]:
    maker = get_sessionmaker()
    async with maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async for session in get_db_async():
        yield session


async def async_ping() -> bool:
    if _async_engine is None:
        init_engines()
    assert _async_engine is not None
    async with _async_engine.connect() as conn:
        result = await conn.exec_driver_sql("SELECT 1")
        return result.scalar() == 1


__all__ = [
    "init_engines",
    "get_sessionmaker",
    "get_db_async",
    "get_db",
    "async_ping",
    "AsyncSessionLocal",
]
