from __future__ import annotations

from datetime import date
from uuid import uuid4

from sqlalchemy import (
    Column,
    String,
    Boolean,
    Date,
    DateTime,
    Numeric,
    ForeignKey,
    Text,
    Integer,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from backend.database.base import Base


class Partner(Base):
    __tablename__ = "partners"  # type: ignore[assignment]

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    code = Column(String(32), nullable=False, unique=True)
    name = Column(String(255), nullable=False)
    partner_type = Column(String(32), nullable=False)  # 'individual' | 'company' | 'agency'

    email = Column(String(255), nullable=False, unique=True)
    phone = Column(String(64), nullable=True)
    address_text = Column(Text, nullable=True)

    bank_account_name = Column(String(255), nullable=True)
    bank_account_iban = Column(String(64), nullable=True)
    bank_account_swift = Column(String(64), nullable=True)
    bank_details_json = Column(JSONB, nullable=True)

    default_b2b_share = Column(Numeric(5, 2), nullable=False, default=60.00)
    default_b2c_share = Column(Numeric(5, 2), nullable=False, default=70.00)
    default_marketplace_share = Column(Numeric(5, 2), nullable=False, default=80.00)

    revenue_total = Column(Numeric(18, 2), nullable=False, default=0)
    revenue_pending = Column(Numeric(18, 2), nullable=False, default=0)
    revenue_paid = Column(Numeric(18, 2), nullable=False, default=0)

    status = Column(String(32), nullable=False, default="pending")  # 'pending' | 'active' | 'suspended' | 'closed'

    joined_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    created_by_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    created_by_user = relationship("backend.models.user.User", lazy="joined")  # No back_populates - User.created_partners not defined

    clients = relationship(
        "PartnerClient",
        back_populates="partner",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    revenues = relationship(
        "PartnerRevenue",
        back_populates="partner",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    payouts = relationship(
        "PartnerPayout",
        back_populates="partner",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    agreements = relationship(
        "PartnerAgreement",
        back_populates="partner",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class PartnerClient(Base):
    __tablename__ = "partner_clients"  # type: ignore[assignment]

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    partner_id = Column(UUID(as_uuid=True), ForeignKey("partners.id", ondelete="CASCADE"), nullable=False)
    client_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    relationship_started_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    relationship_channel = Column(String(32), nullable=False)  # 'link' | 'code' | 'admin'
    is_active = Column(Boolean, nullable=False, default=True)

    partner = relationship("Partner", back_populates="clients", lazy="joined")
    # adjust target model if you have a dedicated Client model instead of User
    client = relationship(
        "backend.models.user.User",
        lazy="joined",
    )


class PartnerRevenue(Base):
    __tablename__ = "partner_revenue"  # type: ignore[assignment]

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    partner_id = Column(UUID(as_uuid=True), ForeignKey("partners.id", ondelete="CASCADE"), nullable=False)
    client_id = Column(UUID(as_uuid=True), nullable=True)
    order_id = Column(UUID(as_uuid=True), nullable=False)

    service_type = Column(String(32), nullable=False)  # 'b2b' | 'b2c' | 'marketplace'
    currency_code = Column(String(3), nullable=False, default="USD")

    gross_amount = Column(Numeric(18, 2), nullable=False)
    net_profit_amount = Column(Numeric(18, 2), nullable=False)
    partner_share_percent = Column(Numeric(5, 2), nullable=False)
    partner_amount = Column(Numeric(18, 2), nullable=False)
    gts_amount = Column(Numeric(18, 2), nullable=False)

    status = Column(
        String(32),
        nullable=False,
        default="pending",  # 'pending' | 'confirmed' | 'rejected' | 'settled' | 'paid'
    )

    period_year = Column(Integer, nullable=False)
    period_month = Column(Integer, nullable=False)

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    partner = relationship("Partner", back_populates="revenues", lazy="joined")


class PartnerPayout(Base):
    __tablename__ = "partner_payouts"  # type: ignore[assignment]

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    partner_id = Column(UUID(as_uuid=True), ForeignKey("partners.id", ondelete="CASCADE"), nullable=False)

    currency_code = Column(String(3), nullable=False, default="USD")
    total_amount = Column(Numeric(18, 2), nullable=False)
    fees_amount = Column(Numeric(18, 2), nullable=False, default=0)
    net_amount = Column(Numeric(18, 2), nullable=False)

    period_start_date = Column(Date, nullable=False)
    period_end_date = Column(Date, nullable=False)

    status = Column(
        String(32),
        nullable=False,
        default="requested",  # 'requested' | 'under_review' | 'approved' | 'paid' | 'rejected'
    )

    requested_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    approved_at = Column(DateTime(timezone=True), nullable=True)
    paid_at = Column(DateTime(timezone=True), nullable=True)
    rejected_at = Column(DateTime(timezone=True), nullable=True)

    payment_reference = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)

    partner = relationship("Partner", back_populates="payouts", lazy="joined")


class PartnerAgreement(Base):
    __tablename__ = "partner_agreements"  # type: ignore[assignment]

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    partner_id = Column(UUID(as_uuid=True), ForeignKey("partners.id", ondelete="CASCADE"), nullable=False)

    agreement_version = Column(String(32), nullable=False)
    agreement_text_hash = Column(String(128), nullable=False)

    signed_at = Column(DateTime(timezone=True), nullable=False)
    ip_address = Column(String(64), nullable=True)
    user_agent = Column(Text, nullable=True)
    signature_name = Column(String(255), nullable=False)
    signature_hash = Column(String(128), nullable=False)

    pdf_url = Column(Text, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    partner = relationship("Partner", back_populates="agreements", lazy="joined")


# Logistics Partners Model for carriers, shippers, brokers, suppliers, customers
class LogisticsPartner(Base):
    __tablename__ = "logistics_partners"  # type: ignore[assignment]

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)
    type = Column(String(32), nullable=False)  # 'carrier', 'shipper', 'broker', 'supplier', 'customer'
    email = Column(String(255), nullable=True)
    phone = Column(String(64), nullable=True)
    address = Column(Text, nullable=True)
    contact_person = Column(String(255), nullable=True)
    mc_number = Column(String(32), nullable=True)  # Motor Carrier number
    dot_number = Column(String(32), nullable=True)  # DOT number
    tax_id = Column(String(32), nullable=True)
    website = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)
    status = Column(String(32), nullable=False, default="active")  # 'active', 'inactive', 'pending'
    rating = Column(Integer, nullable=True)  # 1-5 stars
    tags = Column(JSONB, nullable=True, default=list)  # List of tags

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    users = relationship("User", back_populates="partner", lazy="selectin")
    shipments_as_carrier = relationship(
        "backend.models.models.Shipment",
        foreign_keys="backend.models.models.Shipment.carrier_id",
        back_populates="carrier_partner",
        lazy="selectin",
    )
    shipments_as_shipper = relationship(
        "backend.models.models.Shipment",
        foreign_keys="backend.models.models.Shipment.shipper_id",
        back_populates="shipper_partner",
        lazy="selectin",
    )
    shipments_as_broker = relationship(
        "backend.models.models.Shipment",
        foreign_keys="backend.models.models.Shipment.broker_id",
        back_populates="broker_partner",
        lazy="selectin",
    )

    def __repr__(self):
        return f"<LogisticsPartner(id={self.id}, name='{self.name}', type='{self.type}')>"
