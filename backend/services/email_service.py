"""Email service for sending verification and notification emails."""
import logging
from typing import Optional

logger = logging.getLogger(__name__)


async def send_email_verification(
    email: str,
    verification_token: str,
    subdomain: str
) -> bool:
    """
    Send email verification link to new tenant owner.
    
    Args:
        email: Recipient email address
        verification_token: Unique verification token
        subdomain: Tenant subdomain
    
    Returns:
        True if email sent successfully, False otherwise
    """
    # TODO: Implement actual email sending via SMTP/SendGrid/etc
    verification_url = f"https://{subdomain}.gts-logistics.com/verify-email?token={verification_token}"
    
    logger.warning(
        f"[email_service] STUB: Would send verification email to {email}\n"
        f"  Subdomain: {subdomain}\n"
        f"  Token: {verification_token}\n"
        f"  URL: {verification_url}"
    )
    
    # For development: always return True (email "sent")
    return True


async def send_welcome_email(email: str, subdomain: str) -> bool:
    """Send welcome email after successful verification."""
    logger.warning(f"[email_service] STUB: Would send welcome email to {email} (subdomain: {subdomain})")
    return True


async def send_password_reset(email: str, reset_token: str) -> bool:
    """Send password reset link."""
    logger.warning(f"[email_service] STUB: Would send password reset to {email} (token: {reset_token})")
    return True
