from __future__ import annotations

import asyncio
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from sqlalchemy import text

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.database.session import async_session
from backend.services.email_crypto import encrypt_credentials


@dataclass(frozen=True)
class MailboxSeed:
    email_address: str
    display_name: str
    imap_host: str
    smtp_host: str
    mode: str = "BOT"
    inbound_enabled: bool = True
    outbound_enabled: bool = True
    polling_enabled: bool = True
    auto_reply_enabled: bool = False
    package_scope: str = "SYSTEM"
    tenant_id: Optional[str] = "gts"
    bot_code: Optional[str] = None


MAILBOXES: list[MailboxSeed] = [
    MailboxSeed("accounts@gabanilogistics.com", "Accounts", "mail.gabanilogistics.com", "mail.gabanilogistics.com"),
    MailboxSeed("admin@gabanilogistics.com", "Admin", "mail.gabanilogistics.com", "mail.gabanilogistics.com", mode="HUMAN"),
    MailboxSeed("customers@gabanilogistics.com", "Customer Service", "mail.gabanilogistics.com", "mail.gabanilogistics.com", mode="HUMAN"),
    MailboxSeed("doccontrol@gabanilogistics.com", "Document Control", "mail.gabanilogistics.com", "mail.gabanilogistics.com"),
    MailboxSeed("finance@gabanilogistics.com", "Finance", "mail.gabanilogistics.com", "mail.gabanilogistics.com"),
    MailboxSeed("freight@gabanilogistics.com", "Freight", "mail.gabanilogistics.com", "mail.gabanilogistics.com"),
    MailboxSeed("intel@gabanilogistics.com", "Intelligence", "mail.gabanilogistics.com", "mail.gabanilogistics.com"),
    MailboxSeed("investments@gabanilogistics.com", "Investments", "mail.gabanilogistics.com", "mail.gabanilogistics.com"),
    MailboxSeed("marketing@gabanilogistics.com", "Marketing", "mail.gabanilogistics.com", "mail.gabanilogistics.com"),
    MailboxSeed(
        "no-reply@gabanilogistics.com",
        "No Reply",
        "mail.gabanilogistics.com",
        "mail.gabanilogistics.com",
        inbound_enabled=False,
        outbound_enabled=True,
        polling_enabled=False,
    ),
    MailboxSeed("operations@gabanilogistics.com", "Operations", "mail.gabanilogistics.com", "mail.gabanilogistics.com"),
    MailboxSeed("safety@gabanilogistics.com", "Safety", "mail.gabanilogistics.com", "mail.gabanilogistics.com"),
    MailboxSeed("sales@gabanilogistics.com", "Sales", "mail.gabanilogistics.com", "mail.gabanilogistics.com"),
    MailboxSeed("strategy@gabanilogistics.com", "Strategy", "mail.gabanilogistics.com", "mail.gabanilogistics.com"),
    MailboxSeed("aidispatcher@gabanistore.com", "AI Dispatcher", "mail.gabanistore.com", "mail.gabanistore.com"),
    MailboxSeed("driver@gabanistore.com", "Driver", "mail.gabanistore.com", "mail.gabanistore.com"),
    MailboxSeed("security@gabanistore.com", "Security", "mail.gabanistore.com", "mail.gabanistore.com"),
    MailboxSeed("support@gabanistore.com", "Support", "mail.gabanistore.com", "mail.gabanistore.com"),
]


def _shared_password() -> str:
    password = (
        os.getenv("EMAIL_MAILBOX_PASSWORD")
        or os.getenv("EMAIL_SHARED_PASSWORD")
        or os.getenv("EMAIL_PASSWORD")
    )
    if not password:
        raise SystemExit(
            "Missing shared mailbox password. Set EMAIL_MAILBOX_PASSWORD before running this script."
        )
    return password


FIND_EXISTING_MAILBOX_SQL = text(
    """
    SELECT
        m.id,
        m.tenant_id,
        COALESCE((SELECT COUNT(*) FROM email_messages em WHERE em.mailbox_id = m.id), 0) AS message_count,
        COALESCE((SELECT COUNT(*) FROM email_threads et WHERE et.mailbox_id = m.id), 0) AS thread_count
    FROM mailboxes m
    WHERE m.email_address = :email_address
    ORDER BY
        COALESCE((SELECT COUNT(*) FROM email_messages em WHERE em.mailbox_id = m.id), 0) DESC,
        COALESCE((SELECT COUNT(*) FROM email_threads et WHERE et.mailbox_id = m.id), 0) DESC,
        m.id ASC
    LIMIT 1
    """
)

