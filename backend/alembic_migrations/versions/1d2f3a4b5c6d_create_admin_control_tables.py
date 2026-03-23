"""create admin control tables

Revision ID: 1d2f3a4b5c6d
Revises: 9f0c2c9e7b1a
Create Date: 2025-12-28 00:00:00

"""
from __future__ import annotations

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

def _safe_sa_inspect(bind):
    # EN --sql (offline) bind EN MockConnection
    if context.is_offline_mode():
        return _OfflineInspector()
    return _safe_sa_inspect(bind)

revision: str = "1d2f3a4b5c6d"
down_revision: Union[str, Sequence[str], None] = "9f0c2c9e7b1a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _table_exists(name: str) -> bool:
    bind = op.get_bind()
    insp = _safe_sa_inspect(bind)
    return name in insp.get_table_names()


def _index_exists(table_name: str, index_name: str) -> bool:
    bind = op.get_bind()
    insp = _safe_sa_inspect(bind)
    try:
        indexes = insp.get_indexes(table_name)
    except Exception:
        return False
    return any(ix.get("name") == index_name for ix in indexes)


def _ensure_index(index_name: str, table_name: str, columns: list[str]) -> None:
    if _table_exists(table_name) and not _index_exists(table_name, index_name):
        op.create_index(index_name, table_name, columns)


