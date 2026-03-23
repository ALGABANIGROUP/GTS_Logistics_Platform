from __future__ import annotations

import logging
import os
from datetime import datetime, timezone
from typing import Dict, Optional, Tuple

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.models.email_center import Mailbox, MailboxCredentials
from backend.services.email_crypto import encrypt_credentials
from backend.services.email_config import (
    BOT_CODE_ALIASES,
    BOT_EMAIL_MAP,
    EMAIL_DISABLED_BOTS,
    NO_REPLY_EMAIL,
    SYSTEM_ADMIN_EMAIL,
)

logger = logging.getLogger("email_provisioner")


def _normalize_bot_code(value: Optional[str]) -> str:
    if not value:
        return ""
    return BOT_CODE_ALIASES.get(value, value)


def _resolve_shared_password() -> Optional[str]:
    return (
        os.getenv("EMAIL_SHARED_PASSWORD")
        or os.getenv("EMAIL_PASSWORD")
        or os.getenv("SMTP_PASSWORD")
        or os.getenv("IMAP_PASSWORD")
    )


def _resolve_hosts() -> Tuple[Optional[str], Optional[str]]:
    imap_host = os.getenv("EMAIL_IMAP_HOST") or os.getenv("IMAP_HOST")
    smtp_host = os.getenv("EMAIL_SMTP_HOST") or os.getenv("SMTP_HOST")
    return imap_host, smtp_host


def _resolve_ports() -> Tuple[int, int]:
    imap_port = int(os.getenv("EMAIL_IMAP_PORT") or 993)
    smtp_port = int(os.getenv("EMAIL_SMTP_PORT") or 465)
    return imap_port, smtp_port


async def _upsert_mailbox(
    db: AsyncSession,
    *,
    bot_code: Optional[str],
    email_address: str,
    imap_host: Optional[str],
    smtp_host: Optional[str],
    imap_port: int,
    smtp_port: int,
    inbound_enabled: bool,
    outbound_enabled: bool,
    polling_enabled: bool,
    direction: str,
    mode: str,
    display_name: Optional[str],
    shared_password: Optional[str],
    allow_credentials: bool,
) -> Tuple[Mailbox, bool]:
    normalized_bot = _normalize_bot_code(bot_code)
    res = await db.execute(select(Mailbox).where(Mailbox.email_address == email_address))
    mailbox = res.scalar_one_or_none()
    created = False
    if mailbox is None:
        mailbox = Mailbox(
            bot_code=normalized_bot or None,
            email_address=email_address,
            display_name=display_name,
            mode=mode,
            direction=direction,
            imap_host=imap_host if inbound_enabled else None,
            imap_port=imap_port if inbound_enabled else None,
            imap_user=email_address if inbound_enabled else None,
            imap_ssl=True if inbound_enabled else None,
            smtp_host=smtp_host,
            smtp_port=smtp_port,
            smtp_user=email_address,
            smtp_ssl=True,
            use_tls=True,
            inbound_enabled=inbound_enabled,
            outbound_enabled=outbound_enabled,
            is_enabled=True,
            polling_enabled=polling_enabled,
            auto_reply_enabled=False,
            package_scope="SYSTEM",
            created_at=datetime.now(timezone.utc),
        )
        db.add(mailbox)
        await db.commit()
        await db.refresh(mailbox)
        created = True
    else:
        mailbox.bot_code = normalized_bot or None
        mailbox.display_name = display_name or mailbox.display_name
        mailbox.mode = mode
        mailbox.direction = direction
        mailbox.imap_host = imap_host if inbound_enabled else None
        mailbox.imap_port = imap_port if inbound_enabled else None
        mailbox.imap_user = email_address if inbound_enabled else None
        mailbox.imap_ssl = True if inbound_enabled else None
        mailbox.smtp_host = smtp_host
        mailbox.smtp_port = smtp_port
        mailbox.smtp_user = email_address
        mailbox.smtp_ssl = True
        mailbox.use_tls = True
        mailbox.inbound_enabled = inbound_enabled
        mailbox.outbound_enabled = outbound_enabled
        mailbox.is_enabled = True
        mailbox.polling_enabled = polling_enabled
        mailbox.auto_reply_enabled = False
        mailbox.package_scope = "SYSTEM"
        mailbox.updated_at = datetime.now(timezone.utc)
        await db.commit()

    if shared_password and allow_credentials:
        encrypted, key_version = encrypt_credentials(shared_password)
        creds = await db.get(MailboxCredentials, mailbox.id)
        if creds is None:
            creds = MailboxCredentials(
                mailbox_id=mailbox.id,
                credentials_ciphertext=encrypted,
                key_version=key_version,
                rotated_at=datetime.now(timezone.utc),
            )
            db.add(creds)
        else:
            creds.credentials_ciphertext = encrypted
            creds.key_version = key_version
            creds.rotated_at = datetime.now(timezone.utc)
        await db.commit()

    return mailbox, created


async def ensure_system_mailboxes(db: AsyncSession) -> Dict[str, int]:
    shared_password = _resolve_shared_password()
    imap_host, smtp_host = _resolve_hosts()
    imap_port, smtp_port = _resolve_ports()

    logger.info("[email] Shared password configured: %s", "yes" if shared_password else "no")

    created = 0
    updated = 0
    disabled = 0

    desired = {**BOT_EMAIL_MAP, "system_admin": SYSTEM_ADMIN_EMAIL}

    for bot_key, email_address in desired.items():
        canonical_bot = _normalize_bot_code(bot_key)
        if canonical_bot in EMAIL_DISABLED_BOTS:
            continue
        mailbox, was_created = await _upsert_mailbox(
            db,
            bot_code=canonical_bot,
            email_address=email_address.lower(),
            imap_host=imap_host,
            smtp_host=smtp_host,
            imap_port=imap_port,
            smtp_port=smtp_port,
            inbound_enabled=True,
            outbound_enabled=True,
            polling_enabled=True,
            direction="INBOUND_OUTBOUND",
            mode="BOT" if canonical_bot not in {"system_admin"} else "HUMAN",
            display_name=canonical_bot.replace("_", " ").title() if canonical_bot else None,
            shared_password=shared_password,
            allow_credentials=True,
        )
        if was_created:
            created += 1
        else:
            updated += 1

    await _upsert_mailbox(
        db,
        bot_code=None,
        email_address=NO_REPLY_EMAIL.lower(),
        imap_host=None,
        smtp_host=smtp_host,
        imap_port=imap_port,
        smtp_port=smtp_port,
        inbound_enabled=False,
        outbound_enabled=True,
        polling_enabled=False,
        direction="OUTBOUND_ONLY",
        mode="HUMAN",
        display_name="No Reply",
        shared_password=shared_password,
        allow_credentials=False,
    )

    for disabled_bot in EMAIL_DISABLED_BOTS:
        res = await db.execute(select(Mailbox).where(Mailbox.bot_code == disabled_bot))
        for mailbox in res.scalars().all():
            mailbox.inbound_enabled = False
            mailbox.outbound_enabled = False
            mailbox.polling_enabled = False
            mailbox.is_enabled = False
            mailbox.updated_at = datetime.now(timezone.utc)
            disabled += 1
    await db.commit()

    return {"created": created, "updated": updated, "disabled": disabled}