INSERT_MAILBOX_SQL = text(
    """
    INSERT INTO mailboxes (
        tenant_id,
        owner_user_id,
        bot_code,
        email_address,
        display_name,
        mode,
        direction,
        imap_host,
        imap_port,
        imap_user,
        imap_ssl,
        smtp_host,
        smtp_port,
        smtp_user,
        smtp_ssl,
        use_tls,
        inbound_enabled,
        outbound_enabled,
        is_enabled,
        polling_enabled,
        auto_reply_enabled,
        package_scope
    ) VALUES (
        :tenant_id,
        NULL,
        :bot_code,
        :email_address,
        :display_name,
        :mode,
        'INBOUND_OUTBOUND',
        :imap_host,
        993,
        :imap_user,
        TRUE,
        :smtp_host,
        465,
        :smtp_user,
        TRUE,
        TRUE,
        :inbound_enabled,
        :outbound_enabled,
        TRUE,
        :polling_enabled,
        :auto_reply_enabled,
        :package_scope
    )
    RETURNING id
    """
)

UPDATE_MAILBOX_SQL = text(
    """
    UPDATE mailboxes
    SET
        tenant_id = :tenant_id,
        bot_code = :bot_code,
        display_name = :display_name,
        mode = :mode,
        direction = 'INBOUND_OUTBOUND',
        imap_host = :imap_host,
        imap_port = 993,
        imap_user = :imap_user,
        imap_ssl = TRUE,
        smtp_host = :smtp_host,
        smtp_port = 465,
        smtp_user = :smtp_user,
        smtp_ssl = TRUE,
        use_tls = TRUE,
        inbound_enabled = :inbound_enabled,
        outbound_enabled = :outbound_enabled,
        is_enabled = TRUE,
        polling_enabled = :polling_enabled,
        auto_reply_enabled = :auto_reply_enabled,
        package_scope = :package_scope,
        updated_at = NOW()
    WHERE id = :mailbox_id
    """
)

UPSERT_CREDENTIALS_SQL = text(
    """
    INSERT INTO mailbox_credentials (
        mailbox_id,
        tenant_id,
        credentials_ciphertext,
        key_version,
        rotated_at,
        last_error
    ) VALUES (
        :mailbox_id,
        :tenant_id,
        :credentials_ciphertext,
        :key_version,
        NOW(),
        NULL
    )
    ON CONFLICT (mailbox_id) DO UPDATE SET
        tenant_id = EXCLUDED.tenant_id,
        credentials_ciphertext = EXCLUDED.credentials_ciphertext,
        key_version = EXCLUDED.key_version,
        rotated_at = NOW(),
        last_error = NULL
    """
)

COUNT_MAILBOX_SQL = text("SELECT COUNT(*) FROM mailboxes")


async def main() -> None:
    password = _shared_password()
    encrypted, key_version = encrypt_credentials(password)

    async with async_session() as db:
        for seed in MAILBOXES:
            params = {
                "tenant_id": seed.tenant_id,
                "bot_code": seed.bot_code,
                "email_address": seed.email_address.lower(),
                "display_name": seed.display_name,
                "mode": seed.mode,
                "imap_host": seed.imap_host,
                "imap_user": seed.email_address.lower(),
                "smtp_host": seed.smtp_host,
                "smtp_user": seed.email_address.lower(),
                "inbound_enabled": seed.inbound_enabled,
                "outbound_enabled": seed.outbound_enabled,
                "polling_enabled": seed.polling_enabled,
                "auto_reply_enabled": seed.auto_reply_enabled,
                "package_scope": seed.package_scope,
            }
            existing = (await db.execute(FIND_EXISTING_MAILBOX_SQL, {"email_address": seed.email_address.lower()})).first()
            if existing:
                mailbox_id = int(existing.id)
                params["tenant_id"] = existing.tenant_id or seed.tenant_id
                await db.execute(UPDATE_MAILBOX_SQL, {**params, "mailbox_id": mailbox_id})
            else:
                mailbox_id = await db.scalar(INSERT_MAILBOX_SQL, params)
            await db.execute(
                UPSERT_CREDENTIALS_SQL,
                {
                    "mailbox_id": int(mailbox_id),
                    "tenant_id": seed.tenant_id,
                    "credentials_ciphertext": encrypted,
                    "key_version": key_version,
                },
            )

        await db.commit()
        total = await db.scalar(COUNT_MAILBOX_SQL)

    print({"ok": True, "seeded": len(MAILBOXES), "total_mailboxes": int(total or 0)})


if __name__ == "__main__":
    asyncio.run(main())
