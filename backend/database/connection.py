from __future__ import annotations

import os
import re
from typing import AsyncGenerator, Optional
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse

from dotenv import load_dotenv
from sqlalchemy import create_engine, Engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# ------------------------------------------------------------
# Load .env early (respect process env first; default override=False)
# ------------------------------------------------------------
try:
    load_dotenv()  # do not force override
except Exception:
    pass

MASK = "****"

# ============================================================
# Helpers (masking + DSN normalization)
# ============================================================

def _mask_pw(dsn: str) -> str:
    """Mask password in DSN for logging."""
    try:
        return re.sub(r"://([^:]+):([^@]+)@", r"://\1:****@", dsn)
    except Exception:
        return dsn

def _valid_sslmode(mode: str) -> str:
    """Return a valid asyncpg sslmode."""
    mode = (mode or "").lower().strip()
    if mode in {"disable", "allow", "prefer", "require", "verify-ca", "verify-full"}:
        return mode
    if mode in {"required"}:
        return "require"
    # default safest
    return "require"

def _normalize_asyncpg_ssl(url: str) -> str:
    """
    Normalize any DSN for asyncpg:
    - Convert legacy 'ssl=true' → 'sslmode=require'
    - Ensure 'sslmode' is one of asyncpg's accepted values
    - Apply PGSSLMODE when not present
    """
    if not url:
        return url
    u = urlparse(url)
    q = dict(parse_qsl(u.query, keep_blank_values=True))
    is_asyncpg = url.startswith("postgresql+asyncpg")

    if is_asyncpg:
        if "ssl" in q:
            if str(q.get("ssl", "")).lower() in {"1", "true", "yes"}:
                q["sslmode"] = "require"
            q.pop("ssl", None)

        if "sslmode" in q:
            q["sslmode"] = _valid_sslmode(q.get("sslmode"))

        if "sslmode" not in q:
            pgsslmode = os.getenv("PGSSLMODE", "").strip().lower()
            if pgsslmode:
                q["sslmode"] = _valid_sslmode(pgsslmode)

        if "sslmode" not in q:
            q["sslmode"] = "require"

        return urlunparse(u._replace(query=urlencode(q)))

    if "ssl=true" in u.query.lower():
        q["sslmode"] = "require"
        q.pop("ssl", None)
        return urlunparse(u._replace(query=urlencode(q)))
    return url

def _strip_sslmode_for_asyncpg(url: str) -> tuple[str, dict]:
    """
    asyncpg doesn't accept sslmode=... in query params.
    If sslmode exists, remove it and return connect_args with ssl=True.
    """
    parsed = urlparse(url)
    q = dict(parse_qsl(parsed.query, keep_blank_values=True))

    connect_args: dict = {}
    sslmode = q.pop("sslmode", None)
    ssl_param = q.get("ssl")

    if sslmode:
        connect_args["ssl"] = True

    if str(ssl_param) in {"1", "true", "True", "require"}:
        connect_args["ssl"] = True

    new_query = urlencode(q)
    clean_url = urlunparse(parsed._replace(query=new_query))
    return clean_url, connect_args

def _sanitize_env_dsns() -> None:
    """
    Sanitize environment DSNs very early, so any module that reads them later
    receives normalized values.
    """
    raw_async = os.getenv("ASYNC_DATABASE_URL", "")
    raw_sync = os.getenv("DATABASE_URL", "")

    if not raw_async and raw_sync:
        if raw_sync.startswith("postgres://"):
            raw_sync = raw_sync.replace("postgres://", "postgresql://", 1)
        if raw_sync.startswith("postgresql://"):
            os.environ["ASYNC_DATABASE_URL"] = raw_sync.replace(
                "postgresql://", "postgresql+asyncpg://", 1
            )
        raw_async = os.getenv("ASYNC_DATABASE_URL", "")

    if raw_async:
        fixed_async = _normalize_asyncpg_ssl(raw_async)
        if fixed_async != raw_async:
            os.environ["ASYNC_DATABASE_URL"] = fixed_async

    if raw_sync and "ssl=true" in raw_sync.lower():
        os.environ["DATABASE_URL"] = raw_sync.replace("ssl=true", "sslmode=require")

    # Debug prints (masked)
    if os.getenv("APP_ENV", "development") != "production":
        try:
            print(f"[db.sanitize] ASYNC_DATABASE_URL -> {_mask_pw(os.environ.get('ASYNC_DATABASE_URL',''))}")
            print(f"[db.sanitize] DATABASE_URL     -> {_mask_pw(os.environ.get('DATABASE_URL',''))}")
        except Exception:
            pass

