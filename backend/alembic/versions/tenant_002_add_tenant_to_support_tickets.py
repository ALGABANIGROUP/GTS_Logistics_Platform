"""add tenant to support tickets

Revision ID: tenant_002
Revises: tenant_001
Create Date: 2026-01-08
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "tenant_002"
down_revision: Union[str, None] = "tenant_001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("support_tickets", sa.Column("tenant_id", sa.String(length=64), nullable=True))
    op.create_index("ix_support_tickets_tenant_id", "support_tickets", ["tenant_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_support_tickets_tenant_id", table_name="support_tickets")
    op.drop_column("support_tickets", "tenant_id")
