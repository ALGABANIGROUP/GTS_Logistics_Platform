"""harden expenses: idempotent columns + indexes"""
from alembic import op

# Alembic identifiers
revision = "20250826_01_harden_expenses"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Columns (idempotent)
    op.execute("""
        ALTER TABLE IF EXISTS expenses
            ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'PENDING' NOT NULL
    """)
    op.execute("""ALTER TABLE IF EXISTS expenses ADD COLUMN IF NOT EXISTS dedupe_key TEXT""")
    op.execute("""ALTER TABLE IF EXISTS expenses ADD COLUMN IF NOT EXISTS category VARCHAR""")
    op.execute("""ALTER TABLE IF EXISTS expenses ADD COLUMN IF NOT EXISTS description TEXT""")
    op.execute("""ALTER TABLE IF EXISTS expenses ADD COLUMN IF NOT EXISTS vendor VARCHAR""")
    op.execute("""ALTER TABLE IF EXISTS expenses ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ DEFAULT now()""")
    op.execute("""ALTER TABLE IF EXISTS expenses ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT now()""")

    # Backfill (safe)
    op.execute("""
DO $$
DECLARE
    v_is_enum   boolean := false;
    v_typname   text := NULL;
    v_label     text := NULL;
BEGIN
    -- EN ENUM EN VARCHAREN
    SELECT (data_type = 'USER-DEFINED') AS is_enum, udt_name
    INTO v_is_enum, v_typname
    FROM information_schema.columns
    WHERE table_name = 'expenses' AND column_name = 'status';

    IF v_is_enum THEN
        -- EN ENUM: EN pending/paid EN
        SELECT e.enumlabel
        INTO v_label
        FROM pg_type t
        JOIN pg_enum e ON t.oid = e.enumtypid
        WHERE t.typname = v_typname
          AND lower(e.enumlabel) IN ('pending','paid')
        ORDER BY CASE WHEN lower(e.enumlabel)='pending' THEN 0 ELSE 1 END
        LIMIT 1;

        IF v_label IS NULL THEN
            SELECT e.enumlabel
            INTO v_label
            FROM pg_type t
            JOIN pg_enum e ON t.oid = e.enumtypid
            WHERE t.typname = v_typname
            ORDER BY e.enumlabel
            LIMIT 1;
        END IF;

        EXECUTE format(
            'UPDATE expenses SET status = %L::%I WHERE status IS NULL',
            v_label, v_typname
        );

    ELSE
        -- EN VARCHAR: EN 'PENDING' EN
        UPDATE expenses SET status = 'PENDING' WHERE status IS NULL;
    END IF;
END $$;
""")

    # Indexes (idempotent)
    op.execute("""CREATE INDEX IF NOT EXISTS idx_expenses_status   ON expenses (status)""")
    op.execute("""CREATE INDEX IF NOT EXISTS idx_expenses_vendor   ON expenses (vendor)""")
    op.execute("""CREATE INDEX IF NOT EXISTS idx_expenses_category ON expenses (category)""")
    op.execute("""CREATE INDEX IF NOT EXISTS idx_expenses_created  ON expenses (created_at)""")

    # Partial unique index for dedupe (idempotent)
    op.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS uq_expenses_dedupe
        ON expenses (dedupe_key)
        WHERE dedupe_key IS NOT NULL
    """)

def downgrade():
    # keep hardened schema
    pass
