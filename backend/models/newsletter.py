"""
Newsletter Subscriber Model
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from backend.database.base import Base


class NewsletterSubscriber(Base):
    """Newsletter subscriber model"""

    __tablename__ = "newsletter_subscribers"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=True)
    source = Column(String(50), default="website")  # website, footer, popup, etc.
    consent_given = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True, index=True)
    unsubscribe_token = Column(String(100), nullable=True)
    subscribed_at = Column(DateTime(timezone=True), server_default=func.now())
    unsubscribed_at = Column(DateTime(timezone=True), nullable=True)
    last_sent_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())