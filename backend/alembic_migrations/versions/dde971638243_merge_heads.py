"""merge heads

Revision ID: dde971638243
Revises: 04f61c9082b6, 20260322_add_title_to_ai_bot_issues
Create Date: 2026-04-04 22:27:25.526365

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dde971638243'
down_revision: Union[str, Sequence[str], None] = ('04f61c9082b6', '20260322_add_title_to_ai_bot_issues')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
