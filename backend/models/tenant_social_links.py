from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy import String, Boolean, Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from backend.database.base import Base


class TenantSocialLinks(Base):
    """Social media links per tenant for branding and footer display.

    Stores social media platform links that can be customized per tenant.
    Used in footer and other branding locations.
    """

    __tablename__ = "tenant_social_links"
    __table_args__ = (
        UniqueConstraint("tenant_id", "platform", name="uq_tenant_social_links_tenant_platform"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(64), ForeignKey("tenants.id"), nullable=False)
    platform: Mapped[str] = mapped_column(String(30), nullable=False)  # linkedin, x, facebook, youtube, instagram
    url: Mapped[str] = mapped_column(String, nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    updated_by: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)  # user UUID
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
