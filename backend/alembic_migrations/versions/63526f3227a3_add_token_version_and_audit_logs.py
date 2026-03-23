"""add_token_version_and_audit_logs

Revision ID: 63526f3227a3
Revises: 61a9820e40e3
Create Date: 2026-01-23 15:10:31.104394

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '63526f3227a3'
down_revision: Union[str, Sequence[str], None] = '61a9820e40e3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add token_version to users table with default value
    op.add_column('users', sa.Column('token_version', sa.Integer(), nullable=True, default=0))
    # Update existing rows to have token_version = 0
    op.execute("UPDATE users SET token_version = 0 WHERE token_version IS NULL")
    # Make it NOT NULL
    op.alter_column('users', 'token_version', nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Remove token_version from users table
    op.drop_column('users', 'token_version')
