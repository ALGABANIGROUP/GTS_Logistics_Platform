"""merge admin + email center heads

Revision ID: d602d0e42455
Revises: 1d2f3a4b5c6d, 2f7b8c9d0e1f
Create Date: 2025-12-29 10:11:52.532579

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd602d0e42455'
down_revision: Union[str, Sequence[str], None] = ('1d2f3a4b5c6d', '2f7b8c9d0e1f')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
