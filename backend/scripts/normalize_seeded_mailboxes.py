from __future__ import annotations

import asyncio
import sys
from pathlib import Path

from sqlalchemy import text

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.database.session import async_session


TARGET_EMAILS = [
    "accounts@gabanilogistics.com",
    "admin@gabanilogistics.com",
    "customers@gabanilogistics.com",
    "doccontrol@gabanilogistics.com",
    "finance@gabanilogistics.com",
    "freight@gabanilogistics.com",
    "intel@gabanilogistics.com",
    "investments@gabanilogistics.com",
    "marketing@gabanilogistics.com",
    "no-reply@gabanilogistics.com",
    "operations@gabanilogistics.com",
    "safety@gabanilogistics.com",
    "sales@gabanilogistics.com",
    "strategy@gabanilogistics.com",
    "aidispatcher@gabanistore.com",
]


FIND_ROWS_SQL = text(
    """
    SELECT
        m.id,
        m.email_address,
        m.tenant_id,
        COALESCE((SELECT COUNT(*) FROM email_messages em WHERE em.mailbox_id = m.id), 0) AS message_count,
        COALESCE((SELECT COUNT(*) FROM email_threads et WHERE et.mailbox_id = m.id), 0) AS thread_count
    FROM mailboxes m
    WHERE m.email_address = :email_address
    ORDER BY message_count DESC, thread_count DESC, m.id ASC
    """
)

DELETE_CREDENTIALS_SQL = text("DELETE FROM mailbox_credentials WHERE mailbox_id = :mailbox_id")
DELETE_MAILBOX_SQL = text("DELETE FROM mailboxes WHERE id = :mailbox_id")


async def main() -> None:
    deleted = 0
    kept = 0
    async with async_session() as db:
        for email_address in TARGET_EMAILS:
            rows = (await db.execute(FIND_ROWS_SQL, {"email_address": email_address})).fetchall()
            if len(rows) <= 1:
                if rows:
                    kept += 1
                continue

            keeper = rows[0]
            kept += 1
            for duplicate in rows[1:]:
                if int(duplicate.message_count or 0) > 0 or int(duplicate.thread_count or 0) > 0:
                    continue
                await db.execute(DELETE_CREDENTIALS_SQL, {"mailbox_id": int(duplicate.id)})
                await db.execute(DELETE_MAILBOX_SQL, {"mailbox_id": int(duplicate.id)})
                deleted += 1
        await db.commit()

    print({"ok": True, "kept": kept, "deleted_empty_duplicates": deleted})


if __name__ == "__main__":
    asyncio.run(main())
