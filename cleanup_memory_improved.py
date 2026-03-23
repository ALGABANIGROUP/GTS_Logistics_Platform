#!/usr/bin/env python3
"""
cleanup_memory_improved.py
- recursive __pycache__ removal
- cleanup logs older than N days
- --dry-run option
"""
import argparse, shutil
from pathlib import Path
from datetime import datetime, timedelta

def cleanup_logs(dirpath, days=7, dry=False):
    logs_dir = Path(dirpath)
    if not logs_dir.exists():
        print("logs dir not found:", logs_dir); return 0
    cutoff = datetime.now()-timedelta(days=days)
    removed=0
    for f in logs_dir.rglob("*.log"):
        try:
            if datetime.fromtimestamp(f.stat().st_mtime) < cutoff:
                print("Remove:", f)
                if not dry:
                    f.unlink()
                    removed+=1
        except Exception as e:
            print("Err:",e)
    return removed

def cleanup_pycache(root=".", dry=False):
    removed=0
    for p in Path(root).rglob("__pycache__"):
        print("Remove cache:", p)
        if not dry:
            shutil.rmtree(p)
            removed+=1
    return removed

def cleanup_temp(root=".", dry=False):
    removed=0
    for pattern in ["*.tmp","*.temp","*.cache"]:
        for f in Path(root).rglob(pattern):
            print("Remove temp:", f)
            if not dry:
                try:
                    f.unlink()
                    removed+=1
                except Exception:
                    pass
    return removed

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--logs", default="backend/logs")
    p.add_argument("--days", type=int, default=7)
    p.add_argument("--dry", action="store_true")
    args=p.parse_args()
    print("Dry run:", args.dry)
    r=cleanup_logs(args.logs, args.days, args.dry)
    rc=cleanup_pycache(".", args.dry)
    rt=cleanup_temp(".", args.dry)
    print("Summary removed logs, pycache, temp:", r, rc, rt)

if __name__=="__main__":
    main()
