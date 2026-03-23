# backend/db_ping.py
from __future__ import annotations

import asyncio
import os
from typing import Optional, cast, Tuple, Dict
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy import text


def _get_db_url() -> str:
    """Return a non-empty DB URL or raise a clear error."""
    raw_url: Optional[str] = (
        os.getenv("ASYNC_DATABASE_URL") or os.getenv("DATABASE_URL")
    )
    if not raw_url:
        # Clear runtime error instead of passing None to create_async_engine
        raise RuntimeError(
            "DATABASE_URL (or ASYNC_DATABASE_URL) is not set for db_ping.py"
        )
    # At this point mypy/pylance know it's str, but we cast to satisfy the checker
    return cast(str, raw_url)

def _normalize_async_db_url(url: str) -> Tuple[str, Dict[str, object]]:
    """
    Ensure asyncpg-compatible URL and strip sslmode for asyncpg.
    Returns (clean_url, connect_args).
    """
    parsed = urlparse(url)
    scheme = parsed.scheme
    connect_args: Dict[str, object] = {}

    if scheme in {"postgresql", "postgres"}:
        scheme = "postgresql+asyncpg"
    elif scheme.startswith("postgresql+psycopg"):
        scheme = "postgresql+asyncpg"

    q = dict(parse_qsl(parsed.query, keep_blank_values=True))
    sslmode = q.pop("sslmode", None)
    ssl_param = q.get("ssl")
    if sslmode:
        connect_args["ssl"] = True
    if ssl_param in {"1", "true", "True", "require"}:
        connect_args["ssl"] = True

    clean_url = urlunparse(parsed._replace(scheme=scheme, query=urlencode(q)))
    return clean_url, connect_args


DATABASE_URL: str = _get_db_url()
ASYNC_DATABASE_URL, ASYNC_CONNECT_ARGS = _normalize_async_db_url(DATABASE_URL)
engine: AsyncEngine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=False,
    future=True,
    connect_args=ASYNC_CONNECT_ARGS,
)


async def ping_db() -> bool:
    """Simple SELECT 1 ping against the database."""
    try:
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT 1"))
            row = result.scalar_one_or_none()
            ok = row == 1
            print(f"[db_ping] DB ping result: {ok}")
            return ok
    except Exception as e:
        print(f"[db_ping] DB ping failed: {e}")
        return False
    finally:
        await engine.dispose()


if __name__ == "__main__":
    # For quick manual check:  python -m backend.db_ping   (from project root)
    asyncio.run(ping_db())
