#!/usr/bin/env python
"""Clean up old social media links from database"""

import asyncio
import os
from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Load environment variables from .env
load_dotenv()

async def cleanup():
    db_url = os.getenv('ASYNC_DATABASE_URL')
    if not db_url:
        # Try alternative env var names
        db_url = os.getenv('DATABASE_URL')
    
    if not db_url:
        print("ERROR: Database URL not found in environment variables")
        return
    
    print(f"Connecting to database...")
    engine = create_async_engine(db_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    try:
        async with async_session() as session:
            # Delete all social links
            result = await session.execute(text("DELETE FROM tenant_social_links"))
            await session.commit()
            print(f"✓ Deleted {result.rowcount} old social links from database")
    except Exception as e:
        print(f"ERROR: {str(e)}")
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(cleanup())
