"""add open_web_leads table

Revision ID: 282b5f7c9877
Revises: a5b9c2d3e4f6
Create Date: 2025-11-13 20:30:41.420960

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "282b5f7c9877"
down_revision: Union[str, Sequence[str], None] = "a5b9c2d3e4f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema: create open_web_leads table."""

    op.create_table(
        "open_web_leads",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("source", sa.String(length=255), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("origin", sa.String(length=255), nullable=True),
        sa.Column("destination", sa.String(length=255), nullable=True),
        sa.Column("weight_lbs", sa.Integer(), nullable=True),
        sa.Column("equipment", sa.String(length=100), nullable=True),
        sa.Column("contact_email", sa.String(length=255), nullable=True),
        sa.Column("contact_phone", sa.String(length=100), nullable=True),
        sa.Column("contact_name", sa.String(length=255), nullable=True),
        sa.Column("raw_url", sa.Text(), nullable=False),
        sa.Column("posted_at", sa.DateTime(), nullable=True),
        sa.Column("score", sa.Integer(), nullable=True),
        sa.Column(
            "status",
            sa.String(length=50),
            nullable=False,
            server_default="new",
        ),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint(
            "raw_url",
            "title",
            name="uq_open_web_leads_url_title",
        ),
    )


def downgrade() -> None:
    """Downgrade schema: drop open_web_leads table."""

    op.drop_table("open_web_leads")
