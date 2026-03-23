from __future__ import annotations

import argparse

from sqlalchemy import text
from backend.database.connection import get_sync_engine_from_env

TABLES = ("portal_requests", "portal_access_requests")


def _table_exists(conn, table_name: str) -> bool:
    result = conn.execute(
        text(
            """
            SELECT 1
            FROM information_schema.tables
            WHERE table_schema = 'public' AND table_name = :name
            LIMIT 1
            """
        ),
        {"name": table_name},
    )
    return result.first() is not None


def _count_total(conn, table_name: str) -> int:
    result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
    return int(result.scalar() or 0)


def _count_duplicate_rows(conn, table_name: str) -> int:
    result = conn.execute(
        text(
            f"""
            SELECT COALESCE(SUM(cnt - 1), 0) AS dup_rows
            FROM (
                SELECT COUNT(*) AS cnt
                FROM {table_name}
                WHERE email IS NOT NULL AND BTRIM(email) <> ''
                GROUP BY LOWER(BTRIM(email))
                HAVING COUNT(*) > 1
            ) AS grouped
            """
        )
    )
    return int(result.scalar() or 0)


def _delete_duplicates(conn, table_name: str) -> int:
    result = conn.execute(
        text(
            f"""
            WITH ranked AS (
                SELECT id,
                       ROW_NUMBER() OVER (
                           PARTITION BY LOWER(BTRIM(email))
                           ORDER BY created_at DESC NULLS LAST, id DESC
                       ) AS rn
                FROM {table_name}
                WHERE email IS NOT NULL AND BTRIM(email) <> ''
            )
            DELETE FROM {table_name}
            WHERE id IN (SELECT id FROM ranked WHERE rn > 1)
            RETURNING id
            """
        )
    )
    return len(result.fetchall())


def _create_unique_index(conn, table_name: str) -> None:
    index_name = f"ux_{table_name}_email_norm"
    conn.execute(
        text(
            f"""
            CREATE UNIQUE INDEX IF NOT EXISTS {index_name}
            ON {table_name} (LOWER(BTRIM(email)))
            WHERE email IS NOT NULL AND BTRIM(email) <> ''
            """
        )
    )


def _clean_table(engine, table_name: str, apply: bool) -> None:
    with engine.connect() as conn:
        if not _table_exists(conn, table_name):
            print(f"[cleanup] {table_name}: missing, skipped")
            return

        total = _count_total(conn, table_name)
        dup_rows = _count_duplicate_rows(conn, table_name)
        print(f"[cleanup] {table_name}: total={total} duplicate_rows={dup_rows}")

    if not apply:
        return

    with engine.begin() as conn:
        deleted = _delete_duplicates(conn, table_name)
    print(f"[cleanup] {table_name}: deleted={deleted}")

    with engine.begin() as conn:
        _create_unique_index(conn, table_name)
    print(f"[cleanup] {table_name}: unique index ensured")

    with engine.connect() as conn:
        remaining = _count_duplicate_rows(conn, table_name)
    print(f"[cleanup] {table_name}: duplicate_rows_after={remaining}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Remove duplicate portal requests by normalized email."
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply deletions and create unique indexes.",
    )
    args = parser.parse_args()

    engine = get_sync_engine_from_env()

    for table in TABLES:
        _clean_table(engine, table, apply=args.apply)


if __name__ == "__main__":
    main()

