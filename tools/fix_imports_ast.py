# tools/fix_imports_ast.py
from __future__ import annotations
import ast
import os
import sys
import argparse
from typing import List, Tuple

INTERNAL_TOPS = {"routes", "models", "database", "services", "utils", "core", "ai"}

def is_internal_module(mod: str) -> bool:
    if not mod:
        return False
    head = mod.split(".", 1)[0]
    return head in INTERNAL_TOPS

class ImportRewriter(ast.NodeTransformer):
    def __init__(self) -> None:
        super().__init__()
        self.changed = False

    def visit_ImportFrom(self, node: ast.ImportFrom) -> ast.AST:
        # Ignore relative imports (level > 0): from .x import y
        if getattr(node, "level", 0):
            return node
        mod = node.module or ""
        # already absolute under backend.*
        if mod.startswith("backend."):
            return node
        # Only fix top-level internal modules
        if is_internal_module(mod):
            node.module = f"backend.{mod}"
            self.changed = True
        return node

    def visit_Import(self, node: ast.Import) -> ast.AST:
        for alias in node.names:
            name = alias.name
            if name.startswith("backend."):
                continue
            head = name.split(".", 1)[0]
            if head in INTERNAL_TOPS:
                alias.name = f"backend.{name}"
                self.changed = True
        return node

def find_py_files(root: str) -> List[str]:
    files: List[str] = []
    ignore_dirs = {".venv", "venv", "__pycache__", ".mypy_cache", ".pytest_cache", ".git"}
    for r, ds, fs in os.walk(root):
        parts = set(r.split(os.sep))
        if parts & ignore_dirs:
            continue
        for f in fs:
            if f.endswith(".py") and not f.startswith("__"):
                files.append(os.path.join(r, f))
    return files

def ensure_init_packages(root: str) -> List[str]:
    created: List[str] = []
    for r, ds, fs in os.walk(root):
        parts = r.split(os.sep)
        if "__pycache__" in parts or ".git" in parts:
            continue
        if "backend" not in parts:
            continue
        if "__init__.py" not in fs:
            p = os.path.join(r, "__init__.py")
            try:
                with open(p, "a", encoding="utf-8"):
                    pass
                created.append(p)
            except Exception:
                pass
    return created

def process_file(path: str, dry_run: bool) -> Tuple[bool, str]:
    with open(path, "r", encoding="utf-8") as f:
        src = f.read()
    try:
        tree = ast.parse(src, filename=path)
    except SyntaxError:
        return False, "syntax_error"

    rewriter = ImportRewriter()
    new_tree = rewriter.visit(tree)
    if not rewriter.changed:
        return False, "no_change"

    if not hasattr(ast, "unparse"):
        return False, "no_unparse_support"

    new_code = ast.unparse(new_tree)
    if new_code.strip() == src.strip():
        return False, "no_change"

    if dry_run:
        return True, "would_change"

    bak = path + ".bak"
    try:
        if not os.path.exists(bak):
            with open(bak, "w", encoding="utf-8") as bf:
                bf.write(src)
        with open(path, "w", encoding="utf-8") as wf:
            wf.write(new_code)
        return True, "changed"
    except Exception as e:
        return False, f"write_error:{e}"

def main() -> None:
    parser = argparse.ArgumentParser(description="Normalize internal imports to absolute 'backend.*'.")
    parser.add_argument("--root", default="backend", help="Project backend root dir")
    parser.add_argument("--dry-run", action="store_true", help="Report only; do not write changes")
    args = parser.parse_args()

    # Ensure package structure
    created_inits = ensure_init_packages(args.root)
    if created_inits:
        print(f"[init] created {len(created_inits)} __init__.py files")

    files = find_py_files(args.root)
    print(f"[scan] {len(files)} python files under '{args.root}'")

    changed_total = 0
    for p in files:
        changed, msg = process_file(p, args.dry_run)
        if changed:
            changed_total += 1
            print(f"[fix]  {p} -> {msg}")
        elif msg != "no_change":
            print(f"[skip] {p} -> {msg}")

    print(f"\n[summary] changed: {changed_total} / {len(files)} files")
    if args.dry_run:
        print("[note] dry-run only; run again without --dry-run to apply.")
    else:
        print("[note] backups written as '*.bak' (first time only).")

if __name__ == "__main__":
    sys.path.insert(0, os.getcwd())
    main()
