"""Alembic migration: Add platform infrastructure expenses table"""

revision = 'platform_infra_exp_001'
down_revision = None  # Replace with your current head revision
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
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


def downgrade():
    op.drop_index('ix_platform_infrastructure_expenses_id', table_name='platform_infrastructure_expenses')
    op.drop_index('ix_platform_infra_exp_is_active', table_name='platform_infrastructure_expenses')
    op.drop_index('ix_platform_infra_exp_is_paid', table_name='platform_infrastructure_expenses')
    op.drop_index('ix_platform_infra_exp_billing_date', table_name='platform_infrastructure_expenses')
    op.drop_index('ix_platform_infra_exp_vendor', table_name='platform_infrastructure_expenses')
    op.drop_index('ix_platform_infra_exp_category', table_name='platform_infrastructure_expenses')
    op.drop_table('platform_infrastructure_expenses')
