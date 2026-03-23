from __future__ import annotations

from typing import Dict, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.config import settings
from backend.models.email_center import BotIdentity, EmailMailbox, EmailMailboxRole


BOT_MAILBOX_MAP = {
    "system_admin": "admin@gabanilogistics.com",
    "customer_service": "customers@gabanilogistics.com",
    "documents": "doccontrol@gabanilogistics.com",
    "finance": "finance@gabanilogistics.com",
    "platform_expenses": "accounts@gabanilogistics.com",
    "freight_broker": "freight@gabanilogistics.com",
    "operations_manager": "operations@gabanilogistics.com",
    "safety": "safety@gabanilogistics.com",
    "security": "security@gabanistore.com",
    "partner": "investments@gabanilogistics.com",
    "sales": "marketing@gabanilogistics.com",
    "notifications": settings.SMTP_FROM or "no-reply@gabanilogistics.com",
}

OUTBOUND_ONLY = {"notifications"}
HUMAN_DEFAULT = {"security", "finance", "platform_expenses", "system_admin"}


def _default_mode() -> str:
    mode = settings.EMAIL_DEFAULT_MODE or "BOT"
    return mode.upper()


async def ensure_bot_identities(db: AsyncSession) -> None:
    for bot_name, inbox in BOT_MAILBOX_MAP.items():
        default_mode = "HUMAN" if bot_name in HUMAN_DEFAULT else _default_mode()
        identity = await db.scalar(select(BotIdentity).where(BotIdentity.bot_name == bot_name))
        if identity is None:
            identity = BotIdentity(
                bot_name=bot_name,
                inbox_email=inbox,
                sender_email=inbox,
                allowed_actions=["reply", "draft", "classify"],
                default_mode=default_mode,
            )
            db.add(identity)

        mailbox = await db.scalar(select(EmailMailbox).where(EmailMailbox.email_address == inbox))
        if mailbox is None:
            mailbox = EmailMailbox(
                email_address=inbox,
                display_name=bot_name.replace("_", " ").title(),
                bot_name=bot_name,
                mode=default_mode,
                inbound_enabled=bot_name not in OUTBOUND_ONLY,
                outbound_enabled=True,
            )
            db.add(mailbox)
        await db.flush()

        for role_name in ("admin", "super_admin"):
            existing_role = await db.scalar(
                select(EmailMailboxRole).where(
                    EmailMailboxRole.mailbox_id == mailbox.id,
                    EmailMailboxRole.role_name == role_name,
                )
            )
            if existing_role is None:
                db.add(
                    EmailMailboxRole(
                        mailbox_id=mailbox.id,
                        role_name=role_name,
                        can_read=True,
                        can_send=True,
                        can_manage=True,
                    )
                )
    await db.commit()
