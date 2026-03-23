
"""add invoices table

Revision ID: 10c9eab6dbad
Revises: 8a3aa957f944
Create Date: 2025-07-25 14:04:10.524888
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '10c9eab6dbad'
down_revision = '8a3aa957f944'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Skipped because 'invoices' table already exists
    pass


def downgrade() -> None:
    op.drop_table('invoices')

    enum_types = [
        "expensestatus",
        "shipmentstatus",
        "shipmenttype",
        "userrole",
        "accounttype"
    ]

    for enum_type in set(enum_types):
        op.execute(f'DROP TYPE IF EXISTS {enum_type}')
