from __future__ import annotations

import logging
from typing import Any, Iterable

from backend.config import settings
from backend.utils.email_utils import get_bot_email, send_admin_notification, send_email

logger = logging.getLogger(__name__)


def _normalize_optional_recipients(value: Iterable[str] | str | None) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        candidate = value.strip()
        return [candidate] if candidate else []
    return [item.strip() for item in value if isinstance(item, str) and item.strip()]


async def dispatch_email(
    *,
    bot_name: str,
    to_email: str | list[str],
    subject: str,
    body: str,
    html: bool = True,
    plain_text: str | None = None,
    cc: list[str] | None = None,
    bcc: list[str] | None = None,
    audit_context: dict[str, Any] | None = None,
) -> bool:
    """
    Dispatch an email through the bot's approved sender mailbox.

    CC/BCC are accepted for orchestration metadata even though the current
    SMTP helper sends only to the primary recipient list.
    """
    recipients = _normalize_optional_recipients(to_email)
    if not recipients:
        logger.warning("[email_dispatcher] skipped send for %s: no recipients", bot_name)
        return False

    success = send_email(
        subject=subject,
        body=body,
        to=recipients,
        html=html,
        plain_text=plain_text,
        from_email=get_bot_email(bot_name),
    )

    if success:
        logger.info(
            "[email_dispatcher] sent subject=%s via=%s to=%s cc=%s bcc=%s audit=%s",
            subject,
            bot_name,
            recipients,
            _normalize_optional_recipients(cc),
            _normalize_optional_recipients(bcc),
            audit_context or {},
        )
        return True

    admin_target = settings.ADMIN_EMAIL or settings.SMTP_FROM or settings.SMTP_USER
    if admin_target:
        send_admin_notification(
            subject=f"Email delivery failure: {subject}",
            body=(
                f"Bot: {bot_name}\n"
                f"To: {', '.join(recipients)}\n"
                f"CC: {', '.join(_normalize_optional_recipients(cc)) or '-'}\n"
                f"BCC: {', '.join(_normalize_optional_recipients(bcc)) or '-'}\n"
                f"Audit: {audit_context or {}}\n"
            ),
            bot_name="system_admin",
        )
    return False


def dispatch_email_sync(
    *,
    bot_name: str,
    to_email: str | list[str],
    subject: str,
    body: str,
    html: bool = True,
    plain_text: str | None = None,
    cc: list[str] | None = None,
    bcc: list[str] | None = None,
    audit_context: dict[str, Any] | None = None,
) -> bool:
    recipients = _normalize_optional_recipients(to_email)
    if not recipients:
        logger.warning("[email_dispatcher] skipped sync send for %s: no recipients", bot_name)
        return False

    success = send_email(
        subject=subject,
        body=body,
        to=recipients,
        html=html,
        plain_text=plain_text,
        from_email=get_bot_email(bot_name),
    )
    if success:
        logger.info(
            "[email_dispatcher] sync sent subject=%s via=%s to=%s cc=%s bcc=%s audit=%s",
            subject,
            bot_name,
            recipients,
            _normalize_optional_recipients(cc),
            _normalize_optional_recipients(bcc),
            audit_context or {},
        )
        return True

    admin_target = settings.ADMIN_EMAIL or settings.SMTP_FROM or settings.SMTP_USER
    if admin_target:
        send_admin_notification(
            subject=f"Email delivery failure: {subject}",
            body=(
                f"Bot: {bot_name}\n"
                f"To: {', '.join(recipients)}\n"
                f"CC: {', '.join(_normalize_optional_recipients(cc)) or '-'}\n"
                f"BCC: {', '.join(_normalize_optional_recipients(bcc)) or '-'}\n"
                f"Audit: {audit_context or {}}\n"
            ),
            bot_name="system_admin",
        )
    return False
