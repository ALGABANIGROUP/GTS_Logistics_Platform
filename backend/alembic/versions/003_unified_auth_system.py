"""
Migration: Create unified authentication tables and multi-system permissions

Run using:
python -m alembic -c backend/alembic.ini revision --autogenerate -m "unified_auth_system"
"""

from alembic import op
import sqlalchemy as sa


def upgrade():
    """Add unified authentication tables"""
    
    # Unified users table (if not exists)
    op.create_table(
        'unified_users',
        sa.Column('id', sa.UUID(), nullable=False, primary_key=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('password_hash', sa.String(500), nullable=False),
        sa.Column('full_name', sa.String(255), nullable=False),
        sa.Column('phone', sa.String(20), nullable=True),
        sa.Column('company_name', sa.String(255), nullable=True),
        sa.Column('country', sa.String(100), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('email_verified', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('last_login', sa.DateTime(), nullable=True),
    )
    
    # Multi-system permissions table
    op.create_table(
        'user_systems_access',
        sa.Column('id', sa.UUID(), nullable=False, primary_key=True),
        sa.Column('user_id', sa.UUID(), sa.ForeignKey('unified_users.id'), nullable=False),
        sa.Column('system_type', sa.String(50), nullable=False),  # 'gts_main', 'tms'
        sa.Column('access_level', sa.String(50), nullable=False),  # 'user', 'admin', 'super_admin'
        sa.Column('subscription_plan', sa.String(50), nullable=True),  # For TMS: 'starter', 'professional', 'enterprise'
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('granted_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.UniqueConstraint('user_id', 'system_type', name='uq_user_system'),
    )
    
    # Audit log table - track logins and activities
    op.create_table(
        'auth_audit_log',
        sa.Column('id', sa.UUID(), nullable=False, primary_key=True),
        sa.Column('user_id', sa.UUID(), sa.ForeignKey('unified_users.id'), nullable=True),
        sa.Column('action', sa.String(100), nullable=False),  # 'login', 'logout', 'system_switch', 'access_denied'
        sa.Column('system_type', sa.String(50), nullable=True),
        sa.Column('ip_address', sa.String(50), nullable=True),
        sa.Column('user_agent', sa.String(500), nullable=True),
        sa.Column('success', sa.Boolean(), default=False),
        sa.Column('details', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
    )
    
    # Subscriptions table
    op.create_table(
        'tms_subscriptions',
        sa.Column('id', sa.UUID(), nullable=False, primary_key=True),
        sa.Column('company_id', sa.UUID(), nullable=False),
        sa.Column('plan_name', sa.String(50), nullable=False),  # 'starter', 'professional', 'enterprise'
        sa.Column('plan_tier', sa.String(50), nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('started_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('auto_renew', sa.Boolean(), default=True),
        sa.Column('features', sa.JSON(), nullable=True),
        sa.Column('max_shipments_per_month', sa.Integer(), default=-1),  # -1 for unlimited
        sa.Column('max_team_members', sa.Integer(), default=-1),
    )


def downgrade():
    """Remove unified authentication tables"""
    op.drop_table('tms_subscriptions')
    op.drop_table('auth_audit_log')
    op.drop_table('user_systems_access')
    op.drop_table('unified_users')
