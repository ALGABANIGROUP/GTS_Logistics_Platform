from __future__ import annotations

import asyncio
import sys
from pathlib import Path

from sqlalchemy import text

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.database.session import async_session


SQL_STATEMENTS = [
    "ALTER TABLE mailboxes ADD COLUMN IF NOT EXISTS assigned_bot_key VARCHAR(100)",
    "ALTER TABLE mailboxes ADD COLUMN IF NOT EXISTS bot_config JSONB",
    "CREATE INDEX IF NOT EXISTS ix_mailboxes_assigned_bot_key ON mailboxes (assigned_bot_key)",
]


async def main() -> None:
    async with async_session() as db:
        for sql in SQL_STATEMENTS:
            await db.execute(text(sql))
        await db.commit()
    print({"ok": True, "statements": len(SQL_STATEMENTS)})


if __name__ == "__main__":
    asyncio.run(main())
