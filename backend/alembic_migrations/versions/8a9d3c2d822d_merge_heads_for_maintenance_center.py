"""merge heads for maintenance center

Revision ID: 8a9d3c2d822d
Revises: 004_tms_requests_geo, 550e8400_support_system_001, faab766d1a0f, platform_infra_exp_001, tenant_002
Create Date: 2026-01-15 15:00:08.082547

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8a9d3c2d822d'
down_revision: Union[str, Sequence[str], None] = ('004_tms_requests_geo', 'faab766d1a0f', 'platform_infra_exp_001', 'tenant_002')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
