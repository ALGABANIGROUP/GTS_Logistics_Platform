"""
Email Alert System for Critical Events
Sends notifications for system failures, security events, and important alerts
"""

import logging
import os
from datetime import datetime
from enum import Enum
from typing import List

from backend.utils.email_utils import send_email

logger = logging.getLogger(__name__)


class AlertLevel(Enum):
    """Alert severity levels"""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class EmailAlerter:
    """
    Email alert system for critical events
    """

    def __init__(
        self,
        smtp_host: str = None,
        smtp_port: int = 465,
        smtp_user: str = None,
        smtp_password: str = None,
        from_email: str = None,
        admin_emails: List[str] = None,
    ):
        self.smtp_host = smtp_host or os.getenv("SMTP_HOST", "")
        self.smtp_port = smtp_port or int(os.getenv("SMTP_PORT", "465"))
        self.smtp_user = smtp_user or os.getenv("SMTP_USER", "")
        self.smtp_password = smtp_password or os.getenv("SMTP_PASSWORD", "")
        self.from_email = from_email or os.getenv("MAIL_FROM", self.smtp_user)

        admin_email_str = os.getenv("ADMIN_EMAIL", "")
        self.admin_emails = admin_emails or (admin_email_str.split(",") if admin_email_str else [])

        self.enabled = all([self.smtp_host, self.smtp_user, self.smtp_password])

        if not self.enabled:
            logger.warning("Email alerter not fully configured - alerts will be logged only")

    def send_alert(
        self,
        subject: str,
        message: str,
        level: AlertLevel = AlertLevel.INFO,
        recipients: List[str] = None,
        html: bool = False,
    ) -> bool:
        """
        Send an email alert

        Args:
            subject: Email subject
            message: Email body
            level: Alert severity level
            recipients: List of recipient emails (defaults to admin_emails)
            html: Whether message is HTML formatted

        Returns:
            True if sent successfully, False otherwise
        """
        if not self.enabled:
            logger.warning("Email alert (not sent - not configured): [%s] %s", level.value.upper(), subject)
            return False

        recipients = recipients or self.admin_emails
        if not recipients:
            logger.warning("No recipients configured for alert: %s", subject)
            return False

        formatted_subject = self._format_subject(subject, level)
        formatted_message = message if html else self._format_message(message, level)

        try:
            sent = send_email(
                subject=formatted_subject,
                body=formatted_message,
                to=recipients,
                html=html,
                from_email=self.from_email,
                smtp_user=self.smtp_user,
                smtp_password=self.smtp_password,
                smtp_host=self.smtp_host,
                smtp_port=self.smtp_port,
                smtp_secure=True,
            )
            if not sent:
                return False

            logger.info("Alert email sent: %s to %s recipient(s)", subject, len(recipients))
            return True

        except Exception as exc:
            logger.error("Failed to send alert email: %s", exc)
            return False

    def _format_subject(self, subject: str, level: AlertLevel) -> str:
        """Format email subject with level indicator"""
        icons = {
            AlertLevel.INFO: "[INFO]",
            AlertLevel.WARNING: "[WARNING]",
            AlertLevel.ERROR: "[ERROR]",
            AlertLevel.CRITICAL: "[CRITICAL]",
        }
        icon = icons.get(level, "[EMAIL]")
        return f"[GTS Platform] {icon} {subject}"

    def _format_message(self, message: str, level: AlertLevel) -> str:
        """Format plain text message with header and footer"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        environment = os.getenv("APP_ENV", "development")

        return f"""
========================================
GTS Platform Alert
========================================

Level: {level.value.upper()}
Time: {timestamp}
Environment: {environment}

----------------------------------------
{message}
----------------------------------------

This is an automated alert from GTS Platform.
To configure alert settings, update environment variables.

