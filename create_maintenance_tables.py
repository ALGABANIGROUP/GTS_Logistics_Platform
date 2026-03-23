#!/usr/bin/env python
"""
Create Maintenance tables directly using SQLAlchemy
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

async def main():
    from sqlalchemy.ext.asyncio import create_async_engine
    from backend.maintenance.models import HealthSnapshot, Incident, RemediationAction, MaintenanceAuditLog, AlertRule
    from backend.database.base import Base

    # Get async database URL
    async_db_url = os.getenv("ASYNC_DATABASE_URL")
    if not async_db_url:
        print("ERROR: ASYNC_DATABASE_URL not set in .env")
        return False

    print(f"[maintenance_setup] Creating async engine...")
    engine = create_async_engine(async_db_url, echo=False)

    try:
        async with engine.begin() as conn:
            print(f"[maintenance_setup] Creating health_snapshots table...")
            await conn.run_sync(HealthSnapshot.__table__.create, checkfirst=True)

            print(f"[maintenance_setup] Creating incidents table...")
            await conn.run_sync(Incident.__table__.create, checkfirst=True)

            print(f"[maintenance_setup] Creating remediation_actions table...")
            await conn.run_sync(RemediationAction.__table__.create, checkfirst=True)

            print(f"[maintenance_setup] Creating maintenance_audit_log table...")
            await conn.run_sync(MaintenanceAuditLog.__table__.create, checkfirst=True)

            print(f"[maintenance_setup] Creating maintenance_alert_rules table...")
            await conn.run_sync(AlertRule.__table__.create, checkfirst=True)

            print(f"[maintenance_setup] ✓ All Maintenance tables created successfully")

        return True
    except Exception as e:
        print(f"ERROR: {e}")
        return False
    finally:
        await engine.dispose()

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)