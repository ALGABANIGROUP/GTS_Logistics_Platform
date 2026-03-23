"""merge heads

Revision ID: 89cc2bb1bdf1
Revises: 20250826_01_harden_expenses, 43e868641163
Create Date: 2025-09-27 23:35:22.237321

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '89cc2bb1bdf1'
down_revision: Union[str, Sequence[str], None] = ('20250826_01_harden_expenses', '43e868641163')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
