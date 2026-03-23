from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Boolean,
    ForeignKey,
    Index,
)
from sqlalchemy.orm import relationship, declared_attr
from backend.database.base import Base


class SupportTicket(Base):
    __tablename__: str = "support_tickets"

    id = Column(Integer, primary_key=True, index=True)

    tenant_id = Column(String(64), nullable=True, index=True)

    # Optional user who created the ticket
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Basic ticket info
    subject = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)

    # Priority: "low", "medium", "high", "urgent"
    priority = Column(String(50), nullable=False, default="medium")

    # Status: "open", "in_progress", "resolved", "closed"
    status = Column(String(50), nullable=False, default="open")

    # Assignment info
    assigned_to = Column(String(255), nullable=True)

    # Category or queue, e.g. "billing", "technical", "operations"
    category = Column(String(100), nullable=True)

    # Contact email for this ticket (optional override)
    contact_email = Column(String(255), nullable=True)

    # Flags
    is_internal = Column(Boolean, nullable=False, default=False)

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
    )

    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
    )

    closed_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    __table_args__ = (
        Index("ix_support_tickets_user_id", "user_id"),
        Index("ix_support_tickets_tenant_id", "tenant_id"),
        Index("ix_support_tickets_status", "status"),
        Index("ix_support_tickets_priority", "priority"),
        Index("ix_support_tickets_category", "category"),
    )

    def __repr__(self) -> str:
        return (
            f"<SupportTicket id={self.id} subject={self.subject!r} "
            f"status={self.status} priority={self.priority}>"
        )