========================================
"""

    def info(self, subject: str, message: str, recipients: List[str] = None):
        """Send an info-level alert"""
        return self.send_alert(subject, message, AlertLevel.INFO, recipients)

    def warning(self, subject: str, message: str, recipients: List[str] = None):
        """Send a warning-level alert"""
        return self.send_alert(subject, message, AlertLevel.WARNING, recipients)

    def error(self, subject: str, message: str, recipients: List[str] = None):
        """Send an error-level alert"""
        return self.send_alert(subject, message, AlertLevel.ERROR, recipients)

    def critical(self, subject: str, message: str, recipients: List[str] = None):
        """Send a critical-level alert"""
        return self.send_alert(subject, message, AlertLevel.CRITICAL, recipients)

    def database_backup_failed(self, error_details: str):
        """Alert for database backup failure"""
        subject = "Database Backup Failed"
        message = f"""
Database backup operation has failed.

Error Details:
{error_details}

Action Required:
1. Check database connectivity
2. Verify backup script permissions
3. Ensure sufficient disk space
4. Review backup logs for details

Backup Location: backups/
Log File: backups/backup.log
"""
        return self.critical(subject, message)

    def security_alert(self, event_type: str, details: str):
        """Alert for security events"""
        subject = f"Security Alert: {event_type}"
        message = f"""
A security event has been detected.

Event Type: {event_type}
Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

Details:
{details}

Action Required:
Review security logs and take appropriate action if necessary.

Log Location: logs/security.log
"""
        return self.critical(subject, message)

    def high_error_rate(self, error_count: int, time_period: str):
        """Alert for high error rate"""
        subject = "High Error Rate Detected"
        message = f"""
An unusually high error rate has been detected.

Error Count: {error_count}
Time Period: {time_period}

Action Required:
1. Check error logs: logs/errors.log
2. Review recent deployments
3. Check system resources
4. Monitor application health

Health Check: /api/v1/monitoring/health
"""
        return self.error(subject, message)

    def database_connection_failed(self, error_details: str):
        """Alert for database connection failures"""
        subject = "Database Connection Failed"
        message = f"""
Unable to connect to the database.

Error Details:
{error_details}

Action Required:
1. Check database server status
2. Verify connection credentials
3. Check network connectivity
4. Review database logs

This will affect all application operations.
"""
        return self.critical(subject, message)

    def disk_space_low(self, disk_usage: float, threshold: float):
        """Alert for low disk space"""
        subject = "Low Disk Space Warning"
        message = f"""
Disk space is running low.

Current Usage: {disk_usage:.1f}%
Threshold: {threshold:.1f}%

Action Required:
1. Clean up old log files
2. Remove old database backups
3. Clear temporary files
4. Consider increasing disk capacity

Backup Directory: backups/
Log Directory: logs/
"""
        return self.warning(subject, message)

    def deployment_notification(self, version: str, deployed_by: str):
        """Notify about deployment"""
        subject = f"Deployment Completed: {version}"
        message = f"""
A new version has been deployed successfully.

Version: {version}
Deployed By: {deployed_by}
Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Environment: {os.getenv("APP_ENV", "unknown")}

Post-Deployment Checklist:
[ ] Verify health checks: /api/v1/monitoring/health
[ ] Check error logs for new issues
[ ] Monitor performance metrics
[ ] Test critical user flows

This is an automated notification.
"""
        return self.info(subject, message)


_alerter = None


def get_alerter() -> EmailAlerter:
    """Get or create global email alerter instance"""
    global _alerter
    if _alerter is None:
        _alerter = EmailAlerter()
    return _alerter


def send_alert(subject: str, message: str, level: AlertLevel = AlertLevel.INFO):
    """Send an alert using global alerter instance"""
    return get_alerter().send_alert(subject, message, level)


def alert_critical(subject: str, message: str):
    """Send a critical alert"""
    return get_alerter().critical(subject, message)


def alert_error(subject: str, message: str):
    """Send an error alert"""
    return get_alerter().error(subject, message)


def alert_warning(subject: str, message: str):
    """Send a warning alert"""
    return get_alerter().warning(subject, message)
