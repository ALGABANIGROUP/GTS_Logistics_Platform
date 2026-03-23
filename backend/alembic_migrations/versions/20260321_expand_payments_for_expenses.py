"""Expand payments table for expense payouts

Revision ID: 20260321_expand_payments_for_expenses
Revises: 20260321_add_accounting_system
Create Date: 2026-03-21
"""

from alembic import op
import sqlalchemy as sa


revision = "20260321_expand_payments_for_expenses"
down_revision = "20260321_add_accounting_system"
branch_labels = None
depends_on = None


payment_type_enum = sa.Enum("invoice", "expense", name="paymenttype")


def upgrade():
    bind = op.get_bind()
    payment_type_enum.create(bind, checkfirst=True)

    with op.batch_alter_table("payments") as batch_op:
        batch_op.alter_column("invoice_id", existing_type=sa.Integer(), nullable=True)
        batch_op.add_column(sa.Column("expense_id", sa.Integer(), nullable=True))
        batch_op.add_column(
            sa.Column(
                "payment_type",
                payment_type_enum,
                nullable=False,
                server_default="invoice",
            )
        )
        batch_op.add_column(sa.Column("supplier_name", sa.String(length=200), nullable=True))
        batch_op.create_foreign_key("fk_payments_expense_id_expenses", "expenses", ["expense_id"], ["id"])
        batch_op.create_index("idx_expense_id", ["expense_id"], unique=False)
        batch_op.create_index("idx_payment_type", ["payment_type"], unique=False)
        batch_op.create_check_constraint(
            "ck_payments_reference_type",
            "(payment_type = 'invoice' AND invoice_id IS NOT NULL AND expense_id IS NULL) "
            "OR (payment_type = 'expense' AND expense_id IS NOT NULL AND invoice_id IS NULL)",
        )


def downgrade():
    with op.batch_alter_table("payments") as batch_op:
        batch_op.drop_constraint("ck_payments_reference_type", type_="check")
        batch_op.drop_index("idx_payment_type")
        batch_op.drop_index("idx_expense_id")
        batch_op.drop_constraint("fk_payments_expense_id_expenses", type_="foreignkey")
        batch_op.drop_column("supplier_name")
        batch_op.drop_column("payment_type")
        batch_op.drop_column("expense_id")
        batch_op.alter_column("invoice_id", existing_type=sa.Integer(), nullable=False)

    payment_type_enum.drop(op.get_bind(), checkfirst=True)