# Run sanitation at import-time
_sanitize_env_dsns()

# ============================================================
# DSN Loaders
# ============================================================

def _load_async_dsn_from_env() -> str:
    """
    Priority:
      1) ASYNC_DATABASE_URL
      2) DATABASE_URL
      3) POSTGRES_DSN
      4) SQLALCHEMY_DATABASE_URI
      5) local sqlite (dev)
    """
    for key in ("ASYNC_DATABASE_URL", "DATABASE_URL", "POSTGRES_DSN", "SQLALCHEMY_DATABASE_URI"):
        val = os.getenv(key)
        if val and val.strip():
            return val.strip()
    return "sqlite+aiosqlite:///./gts.db"

def _load_sync_dsn_from_env() -> Optional[str]:
    return os.getenv("DATABASE_URL", None)

# ============================================================
# Engine Factories (public API)
# ============================================================

def get_async_engine_from_env(env_key: str = "ASYNC_DATABASE_URL"):
    """
    Public factory used by routes (e.g., finance_routes).
    Ensures asyncpg DSN is normalized (sslmode=require).
    """
    raw = os.getenv(env_key, "") or _load_async_dsn_from_env()
    if raw.startswith("postgres://"):
        raw = raw.replace("postgres://", "postgresql://", 1)
    if raw.startswith("postgresql://"):
        raw = raw.replace("postgresql://", "postgresql+asyncpg://", 1)
    url = _normalize_asyncpg_ssl(raw)
    connect_args: dict = {}
    if url.startswith("postgresql+asyncpg"):
        url, connect_args = _strip_sslmode_for_asyncpg(url)
    print(f"[db] DSN -> {_mask_pw(url)}")
    return create_async_engine(
        url,
        echo=False,
        pool_pre_ping=True,
        future=True,
        connect_args=connect_args,
    )

def get_sync_engine_from_env(env_key: str = "DATABASE_URL") -> Engine:
    """
    Sync engine (used by Alembic / occasional sync ops).
    """
    raw = os.getenv(env_key, "") or _load_sync_dsn_from_env()
    if not raw:
        raise RuntimeError("DATABASE_URL not set for sync engine.")
    url = _normalize_asyncpg_ssl(raw)  # harmless for psycopg
    print(f"[db] DSN -> {_mask_pw(url)}")
    return create_engine(url, echo=False, pool_pre_ping=True, future=True)

# ============================================================
# Global async engine/session + FastAPI dependency
# ============================================================

# Build a shared async engine/session for general app usage
_async_engine = get_async_engine_from_env()
SessionLocal = async_sessionmaker(bind=_async_engine, class_=AsyncSession, expire_on_commit=False)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency (async).
    NOTE: Routes that need a dedicated session/engine can still create their own
    sessionmaker using get_async_engine_from_env(), but this shared one is fine
    for most cases.
    """
    async with SessionLocal() as session:
        yield session

# ============================================================
# Optional: simple debug helper (imported by a _debug router)
# ============================================================

def current_dsns() -> dict:
    return {
        "ASYNC_DATABASE_URL": _mask_pw(os.getenv("ASYNC_DATABASE_URL", "")),
        "DATABASE_URL": _mask_pw(os.getenv("DATABASE_URL", "")),
    }

__all__ = [
    "get_db",
    "get_async_engine_from_env",
    "get_sync_engine_from_env",
    "current_dsns",
    "SessionLocal",
]
