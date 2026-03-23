"""add maintenance center tables

Revision ID: 802d41db8636
Revises: 8a9d3c2d822d
Create Date: 2026-01-15 19:37:26.918417

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '802d41db8636'
down_revision: Union[str, Sequence[str], None] = '8a9d3c2d822d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "maintenance_runs",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("run_type", sa.String(50), nullable=False, server_default="scheduled"),
        sa.Column("status", sa.String(30), nullable=False, server_default="ok"),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("summary", sa.dialects.postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )

    op.create_table(
        "maintenance_issues",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("run_id", sa.BigInteger(), sa.ForeignKey("maintenance_runs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("severity", sa.String(20), nullable=False, server_default="medium"),
        sa.Column("source", sa.String(50), nullable=False, server_default="system"),
        sa.Column("code", sa.String(100), nullable=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("details", sa.dialects.postgresql.JSONB(), nullable=True),
        sa.Column("status", sa.String(30), nullable=False, server_default="open"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_maintenance_issues_run_id", "maintenance_issues", ["run_id"])
    op.create_index("ix_maintenance_issues_status", "maintenance_issues", ["status"])
    op.create_index("ix_maintenance_issues_severity", "maintenance_issues", ["severity"])

    op.create_table(
        "maintenance_recommendations",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("run_id", sa.BigInteger(), sa.ForeignKey("maintenance_runs.id", ondelete="SET NULL"), nullable=True),
        sa.Column("priority", sa.String(20), nullable=False, server_default="medium"),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("action_type", sa.String(50), nullable=True),
        sa.Column("payload", sa.dialects.postgresql.JSONB(), nullable=True),
        sa.Column("status", sa.String(30), nullable=False, server_default="pending"),
        sa.Column("admin_notes", sa.Text(), nullable=True),
        sa.Column("decided_by", sa.String(255), nullable=True),
        sa.Column("decided_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_maintenance_reco_status", "maintenance_recommendations", ["status"])
    op.create_index("ix_maintenance_reco_priority", "maintenance_recommendations", ["priority"])


def downgrade() -> None:
    op.drop_index("ix_maintenance_reco_priority", table_name="maintenance_recommendations")
    op.drop_index("ix_maintenance_reco_status", table_name="maintenance_recommendations")
    op.drop_table("maintenance_recommendations")

    op.drop_index("ix_maintenance_issues_severity", table_name="maintenance_issues")
    op.drop_index("ix_maintenance_issues_status", table_name="maintenance_issues")
    op.drop_index("ix_maintenance_issues_run_id", table_name="maintenance_issues")
    op.drop_table("maintenance_issues")

    op.drop_table("maintenance_runs")
