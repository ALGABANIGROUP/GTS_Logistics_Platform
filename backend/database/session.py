from __future__ import annotations

from contextlib import asynccontextmanager
from importlib import import_module
from typing import AsyncIterator, Callable, Optional

# Ensure env is loaded before importing database config
try:
    import backend.env_bootstrap  # noqa: F401
except Exception:
    try:
        import env_bootstrap  # type: ignore  # noqa: F401
    except Exception:
        pass

from sqlalchemy.ext.asyncio import AsyncSession

try:
    config = import_module("database.config")
except ModuleNotFoundError:
    config = import_module("backend.database.config")

init_engines = getattr(config, "init_engines", None)

get_sessionmaker = (
    getattr(config, "get_sessionmaker", None)
    or getattr(config, "get_session_maker", None)
    or getattr(config, "get_async_sessionmaker", None)
)

_async_maker: Optional[object] = None


def _ensure_sessionmaker() -> None:
    global _async_maker

    if _async_maker is not None:
        return

    if init_engines is None:
        raise RuntimeError("backend.database.config.init_engines is not available")

    if get_sessionmaker is None:
        raise RuntimeError(
            "backend.database.config does not export a sessionmaker getter. "
            "Expected: get_sessionmaker / get_session_maker / get_async_sessionmaker"
        )

    init_engines()
    _async_maker = get_sessionmaker()
    if _async_maker is None:
        raise RuntimeError("Sessionmaker initialization returned None")


def async_session_maker():
    _ensure_sessionmaker()
    assert _async_maker is not None
    return _async_maker


async def get_async_session() -> AsyncIterator[AsyncSession]:
    """
    FastAPI-compatible dependency.
    """
    _ensure_sessionmaker()
    assert _async_maker is not None
    async with _async_maker() as session:  # type: ignore[operator]
        try:
            yield session
        finally:
            await session.close()


async def get_db() -> AsyncIterator[AsyncSession]:
    async for session in get_async_session():
        yield session


@asynccontextmanager
async def async_session() -> AsyncIterator[AsyncSession]:
    _ensure_sessionmaker()
    assert _async_maker is not None
    async with _async_maker() as session:  # type: ignore[operator]
        try:
            yield session
        finally:
            await session.close()


@asynccontextmanager
async def wrap_session_factory(session_factory: Callable[[], AsyncIterator[AsyncSession]]):
    """Wrap a session factory that may be either an async context manager
    or an async generator (FastAPI dependency style). Yields a session.
    """
    provider = session_factory()
    if hasattr(provider, "__aenter__"):
        async with provider as session:
            yield session
        return
    async for session in provider:
        yield session
        break


__all__ = [
    "async_session",
    "async_session_maker",
    "get_async_session",
    "get_db",
    "wrap_session_factory",
]
