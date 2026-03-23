import asyncio
import os
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import asyncpg

from backend.security.passwords import hash_password


def _normalize_dsn(raw: str) -> str:
    dsn = (raw or "").strip()
    if not dsn:
        raise RuntimeError(
            "Set SYNC_DATABASE_URL, DATABASE_URL, or ASYNC_DATABASE_URL before running this tool."
        )
    if dsn.startswith("postgresql+asyncpg://"):
        dsn = dsn.replace("postgresql+asyncpg://", "postgresql://", 1)
    if dsn.startswith("postgresql+psycopg://"):
        dsn = dsn.replace("postgresql+psycopg://", "postgresql://", 1)

    parts = urlsplit(dsn)
    query = dict(parse_qsl(parts.query, keep_blank_values=True))
    if "ssl" in query:
        query.pop("ssl", None)
        query.setdefault("sslmode", "require")
    elif parts.scheme.startswith("postgresql") and "sslmode" not in query:
        query["sslmode"] = "require"
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment))


DB_DSN = _normalize_dsn(
    os.getenv("SYNC_DATABASE_URL")
    or os.getenv("DATABASE_URL")
    or os.getenv("ASYNC_DATABASE_URL")
    or ""
)

ADMIN_EMAIL = os.getenv("BOOTSTRAP_ADMIN_EMAIL", "").strip().lower()
ADMIN_PASSWORD = os.getenv("BOOTSTRAP_ADMIN_PASSWORD", "")
ADMIN_NAME = os.getenv("BOOTSTRAP_ADMIN_NAME", "Platform Administrator")
ADMIN_ROLE = os.getenv("BOOTSTRAP_ADMIN_ROLE", "super_admin")
FORCE_RESET = os.getenv("BOOTSTRAP_ADMIN_FORCE_RESET", "").lower() in ("1", "true", "yes")


async def main():
    if not ADMIN_EMAIL or not ADMIN_PASSWORD:
        raise RuntimeError(
            "Set BOOTSTRAP_ADMIN_EMAIL and BOOTSTRAP_ADMIN_PASSWORD before running this tool."
        )

    conn = await asyncpg.connect(DB_DSN)

    try:
        # Inspect columns
        cols_rows = await conn.fetch(
            "SELECT column_name FROM information_schema.columns WHERE table_name = 'users';"
        )
        colnames = {r["column_name"] for r in cols_rows}
        print("[INFO] users table columns:", ", ".join(sorted(colnames)))

        # Check if user exists
        row = await conn.fetchrow(
            "SELECT id FROM users WHERE email = $1",
            ADMIN_EMAIL,
        )

        if row:
            if not FORCE_RESET:
                print(f"[INFO] User with email {ADMIN_EMAIL} already exists (id={row['id']})")
                print("[INFO] Set GTS_RESET_ADMIN_PASSWORD=1 to reset the password.")
                return

            hashed_password = hash_password(ADMIN_PASSWORD)
            await conn.execute(
                "UPDATE users SET hashed_password = $1 WHERE email = $2",
                hashed_password,
                ADMIN_EMAIL,
            )
            print(f"[OK] Updated admin password for {ADMIN_EMAIL}")
            return

        hashed_password = hash_password(ADMIN_PASSWORD)

        columns = []
        values = []

        if "email" not in colnames or "hashed_password" not in colnames:
            raise RuntimeError(
                "users table must have at least 'email' and 'hashed_password' columns"
            )

        columns.append("email")
        values.append(ADMIN_EMAIL)

        columns.append("hashed_password")
        values.append(hashed_password)

        if "full_name" in colnames:
            columns.append("full_name")
            values.append(ADMIN_NAME)

        if "role" in colnames:
            columns.append("role")
            values.append(ADMIN_ROLE)

        if "username" in colnames:
            columns.append("username")
            values.append("admin")

        if "is_active" in colnames:
            columns.append("is_active")
            values.append(1)  # integer, because column is integer

        placeholders = ", ".join(f"${i}" for i in range(1, len(values) + 1))
        columns_sql = ", ".join(columns)

        insert_sql = f"""
        INSERT INTO users ({columns_sql})
        VALUES ({placeholders})
        RETURNING id;
        """

        new_id = await conn.fetchval(insert_sql, *values)

        print("[OK] Created admin user:")
        print(f"  ID:       {new_id}")
        print(f"  Email:    {ADMIN_EMAIL}")
        if "role" in colnames:
            print(f"  Role:     {ADMIN_ROLE}")
        print("  Password: [redacted - supplied from environment]")

    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
