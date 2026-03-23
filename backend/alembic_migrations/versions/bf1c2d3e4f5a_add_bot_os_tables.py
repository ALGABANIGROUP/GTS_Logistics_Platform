"""add bot os tables

Revision ID: bf1c2d3e4f5a
Revises: 20250826_01_harden_expenses, 43e868641163, 9f0c2c9e7b1a, YYYYMMDDHHmm_add_documents
Create Date: 2025-12-31 12:00:00

"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import context
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

class _OfflineInspector:
    def get_table_names(self): return []
    def get_columns(self, table_name): return []
    def get_indexes(self, table_name): return []
    def get_unique_constraints(self, table_name): return []
    def get_foreign_keys(self, table_name): return []
    def get_pk_constraint(self, table_name): return {}

def _safe_inspect(bind):
    # EN --sql (offline) bind EN MockConnectionEN inspect
    if context.is_offline_mode():
        return _OfflineInspector()
    return inspect(bind)

revision: str = "bf1c2d3e4f5a"
down_revision: Union[str, Sequence[str], None] = (
    "20250826_01_harden_expenses",
    "43e868641163",
    "9f0c2c9e7b1a",
    "YYYYMMDDHHmm_add_documents",
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _table_exists(insp, name: str) -> bool:
    return name in set(insp.get_table_names())


def upgrade() -> None:
    bind = op.get_bind()
    insp = _safe_inspect(bind)

    if not _table_exists(insp, "bot_registry"):
        op.create_table(
            "bot_registry",
            sa.Column("bot_name", sa.String(length=100), primary_key=True),
            sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.text("true")),
            sa.Column("automation_level", sa.String(length=32), nullable=False, server_default="auto"),
            sa.Column("schedule_cron", sa.String(length=100), nullable=True),
            sa.Column("config_json", sa.JSON(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                server_default=sa.func.now(),
                nullable=False,
            ),
        )
        op.create_index("ix_bot_registry_enabled", "bot_registry", ["enabled"])

    if not _table_exists(insp, "bot_runs"):
        op.create_table(
            "bot_runs",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column(
                "bot_name",
                sa.String(length=100),
                sa.ForeignKey("bot_registry.bot_name", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column("task_type", sa.String(length=100), nullable=False, server_default="run"),
            sa.Column("params_json", sa.JSON(), nullable=True),
            sa.Column("status", sa.String(length=20), nullable=False, server_default="running"),
            sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("result_json", sa.JSON(), nullable=True),
            sa.Column("error", sa.Text(), nullable=True),
        )
        op.create_index("ix_bot_runs_bot_name", "bot_runs", ["bot_name"])
        op.create_index("ix_bot_runs_status", "bot_runs", ["status"])
        op.create_index("ix_bot_runs_started_at", "bot_runs", ["started_at"])

    if not _table_exists(insp, "human_commands"):
        op.create_table(
            "human_commands",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("user_id", sa.Integer(), nullable=True),
            sa.Column("user_email", sa.String(length=255), nullable=True),
            sa.Column("natural_command", sa.Text(), nullable=False),
            sa.Column("parsed_json", sa.JSON(), nullable=True),
            sa.Column("technical_json", sa.JSON(), nullable=True),
            sa.Column("status", sa.String(length=20), nullable=False, server_default="received"),
            sa.Column("result_json", sa.JSON(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        )
        op.create_index("ix_human_commands_status", "human_commands", ["status"])
        op.create_index("ix_human_commands_created_at", "human_commands", ["created_at"])
        op.create_index("ix_human_commands_user_email", "human_commands", ["user_email"])


def downgrade() -> None:
    bind = op.get_bind()
    insp = _safe_inspect(bind)

    if _table_exists(insp, "human_commands"):
        op.drop_index("ix_human_commands_user_email", table_name="human_commands")
        op.drop_index("ix_human_commands_created_at", table_name="human_commands")
        op.drop_index("ix_human_commands_status", table_name="human_commands")
        op.drop_table("human_commands")

    if _table_exists(insp, "bot_runs"):
        op.drop_index("ix_bot_runs_started_at", table_name="bot_runs")
        op.drop_index("ix_bot_runs_status", table_name="bot_runs")
        op.drop_index("ix_bot_runs_bot_name", table_name="bot_runs")
        op.drop_table("bot_runs")

    if _table_exists(insp, "bot_registry"):
        op.drop_index("ix_bot_registry_enabled", table_name="bot_registry")
        op.drop_table("bot_registry")

