"""add governance tables

Revision ID: a1c9e3f0
Revises: 
Create Date: 2026-01-07 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a1c9e3f0"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "governance_bots",
        sa.Column("bot_id", sa.String(length=150), primary_key=True),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("version", sa.String(length=50), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("author", sa.String(length=150), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="under_review"),
        sa.Column("approvals_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("manifest_json", sa.JSON(), nullable=True),
        sa.Column("code_hash", sa.String(length=256), nullable=True),
        sa.Column("config_hash", sa.String(length=256), nullable=True),
        sa.Column("signature", sa.String(length=512), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
    )
    op.create_index("ix_governance_bots_status", "governance_bots", ["status"], unique=False)
    op.create_index("ix_governance_bots_created_at", "governance_bots", ["created_at"], unique=False)

    op.create_table(
        "governance_approvals",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("bot_id", sa.String(length=150), sa.ForeignKey("governance_bots.bot_id", ondelete="CASCADE"), nullable=False),
        sa.Column("approver", sa.String(length=150), nullable=True),
        sa.Column("role", sa.String(length=100), nullable=True),
        sa.Column("decision", sa.String(length=32), nullable=False, server_default="approved"),
        sa.Column("comments", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
    )
    op.create_index("ix_governance_approvals_bot_id", "governance_approvals", ["bot_id"], unique=False)
    op.create_index("ix_governance_approvals_created_at", "governance_approvals", ["created_at"], unique=False)

    op.create_table(
        "governance_activity",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("bot_id", sa.String(length=150), sa.ForeignKey("governance_bots.bot_id", ondelete="CASCADE"), nullable=False),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("environment", sa.String(length=50), nullable=True),
        sa.Column("details", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
    )
    op.create_index("ix_governance_activity_bot_id", "governance_activity", ["bot_id"], unique=False)
    op.create_index("ix_governance_activity_created_at", "governance_activity", ["created_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_governance_activity_created_at", table_name="governance_activity")
    op.drop_index("ix_governance_activity_bot_id", table_name="governance_activity")
    op.drop_table("governance_activity")

    op.drop_index("ix_governance_approvals_created_at", table_name="governance_approvals")
    op.drop_index("ix_governance_approvals_bot_id", table_name="governance_approvals")
    op.drop_table("governance_approvals")

    op.drop_index("ix_governance_bots_created_at", table_name="governance_bots")
    op.drop_index("ix_governance_bots_status", table_name="governance_bots")
    op.drop_table("governance_bots")
