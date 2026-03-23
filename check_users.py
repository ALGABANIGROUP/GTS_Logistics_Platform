"""
EN
"""
import sys
import os
import asyncio
from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, func

# Load .env
from dotenv import load_dotenv
load_dotenv()

sys.path.insert(0, os.path.dirname(__file__))

from backend.models.user import User


async def check_users():
    """EN"""
    
    # Use PostgreSQL from env, not SQLite
    database_url = os.getenv("ASYNC_DATABASE_URL")
    
    if not database_url:
        print("❌ ASYNC_DATABASE_URL not set!")
        return
    
    # Remove sslmode parameter as asyncpg handles it differently
    database_url = database_url.replace("?sslmode=require", "")
    
    engine = create_async_engine(
        database_url, 
        echo=False,
        connect_args={"ssl": True}
    )
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # EN
        result = await session.execute(
            select(User).order_by(User.id)
        )
        users = result.scalars().all()
        
        print(f"\n{'='*70}")
        print(f"📊 EN: {len(users)}")
        print(f"{'='*70}\n")
        
        for user in users:
            print(f"ID: {user.id}")
            print(f"  📧 EN: {user.email}")
            print(f"  👤 EN: {user.full_name or 'EN'}")
            print(f"  🔑 EN: {user.role}")
            print(f"  ✅ EN: {'EN' if user.is_active else 'EN'}")
            print(f"  📅 EN: {user.created_at}")
            print(f"  {'-'*60}\n")
        
        # EN
        result = await session.execute(
            select(User.email, func.count(User.id))
            .group_by(User.email)
            .having(func.count(User.id) > 1)
        )
        duplicates = result.all()
        
        if duplicates:
            print(f"⚠️ EN: EN:")
            for email, count in duplicates:
                print(f"  - {email}: {count} EN")
        else:
            print(f"✅ EN")
    
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(check_users())
