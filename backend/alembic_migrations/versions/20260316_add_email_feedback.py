"""Add email feedback table for routing learning.

Revision ID: 20260316_email_feedback
Revises: 20260316_email_bot_rules
Create Date: 2026-03-16 16:00:00.000000
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import context
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision: str = "20260316_email_feedback"
down_revision: Union[str, Sequence[str], None] = "20260316_email_bot_rules"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


class _OfflineInspector:
    def get_table_names(self):
        return []

    def get_indexes(self, table_name):
        return []


def _safe_inspect(bind):
    if context.is_offline_mode():
        return _OfflineInspector()
    return inspect(bind)


def _table_exists(insp, table_name: str) -> bool:
    return table_name in set(insp.get_table_names())


def _index_exists(insp, table_name: str, index_name: str) -> bool:
    return any(index.get("name") == index_name for index in insp.get_indexes(table_name))


def upgrade() -> None:
    bind = op.get_bind()
    insp = _safe_inspect(bind)

    if not _table_exists(insp, "email_feedback"):
        op.create_table(
            "email_feedback",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column(
                "message_id",
                sa.Integer(),
                sa.ForeignKey("email_messages.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column("bot_key", sa.String(length=100), nullable=True),
            sa.Column("rating", sa.Integer(), nullable=False),
            sa.Column("was_correct", sa.Boolean(), nullable=False),
            sa.Column("user_comment", sa.Text(), nullable=True),
            sa.Column("routing_source", sa.String(length=30), nullable=True),
            sa.Column("routing_confidence", sa.Float(), nullable=True),
            sa.Column(
                "created_by",
                sa.Integer(),
                sa.ForeignKey("users.id", ondelete="SET NULL"),
                nullable=True,
            ),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        )
        insp = _safe_inspect(bind)

    if _table_exists(insp, "email_feedback"):
        if not _index_exists(insp, "email_feedback", "ix_email_feedback_message_id"):
            op.create_index("ix_email_feedback_message_id", "email_feedback", ["message_id"], unique=False)
        if not _index_exists(insp, "email_feedback", "ix_email_feedback_bot_key"):
            op.create_index("ix_email_feedback_bot_key", "email_feedback", ["bot_key"], unique=False)
        if not _index_exists(insp, "email_feedback", "ix_email_feedback_was_correct"):
            op.create_index("ix_email_feedback_was_correct", "email_feedback", ["was_correct"], unique=False)
        if not _index_exists(insp, "email_feedback", "ix_email_feedback_routing_source"):
            op.create_index("ix_email_feedback_routing_source", "email_feedback", ["routing_source"], unique=False)
        if not _index_exists(insp, "email_feedback", "ix_email_feedback_created_at"):
            op.create_index("ix_email_feedback_created_at", "email_feedback", ["created_at"], unique=False)


def downgrade() -> None:
    bind = op.get_bind()
    insp = _safe_inspect(bind)
    if _table_exists(insp, "email_feedback"):
        if _index_exists(insp, "email_feedback", "ix_email_feedback_created_at"):
            op.drop_index("ix_email_feedback_created_at", table_name="email_feedback")
        if _index_exists(insp, "email_feedback", "ix_email_feedback_routing_source"):
            op.drop_index("ix_email_feedback_routing_source", table_name="email_feedback")
        if _index_exists(insp, "email_feedback", "ix_email_feedback_was_correct"):
            op.drop_index("ix_email_feedback_was_correct", table_name="email_feedback")
        if _index_exists(insp, "email_feedback", "ix_email_feedback_bot_key"):
            op.drop_index("ix_email_feedback_bot_key", table_name="email_feedback")
        if _index_exists(insp, "email_feedback", "ix_email_feedback_message_id"):
            op.drop_index("ix_email_feedback_message_id", table_name="email_feedback")
        op.drop_table("email_feedback")
