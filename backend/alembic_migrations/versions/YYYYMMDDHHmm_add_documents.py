"""placeholder for legacy 'add_documents' migration"""

from __future__ import annotations
from alembic import op
import sqlalchemy as sa

# ——— Alembic identifiers ———
revision = "YYYYMMDDHHmm_add_documents"
down_revision = None  # or set to the actual prior revision if you know it
branch_labels = None
depends_on = None

def upgrade() -> None:
    # No-op placeholder so Alembic can continue the chain
    pass

def downgrade() -> None:
    # No-op
    pass