def upgrade() -> None:
    # -----------------------------
    # org_units
    # -----------------------------
    if not _table_exists("org_units"):
        op.create_table(
            "org_units",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("parent_id", sa.Integer(), sa.ForeignKey("org_units.id"), nullable=True),
            sa.Column("name", sa.String(length=255), nullable=False),
            sa.Column("type", sa.String(length=50), nullable=True),
            sa.Column("metadata", sa.JSON(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        )
    _ensure_index("ix_org_units_parent_id", "org_units", ["parent_id"])
    _ensure_index("ix_org_units_created_at", "org_units", ["created_at"])

    # -----------------------------
    # org_memberships
    # -----------------------------
    if not _table_exists("org_memberships"):
        op.create_table(
            "org_memberships",
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
            sa.Column("org_unit_id", sa.Integer(), sa.ForeignKey("org_units.id", ondelete="CASCADE"), primary_key=True),
            sa.Column("title", sa.String(length=255), nullable=True),
            sa.Column("level", sa.String(length=50), nullable=True),
            sa.Column("start_date", sa.Date(), nullable=True),
            sa.Column("end_date", sa.Date(), nullable=True),
        )
    _ensure_index("ix_org_memberships_user_id", "org_memberships", ["user_id"])
    _ensure_index("ix_org_memberships_org_unit_id", "org_memberships", ["org_unit_id"])

    # -----------------------------
    # roles
    # -----------------------------
    if not _table_exists("roles"):
        op.create_table(
            "roles",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("name", sa.String(length=100), nullable=False, unique=True),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("priority", sa.Integer(), nullable=True),
            sa.Column("parent_role_id", sa.Integer(), sa.ForeignKey("roles.id"), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        )
    _ensure_index("ix_roles_parent_role_id", "roles", ["parent_role_id"])

    # -----------------------------
    # permissions
    # -----------------------------
    if not _table_exists("permissions"):
        op.create_table(
            "permissions",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("code", sa.String(length=100), nullable=False, unique=True),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("scope_type", sa.String(length=20), nullable=False),
            sa.Column("scope_key", sa.String(length=100), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        )
    _ensure_index("ix_permissions_scope", "permissions", ["scope_type", "scope_key"])

    # -----------------------------
    # role_permissions
    # -----------------------------
    if not _table_exists("role_permissions"):
        op.create_table(
            "role_permissions",
            sa.Column("role_id", sa.Integer(), sa.ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
            sa.Column(
                "permission_id",
                sa.Integer(),
                sa.ForeignKey("permissions.id", ondelete="CASCADE"),
                primary_key=True,
            ),
        )

    # -----------------------------
    # permission_templates
    # -----------------------------
    if not _table_exists("permission_templates"):
        op.create_table(
            "permission_templates",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("name", sa.String(length=100), nullable=False, unique=True),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        )

    # -----------------------------
    # template_permissions
    # -----------------------------
    if not _table_exists("template_permissions"):
        op.create_table(
            "template_permissions",
            sa.Column(
                "template_id",
                sa.Integer(),
                sa.ForeignKey("permission_templates.id", ondelete="CASCADE"),
                primary_key=True,
            ),
            sa.Column(
                "permission_id",
                sa.Integer(),
                sa.ForeignKey("permissions.id", ondelete="CASCADE"),
                primary_key=True,
            ),
        )

    # -----------------------------
    # user_roles
    # -----------------------------
    if not _table_exists("user_roles"):
        op.create_table(
            "user_roles",
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
            sa.Column("role_id", sa.Integer(), sa.ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
            sa.Column("org_unit_id", sa.Integer(), sa.ForeignKey("org_units.id"), nullable=True),
            sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        )
    _ensure_index("ix_user_roles_user_id", "user_roles", ["user_id"])
    _ensure_index("ix_user_roles_role_id", "user_roles", ["role_id"])
    _ensure_index("ix_user_roles_org_unit_id", "user_roles", ["org_unit_id"])

    # -----------------------------
    # sessions  (EN /users/me EN 401 EN)
    # -----------------------------
    if not _table_exists("sessions"):
        op.create_table(
            "sessions",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("ip", sa.String(length=64), nullable=True),
            sa.Column("user_agent", sa.Text(), nullable=True),
            sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        )
    _ensure_index("ix_sessions_user_id", "sessions", ["user_id"])
    _ensure_index("ix_sessions_created_at", "sessions", ["created_at"])

    # -----------------------------
    # audit_logs
    # -----------------------------
    if not _table_exists("audit_logs"):
        op.create_table(
            "audit_logs",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("actor_user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
            sa.Column("action", sa.String(length=100), nullable=False),
            sa.Column("target_type", sa.String(length=50), nullable=True),
            sa.Column("target_id", sa.String(length=100), nullable=True),
            sa.Column("diff_json", sa.JSON(), nullable=True),
            sa.Column("ip", sa.String(length=64), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.Column("severity", sa.String(length=20), nullable=True),
        )
    _ensure_index("ix_audit_logs_actor_user_id", "audit_logs", ["actor_user_id"])
    _ensure_index("ix_audit_logs_action", "audit_logs", ["action"])
    _ensure_index("ix_audit_logs_target_type", "audit_logs", ["target_type"])
    _ensure_index("ix_audit_logs_created_at", "audit_logs", ["created_at"])
    _ensure_index("ix_audit_logs_severity", "audit_logs", ["severity"])

    # -----------------------------
    # alert_rules
    # -----------------------------
    if not _table_exists("alert_rules"):
        op.create_table(
            "alert_rules",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("name", sa.String(length=200), nullable=False),
            sa.Column("severity", sa.String(length=20), nullable=True),
            sa.Column("condition_json", sa.JSON(), nullable=True),
            sa.Column("channels_json", sa.JSON(), nullable=True),
            sa.Column("is_enabled", sa.Boolean(), server_default=sa.text("true"), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        )
    _ensure_index("ix_alert_rules_severity", "alert_rules", ["severity"])
    _ensure_index("ix_alert_rules_is_enabled", "alert_rules", ["is_enabled"])
    _ensure_index("ix_alert_rules_created_at", "alert_rules", ["created_at"])


def downgrade() -> None:
    # DOWNS: EN
    bind = op.get_bind()
    insp = _safe_sa_inspect(bind)
    tables = set(insp.get_table_names())

    def drop_index_safe(ix_name: str, table: str) -> None:
        if table in tables and _index_exists(table, ix_name):
            op.drop_index(ix_name, table_name=table)

    def drop_table_safe(table: str) -> None:
        if table in tables:
            op.drop_table(table)

    drop_index_safe("ix_alert_rules_created_at", "alert_rules")
    drop_index_safe("ix_alert_rules_is_enabled", "alert_rules")
    drop_index_safe("ix_alert_rules_severity", "alert_rules")
    drop_table_safe("alert_rules")

    drop_index_safe("ix_audit_logs_severity", "audit_logs")
    drop_index_safe("ix_audit_logs_created_at", "audit_logs")
    drop_index_safe("ix_audit_logs_target_type", "audit_logs")
    drop_index_safe("ix_audit_logs_action", "audit_logs")
    drop_index_safe("ix_audit_logs_actor_user_id", "audit_logs")
    drop_table_safe("audit_logs")

    drop_index_safe("ix_sessions_created_at", "sessions")
    drop_index_safe("ix_sessions_user_id", "sessions")
    drop_table_safe("sessions")

    drop_index_safe("ix_user_roles_org_unit_id", "user_roles")
    drop_index_safe("ix_user_roles_role_id", "user_roles")
    drop_index_safe("ix_user_roles_user_id", "user_roles")
    drop_table_safe("user_roles")

    drop_table_safe("template_permissions")
    drop_table_safe("permission_templates")
    drop_table_safe("role_permissions")

    drop_index_safe("ix_permissions_scope", "permissions")
    drop_table_safe("permissions")

    drop_index_safe("ix_roles_parent_role_id", "roles")
    drop_table_safe("roles")

    drop_index_safe("ix_org_memberships_org_unit_id", "org_memberships")
    drop_index_safe("ix_org_memberships_user_id", "org_memberships")
    drop_table_safe("org_memberships")

    drop_index_safe("ix_org_units_created_at", "org_units")
    drop_index_safe("ix_org_units_parent_id", "org_units")
    drop_table_safe("org_units")
