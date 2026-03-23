#!/usr/bin/env python3
import sys

try:
    from backend.main import dump_memory_snapshot
except Exception as e:
    print("Failed to import dump_memory_snapshot from backend.main:", e)
    sys.exit(1)

path = dump_memory_snapshot(top=30)
print("Snapshot written to:", path)
