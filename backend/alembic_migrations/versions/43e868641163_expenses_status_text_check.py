"""expenses.status -> TEXT + CHECK; drop old enum type if unused"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "43e868641163"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Check if we're using PostgreSQL or SQLite
    conn = op.get_bind()
    dialect_name = conn.dialect.name
    
    if dialect_name == 'postgresql':
        # PostgreSQL: convert enum column to TEXT
        op.execute("ALTER TABLE expenses ALTER COLUMN status TYPE TEXT USING status::text;")
        # normalize to upper-case
        op.execute("UPDATE expenses SET status = UPPER(status);")
        # enforce allowed values
        op.create_check_constraint(
            "ck_expenses_status",
            "expenses",
            "status IN ('PENDING','PAID')",
        )
        # best-effort: drop old enum type if no longer used
        op.execute(
            '''
            DO $$
            BEGIN
                IF EXISTS (SELECT 1 FROM pg_type WHERE typname = 'expense_status') THEN
                    BEGIN
                        BEGIN
                            DROP TYPE expense_status;
                        EXCEPTION WHEN dependent_objects_still_exist THEN
                            RAISE NOTICE 'expense_status type still in use; skipping drop';
                        END;
                    END;
                END IF;
            END
            $$;
            '''
        )
    elif dialect_name == 'sqlite':
        # SQLite: Just update values and add check constraint
        # (SQLite doesn't have ENUM types, so no ALTER needed)
        op.execute("UPDATE expenses SET status = UPPER(status) WHERE status IS NOT NULL;")
        # SQLite supports CHECK constraints
        try:
            op.create_check_constraint(
                "ck_expenses_status",
                "expenses",
                "status IN ('PENDING','PAID')",
            )
        except:
            # If table doesn't exist yet, skip
            pass


def downgrade() -> None:
    # Check if we're using PostgreSQL or SQLite
    conn = op.get_bind()
    dialect_name = conn.dialect.name
    
    if dialect_name == 'postgresql':
        # recreate enum type
        op.execute("CREATE TYPE expense_status AS ENUM ('PENDING','PAID');")
        # remove CHECK
        op.drop_constraint("ck_expenses_status", "expenses", type_="check")
        # convert back to enum
        op.execute("ALTER TABLE expenses ALTER COLUMN status TYPE expense_status USING status::expense_status;")
    elif dialect_name == 'sqlite':
        # SQLite: Just remove check constraint
        try:
            op.drop_constraint("ck_expenses_status", "expenses", type_="check")
        except:
            pass