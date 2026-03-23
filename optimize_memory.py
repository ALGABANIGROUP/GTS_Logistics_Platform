#!/usr/bin/env python3
"""Memory Optimization Script for GTS Backend"""

import sys
from pathlib import Path


def optimize_database_config() -> bool:
    """Optimize database connection pool settings"""
    print("🔧 Optimizing database configuration...")
    config_file = Path("backend/database/config.py")
    if not config_file.exists():
        print("❌ config.py not found!")
        return False

    content = config_file.read_text(encoding="utf-8")
    old_config = '''
        else:
            # Production: QueuePool with optimizations
            _async_engine = create_async_engine(
                dsn,
                echo=False,
                future=True,
                pool_size=20,
                max_overflow=30,
                pool_timeout=30,
                pool_pre_ping=True,
                pool_recycle=3600,  # Recycle connections every hour
            )
            print(f"[db] Production mode: Pool configured (size=20, max_overflow=30, timeout=30s)")'''
    new_config = '''
        else:
            # Production: QueuePool with memory optimizations
            # Reduced pool_size to lower memory footprint
            # pool_recycle=600 recycles stale connections faster
            _async_engine = create_async_engine(
                dsn,
                echo=False,
                future=True,
                pool_size=10,  # Reduced from 20 (max ~25 active instead of 50)
                max_overflow=15,  # Reduced from 30
                pool_timeout=20,  # Reduced from 30 seconds
                pool_pre_ping=False,  # Disable to save a bit of memory
                pool_recycle=600,  # Recycle connections every 10 minutes
                connect_args={"timeout": 10, "command_timeout": 10},
            )
            print(f"[db] Production mode: Pool optimized (size=10, max_overflow=15, recycle=600s)")'''

    if new_config.strip() in content:
        print("✅ Database configuration already optimized")
        return True

    if old_config.strip() in content:
        content = content.replace(old_config, new_config)
        config_file.write_text(content, encoding="utf-8")
        print("✅ Database pool settings optimized!")
        return True

    print("⚠️  Could not find exact config pattern to replace")
    return False


def create_memory_monitoring_script() -> bool:
    """Create a script to monitor memory usage"""
    monitor_script = '''#!/usr/bin/env python3
\"\"\"Memory monitoring utility for GTS Backend\"\"\"

import psutil
import time
from datetime import datetime


def monitor_memory(interval: int = 30, threshold: int = 80) -> None:
    \"\"\"Monitor system memory usage\"\"\"
    print(f"🔍 Memory Monitor Started (threshold: {threshold}%)")
    print("=" * 60)
    try:
        while True:
            mem = psutil.virtual_memory()
            cpu = psutil.cpu_percent(interval=1)
            status = "🔴" if mem.percent > threshold else "🟢"
            print(
                f"{status} {datetime.now():%H:%M:%S} | "
                f"Memory: {mem.percent}% ({mem.used // (1024**3)}GB/{mem.total // (1024**3)}GB) | "
                f"CPU: {cpu}%"
            )
            if mem.percent > threshold:
                print("⚠️  WARNING: High memory usage detected!")
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\\n✅ Monitor stopped")


if __name__ == "__main__":
    monitor_memory()
'''
    monitor_file = Path("monitor_memory.py")
    monitor_file.write_text(monitor_script, encoding="utf-8")
    print("✅ Created monitor_memory.py")
    return True


def create_cleanup_script() -> bool:
    """Create cleanup script for logs and cache"""
    cleanup_script = '''#!/usr/bin/env python3
\"\"\"Cleanup script for logs and cache\"\"\"

import shutil
from datetime import datetime, timedelta
from pathlib import Path


def cleanup_old_logs(days: int = 7) -> int:
    \"\"\"Remove logs older than the specified number of days\"\"\"
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
    \"\"\"Clear application cache\"\"\"
    cache_dir = Path("backend/__pycache__")
    if cache_dir.exists():
        try:
            shutil.rmtree(cache_dir)
            print(f"✅ Cleared cache directory: {cache_dir}")
        except Exception as e:
            print(f"⚠️  Error clearing cache: {e}")


def cleanup_temp_files() -> int:
    \"\"\"Remove temporary files\"\"\"
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
'''
    cleanup_file = Path("cleanup_memory.py")
    cleanup_file.write_text(cleanup_script, encoding="utf-8")
    print("✅ Created cleanup_memory.py")
    return True


def main() -> int:
    print("=" * 60)
    print("🚀 GTS Memory Optimization")
    print("=" * 60)

    success = optimize_database_config()
    success = create_memory_monitoring_script() and success
    success = create_cleanup_script() and success

    print("\n" + "=" * 60)
    print("📝 Next Steps:")
    print("=" * 60)
    print("1. Restart backend: python -m uvicorn backend.main:app --reload")
    print("2. Monitor memory: python monitor_memory.py")
    print("3. Cleanup periodically: python cleanup_memory.py")
    print("4. Check results at: http://localhost:5173/test-connection.html")

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
