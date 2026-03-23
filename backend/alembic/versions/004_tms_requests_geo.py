"""Add TMS registration requests and geo restrictions tables

Revision ID: 004_tms_requests_geo
Revises: 003_add_unified_system
Create Date: 2026-01-08 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '004_tms_requests_geo'
down_revision = '003_add_unified_system'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create tms_registration_requests table
    op.create_table(
        'tms_registration_requests',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('company_name', sa.String(length=255), nullable=False),
        sa.Column('contact_name', sa.String(length=255), nullable=False),
        sa.Column('contact_email', sa.String(length=255), nullable=False),
        sa.Column('contact_phone', sa.String(length=50), nullable=True),
        sa.Column('company_website', sa.String(length=255), nullable=True),
        sa.Column('industry_type', sa.String(length=100), nullable=True),
        sa.Column('country_code', sa.String(length=10), nullable=True),
        sa.Column('state_province', sa.String(length=100), nullable=True),
        sa.Column('city', sa.String(length=100), nullable=True),
        sa.Column('request_ip', sa.String(length=50), nullable=True),
        sa.Column('requested_plan', sa.String(length=50), nullable=False, server_default='starter'),
        sa.Column('company_data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('notes', sa.String(length=1000), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='pending'),
        sa.Column('reviewed_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('rejection_reason', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['unified_users.id'], name='fk_tms_request_user'),
        sa.ForeignKeyConstraint(['reviewed_by'], ['unified_users.id'], name='fk_tms_request_reviewer'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tms_registration_requests_created_at'), 'tms_registration_requests', ['created_at'], unique=False)

    # Create geo_restrictions table
    op.create_table(
        'geo_restrictions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('feature_name', sa.String(length=100), nullable=False),
        sa.Column('allowed_countries', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('restriction_message', sa.String(length=500), nullable=True),
        sa.Column('fallback_behavior', sa.String(length=50), nullable=False, server_default='block'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('feature_name', name='uq_geo_restriction_feature')
    )

    # Seed default geo restriction for load_board
    op.execute("""
        INSERT INTO geo_restrictions (id, feature_name, allowed_countries, is_active, restriction_message, fallback_behavior)
        VALUES (
            gen_random_uuid(),
            'load_board',
            '["US", "CA"]'::json,
            true,
            'Load Board feature is only available in United States and Canada',
            'block'
        )
    """)


def downgrade() -> None:
    op.drop_table('geo_restrictions')
    op.drop_index(op.f('ix_tms_registration_requests_created_at'), table_name='tms_registration_requests')
    op.drop_table('tms_registration_requests')
