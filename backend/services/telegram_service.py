"""
Telegram Bot Service for GTS Incident Response System
"""

import requests
import os
import logging
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class TelegramService:
    """
    Telegram service for sending alerts and notifications
    """

    def __init__(self):
        self.token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID')
        self.enabled = os.getenv('TELEGRAM_ENABLED', 'false').lower() == 'true'

        if self.token and self.chat_id:
            self.base_url = f"https://api.telegram.org/bot{self.token}"
        else:
            self.base_url = None
            logger.warning("Telegram bot token or chat ID not configured")

    def is_configured(self) -> bool:
        """Check if the bot is configured correctly"""
        return self.enabled and self.token and self.chat_id and self.base_url

    def send_message(self, text: str, parse_mode: str = 'HTML') -> bool:
        """
        Send a text message via Telegram

        Args:
            text: message text
            parse_mode: parsing mode (HTML or Markdown)

        Returns:
            bool: whether sending was successful or not
        """
        if not self.is_configured():
            logger.info("Telegram service not configured or disabled")
            return False

        try:
            response = requests.post(
                f"{self.base_url}/sendMessage",
                json={
                    "chat_id": self.chat_id,
                    "text": text,
                    "parse_mode": parse_mode,
                    "disable_web_page_preview": True
                },
                timeout=10
            )

            if response.status_code == 200:
                logger.info("✅ Telegram message sent successfully")
                return True
            else:
                logger.error(f"❌ Telegram API error: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            logger.error(f"❌ Telegram send error: {str(e)}")
            return False

    def send_incident_alert(self, incident: Dict[str, Any]) -> bool:
        """
        Send alert for a specific incident

        Args:
            incident: incident data

        Returns:
            bool: whether sending was successful or not
        """
        if not self.is_configured():
            return False

        try:
            incident_id = incident.get('id', 'UNKNOWN')
            severity = incident.get('severity', 'unknown').upper()
            service = incident.get('service', 'Unknown Service')
            error_message = incident.get('error_message', 'No error details')[:300]  # Limit the length
            timestamp = incident.get('timestamp', 'Unknown time')

            # Determine icon based on severity
            severity_icons = {
                'CRITICAL': '🚨',
                'HIGH': '🔴',
                'MEDIUM': '🟡',
                'LOW': '🟢'
            }
            icon = severity_icons.get(severity, '⚠️')

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

        except Exception as e:
            logger.error(f"Error sending incident alert: {str(e)}")
            return False

    def send_system_status(self, status: str, details: Optional[str] = None) -> bool:
        """
        Send system status

        Args:
            status: system status
            details: additional details

        Returns:
            bool: whether sending was successful or not
        """
        if not self.is_configured():
            return False

        try:
            status_icons = {
                'online': '🟢',
                'warning': '🟡',
                'error': '🔴',
                'maintenance': '🔧'
            }
            icon = status_icons.get(status.lower(), 'ℹ️')

            message = f"""
{icon} <b>SYSTEM STATUS</b>

<b>Status:</b> {status.upper()}

{f'<b>Details:</b> {details}' if details else ''}

<i>GTS Monitoring System</i>
            """.strip()

            return self.send_message(message)

        except Exception as e:
            logger.error(f"Error sending system status: {str(e)}")
            return False

    def test_connection(self) -> Dict[str, Any]:
        """
        Test connection to the bot

        Returns:
            Dict: test result
        """
        if not self.is_configured():
            return {
                "success": False,
                "message": "Telegram service not configured",
                "configured": False
            }

        try:
            # Test connection to the bot
            response = requests.get(f"{self.base_url}/getMe", timeout=10)

            if response.status_code == 200:
                bot_info = response.json()
                if bot_info.get('ok'):
                    # Send test message
                    test_message = "🧪 <b>Telegram Bot Test</b>\n\nGTS Incident Response System is connected and working! ✅"
                    test_result = self.send_message(test_message)

                    return {
                        "success": test_result,
                        "message": "Telegram bot connected successfully" if test_result else "Bot connected but test message failed",
                        "configured": True,
                        "bot_username": bot_info['result'].get('username')
                    }
                else:
                    return {
                        "success": False,
                        "message": "Invalid bot token",
                        "configured": True
                    }
            else:
                return {
                    "success": False,
                    "message": f"API error: {response.status_code}",
                    "configured": True
                }

        except Exception as e:
            return {
                "success": False,
                "message": f"Connection error: {str(e)}",
                "configured": True
            }


# Create a single instance of the service
telegram_service = TelegramService()