from __future__ import annotations

from typing import Dict, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.config import settings
from backend.models.email_center import BotIdentity, EmailMailbox, EmailMailboxRole


BOT_MAILBOX_MAP = {
    "operations": "operations@gabanilogistics.com",
    "operations_manager": "operations@gabanilogistics.com",
    "operations_manager_bot": "operations@gabanilogistics.com",
    "general_manager": "operations@gabanilogistics.com",
    "legal": "operations@gabanilogistics.com",
    "legal_bot": "operations@gabanilogistics.com",
    "legal_consultant": "operations@gabanilogistics.com",
    "system_admin": "admin@gabanilogistics.com",
    "system_bot": settings.SMTP_FROM or "no-reply@gabanilogistics.com",
    "system_manager_bot": settings.SMTP_FROM or "no-reply@gabanilogistics.com",
    "customer_service": "customers@gabanilogistics.com",
    "service": "support@gabanilogistics.com",
    "documents": "doccontrol@gabanilogistics.com",
    "documents_manager": "doccontrol@gabanilogistics.com",
    "finance": "finance@gabanilogistics.com",
    "finance_bot": "finance@gabanilogistics.com",
    "platform_expenses": "accounts@gabanilogistics.com",
    "accounts": "accounts@gabanilogistics.com",
    "freight_broker": "freight@gabanilogistics.com",
    "freight_bot": "freight@gabanilogistics.com",
    "freight": "freight@gabanilogistics.com",
    "mapleload": "freight@gabanilogistics.com",
    "mapleload_bot": "freight@gabanilogistics.com",
    "safety": "safety@gabanilogistics.com",
    "safety_manager": "safety@gabanilogistics.com",
    "safety_manager_bot": "safety@gabanilogistics.com",
    "safety_bot": "safety@gabanilogistics.com",
    "security": "security@gabanilogistics.com",
    "security_manager": "security@gabanilogistics.com",
    "security_bot": "security@gabanilogistics.com",
    "partner": "investments@gabanilogistics.com",
    "partner_manager": "investments@gabanilogistics.com",
    "partner_bot": "investments@gabanilogistics.com",
    "information_coordinator": "intel@gabanilogistics.com",
    "intel": "intel@gabanilogistics.com",
    "intelligence_bot": "strategy@gabanilogistics.com",
    "strategy_advisor": "strategy@gabanilogistics.com",
    "marketing": "marketing@gabanilogistics.com",
    "marketing_manager": "marketing@gabanilogistics.com",
    "sales": "sales@gabanilogistics.com",
    "sales_bot": "sales@gabanilogistics.com",
    "ai_dispatcher": "aidispatcher@gabanilogistics.com",
    "aidispatcher": "aidispatcher@gabanilogistics.com",
    "dispatcher": "aidispatcher@gabanilogistics.com",
    "maintenance_dev": settings.SMTP_FROM or "no-reply@gabanilogistics.com",
    "trainer": settings.SMTP_FROM or "no-reply@gabanilogistics.com",
    "training_bot": settings.SMTP_FROM or "no-reply@gabanilogistics.com",
    "trainer_bot": settings.SMTP_FROM or "no-reply@gabanilogistics.com",
    "notifications": settings.SMTP_FROM or "no-reply@gabanilogistics.com",
}

OUTBOUND_ONLY = {"notifications"}
HUMAN_DEFAULT = {
    "security",
    "security_manager",
    "security_bot",
    "finance",
    "finance_bot",
    "platform_expenses",
    "accounts",
    "system_admin",
}


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
