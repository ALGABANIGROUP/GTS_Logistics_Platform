"""Add normalized plan invoice columns and backfill from encoded invoice number.

Revision ID: 20260314_plan_invoice_cols
Revises: 20260310_add_payment_tables
Create Date: 2026-03-14 00:00:00.000000
"""

from __future__ import annotations

import re

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision = "20260314_plan_invoice_cols"
down_revision = "20260310_add_payment_tables"
branch_labels = None
depends_on = None


_PLAN_PATTERN = re.compile(r"^PLANINV-([A-Z0-9_]+)-U([0-9]+)-")


def _has_column(table_name: str, column_name: str) -> bool:
    bind = op.get_bind()
    inspector = inspect(bind)
    columns = inspector.get_columns(table_name)
    return any(col.get("name") == column_name for col in columns)


def _has_index(table_name: str, index_name: str) -> bool:
    bind = op.get_bind()
    inspector = inspect(bind)
    indexes = inspector.get_indexes(table_name)
    return any(idx.get("name") == index_name for idx in indexes)


def _backfill_plan_invoice_columns() -> None:
    bind = op.get_bind()

    rows = bind.execute(sa.text("SELECT id, number FROM invoices WHERE number LIKE 'PLANINV-%'"))
    for row in rows:
        invoice_id = row[0]
        invoice_number = row[1] or ""
        match = _PLAN_PATTERN.match(invoice_number)
        if not match:
            continue

        bind.execute(
            sa.text(
                """
                UPDATE invoices
                SET plan_code = :plan_code,
                    user_id = :user_id
                WHERE id = :invoice_id
                """
            ),
            {
                "plan_code": match.group(1),
                "user_id": int(match.group(2)),
                "invoice_id": invoice_id,
            },
        )


def upgrade() -> None:
    if not _has_column("invoices", "plan_code"):
        op.add_column("invoices", sa.Column("plan_code", sa.String(length=50), nullable=True))

    if not _has_column("invoices", "user_id"):
        op.add_column("invoices", sa.Column("user_id", sa.Integer(), nullable=True))

    _backfill_plan_invoice_columns()

    if not _has_index("invoices", "ix_invoices_plan_code"):
        op.create_index("ix_invoices_plan_code", "invoices", ["plan_code"], unique=False)

    if not _has_index("invoices", "ix_invoices_user_id"):
        op.create_index("ix_invoices_user_id", "invoices", ["user_id"], unique=False)


def downgrade() -> None:
    if _has_index("invoices", "ix_invoices_user_id"):
        op.drop_index("ix_invoices_user_id", table_name="invoices")

    if _has_index("invoices", "ix_invoices_plan_code"):
        op.drop_index("ix_invoices_plan_code", table_name="invoices")

    if _has_column("invoices", "user_id"):
        op.drop_column("invoices", "user_id")

    if _has_column("invoices", "plan_code"):
        op.drop_column("invoices", "plan_code")
