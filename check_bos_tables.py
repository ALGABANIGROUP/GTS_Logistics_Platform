import os
from sqlalchemy import create_engine, text


def pick_url() -> str:
    # Prefer env vars first (common in this repo)
    for k in ("DATABASE_URL", "SYNC_DATABASE_URL", "SQLALCHEMY_DATABASE_URL"):
        v = os.getenv(k)
        if v:
            return v
    raise RuntimeError(
        "No DB url found. Set DATABASE_URL (sync) before running this script."
    )


url = pick_url()
engine = create_engine(url)

with engine.connect() as conn:
    rows = conn.execute(
        text(
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
              AND table_name IN ('bot_registry', 'bot_runs', 'human_commands')
            ORDER BY table_name
            """
        )
    ).fetchall()

print(rows)
