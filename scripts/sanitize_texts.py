import os
import re
import shutil
from pathlib import Path

# 1) Characters that cause problems (RTL/ZW)
BAD_INVISIBLE_RE = re.compile(r"[\u200E\u200F\u202A-\u202E\u2066-\u2069\u200B-\u200D]")

# 2) Put here any "broken sentences" or Arabic phrases you want to convert to English
REPLACEMENTS = {
    "Displayed data is demo (mock) data": "Displayed data is demo (mock) data",
    "Not real server data": "Not real server data",
    "Retry readiness check": "Retry readiness check",  # example: leave as is
    "Dispatcher": "Dispatcher",
    "Shipments": "Shipments",
    "Map": "Map",
    "Expenses": "Expenses",
    "Revenue": "Revenue",
    "Bots": "Bots",
    "Settings": "Settings",
    "Dashboard": "Dashboard",
}

# Files we work on
EXTS = {".js",".jsx",".ts",".tsx",".css",".scss",".json",".md",".py",".env"}

def should_skip(path: Path) -> bool:
    p = str(path).replace("\\", "/")
    return any(x in p for x in ["/node_modules/","/dist/","/build/","/.git/","/__pycache__/","/.venv/","/venv/"])

def sanitize_text(text: str) -> str:
    text2 = BAD_INVISIBLE_RE.sub("", text)
    for src, dst in REPLACEMENTS.items():
        text2 = text2.replace(src, dst)
    return text2

def main(root: str, dry_run: bool = True):
    root_path = Path(root)
    changed = 0
    scanned = 0

    for file_path in root_path.rglob("*"):
        if not file_path.is_file():
            continue
        if should_skip(file_path):
            continue
        if file_path.suffix.lower() not in EXTS:
            continue

        scanned += 1

        try:
            original = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            # If file is not UTF-8, skip it (or modify according to your project)
            continue

        cleaned = sanitize_text(original)

        if cleaned != original:
            changed += 1
            if dry_run:
                print(f"[DRY] would change: {file_path}")
            else:
                backup = file_path.with_suffix(file_path.suffix + ".bak")
                if not backup.exists():
                    shutil.copy2(file_path, backup)
                file_path.write_text(cleaned, encoding="utf-8")
                print(f"[OK] changed: {file_path}")

    print("\n=== Summary ===")
    print(f"Scanned files: {scanned}")
    print(f"Changed files: {changed}")
    print(f"Mode: {'DRY-RUN' if dry_run else 'WRITE'}")

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".", help="Project root folder")
    ap.add_argument("--write", action="store_true", help="Apply changes (default is dry-run)")
    args = ap.parse_args()
    main(args.root, dry_run=not args.write)