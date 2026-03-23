#!/usr/bin/env python3
"""Memory monitoring utility for GTS Backend"""

import psutil
import time
from datetime import datetime


def monitor_memory(interval: int = 30, threshold: int = 80) -> None:
    """Monitor system memory usage"""
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
        print("\n✅ Monitor stopped")


if __name__ == "__main__":
    monitor_memory()
