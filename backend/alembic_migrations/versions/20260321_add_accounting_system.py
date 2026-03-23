"""Add accounting system tables

Revision ID: 20260321_add_accounting_system
Revises: 20260314_plan_invoice_cols
Create Date: 2026-03-21
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260321_add_accounting_system"
down_revision = "20260314_plan_invoice_cols"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "accounts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("account_code", sa.String(length=20), nullable=False),
        sa.Column("account_name", sa.String(length=200), nullable=False),
        sa.Column("account_type", sa.String(length=20), nullable=False),
        sa.Column("parent_id", sa.Integer(), nullable=True),
        sa.Column("level", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("normal_balance", sa.String(length=20), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["parent_id"], ["accounts.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("account_code", name="uq_accounts_account_code"),
    )
    op.create_index("ix_accounts_account_code", "accounts", ["account_code"])
    op.create_index("ix_accounts_account_type", "accounts", ["account_type"])

    op.create_table(
        "journal_entries",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("entry_number", sa.String(length=50), nullable=False),
        sa.Column("entry_date", sa.Date(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("reference_type", sa.String(length=50), nullable=True),
        sa.Column("reference_id", sa.String(length=100), nullable=True),
        sa.Column("posted_by", sa.String(length=100), nullable=True),
        sa.Column("posted_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("is_posted", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("entry_number", name="uq_journal_entries_entry_number"),
    )
    op.create_index("ix_journal_entries_entry_date", "journal_entries", ["entry_date"])
    op.create_index("ix_journal_entries_reference", "journal_entries", ["reference_type", "reference_id"])

    op.create_table(
        "journal_entry_lines",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("entry_id", sa.Integer(), nullable=False),
        sa.Column("account_id", sa.Integer(), nullable=False),
        sa.Column("debit", sa.Float(), nullable=False, server_default="0"),
        sa.Column("credit", sa.Float(), nullable=False, server_default="0"),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["account_id"], ["accounts.id"]),
        sa.ForeignKeyConstraint(["entry_id"], ["journal_entries.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_journal_entry_lines_entry_id", "journal_entry_lines", ["entry_id"])
    op.create_index("ix_journal_entry_lines_account_id", "journal_entry_lines", ["account_id"])

    op.create_table(
        "account_balances",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("account_id", sa.Integer(), nullable=False),
        sa.Column("balance_date", sa.Date(), nullable=False),
        sa.Column("opening_balance", sa.Float(), nullable=False, server_default="0"),
        sa.Column("total_debit", sa.Float(), nullable=False, server_default="0"),
        sa.Column("total_credit", sa.Float(), nullable=False, server_default="0"),
        sa.Column("closing_balance", sa.Float(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["account_id"], ["accounts.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("account_id", "balance_date", name="uq_account_balances_account_date"),
    )

    op.create_table(
        "accounting_invoices",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("invoice_number", sa.String(length=50), nullable=False),
        sa.Column("invoice_date", sa.Date(), nullable=False),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column("customer_id", sa.Integer(), nullable=True),
        sa.Column("customer_name", sa.String(length=200), nullable=True),
        sa.Column("total_amount", sa.Float(), nullable=False),
        sa.Column("tax_amount", sa.Float(), nullable=False, server_default="0"),
        sa.Column("discount_amount", sa.Float(), nullable=False, server_default="0"),
        sa.Column("net_amount", sa.Float(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="draft"),
        sa.Column("journal_entry_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["journal_entry_id"], ["journal_entries.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("invoice_number", name="uq_accounting_invoices_invoice_number"),
    )
    op.create_index("ix_accounting_invoices_status", "accounting_invoices", ["status"])
    op.create_index("ix_accounting_invoices_invoice_date", "accounting_invoices", ["invoice_date"])

    op.create_table(
        "expense_invoices",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("invoice_number", sa.String(length=50), nullable=False),
        sa.Column("invoice_date", sa.Date(), nullable=False),
        sa.Column("supplier_name", sa.String(length=200), nullable=True),
        sa.Column("total_amount", sa.Float(), nullable=False),
        sa.Column("tax_amount", sa.Float(), nullable=False, server_default="0"),
        sa.Column("net_amount", sa.Float(), nullable=False),
        sa.Column("expense_account_id", sa.Integer(), nullable=False),
        sa.Column("journal_entry_id", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["expense_account_id"], ["accounts.id"]),
        sa.ForeignKeyConstraint(["journal_entry_id"], ["journal_entries.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("invoice_number", name="uq_expense_invoices_invoice_number"),
    )
    op.create_index("ix_expense_invoices_status", "expense_invoices", ["status"])

    op.create_table(
        "financial_reports",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("report_type", sa.String(length=30), nullable=False),
        sa.Column("report_date", sa.Date(), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("data", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("generated_by", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_financial_reports_report_type", "financial_reports", ["report_type"])
    op.create_index("ix_financial_reports_report_date", "financial_reports", ["report_date"])

    account_table = sa.table(
        "accounts",
        sa.column("account_code", sa.String),
        sa.column("account_name", sa.String),
        sa.column("account_type", sa.String),
        sa.column("level", sa.Integer),
        sa.column("normal_balance", sa.String),
        sa.column("description", sa.Text),
    )
    op.bulk_insert(
        account_table,
        [
            {"account_code": "1", "account_name": "Assets", "account_type": "asset", "level": 1, "normal_balance": "debit", "description": "Top-level asset accounts"},
            {"account_code": "1.1", "account_name": "Cash", "account_type": "asset", "level": 2, "normal_balance": "debit", "description": "Cash and cash equivalents"},
            {"account_code": "1.1.1", "account_name": "Cash on Hand", "account_type": "asset", "level": 3, "normal_balance": "debit", "description": "Physical cash"},
            {"account_code": "1.1.2", "account_name": "Bank Account - Main", "account_type": "asset", "level": 3, "normal_balance": "debit", "description": "Primary bank account"},
            {"account_code": "1.2", "account_name": "Accounts Receivable", "account_type": "asset", "level": 2, "normal_balance": "debit", "description": "Outstanding customer balances"},
            {"account_code": "1.3", "account_name": "Inventory", "account_type": "asset", "level": 2, "normal_balance": "debit", "description": "Inventory and stock"},
            {"account_code": "2", "account_name": "Liabilities", "account_type": "liability", "level": 1, "normal_balance": "credit", "description": "Top-level liability accounts"},
            {"account_code": "2.1", "account_name": "Accounts Payable / Tax Liability", "account_type": "liability", "level": 2, "normal_balance": "credit", "description": "Trade and tax liabilities"},
            {"account_code": "2.2", "account_name": "Loans Payable", "account_type": "liability", "level": 2, "normal_balance": "credit", "description": "Borrowed funds"},
            {"account_code": "3", "account_name": "Equity", "account_type": "equity", "level": 1, "normal_balance": "credit", "description": "Top-level equity accounts"},
            {"account_code": "3.1", "account_name": "Share Capital", "account_type": "equity", "level": 2, "normal_balance": "credit", "description": "Capital contributions"},
            {"account_code": "3.2", "account_name": "Retained Earnings", "account_type": "equity", "level": 2, "normal_balance": "credit", "description": "Accumulated earnings"},
            {"account_code": "4", "account_name": "Revenue", "account_type": "revenue", "level": 1, "normal_balance": "credit", "description": "Top-level revenue accounts"},
            {"account_code": "4.1", "account_name": "Shipping Revenue", "account_type": "revenue", "level": 2, "normal_balance": "credit", "description": "Freight and delivery revenue"},
            {"account_code": "4.2", "account_name": "Service Revenue", "account_type": "revenue", "level": 2, "normal_balance": "credit", "description": "Professional and platform service revenue"},
            {"account_code": "5", "account_name": "Expenses", "account_type": "expense", "level": 1, "normal_balance": "debit", "description": "Top-level expense accounts"},
            {"account_code": "5.1", "account_name": "Fuel Expense", "account_type": "expense", "level": 2, "normal_balance": "debit", "description": "Fuel and energy costs"},
            {"account_code": "5.2", "account_name": "Maintenance Expense", "account_type": "expense", "level": 2, "normal_balance": "debit", "description": "Maintenance and repair costs"},
            {"account_code": "5.3", "account_name": "Salaries Expense", "account_type": "expense", "level": 2, "normal_balance": "debit", "description": "Payroll costs"},
            {"account_code": "5.4", "account_name": "Sales Discounts", "account_type": "expense", "level": 2, "normal_balance": "debit", "description": "Revenue discounts and concessions"},
        ],
    )


def downgrade():
    op.drop_index("ix_financial_reports_report_date", table_name="financial_reports")
    op.drop_index("ix_financial_reports_report_type", table_name="financial_reports")
    op.drop_table("financial_reports")

    op.drop_index("ix_expense_invoices_status", table_name="expense_invoices")
    op.drop_table("expense_invoices")

    op.drop_index("ix_accounting_invoices_invoice_date", table_name="accounting_invoices")
    op.drop_index("ix_accounting_invoices_status", table_name="accounting_invoices")
    op.drop_table("accounting_invoices")

    op.drop_table("account_balances")

    op.drop_index("ix_journal_entry_lines_account_id", table_name="journal_entry_lines")
    op.drop_index("ix_journal_entry_lines_entry_id", table_name="journal_entry_lines")
    op.drop_table("journal_entry_lines")

    op.drop_index("ix_journal_entries_reference", table_name="journal_entries")
    op.drop_index("ix_journal_entries_entry_date", table_name="journal_entries")
    op.drop_table("journal_entries")

    op.drop_index("ix_accounts_account_type", table_name="accounts")
    op.drop_index("ix_accounts_account_code", table_name="accounts")
    op.drop_table("accounts")
