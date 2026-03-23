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
    """
    CREATE TABLE IF NOT EXISTS bot_mailbox_rules (
        id SERIAL PRIMARY KEY,
        mailbox_id INTEGER NOT NULL REFERENCES mailboxes(id) ON DELETE CASCADE,
        bot_key VARCHAR(100),
        condition_field VARCHAR(50) NOT NULL,
        condition_operator VARCHAR(20) NOT NULL,
        condition_value JSONB NOT NULL,
        condition_match_all BOOLEAN NOT NULL DEFAULT FALSE,
        action_type VARCHAR(50) NOT NULL,
        action_config JSONB,
        priority INTEGER NOT NULL DEFAULT 0,
        is_active BOOLEAN NOT NULL DEFAULT TRUE,
        times_matched INTEGER NOT NULL DEFAULT 0,
        last_matched_at TIMESTAMPTZ,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        created_by INTEGER REFERENCES users(id) ON DELETE SET NULL
    )
    """,
    "CREATE INDEX IF NOT EXISTS ix_bot_mailbox_rules_mailbox_id ON bot_mailbox_rules (mailbox_id)",
    "CREATE INDEX IF NOT EXISTS ix_bot_mailbox_rules_bot_key ON bot_mailbox_rules (bot_key)",
    "CREATE INDEX IF NOT EXISTS ix_bot_mailbox_rules_priority ON bot_mailbox_rules (priority)",
    "CREATE INDEX IF NOT EXISTS ix_bot_mailbox_rules_is_active ON bot_mailbox_rules (is_active)",
    "ALTER TABLE email_messages ADD COLUMN IF NOT EXISTS analyzed_at TIMESTAMPTZ",
    "ALTER TABLE email_messages ADD COLUMN IF NOT EXISTS analysis_result JSONB",
    "ALTER TABLE email_messages ADD COLUMN IF NOT EXISTS applied_rule_id INTEGER",
    "ALTER TABLE email_messages ADD COLUMN IF NOT EXISTS processed_by_bot VARCHAR(100)",
    "ALTER TABLE email_messages ADD COLUMN IF NOT EXISTS processed_at TIMESTAMPTZ",
    """
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1
            FROM pg_constraint
            WHERE conname = 'fk_email_messages_applied_rule_id_bot_mailbox_rules'
        ) THEN
            ALTER TABLE email_messages
            ADD CONSTRAINT fk_email_messages_applied_rule_id_bot_mailbox_rules
            FOREIGN KEY (applied_rule_id) REFERENCES bot_mailbox_rules(id) ON DELETE SET NULL;
        END IF;
    END $$;
    """,
    "CREATE INDEX IF NOT EXISTS ix_email_messages_applied_rule_id ON email_messages (applied_rule_id)",
    "CREATE INDEX IF NOT EXISTS ix_email_messages_processed_by_bot ON email_messages (processed_by_bot)",
]


async def main() -> None:
    async with async_session() as db:
        for sql in SQL_STATEMENTS:
            await db.execute(text(sql))
        await db.commit()
    print({"ok": True, "statements": len(SQL_STATEMENTS)})


if __name__ == "__main__":
    asyncio.run(main())
