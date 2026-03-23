import os, ssl, asyncio, asyncpg
from urllib.parse import urlparse, unquote

def parse_pg_dsn(dsn: str) -> dict:
    url = urlparse(dsn)
    if url.scheme not in ("postgresql", "postgresql+asyncpg"):
        raise RuntimeError(f"Unsupported scheme: {url.scheme}")
    return {
        "user": unquote(url.username or ""),
        "password": unquote(url.password or ""),
        "host": url.hostname or "localhost",
        "port": url.port or 5432,
        "database": (url.path or "/").lstrip("/"),
    }

CREATE_SQL = """
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    file_url TEXT NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    notify_before_days INTEGER NOT NULL DEFAULT 7,
    notified_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_documents_expires_at ON documents(expires_at);
"""

async def main():
    dsn = os.getenv("ASYNC_DATABASE_URL") or os.getenv("DATABASE_URL")
    if not dsn:
        raise RuntimeError("Set ASYNC_DATABASE_URL or DATABASE_URL")
    base = dsn.split("?", 1)[0]
    cfg = parse_pg_dsn(base)
    ctx = ssl.create_default_context()
    conn = await asyncpg.connect(ssl=ctx, **cfg)
    await conn.execute(CREATE_SQL)
    await conn.close()
    print("OK")

if __name__ == "__main__":
    asyncio.run(main())
