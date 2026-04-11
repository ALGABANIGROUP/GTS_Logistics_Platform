# backend/models/user.py
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional, List, ClassVar

from sqlalchemy import Integer, String, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship


from backend.database.base import Base
from backend.models.mixins import TenantScopedMixin

# Import Tenant before User class definition to ensure ForeignKey can resolve
from .tenant import Tenant
from .audit_log import AuditLog

if TYPE_CHECKING:
    from .document import Document
    from .audit_log import AuditLog
    from .models import Shipment as LegacyShipment


class User(Base, TenantScopedMixin):
    __tablename__: ClassVar[str] = "users"
    __table_args__ = {"extend_existing": True}

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )

    full_name: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    username: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    hashed_password: Mapped[Optional[str]] = mapped_column(
        String(512),
        nullable=True,
    )

    company: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    country: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )

    city: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )

    user_type: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )

    phone_number: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )

    system_type: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )

    subscription_tier: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        default="demo",
    )

    role: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="user",
    )

    assigned_bots: Mapped[Optional[list[str]]] = mapped_column(
        JSON,
        nullable=True,
    )

    features: Mapped[Optional[list[str]]] = mapped_column(
        JSON,
        nullable=True,
    )

    manager_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        nullable=True,
        index=True,
    )

    tenant_id: Mapped[Optional[str]] = mapped_column(
        String(64),
        ForeignKey(Tenant.id),
        nullable=True,
        index=True,
    )

    # increments whenever we want to revoke all sessions (e.g. after password change)
    token_version: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Security fields - all optional to allow gradual migration
    failed_login_attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    
    lockout_until: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    
    password_changed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    
    two_factor_enabled: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )
    
    two_factor_secret: Mapped[Optional[str]] = mapped_column(
        String(512),
        nullable=True,
    )
    
    two_factor_backup_codes: Mapped[Optional[str]] = mapped_column(
        String(2000),
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    is_banned: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    ban_reason: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )

    banned_until: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    last_login: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    # DEV: disable Document relationship to avoid mapper errors when Document model is missing.
    # documents: Mapped[List["Document"]] = relationship(
    #     "Document",
    #     back_populates="owner",
    #     lazy="select",
    #     cascade="all, delete-orphan",
    # )

    tenant: Mapped[Optional["Tenant"]] = relationship(
        lambda: Tenant,
        back_populates="users",
        lazy="select",
    )

    # Import LogisticsPartner here to avoid circular imports
    # from .partner import LogisticsPartner
    # partner: Mapped[Optional["LogisticsPartner"]] = relationship(
    #     lambda: LogisticsPartner,
    #     lazy="select",
    # )

    # Keep this relationship enabled: several auth/email flows instantiate AuditLog
    # rows through User, and CI tests rely on this mapper being configured.
    audit_logs: Mapped[List["AuditLog"]] = relationship(
        lambda: AuditLog,
        back_populates="user",
        lazy="select",
        cascade="all, delete-orphan",
    )

    shipments: Mapped[List["LegacyShipment"]] = relationship(
        "backend.models.models.Shipment",
        back_populates="user",
        lazy="select",
        cascade="all, delete-orphan",
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "email": self.email,
            "full_name": self.full_name,
            "company": self.company,
            "country": self.country,
            "city": self.city,
            "user_type": self.user_type,
            "phone_number": self.phone_number,
            "system_type": self.system_type,
            "subscription_tier": self.subscription_tier,
            "role": self.role,
            "assigned_bots": self.assigned_bots,
            "features": self.features,
            "is_active": self.is_active,
            "is_deleted": self.is_deleted,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email} name={self.full_name}>"
