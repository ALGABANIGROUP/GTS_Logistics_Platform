"""merge finance and email heads

Revision ID: 04f61c9082b6
Revises: 20260321_expand_payments_for_expenses, 20260316_email_feedback
Create Date: 2026-03-21 14:08:29.817781

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '04f61c9082b6'
down_revision: Union[str, Sequence[str], None] = ('20260321_expand_payments_for_expenses', '20260316_email_feedback')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
