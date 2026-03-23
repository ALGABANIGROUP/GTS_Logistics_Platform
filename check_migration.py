#!/usr/bin/env python
"""Check social media tables migration status"""
import sys
import subprocess
from pathlib import Path

repo_root = Path(__file__).parent

# Check current migration status
print("Checking Alembic status...")
result = subprocess.run(
    [sys.executable, "-m", "alembic", "-c", "backend/alembic.ini", "current"],
    cwd=repo_root,
    capture_output=True,
    text=True
)
print("STDOUT:", result.stdout)
print("STDERR:", result.stderr)
print("Return code:", result.returncode)

print("\nChecking migration history...")
result = subprocess.run(
    [sys.executable, "-m", "alembic", "-c", "backend/alembic.ini", "history"],
    cwd=repo_root,
    capture_output=True,
    text=True
)
print("STDOUT:", result.stdout)
print("STDERR:", result.stderr)
print("Return code:", result.returncode)
