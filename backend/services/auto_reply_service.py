# Auto Reply Service for GTS Logistics
import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class AutoReplyService:
    """Service for handling automatic email replies"""

    def __init__(self):
        self.enabled = self._is_enabled()

    def _is_enabled(self) -> bool:
        """Check if auto-reply is enabled"""
        return os.getenv("AUTO_REPLY_ENABLED", "true").lower() in ("1", "true", "yes")

    def send_auto_reply(self, to_email: str, name: str, inquiry_type: str, reference: Optional[str] = None) -> bool:
        """Send an automatic reply to customer inquiry"""
        if not self.enabled:
            logger.info("Auto-reply is disabled, skipping")
            return False

        try:
            # Import email service
            from backend.services.email_service import send_email

            subject = self._get_subject(inquiry_type)
            body = self._get_body(name, inquiry_type, reference)

            # Send the email
            success = send_email(
                to_email=to_email,
                subject=subject,
                body=body,
                is_html=True
            )

            if success:
                logger.info(f"Auto-reply sent to {to_email} for {inquiry_type}")
            else:
                logger.error(f"Failed to send auto-reply to {to_email}")

            return success

        except Exception as e:
            logger.error(f"Error sending auto-reply: {e}")
            return False

    def _get_subject(self, inquiry_type: str) -> str:
        """Get email subject based on inquiry type"""
        subjects = {
            "billing": "Thank you for your billing inquiry - GTS Logistics",
            "shipping": "Thank you for your shipping inquiry - GTS Logistics",
            "support": "Thank you for contacting GTS Logistics Support",
            "general": "Thank you for your inquiry - GTS Logistics"
        }
        return subjects.get(inquiry_type, subjects["general"])

    def _get_body(self, name: str, inquiry_type: str, reference: Optional[str] = None) -> str:
        """Get email body based on inquiry type"""
        greeting = f"Dear {name}," if name else "Dear Customer,"

        reference_text = f"\n\nReference: {reference}" if reference else ""

        bodies = {
            "billing": f"""
{greeting}

Thank you for your billing inquiry. We have received your message and our finance team will review it shortly.

Our typical response time is 24-48 hours during business days. For urgent billing matters, please call us at +1 (778) 651-8297.{reference_text}

Best regards,
GTS Logistics Finance Team
support@gtslogistics.com
+1 (778) 651-8297
""",
            "shipping": f"""
{greeting}

Thank you for your shipping inquiry. We have received your message and our operations team will assist you shortly.

Our typical response time is 12-24 hours during business days. For time-sensitive shipping matters, please call us at +1 (778) 651-8297.{reference_text}

Best regards,
GTS Logistics Operations Team
operations@gtslogistics.com
+1 (778) 651-8297
""",
            "support": f"""
{greeting}

Thank you for contacting GTS Logistics support. We have received your message and our support team will assist you shortly.

Our typical response time is 12-24 hours during business days. For urgent technical issues, please call us at +1 (778) 651-8297.{reference_text}

Best regards,
GTS Logistics Support Team
support@gtslogistics.com
+1 (778) 651-8297
""",
            "general": f"""
{greeting}

Thank you for your inquiry. We have received your message and our team will respond shortly.

Our typical response time is 24-48 hours during business days. For urgent matters, please call us at +1 (778) 651-8297.{reference_text}

Best regards,
GTS Logistics Team
info@gtslogistics.com
+1 (778) 651-8297
"""
        }

        body = bodies.get(inquiry_type, bodies["general"])
        return body.strip()


# Global instance
auto_reply_service = AutoReplyService()


def get_auto_reply() -> AutoReplyService:
    """Get the global auto-reply service instance"""
    return auto_reply_service


def is_auto_reply_enabled() -> bool:
    """Check if auto-reply is enabled"""
    return auto_reply_service.enabled