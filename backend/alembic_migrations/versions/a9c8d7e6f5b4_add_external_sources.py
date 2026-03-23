"""Add external sources tracking tables

Revision ID: a9c8d7e6f5b4
Revises: d8a1b2c3d4e5
Create Date: 2026-01-03

"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "a9c8d7e6f5b4"
down_revision: Union[str, Sequence[str], None] = "d8a1b2c3d4e5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "external_records",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source", sa.String(length=128), nullable=False),
        sa.Column("entity_type", sa.String(length=64), nullable=False),
        sa.Column("title", sa.String(length=512), nullable=False),
        sa.Column("location", sa.String(length=256), nullable=True),
        sa.Column("tags", sa.JSON(), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("raw", sa.JSON(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("fetched_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("is_real", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_external_records_source", "external_records", ["source"])
    op.create_table(
        "bot_executions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source", sa.String(length=128), nullable=False),
        sa.Column("records_synced", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("succeeded", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("executed_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_index("ix_external_records_source", table_name="external_records")
    op.drop_table("bot_executions")
    op.drop_table("external_records")
