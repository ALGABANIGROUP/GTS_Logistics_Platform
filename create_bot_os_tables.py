#!/usr/bin/env python
"""
Create BOS tables directly using SQLAlchemy
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
    from backend.models.bot_os import BotRegistry, BotRun, HumanCommand
    from backend.models.base import Base
    
    # Get async database URL
    async_db_url = os.getenv("ASYNC_DATABASE_URL")
    if not async_db_url:
        print("ERROR: ASYNC_DATABASE_URL not set in .env")
        return False
    
    print(f"[bot_os_setup] Creating async engine...")
    engine = create_async_engine(async_db_url, echo=False)
    
    try:
        async with engine.begin() as conn:
            print(f"[bot_os_setup] Creating bot_registry table...")
            await conn.run_sync(BotRegistry.__table__.create, checkfirst=True)
            
            print(f"[bot_os_setup] Creating bot_runs table...")
            await conn.run_sync(BotRun.__table__.create, checkfirst=True)
            
            print(f"[bot_os_setup] Creating human_commands table...")
            await conn.run_sync(HumanCommand.__table__.create, checkfirst=True)
            
            print(f"[bot_os_setup] ✓ All BOS tables created successfully")
        
        return True
    except Exception as e:
        print(f"ERROR: {e}")
        return False
    finally:
        await engine.dispose()

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)
