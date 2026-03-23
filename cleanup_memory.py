#!/usr/bin/env python3
"""Cleanup script for logs and cache"""

import shutil
from datetime import datetime, timedelta
from pathlib import Path


def cleanup_old_logs(days: int = 7) -> int:
    """Remove logs older than the specified number of days"""
    logs_dir = Path("backend/logs")
    if not logs_dir.exists():
        print("❌ logs directory not found")
        return 0

    cutoff_time = datetime.now() - timedelta(days=days)
    removed = 0
    for log_file in logs_dir.glob("*.log"):
        try:
            mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
            if mtime < cutoff_time:
                log_file.unlink()
                removed += 1
                print(f"🗑️  Removed: {log_file.name}")
        except Exception as e:
            print(f"⚠️  Error removing {log_file}: {e}")
    print(f"✅ Cleaned {removed} old log files")
    return removed


def cleanup_cache() -> None:
    """Clear application cache"""
    cache_dir = Path("backend/__pycache__")
    if cache_dir.exists():
        try:
            shutil.rmtree(cache_dir)
            print(f"✅ Cleared cache directory: {cache_dir}")
        except Exception as e:
            print(f"⚠️  Error clearing cache: {e}")


def cleanup_temp_files() -> int:
    """Remove temporary files"""
    patterns = ["*.tmp", "*.temp", "*.cache"]
    removed = 0
    for pattern in patterns:
        for file in Path(".").glob(f"**/{pattern}"):
            try:
                file.unlink()
                removed += 1
            except Exception:
                pass
    print(f"✅ Removed {removed} temporary files")
    return removed


if __name__ == "__main__":
    print("🧹 Cleanup Starting...")
    print("=" * 60)
    cleanup_old_logs(days=7)
    cleanup_cache()
    cleanup_temp_files()
    print("=" * 60)
    print("✅ Cleanup completed!")
