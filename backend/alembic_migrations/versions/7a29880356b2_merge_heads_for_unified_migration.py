"""merge heads for unified migration

Revision ID: 7a29880356b2
Revises: 20260206_dispatch_tables, add_user_system_setup_002
Create Date: 2026-02-06 08:16:49.208950

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7a29880356b2'
down_revision: Union[str, Sequence[str], None] = ('20260206_dispatch_tables', 'add_user_system_setup_002')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
