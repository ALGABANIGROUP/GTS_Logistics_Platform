"""
Unified Email System for GTS Platform
Handles all email notifications across GTS Main & TMS systems
"""

import logging
from datetime import datetime
from typing import Dict, List

from backend.utils.email_utils import send_email

logger = logging.getLogger(__name__)


class UnifiedEmailSystem:
    """Unified email system for all GTS systems"""

    EMAIL_CONFIG = {
        "smtp_host": "smtp.gmail.com",
        "smtp_port": 587,
        "from_email": "no-reply@gabanilogistics.com",
        "admin_email": "admin@gabanilogistics.com",
        "support_email": "support@gts.com",
        "tms_alerts_email": "tms-alerts@gts.com",
    }

    @staticmethod
    def send_email(to_email: str | None, subject: str, html_content: str, text_content: str | None = None) -> bool:
        """Send an email (base function)"""
        if not to_email:
            return False

        try:
            sent = send_email(
                subject=subject,
                body=html_content,
                to=[to_email],
                html=True,
                plain_text=text_content,
                from_email=UnifiedEmailSystem.EMAIL_CONFIG["from_email"],
            )
            if sent:
                logger.info("Email sent to %s: %s", to_email, subject)
            return sent
        except Exception as exc:
            logger.error("Failed to send email to %s: %s", to_email, exc)
            return False

    @staticmethod
    def send_welcome_email(user_email: str, full_name: str, systems_granted: List[Dict]) -> bool:
        """Send welcome email with granted systems"""

        systems_list_html = ""
        for system in systems_granted:
            icon = "Truck" if system["type"] == "gts_main" else "TMS"
            systems_list_html += f"""
            <li style="margin: 10px 0;">
                <strong>{icon} {system['name']}</strong><br>
                Access Level: {system['access_level']}<br>
                Dashboard: <a href="{system['url']}">{system['url']}</a>
            </li>
            """

        subject = f"Welcome to Gabani Transport Solutions (GTS) - Access to {len(systems_granted)} system(s)"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <body>
            <p>Hi {full_name},</p>
            <p>Your Gabani Transport Solutions (GTS) account has been successfully created with access to the following systems:</p>
            <ul>
                {systems_list_html}
            </ul>
            <p>Important notes:</p>
            <ul>
                <li>Use the same credentials to access all systems.</li>
                <li>You can switch between systems from your dashboard.</li>
                <li>Contact admin if you need access to additional systems.</li>
                <li>Keep your password secure and change it regularly.</li>
            </ul>
            <p>Need help? Contact us at <a href="mailto:{UnifiedEmailSystem.EMAIL_CONFIG['support_email']}">{UnifiedEmailSystem.EMAIL_CONFIG['support_email']}</a></p>
            <p>Best regards,<br><strong>Gabani Transport Solutions (GTS) Team</strong></p>
        </body>
        </html>
        """

        return UnifiedEmailSystem.send_email(user_email, subject, html_content)

    @staticmethod
    def send_tms_approval_email(user_email: str, full_name: str, company_name: str, plan: str) -> bool:
        """Send TMS request approval notification"""

        subject = "TMS Access Approved"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <body>
            <p>Hi {full_name},</p>
            <p>Your access to the Transport Management System (TMS) has been approved.</p>
            <ul>
                <li><strong>Company:</strong> {company_name}</li>
                <li><strong>Plan:</strong> {plan.upper()}</li>
                <li><strong>Dashboard:</strong> <a href="http://127.0.0.1:5173/dashboard/tms">Access TMS Dashboard</a></li>
            </ul>
            <p>The TMS Load Board feature is currently restricted to US and Canada.</p>
            <p>Questions? Contact our support team at <a href="mailto:{UnifiedEmailSystem.EMAIL_CONFIG['support_email']}">{UnifiedEmailSystem.EMAIL_CONFIG['support_email']}</a></p>
            <p>Best regards,<br><strong>GTS TMS Team</strong></p>
        </body>
        </html>
        """

        return UnifiedEmailSystem.send_email(user_email, subject, html_content)

    @staticmethod
    def send_tms_rejection_email(user_email: str, full_name: str, reason: str) -> bool:
        """Send rejection email for TMS access requests."""

        subject = "TMS Access Request - Update Required"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <body>
            <p>Hi {full_name},</p>
            <p>We need more information before we can approve your TMS access request.</p>
            <p><strong>Reason:</strong> {reason}</p>
            <p>Please submit a new request with the required information, or contact our team for assistance.</p>
            <p>Contact: <a href="mailto:{UnifiedEmailSystem.EMAIL_CONFIG['support_email']}">{UnifiedEmailSystem.EMAIL_CONFIG['support_email']}</a></p>
            <p>Best regards,<br><strong>GTS Team</strong></p>
        </body>
        </html>
        """

        return UnifiedEmailSystem.send_email(user_email, subject, html_content)

    @staticmethod
    def notify_admin_new_tms_request(request_id: str, company_name: str, contact_email: str) -> bool:
        """Send admin notification for a new TMS registration request."""

        admin_email = UnifiedEmailSystem.EMAIL_CONFIG["admin_email"]
        subject = f"New TMS Registration Request: {company_name}"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <body>
            <h2>New TMS Access Request</h2>
            <ul>
                <li><strong>Company:</strong> {company_name}</li>
                <li><strong>Contact Email:</strong> {contact_email}</li>
                <li><strong>Request ID:</strong> {request_id}</li>
                <li><strong>Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M')}</li>
            </ul>
            <p><a href="http://127.0.0.1:5173/admin/unified-dashboard?tab=tms-requests">Review Request</a></p>
        </body>
        </html>
        """

        return UnifiedEmailSystem.send_email(admin_email, subject, html_content)

    @staticmethod
    def send_system_alert(alert_type: str, message: str, severity: str = "info") -> bool:
        """Send a formatted platform system alert email to administrators."""

        admin_email = UnifiedEmailSystem.EMAIL_CONFIG["admin_email"]
        subject = f"[{severity.upper()}] GTS System Alert: {alert_type}"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <body>
            <h2>{alert_type}</h2>
            <p>{message}</p>
            <p><small>Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</small></p>
        </body>
        </html>
        """

        return UnifiedEmailSystem.send_email(admin_email, subject, html_content)
