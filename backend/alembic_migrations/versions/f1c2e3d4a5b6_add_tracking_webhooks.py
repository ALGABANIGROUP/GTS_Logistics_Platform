"""Add tracking + webhook tables

Revision ID: f1c2e3d4a5b6
Revises: b2c7d6e5f4a3
Create Date: 2026-01-06

"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "f1c2e3d4a5b6"
down_revision: Union[str, Sequence[str], None] = "b2c7d6e5f4a3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


shipment_status_enum = sa.Enum(
    "created",
    "picked_up",
    "in_transit",
    "delayed",
    "delivered",
    "cancelled",
    name="shipment_status_enum",
)

invoice_status_enum = sa.Enum(
    "draft",
    "pending",
    "sent",
    "paid",
    "overdue",
    "cancelled",
    name="invoice_status_enum",
)


def upgrade() -> None:
    bind = op.get_bind()
    shipment_status_enum.create(bind, checkfirst=True)
    invoice_status_enum.create(bind, checkfirst=True)

    op.create_table(
        "tracking_shipments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("external_tracking_id", sa.String(), nullable=False),
        sa.Column("shipment_reference", sa.String(), nullable=True),
        sa.Column("status", shipment_status_enum, nullable=False, server_default="created"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=True),
        sa.Column("picked_up_at", sa.DateTime(), nullable=True),
        sa.Column("delivered_at", sa.DateTime(), nullable=True),
        sa.Column("shipper_id", sa.Integer(), nullable=True),
        sa.Column("consignee_id", sa.Integer(), nullable=True),
        sa.Column("carrier_id", sa.Integer(), nullable=True),
        sa.Column("broker_id", sa.Integer(), nullable=True),
        sa.Column("invoice_id", sa.Integer(), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.UniqueConstraint("external_tracking_id", name="uq_tracking_shipments_external_id"),
    )
    op.create_index(
        "idx_tracking_shipments_status_date",
        "tracking_shipments",
        ["status", "created_at"],
    )
    op.create_index(
        "idx_tracking_shipments_tracking_reference",
        "tracking_shipments",
        ["external_tracking_id", "shipment_reference"],
    )
    op.create_index(
        "idx_tracking_shipments_carrier_status",
        "tracking_shipments",
        ["carrier_id", "status"],
    )

    op.create_table(
        "tracking_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("shipment_id", sa.Integer(), sa.ForeignKey("tracking_shipments.id", ondelete="CASCADE"), nullable=False),
        sa.Column("event_type", shipment_status_enum, nullable=False),
        sa.Column("event_time", sa.DateTime(), nullable=False),
        sa.Column("location", sa.String(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column("webhook_received_at", sa.DateTime(), server_default=sa.text("now()"), nullable=True),
        sa.Column("processed", sa.Boolean(), server_default=sa.text("false"), nullable=True),
    )
    op.create_index(
        "idx_tracking_events_shipment_time",
        "tracking_events",
        ["shipment_id", "event_time"],
    )
    op.create_index(
        "idx_tracking_events_processed_time",
        "tracking_events",
        ["processed", "webhook_received_at"],
    )

    op.create_table(
        "tracking_invoices",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("invoice_number", sa.String(), nullable=False),
        sa.Column("shipment_id", sa.Integer(), sa.ForeignKey("tracking_shipments.id", ondelete="SET NULL"), nullable=False),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("tax_amount", sa.Float(), nullable=True),
        sa.Column("total_amount", sa.Float(), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=True, server_default="USD"),
        sa.Column("issue_date", sa.DateTime(), server_default=sa.text("now()"), nullable=True),
        sa.Column("due_date", sa.DateTime(), nullable=False),
        sa.Column("paid_at", sa.DateTime(), nullable=True),
        sa.Column("status", invoice_status_enum, nullable=True, server_default="pending"),
        sa.Column("pdf_url", sa.String(), nullable=True),
        sa.Column("line_items", sa.JSON(), nullable=True),
        sa.Column("customer_id", sa.Integer(), nullable=False),
        sa.Column("carrier_id", sa.Integer(), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.UniqueConstraint("invoice_number", name="uq_tracking_invoice_number"),
    )
    op.create_index(
        "idx_tracking_invoice_status_due",
        "tracking_invoices",
        ["status", "due_date"],
    )
    op.create_index(
        "idx_tracking_invoice_customer_date",
        "tracking_invoices",
        ["customer_id", "issue_date"],
    )
    op.create_index(
        "idx_tracking_invoice_carrier",
        "tracking_invoices",
        ["carrier_id", "status"],
    )

    op.create_table(
        "webhook_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("client_id", sa.String(), nullable=True),
        sa.Column("endpoint", sa.String(), nullable=True),
        sa.Column("payload", sa.JSON(), nullable=True),
        sa.Column("signature", sa.String(), nullable=True),
        sa.Column("headers", sa.JSON(), nullable=True),
        sa.Column("idempotency_key", sa.String(), nullable=True),
        sa.Column("received_at", sa.DateTime(), server_default=sa.text("now()"), nullable=True),
        sa.Column("processed", sa.Boolean(), server_default=sa.text("false"), nullable=True),
        sa.Column("processed_at", sa.DateTime(), nullable=True),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("response_status", sa.Integer(), nullable=True),
        sa.UniqueConstraint("idempotency_key", name="uq_webhook_logs_idempotency"),
    )
    op.create_index("idx_webhook_client_time", "webhook_logs", ["client_id", "received_at"])
    op.create_index("idx_webhook_processed_status", "webhook_logs", ["processed", "response_status"])


def downgrade() -> None:
    op.drop_index("idx_webhook_processed_status", table_name="webhook_logs")
    op.drop_index("idx_webhook_client_time", table_name="webhook_logs")
    op.drop_table("webhook_logs")

    op.drop_index("idx_tracking_invoice_carrier", table_name="tracking_invoices")
    op.drop_index("idx_tracking_invoice_customer_date", table_name="tracking_invoices")
    op.drop_index("idx_tracking_invoice_status_due", table_name="tracking_invoices")
    op.drop_table("tracking_invoices")

    op.drop_index("idx_tracking_events_processed_time", table_name="tracking_events")
    op.drop_index("idx_tracking_events_shipment_time", table_name="tracking_events")
    op.drop_table("tracking_events")

    op.drop_index("idx_tracking_shipments_carrier_status", table_name="tracking_shipments")
    op.drop_index("idx_tracking_shipments_tracking_reference", table_name="tracking_shipments")
    op.drop_index("idx_tracking_shipments_status_date", table_name="tracking_shipments")
    op.drop_table("tracking_shipments")

    bind = op.get_bind()
    invoice_status_enum.drop(bind, checkfirst=True)
    shipment_status_enum.drop(bind, checkfirst=True)
