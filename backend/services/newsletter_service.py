"""
Newsletter Service - Manage subscribers and send updates
"""

import os
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class NewsletterService:
    """Newsletter subscription management service"""

    def __init__(self, session: AsyncSession = None):
        self.session = session
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.from_email = os.getenv("SMTP_FROM", "newsletter@gtslogistics.com")
        self.enabled = bool(self.smtp_user and self.smtp_password)

    async def subscribe(self, email: str, source: str = "website", consent: bool = True) -> Dict[str, Any]:
        """Subscribe a new user to newsletter"""
        try:
            from backend.models.newsletter import NewsletterSubscriber

            # Check if already subscribed
            existing = await self.session.execute(
                select(NewsletterSubscriber).where(NewsletterSubscriber.email == email)
            )
            subscriber = existing.scalar_one_or_none()

            if subscriber:
                if subscriber.is_active:
                    return {
                        "success": False,
                        "message": "This email is already subscribed to our newsletter."
                    }
                else:
                    # Reactivate
                    subscriber.is_active = True
                    subscriber.unsubscribed_at = None
                    subscriber.updated_at = datetime.now()
                    await self.session.commit()
                    return {
                        "success": True,
                        "message": "Welcome back! You have been resubscribed."
                    }

            # Create new subscriber
            new_subscriber = NewsletterSubscriber(
                email=email,
                source=source,
                consent_given=consent,
                is_active=True,
                subscribed_at=datetime.now()
            )
            self.session.add(new_subscriber)
            await self.session.commit()

            # Send welcome email
            await self._send_welcome_email(email)

            return {
                "success": True,
                "message": "Thank you for subscribing! Check your inbox for confirmation."
            }

        except Exception as e:
            logger.error(f"Newsletter subscription failed: {e}")
            await self.session.rollback()
            return {
                "success": False,
                "message": f"Failed to subscribe: {str(e)}"
            }

    async def unsubscribe(self, email: str, token: str = None) -> Dict[str, Any]:
        """Unsubscribe a user from newsletter"""
        try:
            from backend.models.newsletter import NewsletterSubscriber

            query = select(NewsletterSubscriber).where(NewsletterSubscriber.email == email)
            if token:
                query = query.where(NewsletterSubscriber.unsubscribe_token == token)

            result = await self.session.execute(query)
            subscriber = result.scalar_one_or_none()

            if not subscriber:
                return {
                    "success": False,
                    "message": "Email not found in our records."
                }

            subscriber.is_active = False
            subscriber.unsubscribed_at = datetime.now()
            await self.session.commit()

            return {
                "success": True,
                "message": "You have been unsubscribed from our newsletter."
            }

        except Exception as e:
            logger.error(f"Newsletter unsubscribe failed: {e}")
            await self.session.rollback()
            return {
                "success": False,
                "message": f"Failed to unsubscribe: {str(e)}"
            }

    async def get_subscribers(self, active_only: bool = True, limit: int = 100) -> List[Dict[str, Any]]:
        """Get list of subscribers"""
        try:
            from backend.models.newsletter import NewsletterSubscriber

            query = select(NewsletterSubscriber)
            if active_only:
                query = query.where(NewsletterSubscriber.is_active == True)

            query = query.order_by(NewsletterSubscriber.subscribed_at.desc()).limit(limit)

            result = await self.session.execute(query)
            subscribers = result.scalars().all()

            return [
                {
                    "id": s.id,
                    "email": s.email,
                    "source": s.source,
                    "subscribed_at": s.subscribed_at.isoformat() if s.subscribed_at else None,
                    "is_active": s.is_active
                }
                for s in subscribers
            ]

        except Exception as e:
            logger.error(f"Failed to get subscribers: {e}")
            return []

    async def get_subscriber_count(self, active_only: bool = True) -> int:
        """Get total subscriber count"""
        try:
            from backend.models.newsletter import NewsletterSubscriber

            query = select(func.count()).select_from(NewsletterSubscriber)
            if active_only:
                query = query.where(NewsletterSubscriber.is_active == True)

            result = await self.session.execute(query)
            return result.scalar() or 0

        except Exception as e:
            logger.error(f"Failed to get subscriber count: {e}")
            return 0

    async def send_newsletter(self, subject: str, content: str, html_content: str = None) -> Dict[str, Any]:
        """Send newsletter to all active subscribers"""
        if not self.enabled:
            return {
                "success": False,
                "message": "Email service not configured. Set SMTP credentials to enable."
            }

        subscribers = await self.get_subscribers(active_only=True)
        if not subscribers:
            return {
                "success": False,
                "message": "No active subscribers found."
            }

        sent = 0
        failed = 0

        for subscriber in subscribers:
            try:
                success = await self._send_email(
                    to_email=subscriber["email"],
                    subject=subject,
                    content=content,
                    html_content=html_content
                )
                if success:
                    sent += 1
                else:
                    failed += 1
            except Exception as e:
                logger.error(f"Failed to send to {subscriber['email']}: {e}")
                failed += 1

        return {
            "success": True,
            "sent": sent,
            "failed": failed,
            "total": len(subscribers),
            "message": f"Newsletter sent to {sent} subscribers, failed: {failed}"
        }

    async def _send_welcome_email(self, to_email: str) -> bool:
        """Send welcome email to new subscriber"""
        if not self.enabled:
            return False

        subject = "Welcome to GTS Logistics Newsletter!"
        content = f"""
        Hello!

        Thank you for subscribing to the GTS Logistics newsletter.

        You'll receive:
        - Weekly market insights and rate updates
        - Platform feature announcements
        - Industry news and trends
        - Exclusive offers and tips

        To unsubscribe, click here: https://gtslogistics.com/unsubscribe?email={to_email}

        Welcome aboard!

        The GTS Logistics Team
        """

        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #d32f2f;">Welcome to GTS Logistics!</h2>
            <p>Thank you for subscribing to our newsletter.</p>
            <p>You'll receive:</p>
            <ul>
                <li>Weekly market insights and rate updates</li>
                <li>Platform feature announcements</li>
                <li>Industry news and trends</li>
                <li>Exclusive offers and tips</li>
            </ul>
            <p>To unsubscribe, <a href="https://gtslogistics.com/unsubscribe?email={to_email}">click here</a>.</p>
            <hr>
            <p style="color: #666; font-size: 12px;">GTS Logistics - Gabani Transport Solutions</p>
        </body>
        </html>
        """

        return await self._send_email(to_email, subject, content, html_content)

    async def _send_email(self, to_email: str, subject: str, content: str, html_content: str = None) -> bool:
        """Send email via SMTP"""
        if not self.enabled:
            return False

        try:
            msg = MIMEMultipart("alternative")
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = subject

            msg.attach(MIMEText(content, 'plain'))
            if html_content:
                msg.attach(MIMEText(html_content, 'html'))

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)

            logger.info(f"Newsletter email sent to {to_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False


# Singleton instance
_newsletter_service = None


def get_newsletter_service(session: AsyncSession = None) -> NewsletterService:
    """Get newsletter service instance"""
    global _newsletter_service
    if _newsletter_service is None or session:
        _newsletter_service = NewsletterService(session)
    return _newsletter_service