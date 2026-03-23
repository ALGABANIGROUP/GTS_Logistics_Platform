#!/usr/bin/env python
"""
Direct migration runner that bypasses Alembic's sync DB URL issues
"""
import os
import sys
import asyncio
from pathlib import Path

# Setup paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Load environment
from dotenv import load_dotenv
load_dotenv(project_root / ".env")

# Get async database URL
async_db_url = os.getenv("ASYNC_DATABASE_URL")
if not async_db_url:
    print("ERROR: ASYNC_DATABASE_URL not set in .env")
    sys.exit(1)

print(f"[migration] Using database URL...")

# Convert async URL to sync for psycopg2
sync_db_url = async_db_url.replace("postgresql+asyncpg://", "postgresql://")
sync_db_url = sync_db_url.replace("asyncpg://", "postgresql://")

print(f"[migration] Sync DB URL prepared")

# Setup sqlalchemy for migration
os.environ["SQLALCHEMY_DATABASE_URL"] = sync_db_url

# Now run Alembic
from alembic import main as alembic_main

alembic_dir = project_root / "backend" / "alembic_migrations"
sys.argv = ["alembic", "-c", str(alembic_dir.parent / "alembic.ini"), "upgrade", "head"]

try:
    alembic_main.main()
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)
