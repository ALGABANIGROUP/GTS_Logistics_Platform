"""merge docs and expenses heads

Revision ID: a5b9c2d3e4f6
Revises: 89cc2bb1bdf1, YYYYMMDDHHmm_add_documents
Create Date: 2025-11-09 13:20:29.709035

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a5b9c2d3e4f6'
down_revision: Union[str, Sequence[str], None] = ('89cc2bb1bdf1', 'YYYYMMDDHHmm_add_documents')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
