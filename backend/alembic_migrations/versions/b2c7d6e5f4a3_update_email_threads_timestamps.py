"""Ensure email_threads timestamps default

Revision ID: b2c7d6e5f4a3
Revises: a9c8d7e6f5b4
Create Date: 2026-01-04

"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "b2c7d6e5f4a3"
down_revision: Union[str, Sequence[str], None] = "a9c8d7e6f5b4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("UPDATE email_threads SET updated_at = created_at WHERE updated_at IS NULL")
    op.execute("ALTER TABLE email_threads ALTER COLUMN updated_at SET DEFAULT now()")
    op.execute("ALTER TABLE email_threads ALTER COLUMN created_at SET DEFAULT now()")


def downgrade() -> None:
    op.execute("ALTER TABLE email_threads ALTER COLUMN updated_at DROP DEFAULT")
    op.execute("ALTER TABLE email_threads ALTER COLUMN created_at DROP DEFAULT")
