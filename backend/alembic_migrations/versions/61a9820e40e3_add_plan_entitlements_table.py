from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "61a9820e40e3"
down_revision = "3106f4e0626c"  # EN revision EN
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "plan_entitlements",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("plan_id", sa.String(length=64), nullable=False),
        sa.Column("key", sa.String(length=128), nullable=False),
        sa.Column("value_json", sa.JSON, nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    op.create_index(
        "ix_plan_entitlements_plan_id",
        "plan_entitlements",
        ["plan_id"],
    )


def downgrade():
    op.drop_index(
        "ix_plan_entitlements_plan_id",
        table_name="plan_entitlements",
    )
    op.drop_table("plan_entitlements")
