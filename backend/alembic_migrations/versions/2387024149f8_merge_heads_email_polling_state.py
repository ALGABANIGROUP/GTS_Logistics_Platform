"""merge heads (email polling state)

Revision ID: 2387024149f8
Revises: 3c1d9d5b7a2f, d602d0e42455
Create Date: 2025-12-29 15:28:38.646616

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2387024149f8'
down_revision: Union[str, Sequence[str], None] = ('3c1d9d5b7a2f', 'd602d0e42455')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
