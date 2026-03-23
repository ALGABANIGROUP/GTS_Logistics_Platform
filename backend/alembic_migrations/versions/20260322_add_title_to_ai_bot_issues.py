"""add_title_column_to_ai_bot_issues

Revision ID: 20260322_add_title_to_ai_bot_issues
Revises: faab766d1a0f
Create Date: 2026-03-22 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20260322_add_title_to_ai_bot_issues'
down_revision: Union[str, None] = 'faab766d1a0f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add title column to ai_bot_issues table
    op.add_column('ai_bot_issues', sa.Column('title', sa.String(length=500), nullable=True))

    # Update existing records with default title
    op.execute("UPDATE ai_bot_issues SET title = 'Issue ' || id::text WHERE title IS NULL")

    # Make title column NOT NULL
    op.alter_column('ai_bot_issues', 'title', nullable=False)

    # Add other missing columns that are in the model but not in migration
    op.add_column('ai_bot_issues', sa.Column('severity', sa.String(length=20), nullable=True, default='low'))
    op.add_column('ai_bot_issues', sa.Column('status', sa.String(length=20), nullable=True, default='open'))
    op.add_column('ai_bot_issues', sa.Column('reported_by', sa.String(length=255), nullable=True, default='system'))
    op.add_column('ai_bot_issues', sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True))

    # Update existing records
    op.execute("UPDATE ai_bot_issues SET severity = 'low' WHERE severity IS NULL")
    op.execute("UPDATE ai_bot_issues SET status = 'open' WHERE status IS NULL")
    op.execute("UPDATE ai_bot_issues SET reported_by = 'system' WHERE reported_by IS NULL")

    # Make columns NOT NULL where required by model
    op.alter_column('ai_bot_issues', 'severity', nullable=False)
    op.alter_column('ai_bot_issues', 'status', nullable=False)
    op.alter_column('ai_bot_issues', 'reported_by', nullable=False)


def downgrade() -> None:
    # Remove the added columns
    op.drop_column('ai_bot_issues', 'title')
    op.drop_column('ai_bot_issues', 'severity')
    op.drop_column('ai_bot_issues', 'status')
    op.drop_column('ai_bot_issues', 'reported_by')
    op.drop_column('ai_bot_issues', 'updated_at')