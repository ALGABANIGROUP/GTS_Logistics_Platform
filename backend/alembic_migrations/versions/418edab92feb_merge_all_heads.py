"""merge all heads

Revision ID: 418edab92feb
Revises: 7b9c1a2d3e4f, b2c7d6e5f4a3, bf1c2d3e4f5a
Create Date: 2026-01-05 08:27:05.366266

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '418edab92feb'
down_revision: Union[str, Sequence[str], None] = ('7b9c1a2d3e4f', 'b2c7d6e5f4a3', 'bf1c2d3e4f5a')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
