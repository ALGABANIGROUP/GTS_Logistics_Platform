"""merge heads

Revision ID: 7fe56a940afa
Revises: 418edab92feb, a1c9e3f0, f1c2e3d4a5b6
Create Date: 2026-01-07 22:44:20.065761

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7fe56a940afa'
down_revision: Union[str, Sequence[str], None] = ('418edab92feb', 'a1c9e3f0', 'f1c2e3d4a5b6')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
