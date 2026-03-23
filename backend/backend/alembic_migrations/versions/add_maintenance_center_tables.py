from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "add_maintenance_center_tables"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "maintenance_runs",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="running"),
        sa.Column("trigger", sa.String(length=32), nullable=False, server_default="scheduler"),
        sa.Column("summary", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_by", sa.String(length=255), nullable=True),
    )
    op.create_index("ix_maintenance_runs_started_at", "maintenance_runs", ["started_at"])

    op.create_table(
        "issues",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("run_id", sa.BigInteger(), sa.ForeignKey("maintenance_runs.id", ondelete="SET NULL"), nullable=True),
        sa.Column("severity", sa.String(length=16), nullable=False, server_default="medium"),
        sa.Column("code", sa.String(length=64), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="open"),
        sa.Column("meta", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_issues_status", "issues", ["status"])
    op.create_index("ix_issues_severity", "issues", ["severity"])
    op.create_index("ix_issues_created_at", "issues", ["created_at"])

    op.create_table(
        "recommendations",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("run_id", sa.BigInteger(), sa.ForeignKey("maintenance_runs.id", ondelete="SET NULL"), nullable=True),
        sa.Column("severity", sa.String(length=16), nullable=False, server_default="low"),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("action", sa.String(length=64), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="new"),
        sa.Column("admin_notes", sa.Text(), nullable=True),
        sa.Column("decided_by", sa.String(length=255), nullable=True),
        sa.Column("decided_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("meta", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
    )
    op.create_index("ix_recommendations_status", "recommendations", ["status"])
    op.create_index("ix_recommendations_created_at", "recommendations", ["created_at"])


def downgrade():
    # EN
    pass
