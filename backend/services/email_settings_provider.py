"""
Email Settings Provider
Provides email configuration from platform settings to email services and Email Command Center
"""
from __future__ import annotations

import logging
import os
from typing import Dict, Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


async def get_email_settings(session: AsyncSession) -> Dict[str, Any]:
    """
    Get email configuration from platform settings with fallbacks to env variables
    
    Returns:
        Dict containing: smtpServer, smtpPort, smtpPassword, fromEmail, fromName, useSSL, useTLS
    """
    try:
        from backend.services.platform_settings_store import _get_platform_settings_raw
        
        # Get raw settings (with unmasked passwords)
        settings = await _get_platform_settings_raw(session)
        email_config = settings.get("email", {})
        
        # Build config with fallbacks to environment variables
        return {
            "smtpServer": email_config.get("smtpServer") or os.getenv("SMTP_HOST", ""),
            "smtpPort": email_config.get("smtpPort") or int(os.getenv("SMTP_PORT", "587")),
            "smtpPassword": email_config.get("smtpPassword") or os.getenv("EMAIL_SHARED_PASSWORD") or os.getenv("SMTP_PASSWORD", ""),
            "fromEmail": email_config.get("fromEmail") or os.getenv("MAIL_FROM", os.getenv("SMTP_FROM", "")),
            "fromName": email_config.get("fromName") or os.getenv("MAIL_FROM_NAME", "GTS Platform"),
            "useSSL": email_config.get("useSSL", True),
            "useTLS": email_config.get("useTLS", True),
        }
    except Exception as e:
        logger.warning(f"Failed to load email settings from platform settings: {e}")
        # Fallback to env variables only
        return {
            "smtpServer": os.getenv("SMTP_HOST", ""),
            "smtpPort": int(os.getenv("SMTP_PORT", "587")),
            "smtpPassword": os.getenv("EMAIL_SHARED_PASSWORD") or os.getenv("SMTP_PASSWORD", ""),
            "fromEmail": os.getenv("MAIL_FROM", os.getenv("SMTP_FROM", "")),
            "fromName": os.getenv("MAIL_FROM_NAME", "GTS Platform"),
            "useSSL": True,
            "useTLS": True,
        }


async def is_email_configured(session: AsyncSession) -> bool:
    """Check if email is properly configured"""
    config = await get_email_settings(session)
    return bool(config.get("smtpServer") and config.get("fromEmail"))


async def update_email_settings(
    session: AsyncSession,
    smtp_server: str,
    smtp_port: int,
    from_email: str,
    from_name: str,
    use_ssl: bool = True,
    use_tls: bool = True
) -> Dict[str, Any]:
    """
    Update email settings in platform settings
    
    Args:
        session: Database session
        smtp_server: SMTP server hostname
        smtp_port: SMTP server port
        from_email: Default from email address
        from_name: Default from name
        use_ssl: Use SSL connection
        use_tls: Use TLS/STARTTLS
        
    Returns:
        Updated email settings
    """
    try:
        from backend.services.platform_settings_store import update_platform_settings
        
        email_payload = {
            "email": {
                "smtpServer": smtp_server,
                "smtpPort": smtp_port,
                "fromEmail": from_email,
                "fromName": from_name,
                "useSSL": use_ssl,
                "useTLS": use_tls,
            }
        }
        
        updated = await update_platform_settings(session, email_payload, updated_by="system")
        logger.info(f"Email settings updated: {from_email} via {smtp_server}:{smtp_port}")
        
        return updated.get("email", {})
    except Exception as e:
        logger.error(f"Failed to update email settings: {e}")
        raise


async def get_smtp_config_for_mailbox(
    session: AsyncSession,
    mailbox_email: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get SMTP configuration for a specific mailbox, using platform settings as defaults
    
    Args:
        session: Database session
        mailbox_email: Optional specific mailbox email
        
    Returns:
        Dict with smtp_host, smtp_port, smtp_user, smtp_password, use_ssl, use_tls
    """
    platform_config = await get_email_settings(session)
    
    config = {
        "smtp_host": platform_config.get("smtpServer"),
        "smtp_port": platform_config.get("smtpPort"),
        "smtp_user": mailbox_email or platform_config.get("fromEmail"),
        "smtp_password": os.getenv("EMAIL_SHARED_PASSWORD") or os.getenv("SMTP_PASSWORD", ""),
        "use_ssl": platform_config.get("useSSL", True),
        "use_tls": platform_config.get("useTLS", True),
        "from_email": platform_config.get("fromEmail"),
        "from_name": platform_config.get("fromName"),
    }
    
    return config
