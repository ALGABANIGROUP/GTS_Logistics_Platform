from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "3106f4e0626c"
down_revision = "2837ab1f9c72"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "subscription_addons",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("subscription_id", sa.Integer, nullable=False),
        sa.Column("addon_code", sa.String(length=100), nullable=False),
        sa.Column("enabled", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("metadata", sa.JSON, nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )


def downgrade():
    op.drop_table("subscription_addons")
