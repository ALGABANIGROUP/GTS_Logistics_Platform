"""add_tenant_social_links_table

Revision ID: 2837ab1f9c72
Revises: f23ea0942a9a
Create Date: 2026-01-17 18:22:11.014601

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2837ab1f9c72'
down_revision: Union[str, Sequence[str], None] = 'f23ea0942a9a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'tenant_social_links',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('tenant_id', sa.String(64), nullable=False),
        sa.Column('platform', sa.String(30), nullable=False),
        sa.Column('url', sa.Text(), nullable=False),
        sa.Column('enabled', sa.Boolean(), nullable=False, default=True),
        sa.Column('sort_order', sa.Integer(), nullable=False, default=0),
        sa.Column('updated_by', sa.String(36), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
        sa.UniqueConstraint('tenant_id', 'platform', name='uq_tenant_social_links_tenant_platform')
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('tenant_social_links')
