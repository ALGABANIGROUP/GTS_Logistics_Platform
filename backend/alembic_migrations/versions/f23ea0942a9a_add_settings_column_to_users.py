"""add_settings_column_to_users

Revision ID: f23ea0942a9a
Revises: 802d41db8636
Create Date: 2026-01-17 15:37:38.815130

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f23ea0942a9a'
down_revision: Union[str, Sequence[str], None] = '802d41db8636'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add settings column to users table
    op.add_column('users', sa.Column('settings', sa.JSON(), nullable=True, default=sa.text("'{}'::json")))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove settings column from users table
    op.drop_column('users', 'settings')
