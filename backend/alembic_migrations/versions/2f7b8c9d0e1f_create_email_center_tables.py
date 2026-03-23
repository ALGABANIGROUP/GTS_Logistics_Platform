"""create email center tables

Revision ID: 2f7b8c9d0e1f
Revises: 9f0c2c9e7b1a
Create Date: 2025-12-28 00:00:00

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
    return _safe_inspect(bind)

revision: str = "2f7b8c9d0e1f"
down_revision: Union[str, Sequence[str], None] = "9f0c2c9e7b1a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _table_exists(insp, name: str) -> bool:
    return name in set(insp.get_table_names())


def _ix_exists(bind, ix_name: str) -> bool:
    q = sa.text("SELECT 1 FROM pg_class WHERE relkind='i' AND relname = :n LIMIT 1")
    return bind.execute(q, {"n": ix_name}).first() is not None


def _constraint_exists(bind, name: str) -> bool:
    q = sa.text("SELECT 1 FROM pg_constraint WHERE conname = :n LIMIT 1")
    return bind.execute(q, {"n": name}).first() is not None


def upgrade() -> None:
    bind = op.get_bind()
    insp = _safe_inspect(bind)

    # -------------------------
    # mailboxes
    # -------------------------
    if not _table_exists(insp, "mailboxes"):
        op.create_table(
            "mailboxes",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("tenant_id", sa.String(length=64), nullable=True),
            sa.Column(
                "owner_user_id",
                sa.Integer(),
                sa.ForeignKey("users.id", ondelete="SET NULL"),
                nullable=True,
            ),
            sa.Column("bot_code", sa.String(length=100), nullable=True),
            sa.Column("email_address", sa.String(length=255), nullable=False),
            sa.Column("display_name", sa.String(length=255), nullable=True),
            sa.Column("mode", sa.String(length=20), nullable=False, server_default=sa.text("'HUMAN'")),
            sa.Column(
                "direction",
                sa.String(length=30),
                nullable=False,
                server_default=sa.text("'INBOUND_OUTBOUND'"),
            ),
            sa.Column("imap_host", sa.String(length=255), nullable=True),
            sa.Column("imap_port", sa.Integer(), nullable=True),
            sa.Column("imap_user", sa.String(length=255), nullable=True),
            sa.Column("imap_ssl", sa.Boolean(), server_default=sa.text("true"), nullable=True),
            sa.Column("smtp_host", sa.String(length=255), nullable=True),
            sa.Column("smtp_port", sa.Integer(), nullable=True),
            sa.Column("smtp_user", sa.String(length=255), nullable=True),
            sa.Column("smtp_ssl", sa.Boolean(), server_default=sa.text("true"), nullable=True),
            sa.Column("use_tls", sa.Boolean(), server_default=sa.text("true"), nullable=True),
            sa.Column("inbound_enabled", sa.Boolean(), server_default=sa.text("true"), nullable=False),
            sa.Column("outbound_enabled", sa.Boolean(), server_default=sa.text("true"), nullable=False),
            sa.Column("is_enabled", sa.Boolean(), server_default=sa.text("true"), nullable=False),
            sa.Column("polling_enabled", sa.Boolean(), server_default=sa.text("true"), nullable=False),
            sa.Column("auto_reply_enabled", sa.Boolean(), server_default=sa.text("false"), nullable=False),
            sa.Column("package_scope", sa.String(length=20), nullable=False, server_default=sa.text("'SYSTEM'")),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("tenant_id", "email_address", name="uq_mailboxes_tenant_email"),
        )
        insp = _safe_inspect(bind)

    # mailboxes indexes
    if _table_exists(insp, "mailboxes"):
        if not _ix_exists(bind, "ix_mailboxes_owner_user_id"):
            op.create_index("ix_mailboxes_owner_user_id", "mailboxes", ["owner_user_id"])
        if not _ix_exists(bind, "ix_mailboxes_bot_code"):
            op.create_index("ix_mailboxes_bot_code", "mailboxes", ["bot_code"])
        if not _ix_exists(bind, "ix_mailboxes_enabled"):
            op.create_index("ix_mailboxes_enabled", "mailboxes", ["is_enabled"])

    # -------------------------
    # mailbox_credentials
    # -------------------------
    if not _table_exists(insp, "mailbox_credentials"):
        op.create_table(
            "mailbox_credentials",
            sa.Column(
                "mailbox_id",
                sa.Integer(),
                sa.ForeignKey("mailboxes.id", ondelete="CASCADE"),
                primary_key=True,
            ),
            sa.Column("credentials_ciphertext", sa.Text(), nullable=False),
            sa.Column("key_version", sa.String(length=50), nullable=True),
            sa.Column("rotated_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("last_verified_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("last_error", sa.Text(), nullable=True),
        )
        insp = _safe_inspect(bind)

    # -------------------------
    # email_threads
    # -------------------------
    if not _table_exists(insp, "email_threads"):
        op.create_table(
            "email_threads",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column(
                "mailbox_id",
                sa.Integer(),
                sa.ForeignKey("mailboxes.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column("subject", sa.String(length=255), nullable=True),
            sa.Column("status", sa.String(length=50), nullable=False, server_default=sa.text("'open'")),
            sa.Column("tags", sa.JSON(), nullable=True),
            sa.Column("priority", sa.String(length=50), nullable=True),
            sa.Column("assigned_to_user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
            sa.Column("last_message_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        )
        insp = _safe_inspect(bind)
    else:
        # ensure FK exists if table pre-existed without FK
        fk_name = "fk_email_threads_mailbox_id_mailboxes"
        if not _constraint_exists(bind, fk_name):
            op.create_foreign_key(
                fk_name,
                "email_threads",
                "mailboxes",
                ["mailbox_id"],
                ["id"],
                ondelete="CASCADE",
            )

    # email_threads indexes
    if _table_exists(insp, "email_threads"):
        if not _ix_exists(bind, "ix_email_threads_mailbox_id"):
            op.create_index("ix_email_threads_mailbox_id", "email_threads", ["mailbox_id"])
        if not _ix_exists(bind, "ix_email_threads_created_at"):
            op.create_index("ix_email_threads_created_at", "email_threads", ["created_at"])

    # -------------------------
    # email_messages
    # -------------------------
    if not _table_exists(insp, "email_messages"):
        op.create_table(
            "email_messages",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column(
                "mailbox_id",
                sa.Integer(),
                sa.ForeignKey("mailboxes.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column("message_id", sa.String(length=255), nullable=True),
            sa.Column("thread_id", sa.Integer(), sa.ForeignKey("email_threads.id"), nullable=True),
            sa.Column("direction", sa.String(length=20), nullable=False),
            sa.Column("from_addr", sa.String(length=255), nullable=True),
            sa.Column("to_addrs", sa.JSON(), nullable=True),
            sa.Column("cc_addrs", sa.JSON(), nullable=True),
            sa.Column("subject", sa.String(length=255), nullable=True),
            sa.Column("received_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("body_preview", sa.Text(), nullable=True),
            sa.Column("body_storage_ref", sa.String(length=255), nullable=True),
            sa.Column("status", sa.String(length=50), nullable=False, server_default=sa.text("'new'")),
            sa.Column("assigned_bot", sa.String(length=100), nullable=True),
            sa.Column("workflow_id", sa.String(length=100), nullable=True),
            sa.Column("raw_headers_json", sa.JSON(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.UniqueConstraint("mailbox_id", "message_id", name="uq_email_messages_mailbox_message_id"),
        )
        insp = _safe_inspect(bind)
    else:
        fk_mailbox = "fk_email_messages_mailbox_id_mailboxes"
        if not _constraint_exists(bind, fk_mailbox):
            op.create_foreign_key(
                fk_mailbox,
                "email_messages",
                "mailboxes",
                ["mailbox_id"],
                ["id"],
                ondelete="CASCADE",
            )
        fk_thread = "fk_email_messages_thread_id_email_threads"
        if not _constraint_exists(bind, fk_thread):
            op.create_foreign_key(
                fk_thread,
                "email_messages",
                "email_threads",
                ["thread_id"],
                ["id"],
            )

    # email_messages indexes
    if _table_exists(insp, "email_messages"):
        if not _ix_exists(bind, "ix_email_messages_mailbox_id"):
            op.create_index("ix_email_messages_mailbox_id", "email_messages", ["mailbox_id"])
        if not _ix_exists(bind, "ix_email_messages_status"):
            op.create_index("ix_email_messages_status", "email_messages", ["status"])
        if not _ix_exists(bind, "ix_email_messages_created_at"):
            op.create_index("ix_email_messages_created_at", "email_messages", ["created_at"])

    # -------------------------
    # email_attachments
    # -------------------------
    if not _table_exists(insp, "email_attachments"):
        op.create_table(
            "email_attachments",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column(
                "message_id",
                sa.Integer(),
                sa.ForeignKey("email_messages.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column("filename", sa.String(length=255), nullable=True),
            sa.Column("content_type", sa.String(length=100), nullable=True),
            sa.Column("size", sa.Integer(), nullable=True),
            sa.Column("storage_ref", sa.String(length=255), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        )
        insp = _safe_inspect(bind)
    else:
        fk_msg = "fk_email_attachments_message_id_email_messages"
        if not _constraint_exists(bind, fk_msg):
            op.create_foreign_key(
                fk_msg,
                "email_attachments",
                "email_messages",
                ["message_id"],
                ["id"],
                ondelete="CASCADE",
            )

    # email_attachments index
    if _table_exists(insp, "email_attachments"):
        if not _ix_exists(bind, "ix_email_attachments_message_id"):
            op.create_index("ix_email_attachments_message_id", "email_attachments", ["message_id"])

    # -------------------------
    # email_audit_logs
    # -------------------------
    if not _table_exists(insp, "email_audit_logs"):
        op.create_table(
            "email_audit_logs",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("actor_user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
            sa.Column("action", sa.String(length=100), nullable=False),
            sa.Column("mailbox_id", sa.Integer(), sa.ForeignKey("mailboxes.id"), nullable=True),
            sa.Column("message_id", sa.Integer(), sa.ForeignKey("email_messages.id"), nullable=True),
            sa.Column("ip", sa.String(length=64), nullable=True),
            sa.Column("diff_json", sa.JSON(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.Column("severity", sa.String(length=20), nullable=True),
        )
        insp = _safe_inspect(bind)

    # email_audit_logs indexes
    if _table_exists(insp, "email_audit_logs"):
        if not _ix_exists(bind, "ix_email_audit_logs_created_at"):
            op.create_index("ix_email_audit_logs_created_at", "email_audit_logs", ["created_at"])
        if not _ix_exists(bind, "ix_email_audit_logs_actor_user_id"):
            op.create_index("ix_email_audit_logs_actor_user_id", "email_audit_logs", ["actor_user_id"])
        if not _ix_exists(bind, "ix_email_audit_logs_action"):
            op.create_index("ix_email_audit_logs_action", "email_audit_logs", ["action"])

    # -------------------------
    # mailbox_requests
    # -------------------------
    if not _table_exists(insp, "mailbox_requests"):
        op.create_table(
            "mailbox_requests",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column(
                "requester_user_id",
                sa.Integer(),
                sa.ForeignKey("users.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column("requested_email", sa.String(length=255), nullable=False),
            sa.Column("desired_mode", sa.String(length=20), nullable=False, server_default=sa.text("'HUMAN'")),
            sa.Column("package_name", sa.String(length=100), nullable=True),
            sa.Column("status", sa.String(length=20), nullable=False, server_default=sa.text("'pending'")),
            sa.Column("approved_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
            sa.Column("decided_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("reason", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        )
        insp = _safe_inspect(bind)

    # mailbox_requests indexes
    if _table_exists(insp, "mailbox_requests"):
        if not _ix_exists(bind, "ix_mailbox_requests_status"):
            op.create_index("ix_mailbox_requests_status", "mailbox_requests", ["status"])
        if not _ix_exists(bind, "ix_mailbox_requests_requester"):
            op.create_index("ix_mailbox_requests_requester", "mailbox_requests", ["requester_user_id"])
        if not _ix_exists(bind, "ix_mailbox_requests_created_at"):
            op.create_index("ix_mailbox_requests_created_at", "mailbox_requests", ["created_at"])


def downgrade() -> None:
    # Safe teardown for partially-created DBs
    bind = op.get_bind()

    for ix_name in [
        "ix_mailbox_requests_created_at",
        "ix_mailbox_requests_requester",
        "ix_mailbox_requests_status",
        "ix_email_audit_logs_action",
        "ix_email_audit_logs_actor_user_id",
        "ix_email_audit_logs_created_at",
        "ix_email_attachments_message_id",
        "ix_email_messages_created_at",
        "ix_email_messages_status",
        "ix_email_messages_mailbox_id",
        "ix_email_threads_created_at",
        "ix_email_threads_mailbox_id",
        "ix_mailboxes_enabled",
        "ix_mailboxes_bot_code",
        "ix_mailboxes_owner_user_id",
    ]:
        try:
            if _ix_exists(bind, ix_name):
                op.execute(sa.text(f'DROP INDEX IF EXISTS "{ix_name}"'))
        except Exception:
            pass

    # Drop tables (order matters)
    for table_name in [
        "mailbox_requests",
        "email_audit_logs",
        "email_attachments",
        "email_messages",
        "email_threads",
        "mailbox_credentials",
        "mailboxes",
    ]:
        op.execute(sa.text(f'DROP TABLE IF EXISTS "{table_name}" CASCADE'))
