# backend/tools/open_web_leads/models.py

from datetime import datetime
from typing import Optional
from enum import Enum

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Text,
    UniqueConstraint,
)

# 👇 Important: always use the project's official Base class
from backend.database.base import Base


class OpenWebLeadStatus(str, Enum):
    NEW = "new"
    CONTACTED = "contacted"
    CLOSED = "closed"
    IGNORED = "ignored"


class OpenWebLead(Base):
    __tablename__ = "open_web_leads"

    id = Column(Integer, primary_key=True, index=True)

    # Source of the lead (e.g., "acme-logistics.com")
    source = Column(String(255), nullable=False)

    # Lead title or shipment description
    title = Column(String(500), nullable=False)

    origin = Column(String(255), nullable=True)
    destination = Column(String(255), nullable=True)
    weight_lbs = Column(Integer, nullable=True)
    equipment = Column(String(100), nullable=True)

    contact_email = Column(String(255), nullable=True)
    contact_phone = Column(String(100), nullable=True)
    contact_name = Column(String(255), nullable=True)

    raw_url = Column(Text, nullable=False)
    posted_at = Column(DateTime, nullable=True)

    # Priority / confidence score
    score = Column(Integer, nullable=True)

    status = Column(
        String(50),
        nullable=False,
        default=OpenWebLeadStatus.NEW.value,
        index=True,
    )

    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    __table_args__ = (
        # raw_url + title → considered a duplicate lead
        UniqueConstraint("raw_url", "title", name="uq_open_web_leads_url_title"),
    )

    def __repr__(self) -> str:
        return f"<OpenWebLead(id={self.id}, source={self.source}, title={self.title})>"

