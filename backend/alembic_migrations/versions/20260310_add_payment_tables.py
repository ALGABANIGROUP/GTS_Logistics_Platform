"""Add payment tables for SUDAPAY integration

Revision ID: 20260310_add_payment_tables
Revises: faab766d1a0f
Create Date: 2026-03-10

Payment system tables:
- payments: Core payment records
- payment_methods: Secure payment tokens
- payment_transactions: Audit trail
- refunds: Refund tracking
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '20260310_add_payment_tables'
down_revision = 'faab766d1a0f'
branch_labels = None
depends_on = None


def upgrade():
    # Create payment_methods table
    op.create_table(
        'payment_methods',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('method_type', sa.VARCHAR(length=20), nullable=False),
        sa.Column('token', sa.VARCHAR(length=200), nullable=False),
        sa.Column('display_name', sa.VARCHAR(length=100), nullable=True),
        sa.Column('brand', sa.VARCHAR(length=50), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('is_default', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('gateway', sa.VARCHAR(length=20), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('token', 'user_id', name='uq_payment_methods_token_user'),
    )
    op.create_index('ix_payment_methods_user_id', 'payment_methods', ['user_id'])
    op.create_index('ix_payment_methods_is_default', 'payment_methods', ['is_default'])

    # Create payments table
    op.create_table(
        'payments',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('reference_id', sa.VARCHAR(length=50), nullable=False),
        sa.Column('invoice_id', sa.BigInteger(), nullable=False),
        sa.Column('payment_method_id', sa.BigInteger(), nullable=True),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('amount', sa.DECIMAL(precision=10, scale=2), nullable=False),
        sa.Column('currency', sa.VARCHAR(length=3), nullable=False, server_default='SDG'),
        sa.Column('status', sa.VARCHAR(length=20), nullable=False, server_default='pending'),
        sa.Column('payment_gateway', sa.VARCHAR(length=20), nullable=False),
        sa.Column('gateway_transaction_id', sa.VARCHAR(length=100), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['invoice_id'], ['invoices.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['payment_method_id'], ['payment_methods.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('reference_id', name='uq_payments_reference_id'),
    )
    op.create_index('ix_payments_reference_id', 'payments', ['reference_id'])
    op.create_index('ix_payments_invoice_id', 'payments', ['invoice_id'])
    op.create_index('ix_payments_user_id', 'payments', ['user_id'])
    op.create_index('ix_payments_status', 'payments', ['status'])
    op.create_index('ix_payments_payment_gateway', 'payments', ['payment_gateway'])
    op.create_index('ix_payments_gateway_transaction_id', 'payments', ['gateway_transaction_id'])
    op.create_index('ix_payments_created_at', 'payments', ['created_at'])

    # Create payment_transactions table
    op.create_table(
        'payment_transactions',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('payment_id', sa.BigInteger(), nullable=False),
        sa.Column('transaction_type', sa.VARCHAR(length=20), nullable=False),
        sa.Column('amount', sa.DECIMAL(precision=10, scale=2), nullable=False),
        sa.Column('status', sa.VARCHAR(length=20), nullable=False),
        sa.Column('error_code', sa.VARCHAR(length=50), nullable=True),
        sa.Column('error_message', sa.VARCHAR(length=500), nullable=True),
        sa.Column('gateway_response', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['payment_id'], ['payments.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_payment_transactions_payment_id', 'payment_transactions', ['payment_id'])
    op.create_index('ix_payment_transactions_transaction_type', 'payment_transactions', ['transaction_type'])
    op.create_index('ix_payment_transactions_status', 'payment_transactions', ['status'])
    op.create_index('ix_payment_transactions_created_at', 'payment_transactions', ['created_at'])

    # Create refunds table
    op.create_table(
        'refunds',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('reference_id', sa.VARCHAR(length=50), nullable=False),
        sa.Column('payment_id', sa.BigInteger(), nullable=False),
        sa.Column('amount', sa.DECIMAL(precision=10, scale=2), nullable=False),
        sa.Column('reason', sa.VARCHAR(length=200), nullable=True),
        sa.Column('status', sa.VARCHAR(length=20), nullable=False, server_default='pending'),
        sa.Column('gateway_refund_id', sa.VARCHAR(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['payment_id'], ['payments.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('reference_id', name='uq_refunds_reference_id'),
    )
    op.create_index('ix_refunds_reference_id', 'refunds', ['reference_id'])
    op.create_index('ix_refunds_payment_id', 'refunds', ['payment_id'])
    op.create_index('ix_refunds_status', 'refunds', ['status'])
    op.create_index('ix_refunds_created_at', 'refunds', ['created_at'])


def downgrade():
    op.drop_index('ix_refunds_created_at', table_name='refunds')
    op.drop_index('ix_refunds_status', table_name='refunds')
    op.drop_index('ix_refunds_payment_id', table_name='refunds')
    op.drop_index('ix_refunds_reference_id', table_name='refunds')
    op.drop_table('refunds')

    op.drop_index('ix_payment_transactions_created_at', table_name='payment_transactions')
    op.drop_index('ix_payment_transactions_status', table_name='payment_transactions')
    op.drop_index('ix_payment_transactions_transaction_type', table_name='payment_transactions')
    op.drop_index('ix_payment_transactions_payment_id', table_name='payment_transactions')
    op.drop_table('payment_transactions')

    op.drop_index('ix_payments_created_at', table_name='payments')
    op.drop_index('ix_payments_gateway_transaction_id', table_name='payments')
    op.drop_index('ix_payments_payment_gateway', table_name='payments')
    op.drop_index('ix_payments_status', table_name='payments')
    op.drop_index('ix_payments_user_id', table_name='payments')
    op.drop_index('ix_payments_invoice_id', table_name='payments')
    op.drop_index('ix_payments_reference_id', table_name='payments')
    op.drop_table('payments')

    op.drop_index('ix_payment_methods_is_default', table_name='payment_methods')
    op.drop_index('ix_payment_methods_user_id', table_name='payment_methods')
    op.drop_table('payment_methods')
