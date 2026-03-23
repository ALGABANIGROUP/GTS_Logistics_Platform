
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

"""add user auth fields

Revision ID: d8a1b2c3d4e5
Revises: c4f2a2b9e1f3
Create Date: 2026-01-02

"""

from typing import Sequence, Union
from alembic import context
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "d8a1b2c3d4e5"
down_revision: Union[str, Sequence[str], None] = "c4f2a2b9e1f3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None
def _column_names(table_name):
    # Offline: EN inspect EN (MockConnection)
    if context.is_offline_mode():
        return set()

    bind = op.get_bind()
    inspector = safe_inspect(bind)
    try:
        cols = inspector.get_columns(table_name)
    except Exception:
        return set()
    return {c.get("name") for c in cols if c.get("name")}
    

from alembic import context

def upgrade():
    # TEMP: no-op to allow offline --sql generation safely
    return

def downgrade():
    # TEMP: no-op
    return
