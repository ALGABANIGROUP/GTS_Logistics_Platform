"""Email service wrappers used by signup and auth flows."""

from __future__ import annotations

import asyncio
import logging
from typing import Optional

from backend.config import settings
from backend.utils.email_utils import send_email

logger = logging.getLogger(__name__)


class EmailService:
    """Thin async wrapper around the shared SMTP mailer."""

    def __init__(self) -> None:
        self.enabled = bool(settings.SMTP_HOST and settings.SMTP_USER)
        self.frontend_url = (settings.FRONTEND_URL or "http://localhost:5173").rstrip("/")

    async def send_email(
        self,
        *,
        to_email: str,
        subject: str,
        content: str,
        html_content: Optional[str] = None,
    ) -> bool:
        if not self.enabled:
            logger.info("[email_service] SMTP not configured; skipping email to %s", to_email)
            return False

        return await asyncio.to_thread(
            send_email,
            subject=subject,
            body=html_content or content,
            to=[to_email],
            html=bool(html_content),
            plain_text=content,
        )

    async def send_email_verification(
        self,
        *,
        email: str,
        verification_token: Optional[str] = None,
        subdomain: Optional[str] = None,
        company_name: Optional[str] = None,
        verification_link: Optional[str] = None,
        owner_name: Optional[str] = None,
    ) -> bool:
        resolved_link = verification_link
        if not resolved_link and verification_token:
            if subdomain:
                resolved_link = f"https://{subdomain}.gtsdispatcher.com/verify?token={verification_token}"
            else:
                resolved_link = f"{self.frontend_url}/verify-email?token={verification_token}"

        display_name = owner_name or company_name or "there"
        subject = "Verify your GTS Logistics account"
        content = (
            f"Hello {display_name},\n\n"
            "Please verify your email address to activate your account.\n"
            f"{resolved_link or self.frontend_url}\n\n"
            "If you did not request this account, you can ignore this message."
        )
        html = f"""
        <p>Hello {display_name},</p>
        <p>Please verify your email address to activate your GTS Logistics account.</p>
        <p><a href="{resolved_link or self.frontend_url}">Verify your account</a></p>
        <p>If you did not request this account, you can ignore this message.</p>
        """
        return await self.send_email(
            to_email=email,
            subject=subject,
            content=content,
            html_content=html,
        )

    async def send_welcome_email(
        self,
        *,
        email: str,
        subdomain: Optional[str] = None,
    ) -> bool:
        subject = "Welcome to GTS Logistics"
        login_url = f"https://{subdomain}.gtsdispatcher.com/login" if subdomain else f"{self.frontend_url}/login"
        content = (
            "Welcome to GTS Logistics.\n\n"
            f"You can sign in here: {login_url}\n"
        )
        html = f"""
        <p>Welcome to GTS Logistics.</p>
        <p><a href="{login_url}">Open your workspace</a></p>
        """
        return await self.send_email(
            to_email=email,
            subject=subject,
            content=content,
            html_content=html,
        )

    async def send_password_reset(self, *, email: str, reset_token: str) -> bool:
        reset_url = f"{self.frontend_url}/reset-password?token={reset_token}"
        subject = "Reset your password"
        content = (
            "We received a request to reset your password.\n\n"
            f"Reset link: {reset_url}\n\n"
            "If you did not request this reset, ignore this email."
        )
        html = f"""
        <p>We received a request to reset your password.</p>
        <p><a href="{reset_url}">Reset your password</a></p>
        <p>If you did not request this reset, ignore this email.</p>
        """
        return await self.send_email(
            to_email=email,
            subject=subject,
            content=content,
            html_content=html,
        )


_email_service: Optional[EmailService] = None


def get_email_service() -> EmailService:
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service


async def send_email_verification(
    email: str,
    verification_token: Optional[str] = None,
    subdomain: Optional[str] = None,
    **kwargs,
) -> bool:
    return await get_email_service().send_email_verification(
        email=email,
        verification_token=verification_token,
        subdomain=subdomain,
        company_name=kwargs.get("company_name"),
        verification_link=kwargs.get("verification_link"),
        owner_name=kwargs.get("owner_name"),
    )


async def send_welcome_email(email: str, subdomain: Optional[str] = None) -> bool:
    return await get_email_service().send_welcome_email(email=email, subdomain=subdomain)


async def send_password_reset(email: str, reset_token: str) -> bool:
    return await get_email_service().send_password_reset(email=email, reset_token=reset_token)
