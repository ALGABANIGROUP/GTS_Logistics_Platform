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
    return inspect(bind)

"""create partner manager tables

Revision ID: 9f0c2c9e7b1a
Revises: c4f2a2b9e1f3
Create Date: 2025-12-29
"""


from alembic import op, context
from alembic import context
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = "9f0c2c9e7b1a"
down_revision = "c4f2a2b9e1f3"
branch_labels = None
depends_on = None



def _is_offline() -> bool:
    try:
        return context.is_offline_mode()
    except Exception:
        return False

def table_exists(table_name: str) -> bool:
    # EN --sql EN DB EN => EN Alembic EN SQL EN
    if _is_offline():
        return False
    bind = op.get_bind()
    insp = safe_inspect(bind)
    return insp.has_table(table_name)


def index_exists(table_name: str, index_name: str) -> bool:
    if context.is_offline_mode():
        return False
    # EN --sql (offline) EN DB EN inspect
    if context.is_offline_mode():
        return False
    bind = op.get_bind()
    inspector = safe_inspect(bind)
    if table_name not in inspector.get_table_names():
        return False
    return index_name in {ix["name"] for ix in inspector.get_indexes(table_name)}


def column_exists(table_name: str, column_name: str) -> bool:
    if context.is_offline_mode():
        return False
    # EN --sql (offline) EN DB EN inspect
    if context.is_offline_mode():
        return False
    bind = op.get_bind()
    insp = safe_inspect(bind)
    cols = insp.get_columns(table_name)
    return any(c.get("name") == column_name for c in cols)


def upgrade():
    if not table_exists("partners"):
        op.create_table(
            "partners",
            sa.Column("id", sa.Integer, primary_key=True),
            sa.Column("name", sa.String(255), nullable=False),
            sa.Column("status", sa.String(50), server_default="pending", nullable=False),
            sa.Column("tier", sa.String(50)),
            sa.Column("contact_name", sa.String(255)),
            sa.Column("contact_email", sa.String(255)),
            sa.Column("contact_phone", sa.String(50)),
            sa.Column("website", sa.String(255)),
            sa.Column("metadata", sa.JSON),
            sa.Column("created_by", sa.Integer),
            sa.Column("updated_by", sa.Integer),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True)),
        )

    if not column_exists("partners", "tier"):
        op.add_column("partners", sa.Column("tier", sa.String(50)))

    if column_exists("partners", "meta") and not column_exists("partners", "metadata"):
        op.alter_column("partners", "meta", new_column_name="metadata")
    elif not column_exists("partners", "metadata"):
        op.add_column("partners", sa.Column("metadata", sa.JSON))

    if not index_exists("partners", "ix_partners_status"):
        op.create_index("ix_partners_status", "partners", ["status"])

    if column_exists("partners", "tier") and not index_exists("partners", "ix_partners_tier"):
        op.create_index("ix_partners_tier", "partners", ["tier"])


def downgrade():
    if index_exists("partners", "ix_partners_status"):
        op.drop_index("ix_partners_status", table_name="partners")

    if index_exists("partners", "ix_partners_tier"):
        op.drop_index("ix_partners_tier", table_name="partners")

    if table_exists("partners"):
        op.drop_table("partners")
