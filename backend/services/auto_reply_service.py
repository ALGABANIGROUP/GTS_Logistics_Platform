"""
Auto Reply Service - Automated email responses
"""

import os
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class AutoReplyService:
    """
    Automated email reply service for customer inquiries
    """

    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.from_email = os.getenv("SMTP_FROM", "no-reply@gabanilogistics.com")
        self.enabled = bool(self.smtp_user and self.smtp_password)

        # Reply templates
        self.templates = {
            "general": {
                "subject": "Thank you for contacting GTS Logistics",
                "body": """
                Hello {name},
                
                Thank you for reaching out to GTS Logistics. We have received your message and will respond within 24 hours.
                
                Your reference: {reference}
                
                In the meantime, you can:
                - Visit our Pricing page: https://gtslogistics.com/pricing
                - Check our Resources: https://gtslogistics.com/resources
                - Chat with our AI assistant on our website
                
                Best regards,
                GTS Logistics Support Team
                """
            },
            "sales": {
                "subject": "GTS Logistics - Sales Inquiry",
                "body": """
                Hello {name},
                
                Thank you for your interest in GTS Logistics! Our sales team has received your inquiry and will contact you shortly.
                
                Your reference: {reference}
                
                While you wait, here are some resources:
                - View our pricing plans: https://gtslogistics.com/pricing
                - Request a demo: https://gtslogistics.com/demo
                - Learn about our AI bots: https://gtslogistics.com/ai-bots
                
                We look forward to helping you grow your business!
                
                Best regards,
                GTS Logistics Sales Team
                """
            },
            "support": {
                "subject": "GTS Logistics - Support Ticket Created",
                "body": """
                Hello {name},
                
                Your support request has been received and a ticket has been created.
                
                Reference: {reference}
                Type: {inquiry_type}
                
                Our support team will review your request and respond as soon as possible. For urgent matters, please call +1 (888) 364-1189.
                
                You can also check our FAQ: https://gtslogistics.com/faq
                
                Best regards,
                GTS Logistics Support Team
                """
            }
        }

    def send_auto_reply(
        self, 
        to_email: str, 
        name: str, 
        inquiry_type: str = "general",
        reference: Optional[str] = None
    ) -> bool:
        """Send auto-reply email"""
        if not self.enabled:
            logger.warning("Auto-reply disabled - SMTP not configured")
            return False

        try:
            template = self.templates.get(inquiry_type, self.templates["general"])
            ref = reference or f"{datetime.now().strftime('%Y%m%d')}-{name[:3].upper()}"
            
            body = template["body"].format(
                name=name,
                reference=ref,
                inquiry_type=inquiry_type
            )

            msg = MIMEMultipart("alternative")
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = template["subject"]

            # Plain text
            msg.attach(MIMEText(body, 'plain'))

            # HTML version
            html_body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2 style="color: #d32f2f;">GTS Logistics</h2>
                <p>Hello <strong>{name}</strong>,</p>
                <p>{body.split('Best regards')[0]}</p>
                <hr style="border: none; border-top: 1px solid #ddd;">
                <p style="color: #666; font-size: 12px;">
                    GTS Logistics - Gabani Transport Solutions<br>
                    <a href="https://gtslogistics.com">gtslogistics.com</a> | support@gtslogistics.com | +1 (888) 364-1189
                </p>
            </body>
            </html>
            """
            msg.attach(MIMEText(html_body, 'html'))

            # Send
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)

            logger.info(f"Auto-reply sent to {to_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send auto-reply: {e}")
            return False


# Singleton instance
_auto_reply = None


def get_auto_reply() -> AutoReplyService:
    """Get auto-reply service instance"""
    global _auto_reply
    if _auto_reply is None:
        _auto_reply = AutoReplyService()
    return _auto_reply