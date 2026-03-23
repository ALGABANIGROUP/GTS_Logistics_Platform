"""add_platform_infrastructure_expenses

Revision ID: c1c4546306e6
Revises: 7fe56a940afa
Create Date: 2026-01-08 09:11:49.448055

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c1c4546306e6'
down_revision: Union[str, Sequence[str], None] = '7fe56a940afa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create platform_infrastructure_expenses table"""
    op.create_table(
        'platform_infrastructure_expenses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('category', sa.String(), nullable=False),
        sa.Column('service_name', sa.String(), nullable=False),
        sa.Column('vendor', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('currency', sa.String(), nullable=False),
        sa.Column('billing_frequency', sa.String(), nullable=False),
        sa.Column('is_recurring', sa.Boolean(), nullable=True),
        sa.Column('invoice_number', sa.String(), nullable=True),
        sa.Column('invoice_url', sa.String(), nullable=True),
        sa.Column('attachment_path', sa.String(), nullable=True),
        sa.Column('billing_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('due_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('paid_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_paid', sa.Boolean(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('notes', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_platform_infra_exp_category', 'platform_infrastructure_expenses', ['category'], unique=False)
    op.create_index('ix_platform_infra_exp_vendor', 'platform_infrastructure_expenses', ['vendor'], unique=False)
    op.create_index('ix_platform_infra_exp_billing_date', 'platform_infrastructure_expenses', ['billing_date'], unique=False)
    op.create_index('ix_platform_infra_exp_is_paid', 'platform_infrastructure_expenses', ['is_paid'], unique=False)
    op.create_index('ix_platform_infra_exp_is_active', 'platform_infrastructure_expenses', ['is_active'], unique=False)
    op.create_index('ix_platform_infrastructure_expenses_id', 'platform_infrastructure_expenses', ['id'], unique=False)


def downgrade() -> None:
    """Drop platform_infrastructure_expenses table"""
    op.drop_index('ix_platform_infrastructure_expenses_id', table_name='platform_infrastructure_expenses')
    op.drop_index('ix_platform_infra_exp_is_active', table_name='platform_infrastructure_expenses')
    op.drop_index('ix_platform_infra_exp_is_paid', table_name='platform_infrastructure_expenses')
    op.drop_index('ix_platform_infra_exp_billing_date', table_name='platform_infrastructure_expenses')
    op.drop_index('ix_platform_infra_exp_vendor', table_name='platform_infrastructure_expenses')
    op.drop_index('ix_platform_infra_exp_category', table_name='platform_infrastructure_expenses')
    op.drop_table('platform_infrastructure_expenses')
