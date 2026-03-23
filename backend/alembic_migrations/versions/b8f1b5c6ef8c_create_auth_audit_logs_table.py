"""create_auth_audit_logs_table

Revision ID: b8f1b5c6ef8c
Revises: 63526f3227a3
Create Date: 2026-01-23 15:19:57.836748

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b8f1b5c6ef8c'
down_revision: Union[str, Sequence[str], None] = '63526f3227a3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create auth_audit_logs table
    op.create_table('auth_audit_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('action', sa.String(length=50), nullable=False),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.String(length=255), nullable=True),
        sa.Column('details', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    # Create indexes
    op.create_index(op.f('ix_auth_audit_logs_id'), 'auth_audit_logs', ['id'], unique=False)
    op.create_index(op.f('ix_auth_audit_logs_user_id'), 'auth_audit_logs', ['user_id'], unique=False)
    op.create_index(op.f('ix_auth_audit_logs_action'), 'auth_audit_logs', ['action'], unique=False)
    op.create_index(op.f('ix_auth_audit_logs_created_at'), 'auth_audit_logs', ['created_at'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Drop auth_audit_logs table
    op.drop_index(op.f('ix_auth_audit_logs_created_at'), table_name='auth_audit_logs')
    op.drop_index(op.f('ix_auth_audit_logs_action'), table_name='auth_audit_logs')
    op.drop_index(op.f('ix_auth_audit_logs_user_id'), table_name='auth_audit_logs')
    op.drop_index(op.f('ix_auth_audit_logs_id'), table_name='auth_audit_logs')
    op.drop_table('auth_audit_logs')
