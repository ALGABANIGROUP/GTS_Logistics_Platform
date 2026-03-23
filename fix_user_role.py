"""
EN super_admin EN
"""
import sys
import os
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

sys.path.insert(0, os.path.dirname(__file__))

from backend.models.user import User


async def update_user_role():
    """EN"""
    
    database_url = "sqlite+aiosqlite:///./gts_database.db"
    
    engine = create_async_engine(database_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # EN
        result = await session.execute(
            select(User).where(User.email == "enjoy983@hotmail.com")
        )
        user = result.scalar_one_or_none()
        
        if user:
            print(f"\n{'='*70}")
            print(f"📋 EN:")
            print(f"{'='*70}")
            print(f"  ID: {user.id}")
            print(f"  EN: {user.email}")
            print(f"  EN: {user.full_name}")
            print(f"  EN: {user.role}")
            print(f"  EN: {user.is_active}")
            print(f"  EN: {user.is_banned}")
            print(f"  token_version: {user.token_version}")
            print(f"{'='*70}\n")
            
            # EN
            user.role = "super_admin"
            user.is_active = True
            user.is_banned = False
            user.token_version += 1  # EN tokens EN
            
            session.add(user)
            await session.commit()
            await session.refresh(user)
            
            print(f"{'='*70}")
            print(f"✅ EN!")
            print(f"{'='*70}")
            print(f"  EN: {user.role}")
            print(f"  token_version EN: {user.token_version}")
            print(f"{'='*70}\n")
            print(f"⚠️ EN: EN")
            print(f"   EN token_version EN tokens EN\n")
        else:
            print(f"❌ EN!")
    
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(update_user_role())
