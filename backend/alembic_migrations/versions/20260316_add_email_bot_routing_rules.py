"""Add mailbox bot routing fields and rules table.

Revision ID: 20260316_email_bot_rules
Revises: 20260210_0001, 20260314_plan_invoice_cols, b8f1b5c6ef8c
Create Date: 2026-03-16 12:00:00.000000
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import context
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision: str = "20260316_email_bot_rules"
down_revision: Union[str, Sequence[str], None] = (
    "20260210_0001",
    "20260314_plan_invoice_cols",
    "b8f1b5c6ef8c",
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


class _OfflineInspector:
    def get_table_names(self):
        return []

    def get_columns(self, table_name):
        return []

    def get_indexes(self, table_name):
        return []

    def get_unique_constraints(self, table_name):
        return []

    def get_foreign_keys(self, table_name):
        return []

    def get_pk_constraint(self, table_name):
        return {}


def _safe_inspect(bind):
    if context.is_offline_mode():
        return _OfflineInspector()
    return inspect(bind)


def _table_exists(insp, table_name: str) -> bool:
    return table_name in set(insp.get_table_names())


def _column_exists(insp, table_name: str, column_name: str) -> bool:
    return any(column.get("name") == column_name for column in insp.get_columns(table_name))


def _index_exists(insp, table_name: str, index_name: str) -> bool:
    return any(index.get("name") == index_name for index in insp.get_indexes(table_name))


def _foreign_key_exists(bind, name: str) -> bool:
    query = sa.text("SELECT 1 FROM pg_constraint WHERE conname = :name LIMIT 1")
    return bind.execute(query, {"name": name}).first() is not None


def upgrade() -> None:
    bind = op.get_bind()
    insp = _safe_inspect(bind)

    if _table_exists(insp, "mailboxes"):
        if not _column_exists(insp, "mailboxes", "assigned_bot_key"):
            op.add_column("mailboxes", sa.Column("assigned_bot_key", sa.String(length=100), nullable=True))
        if not _column_exists(insp, "mailboxes", "bot_config"):
            op.add_column("mailboxes", sa.Column("bot_config", sa.JSON(), nullable=True))
        insp = _safe_inspect(bind)
        if not _index_exists(insp, "mailboxes", "ix_mailboxes_assigned_bot_key"):
            op.create_index("ix_mailboxes_assigned_bot_key", "mailboxes", ["assigned_bot_key"], unique=False)

    insp = _safe_inspect(bind)
    if not _table_exists(insp, "bot_mailbox_rules"):
        op.create_table(
            "bot_mailbox_rules",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column(
                "mailbox_id",
                sa.Integer(),
                sa.ForeignKey("mailboxes.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column("bot_key", sa.String(length=100), nullable=True),
            sa.Column("condition_field", sa.String(length=50), nullable=False),
            sa.Column("condition_operator", sa.String(length=20), nullable=False),
            sa.Column("condition_value", sa.JSON(), nullable=False),
            sa.Column("condition_match_all", sa.Boolean(), nullable=False, server_default=sa.text("false")),
            sa.Column("action_type", sa.String(length=50), nullable=False),
            sa.Column("action_config", sa.JSON(), nullable=True),
            sa.Column("priority", sa.Integer(), nullable=False, server_default=sa.text("0")),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
            sa.Column("times_matched", sa.Integer(), nullable=False, server_default=sa.text("0")),
            sa.Column("last_matched_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
            sa.Column(
                "created_by",
                sa.Integer(),
                sa.ForeignKey("users.id", ondelete="SET NULL"),
                nullable=True,
            ),
        )
        insp = _safe_inspect(bind)

    if _table_exists(insp, "bot_mailbox_rules"):
        if not _index_exists(insp, "bot_mailbox_rules", "ix_bot_mailbox_rules_mailbox_id"):
            op.create_index("ix_bot_mailbox_rules_mailbox_id", "bot_mailbox_rules", ["mailbox_id"], unique=False)
        if not _index_exists(insp, "bot_mailbox_rules", "ix_bot_mailbox_rules_bot_key"):
            op.create_index("ix_bot_mailbox_rules_bot_key", "bot_mailbox_rules", ["bot_key"], unique=False)
        if not _index_exists(insp, "bot_mailbox_rules", "ix_bot_mailbox_rules_priority"):
            op.create_index("ix_bot_mailbox_rules_priority", "bot_mailbox_rules", ["priority"], unique=False)
        if not _index_exists(insp, "bot_mailbox_rules", "ix_bot_mailbox_rules_is_active"):
            op.create_index("ix_bot_mailbox_rules_is_active", "bot_mailbox_rules", ["is_active"], unique=False)

    insp = _safe_inspect(bind)
    if _table_exists(insp, "email_messages"):
        if not _column_exists(insp, "email_messages", "analyzed_at"):
            op.add_column("email_messages", sa.Column("analyzed_at", sa.DateTime(timezone=True), nullable=True))
        if not _column_exists(insp, "email_messages", "analysis_result"):
            op.add_column("email_messages", sa.Column("analysis_result", sa.JSON(), nullable=True))
        if not _column_exists(insp, "email_messages", "applied_rule_id"):
            op.add_column("email_messages", sa.Column("applied_rule_id", sa.Integer(), nullable=True))
        if not _column_exists(insp, "email_messages", "processed_by_bot"):
            op.add_column("email_messages", sa.Column("processed_by_bot", sa.String(length=100), nullable=True))
        if not _column_exists(insp, "email_messages", "processed_at"):
            op.add_column("email_messages", sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True))
        if not _foreign_key_exists(bind, "fk_email_messages_applied_rule_id_bot_mailbox_rules"):
            op.create_foreign_key(
                "fk_email_messages_applied_rule_id_bot_mailbox_rules",
                "email_messages",
                "bot_mailbox_rules",
                ["applied_rule_id"],
                ["id"],
                ondelete="SET NULL",
            )
        insp = _safe_inspect(bind)
        if not _index_exists(insp, "email_messages", "ix_email_messages_applied_rule_id"):
            op.create_index("ix_email_messages_applied_rule_id", "email_messages", ["applied_rule_id"], unique=False)
        if not _index_exists(insp, "email_messages", "ix_email_messages_processed_by_bot"):
            op.create_index(
                "ix_email_messages_processed_by_bot",
                "email_messages",
                ["processed_by_bot"],
                unique=False,
            )


def downgrade() -> None:
    bind = op.get_bind()
    insp = _safe_inspect(bind)

    if _table_exists(insp, "email_messages"):
        if _index_exists(insp, "email_messages", "ix_email_messages_processed_by_bot"):
            op.drop_index("ix_email_messages_processed_by_bot", table_name="email_messages")
        if _index_exists(insp, "email_messages", "ix_email_messages_applied_rule_id"):
            op.drop_index("ix_email_messages_applied_rule_id", table_name="email_messages")
        if _foreign_key_exists(bind, "fk_email_messages_applied_rule_id_bot_mailbox_rules"):
            op.drop_constraint(
                "fk_email_messages_applied_rule_id_bot_mailbox_rules",
                "email_messages",
                type_="foreignkey",
            )
        insp = _safe_inspect(bind)
        if _column_exists(insp, "email_messages", "processed_at"):
            op.drop_column("email_messages", "processed_at")
        if _column_exists(insp, "email_messages", "processed_by_bot"):
            op.drop_column("email_messages", "processed_by_bot")
        if _column_exists(insp, "email_messages", "applied_rule_id"):
            op.drop_column("email_messages", "applied_rule_id")
        if _column_exists(insp, "email_messages", "analysis_result"):
            op.drop_column("email_messages", "analysis_result")
        if _column_exists(insp, "email_messages", "analyzed_at"):
            op.drop_column("email_messages", "analyzed_at")

    insp = _safe_inspect(bind)
    if _table_exists(insp, "bot_mailbox_rules"):
        if _index_exists(insp, "bot_mailbox_rules", "ix_bot_mailbox_rules_is_active"):
            op.drop_index("ix_bot_mailbox_rules_is_active", table_name="bot_mailbox_rules")
        if _index_exists(insp, "bot_mailbox_rules", "ix_bot_mailbox_rules_priority"):
            op.drop_index("ix_bot_mailbox_rules_priority", table_name="bot_mailbox_rules")
        if _index_exists(insp, "bot_mailbox_rules", "ix_bot_mailbox_rules_bot_key"):
            op.drop_index("ix_bot_mailbox_rules_bot_key", table_name="bot_mailbox_rules")
        if _index_exists(insp, "bot_mailbox_rules", "ix_bot_mailbox_rules_mailbox_id"):
            op.drop_index("ix_bot_mailbox_rules_mailbox_id", table_name="bot_mailbox_rules")
        op.drop_table("bot_mailbox_rules")

    insp = _safe_inspect(bind)
    if _table_exists(insp, "mailboxes"):
        if _index_exists(insp, "mailboxes", "ix_mailboxes_assigned_bot_key"):
            op.drop_index("ix_mailboxes_assigned_bot_key", table_name="mailboxes")
        if _column_exists(insp, "mailboxes", "bot_config"):
            op.drop_column("mailboxes", "bot_config")
        if _column_exists(insp, "mailboxes", "assigned_bot_key"):
            op.drop_column("mailboxes", "assigned_bot_key")
