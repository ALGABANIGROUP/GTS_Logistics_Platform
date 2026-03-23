"""Add system_type and subscription_tier to users table

Revision ID: add_user_system_setup_002
Revises: api_connections_001
Create Date: 2026-01-15

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_user_system_setup_002'
down_revision = 'api_connections_001'
branch_labels = None
depends_on = None


def upgrade():
    # Add system_type column
    op.add_column('users', sa.Column('system_type', sa.String(50), nullable=True))
    
    # Add subscription_tier column with default value
    op.add_column('users', sa.Column('subscription_tier', sa.String(50), nullable=True, server_default='demo'))
    
    # Create indexes for better query performance
    op.create_index(op.f('ix_users_system_type'), 'users', ['system_type'])
    op.create_index(op.f('ix_users_subscription_tier'), 'users', ['subscription_tier'])


def downgrade():
    # Drop indexes
    op.drop_index(op.f('ix_users_subscription_tier'), table_name='users')
    op.drop_index(op.f('ix_users_system_type'), table_name='users')
    
    # Drop columns
    op.drop_column('users', 'subscription_tier')
    op.drop_column('users', 'system_type')
