"""create tenants table

Revision ID: tenant_001
Revises: sm_001_add_social_media_tables
Create Date: 2026-01-08
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "tenant_001"
down_revision: Union[str, None] = "sm_001_add_social_media_tables"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "tenants",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("subdomain", sa.String(length=100), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("is_default", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.UniqueConstraint("subdomain", name="uq_tenants_subdomain"),
    )

    op.create_index("ix_tenants_is_default", "tenants", ["is_default"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_tenants_is_default", table_name="tenants")
    op.drop_table("tenants")
