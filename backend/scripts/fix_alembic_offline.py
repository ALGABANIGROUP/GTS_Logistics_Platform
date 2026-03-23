# backend/scripts/fix_alembic_offline.py
from __future__ import annotations

import argparse
import re
from pathlib import Path

HELPER_BLOCK = r'''
class _OfflineInspector:
    def get_table_names(self): return []
    def get_columns(self, table_name): return []
    def get_indexes(self, table_name): return []
    def get_unique_constraints(self, table_name): return []
    def get_foreign_keys(self, table_name): return []
    def get_pk_constraint(self, table_name): return {}

def safe_inspect(bind):
    # In --sql (offline) bind is a MockConnection; sqlalchemy.inspect() will fail.
    if context.is_offline_mode():
        return _OfflineInspector()
    return sa.inspect(bind)
'''.strip() + "\n\n"


def ensure_context_import(src: str) -> str:
    if re.search(r'(?m)^\s*from alembic import context\s*$', src):
        return src

    # If "from alembic import op" exists, insert context above it
    if re.search(r'(?m)^\s*from alembic import op\s*$', src):
        return re.sub(
            r'(?m)^\s*from alembic import op\s*$',
            "from alembic import context\nfrom alembic import op",
            src,
            count=1,
        )

    # Otherwise insert after first "from alembic import ..."
    m = re.search(r'(?m)^(from alembic import .+)$', src)
    if m:
        return src[: m.end()] + "\nfrom alembic import context" + src[m.end():]

    # Fallback: prepend
    return "from alembic import context\n" + src


def ensure_sa_import(src: str) -> str:
    # We rely on "import sqlalchemy as sa"
    if re.search(r'(?m)^\s*import sqlalchemy as sa\s*$', src):
        return src
    # If there's "from sqlalchemy import ..." we still prefer adding sa import
    # Insert after last import line near top
    m = re.search(r'(?ms)\A((?:\s*(?:from|import)\s+[^\n]+\n)+)', src)
    if m:
        block = m.group(1)
        return src.replace(block, block + "import sqlalchemy as sa\n", 1)
    return "import sqlalchemy as sa\n" + src


def ensure_helper(src: str) -> str:
    if re.search(r'(?m)^\s*def\s+safe_inspect\s*\(', src):
        return src

    # Put helper after sqlalchemy import block (near top)
    m = re.search(r'(?ms)\A((?:\s*(?:from|import)\s+[^\n]+\n)+)\s*\n', src)
    if m:
        imports_block = m.group(1)
        return src.replace(imports_block, imports_block + "\n" + HELPER_BLOCK, 1)

    # Fallback: prepend helper
    return HELPER_BLOCK + src


def replace_inspects(src: str) -> str:
    # Replace sa.inspect(bind) -> safe_inspect(bind)
    src = re.sub(r'\bsa\.inspect\s*\(\s*bind\s*\)', 'safe_inspect(bind)', src)

    # Replace inspect(bind) -> safe_inspect(bind) ONLY when it's not already safe_inspect
    src = re.sub(r'(?<!safe_)inspect\s*\(\s*bind\s*\)', 'safe_inspect(bind)', src)

    return src


def check_upgrade_downgrade(path: Path, src: str) -> list[str]:
    warns = []
    if not re.search(r'(?m)^\s*def\s+upgrade\s*\(', src):
        warns.append(f"[WARN] {path.name}: missing def upgrade()")
    if not re.search(r'(?m)^\s*def\s+downgrade\s*\(', src):
        warns.append(f"[WARN] {path.name}: missing def downgrade()")
    return warns


def patch_file(path: Path, apply: bool) -> list[str]:
    src = path.read_text(encoding="utf-8", errors="replace")

    # Only patch files that look like they use bind inspection
    if not (re.search(r'\binspect\s*\(\s*bind\s*\)', src) or re.search(r'\bsa\.inspect\s*\(\s*bind\s*\)', src)):
        return []

    original = src

    src = ensure_context_import(src)
    src = ensure_sa_import(src)
    src = ensure_helper(src)
    src = replace_inspects(src)

    warnings = check_upgrade_downgrade(path, src)

    if apply and src != original:
        path.write_text(src, encoding="utf-8", newline="\n")

    return warnings


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--versions", default="alembic_migrations/versions", help="Path to Alembic versions folder")
    ap.add_argument("--apply", action="store_true", help="Write changes (otherwise dry-run)")
    args = ap.parse_args()

    versions = Path(args.versions)
    if not versions.exists():
        print(f"[ERROR] versions folder not found: {versions}")
        return 2

    files = sorted(versions.glob("*.py"))
    touched = 0
    all_warns: list[str] = []

    for f in files:
        before = f.read_text(encoding="utf-8", errors="replace")
        warns = patch_file(f, apply=args.apply)
        after = f.read_text(encoding="utf-8", errors="replace")

        if before != after:
            touched += 1
            print(f"[OK] patched: {f.name}")

        all_warns.extend(warns)

    mode = "APPLIED" if args.apply else "DRY-RUN"
    print(f"\n[{mode}] done. files_changed={touched}")

    if all_warns:
        print("\n".join(all_warns))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
