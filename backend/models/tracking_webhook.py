from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Enum, Float, ForeignKey, Index, Integer, JSON, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from backend.database.base import Base
from backend.schemas.webhook import InvoiceStatus, ShipmentStatus


class TrackingShipment(Base):
    __tablename__ = "tracking_shipments"

    id = Column(Integer, primary_key=True, index=True)
    external_tracking_id = Column(String, unique=True, index=True, nullable=False)
    shipment_reference = Column(String, index=True, nullable=True)
    status = Column(
        Enum(ShipmentStatus, name="shipment_status_enum"),
        default=ShipmentStatus.created,
        index=True,
        nullable=False,
    )

    created_at = Column(DateTime, server_default=func.now(), index=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    picked_up_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)

    shipper_id = Column(Integer, index=True, nullable=True)
    consignee_id = Column(Integer, index=True, nullable=True)
    carrier_id = Column(Integer, index=True, nullable=True)
    broker_id = Column(Integer, index=True, nullable=True)

    invoice_id = Column(Integer, index=True, nullable=True)
    metadata_json = Column("metadata", JSON, default=dict)

    __table_args__ = (
        Index("idx_tracking_shipments_status_date", "status", "created_at"),
        Index("idx_tracking_shipments_tracking_reference", "external_tracking_id", "shipment_reference"),
        Index("idx_tracking_shipments_carrier_status", "carrier_id", "status"),
    )


class TrackingEvent(Base):
    __tablename__ = "tracking_events"

    id = Column(Integer, primary_key=True, index=True)
    shipment_id = Column(Integer, ForeignKey("tracking_shipments.id", ondelete="CASCADE"), nullable=False, index=True)
    event_type = Column(Enum(ShipmentStatus, name="shipment_status_enum"), nullable=False, index=True)
    event_time = Column(DateTime, nullable=False, index=True)
    location = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    metadata_json = Column("metadata", JSON, default=dict)
    webhook_received_at = Column(DateTime, server_default=func.now())
    processed = Column(Boolean, default=False, index=True)

    __table_args__ = (
        Index("idx_tracking_events_shipment_time", "shipment_id", "event_time"),
        Index("idx_tracking_events_processed_time", "processed", "webhook_received_at"),
    )


class TrackingInvoice(Base):
    __tablename__ = "tracking_invoices"

    id = Column(Integer, primary_key=True, index=True)
    invoice_number = Column(String, unique=True, index=True, nullable=False)
    shipment_id = Column(Integer, ForeignKey("tracking_shipments.id", ondelete="SET NULL"), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    tax_amount = Column(Float, default=0.0)
    total_amount = Column(Float, nullable=False)
    currency = Column(String(3), default="USD")
    issue_date = Column(DateTime, server_default=func.now())
    due_date = Column(DateTime, nullable=False, index=True)
    paid_at = Column(DateTime, nullable=True)
    status = Column(Enum(InvoiceStatus, name="invoice_status_enum"), default=InvoiceStatus.pending, index=True)
    pdf_url = Column(String, nullable=True)
    line_items = Column(JSON, default=list)
    customer_id = Column(Integer, index=True, nullable=False)
    carrier_id = Column(Integer, index=True, nullable=True)
    metadata_json = Column("metadata", JSON, default=dict)

    __table_args__ = (
        Index("idx_tracking_invoice_status_due", "status", "due_date"),
        Index("idx_tracking_invoice_customer_date", "customer_id", "issue_date"),
        Index("idx_tracking_invoice_carrier", "carrier_id", "status"),
    )


class WebhookLog(Base):
    __tablename__ = "webhook_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(String, index=True, nullable=True)
    endpoint = Column(String, nullable=True)
    payload = Column(JSON, nullable=True)
    signature = Column(String, nullable=True)
    headers = Column(JSON, nullable=True)
    idempotency_key = Column(String, unique=True, index=True, nullable=True)
    received_at = Column(DateTime, server_default=func.now(), index=True)
    processed = Column(Boolean, default=False, index=True)
    processed_at = Column(DateTime, nullable=True)
    error = Column(Text, nullable=True)
    response_status = Column(Integer, nullable=True)

    __table_args__ = (
        Index("idx_webhook_client_time", "client_id", "received_at"),
        Index("idx_webhook_processed_status", "processed", "response_status"),
    )

