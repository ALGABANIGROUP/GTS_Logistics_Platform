"""
Telegram Bot Service for GTS Incident Response System
"""

from __future__ import annotations

import logging
import os
from typing import Any, Dict, Optional

import requests
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class TelegramService:
    """
    Telegram service for sending alerts and notifications.

    Token configuration enables bot-level operations. A default chat ID is only
    required for proactive alert delivery methods that do not receive an
    explicit destination.
    """

    def __init__(self):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")
        self.enabled = os.getenv("TELEGRAM_ENABLED", "false").lower() == "true"
        self.base_url = f"https://api.telegram.org/bot{self.token}" if self.token else None

        if self.enabled and not self.token:
            logger.warning("Telegram bot token not configured")
        elif self.enabled and not self.chat_id:
            logger.info(
                "Telegram chat ID not configured; alert delivery requires explicit chat_id or TELEGRAM_CHAT_ID"
            )

    def is_configured(self) -> bool:
        """Check if the Telegram bot itself is enabled and token-configured."""
        return bool(self.enabled and self.token and self.base_url)

    def can_send_alerts(self) -> bool:
        """Check if the service has a default alert destination."""
        return bool(self.is_configured() and self.chat_id)

    def send_message(
        self,
        text: str,
        parse_mode: str = "HTML",
        chat_id: Optional[str] = None,
    ) -> bool:
        """
        Send a text message via Telegram.

        Args:
            text: Message text.
            parse_mode: Parsing mode (HTML or Markdown).
            chat_id: Destination chat override. Falls back to TELEGRAM_CHAT_ID.

        Returns:
            bool: Whether sending was successful.
        """
        if not self.is_configured():
            logger.info("Telegram bot not configured or disabled")
            return False

        target_chat_id = chat_id or self.chat_id
        if not target_chat_id:
            logger.info("Telegram chat ID not configured; skipping message delivery")
            return False

        try:
            response = requests.post(
                f"{self.base_url}/sendMessage",
                json={
                    "chat_id": target_chat_id,
                    "text": text,
                    "parse_mode": parse_mode,
                    "disable_web_page_preview": True,
                },
                timeout=10,
            )

            if response.status_code == 200:
                logger.info("Telegram message sent successfully")
                return True

            logger.error("Telegram API error: %s - %s", response.status_code, response.text)
            return False
        except Exception as exc:
            logger.error("Telegram send error: %s", exc)
            return False

    def send_incident_alert(self, incident: Dict[str, Any]) -> bool:
        """
        Send alert for a specific incident.

        Args:
            incident: Incident data.

        Returns:
            bool: Whether sending was successful.
        """
        if not self.can_send_alerts():
            return False

        try:
            incident_id = incident.get("id", "UNKNOWN")
            severity = incident.get("severity", "unknown").upper()
            service = incident.get("service", "Unknown Service")
            error_message = incident.get("error_message", "No error details")[:300]
            timestamp = incident.get("timestamp", "Unknown time")

            severity_icons = {
                "CRITICAL": "[CRITICAL]",
                "HIGH": "[HIGH]",
                "MEDIUM": "[MEDIUM]",
                "LOW": "[LOW]",
            }
            icon = severity_icons.get(severity, "[ALERT]")

            message = f"""
{icon} <b>INCIDENT DETECTED</b> {icon}

<b>ID:</b> {incident_id}
<b>Severity:</b> {severity}
<b>Service:</b> {service}
<b>Time:</b> {timestamp}

<b>Error:</b> {error_message}

<i>GTS Incident Response System</i>
            """.strip()

            return self.send_message(message)
        except Exception as exc:
            logger.error("Error sending incident alert: %s", exc)
            return False

    def send_system_status(self, status: str, details: Optional[str] = None) -> bool:
        """
        Send system status.

        Args:
            status: System status.
            details: Additional details.

        Returns:
            bool: Whether sending was successful.
        """
        if not self.can_send_alerts():
            return False

        try:
            status_icons = {
                "online": "[ONLINE]",
                "warning": "[WARNING]",
                "error": "[ERROR]",
                "maintenance": "[MAINTENANCE]",
            }
            icon = status_icons.get(status.lower(), "[INFO]")

            details_block = f"<b>Details:</b> {details}" if details else ""
            message = f"""
{icon} <b>SYSTEM STATUS</b>

<b>Status:</b> {status.upper()}

{details_block}

<i>GTS Monitoring System</i>
            """.strip()

            return self.send_message(message)
        except Exception as exc:
            logger.error("Error sending system status: %s", exc)
            return False

    def test_connection(self) -> Dict[str, Any]:
        """
        Test connection to the bot.

        Returns:
            Dict: Test result.
        """
        if not self.is_configured():
            return {
                "success": False,
                "message": "Telegram bot token not configured or service disabled",
                "configured": False,
            }

        try:
            response = requests.get(f"{self.base_url}/getMe", timeout=10)

            if response.status_code != 200:
                return {
                    "success": False,
                    "message": f"API error: {response.status_code}",
                    "configured": True,
                    "delivery_configured": bool(self.chat_id),
                }

            bot_info = response.json()
            if not bot_info.get("ok"):
                return {
                    "success": False,
                    "message": "Invalid bot token",
                    "configured": True,
                    "delivery_configured": bool(self.chat_id),
                }

            delivery_configured = bool(self.chat_id)
            test_result = self.send_message(
                "Telegram Bot Test: GTS Incident Response System is connected and working."
            ) if delivery_configured else False

            return {
                "success": True,
                "message": (
                    "Telegram bot connected successfully"
                    if test_result
                    else "Telegram bot token is valid, but no TELEGRAM_CHAT_ID is configured for test delivery"
                ),
                "configured": True,
                "delivery_configured": delivery_configured,
                "bot_username": bot_info["result"].get("username"),
            }
        except Exception as exc:
            return {
                "success": False,
                "message": f"Connection error: {exc}",
                "configured": True,
                "delivery_configured": bool(self.chat_id),
            }


telegram_service = TelegramService()
