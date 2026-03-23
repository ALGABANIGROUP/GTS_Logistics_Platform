# backend/services/email_manager.py
from __future__ import annotations

from typing import Optional, Sequence

from backend.config import settings
from backend.utils.email_utils import send_email, send_bot_email


class EmailManager:
    """
    Central email façade used by the backend.

    This class wraps backend.utils.email_utils so the rest of the codebase
    has a single, clean interface for sending emails.
    """

    def __init__(
        self,
        default_from: Optional[str] = None,
        admin_email: Optional[str] = None,
    ) -> None:
        self.default_from = default_from or str(settings.SMTP_FROM)
        self.admin_email = admin_email or str(settings.ADMIN_EMAIL)

    async def send_system_email(
        self,
        to: str | Sequence[str],
        subject: str,
        body: str,
        bot_name: Optional[str] = None,
    ) -> None:
        """
        Generic helper for sending system emails.
        """
        if bot_name:
            send_bot_email(
                bot_name=bot_name,
                to=to,
                subject=subject,
                body=body,
            )
            return

        send_email(to=to, subject=subject, body=body)

    async def notify_admin(
        self,
        subject: str,
        body: str,
        bot_name: Optional[str] = None,
    ) -> None:
        """
        Convenience helper: send a notification to the configured admin email.
        """
        if not self.admin_email:
            return

        await self.send_system_email(
            to=self.admin_email,
            subject=subject,
            body=body,
            bot_name=bot_name,
        )


# Singleton instance used by other modules
email_manager = EmailManager()
