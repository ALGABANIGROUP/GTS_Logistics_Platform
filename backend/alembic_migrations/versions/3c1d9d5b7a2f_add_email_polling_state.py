
from __future__ import annotations

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

"""add email polling state fields

Revision ID: 3c1d9d5b7a2f
Revises: 2f7b8c9d0e1f
Create Date: 2025-12-29 09:10:00

"""

from typing import Sequence, Union
from alembic import context
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision: str = "3c1d9d5b7a2f"
down_revision: Union[str, Sequence[str], None] = "2f7b8c9d0e1f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _table_exists(insp, name: str) -> bool:
    return name in set(insp.get_table_names())


def _column_exists(insp, table: str, column: str) -> bool:
    cols = insp.get_columns(table)
    return any(c.get("name") == column for c in cols)


def _constraint_exists(bind, name: str) -> bool:
    q = sa.text("SELECT 1 FROM pg_constraint WHERE conname = :n LIMIT 1")
    return bind.execute(q, {"n": name}).first() is not None


def upgrade() -> None:
    bind = op.get_bind()
    insp = safe_inspect(bind)

    if _table_exists(insp, "mailboxes"):
        if not _column_exists(insp, "mailboxes", "last_polled_at"):
            op.add_column("mailboxes", sa.Column("last_polled_at", sa.DateTime(timezone=True), nullable=True))
        if not _column_exists(insp, "mailboxes", "last_uid"):
            op.add_column("mailboxes", sa.Column("last_uid", sa.BigInteger(), nullable=True))
        if not _column_exists(insp, "mailboxes", "last_message_id"):
            op.add_column("mailboxes", sa.Column("last_message_id", sa.String(length=255), nullable=True))

    if _table_exists(insp, "email_messages"):
        if not _column_exists(insp, "email_messages", "imap_uid"):
            op.add_column("email_messages", sa.Column("imap_uid", sa.BigInteger(), nullable=True))
        if not _constraint_exists(bind, "uq_email_messages_mailbox_imap_uid"):
            op.create_unique_constraint(
                "uq_email_messages_mailbox_imap_uid",
                "email_messages",
                ["mailbox_id", "imap_uid"],
            )


def downgrade() -> None:
    bind = op.get_bind()
    insp = safe_inspect(bind)

    if _table_exists(insp, "email_messages") and _constraint_exists(bind, "uq_email_messages_mailbox_imap_uid"):
        op.drop_constraint("uq_email_messages_mailbox_imap_uid", "email_messages", type_="unique")
    if _table_exists(insp, "email_messages") and _column_exists(insp, "email_messages", "imap_uid"):
        op.drop_column("email_messages", "imap_uid")

    if _table_exists(insp, "mailboxes"):
        if _column_exists(insp, "mailboxes", "last_message_id"):
            op.drop_column("mailboxes", "last_message_id")
        if _column_exists(insp, "mailboxes", "last_uid"):
            op.drop_column("mailboxes", "last_uid")
        if _column_exists(insp, "mailboxes", "last_polled_at"):
            op.drop_column("mailboxes", "last_polled_at")
