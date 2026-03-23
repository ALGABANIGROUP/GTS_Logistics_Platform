from __future__ import annotations

from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Index
from sqlalchemy.orm import relationship

from backend.database.base import Base

class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Store hashed token only (never raw token)
    token_hash = Column(String(128), nullable=False, unique=True, index=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False, index=True)
    used_at = Column(DateTime, nullable=True)

    # Request metadata
    request_ip = Column(String(64), nullable=True)
    user_agent = Column(String(256), nullable=True)

    user = relationship("User", backref="password_reset_tokens")

Index("ix_pwd_reset_user_active", PasswordResetToken.user_id, PasswordResetToken.used_at, PasswordResetToken.expires_at)