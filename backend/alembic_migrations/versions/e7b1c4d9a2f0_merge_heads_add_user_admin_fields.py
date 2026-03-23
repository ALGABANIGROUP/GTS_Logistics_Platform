class _OfflineInspector:
    def get_table_names(self): return []
    def get_columns(self, table_name): return []
    def get_indexes(self, table_name): return []
    def get_unique_constraints(self, table_name): return []
    def get_foreign_keys(self, table_name): return []
    def get_pk_constraint(self, table_name): return {}

def safe_inspect(bind):
    # In --sql (offline) bind is a MockConnection; sqlalchemy.inspect() will fail.
    if context.is_offline_mode():
        return _OfflineInspector()
    return safe_inspect(bind)

"""merge heads + add admin user fields

Revision ID: e7b1c4d9a2f0
Revises: d602d0e42455, 9f0c2c9e7b1a
Create Date: 2025-12-29
"""

from typing import Sequence, Union
from alembic import context
from alembic import op
import sqlalchemy as sa

class _OfflineInspector:
    def get_table_names(self): return []
    def get_columns(self, table_name): return []
    def get_indexes(self, table_name): return []
    def get_unique_constraints(self, table_name): return []
    def get_foreign_keys(self, table_name): return []
    def get_pk_constraint(self, table_name): return {}

def _safe_sa_safe_inspect(bind):
    # EN --sql (offline) bind EN MockConnection
    if context.is_offline_mode():
        return _OfflineInspector()
    return _safe_sa_safe_inspect(bind)

from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = "e7b1c4d9a2f0"
down_revision: Union[str, Sequence[str], None] = ("d602d0e42455", "9f0c2c9e7b1a")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _column_exists(table: str, column: str) -> bool:
    bind = op.get_bind()
    inspector = safe_inspect(bind)
    return column in {col["name"] for col in inspector.get_columns(table)}


def _index_exists(table: str, index: str) -> bool:
    bind = op.get_bind()
    inspector = safe_inspect(bind)
    return index in {idx["name"] for idx in inspector.get_indexes(table)}


def upgrade() -> None:
    with op.batch_alter_table("users") as batch:
        if not _column_exists("users", "is_banned"):
            batch.add_column(sa.Column("is_banned", sa.Boolean(), nullable=False, server_default=sa.false()))
        if not _column_exists("users", "ban_reason"):
            batch.add_column(sa.Column("ban_reason", sa.String(length=255), nullable=True))
        if not _column_exists("users", "banned_until"):
            batch.add_column(sa.Column("banned_until", sa.DateTime(timezone=True), nullable=True))
        if not _column_exists("users", "is_deleted"):
            batch.add_column(sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.false()))
        if not _column_exists("users", "deleted_at"):
            batch.add_column(sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True))
        if not _column_exists("users", "manager_id"):
            batch.add_column(
                sa.Column("manager_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
            )

    if not _index_exists("users", "ix_users_manager_id"):
        op.create_index("ix_users_manager_id", "users", ["manager_id"])


def downgrade() -> None:
    if _index_exists("users", "ix_users_manager_id"):
        op.drop_index("ix_users_manager_id", table_name="users")

    with op.batch_alter_table("users") as batch:
        if _column_exists("users", "manager_id"):
            batch.drop_column("manager_id")
        if _column_exists("users", "deleted_at"):
            batch.drop_column("deleted_at")
        if _column_exists("users", "is_deleted"):
            batch.drop_column("is_deleted")
        if _column_exists("users", "banned_until"):
            batch.drop_column("banned_until")
        if _column_exists("users", "ban_reason"):
            batch.drop_column("ban_reason")
        if _column_exists("users", "is_banned"):
            batch.drop_column("is_banned")
