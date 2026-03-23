"""
EN token_version EN
"""
import sys
import os
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, text

sys.path.insert(0, os.path.dirname(__file__))

from backend.models.user import User


async def force_logout():
    """EN token_version EN"""
    
    database_url = "sqlite+aiosqlite:///./gts_database.db"
    
    engine = create_async_engine(database_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # EN
        result = await session.execute(text("SELECT id, email, role, token_version, is_active FROM users"))
        users = result.fetchall()
        
        print(f"\n{'='*70}")
        print(f"👥 EN:")
        print(f"{'='*70}")
        for u in users:
            print(f"  ID: {u[0]} | Email: {u[1]} | Role: {u[2]} | Token V: {u[3]} | Active: {u[4]}")
        print(f"{'='*70}\n")
        
        # EN
        result = await session.execute(
            select(User).where(User.email == "enjoy983@hotmail.com")
        )
        user = result.scalar_one_or_none()
        
        if user:
            print(f"📋 EN:")
            print(f"  ID: {user.id}")
            print(f"  EN: {user.email}")
            print(f"  EN: {user.full_name}")
            print(f"  EN: {user.role}")
            print(f"  EN: {user.is_active}")
            print(f"  token_version: {user.token_version}\n")
            
            # EN token_version EN
            old_version = user.token_version
            user.token_version = 999  # EN tokens
            user.role = "super_admin"
            user.is_active = True
            user.is_banned = False
            
            session.add(user)
            await session.commit()
            await session.refresh(user)
            
            print(f"{'='*70}")
            print(f"✅ EN token_version EN!")
            print(f"{'='*70}")
            print(f"  token_version EN: {old_version}")
            print(f"  token_version EN: {user.token_version}")
            print(f"  EN: {user.role}")
            print(f"{'='*70}\n")
            
            print(f"⚠️⚠️⚠️ EN ⚠️⚠️⚠️")
            print(f"{'='*70}")
            print(f"1. EN 'Sign Out' EN")
            print(f"2. EN (F12)")
            print(f"3. EN: Application → Local Storage → http://localhost:5173")
            print(f"4. EN 'token' EN 'Clear All'")
            print(f"5. EN (Ctrl+Shift+R)")
            print(f"6. EN: enjoy983@hotmail.com / password123")
            print(f"{'='*70}\n")
            
            print(f"⚠️ EN: JWT Token EN")
            print(f"   token_version EN ({old_version}) EN!")
            print(f"   EN Token EN token EN\n")
        else:
            print(f"❌ EN!")
    
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(force_logout())
