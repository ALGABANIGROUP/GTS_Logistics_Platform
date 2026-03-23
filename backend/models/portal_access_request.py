from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Text,
)
from backend.database.base import Base


class PortalAccessRequest(Base):
    __tablename__ = "portal_access_requests"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    status = Column(String(32), default="pending", index=True)

    full_name = Column(String(255), nullable=False)
    company = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, index=True)
    mobile = Column(String(64), nullable=False)

    comment = Column(Text, nullable=True)

    country = Column(String(2), nullable=False)  # "US" or "CA"
    user_type = Column(String(32), nullable=False)  # "carrier" / "broker"

    us_state = Column(String(2), nullable=True)
    dot_number = Column(String(64), nullable=True)
    mc_number = Column(String(64), nullable=True)
    us_business_address = Column(Text, nullable=True)

    ca_province = Column(String(2), nullable=True)
    ca_registered_address = Column(Text, nullable=True)
    ca_company_number = Column(String(128), nullable=True)

    document_name = Column(String(255), nullable=True)

    approved_by = Column(String(255), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    rejected_by = Column(String(255), nullable=True)
    rejected_at = Column(DateTime(timezone=True), nullable=True)
    rejection_reason = Column(Text, nullable=True)
    def __repr__(self) -> str:
        return (
            f"<PortalAccessRequest(id={self.id}, full_name={self.full_name}, "
            f"company={self.company}, email={self.email}, status={self.status})>"
        )