"""
EN SQLite EN
"""
import os
import sys
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

# Import all models to ensure they're registered
from backend.models.base import Base
from backend.models.user import User
from backend.models.tenant import Tenant

# Import available models with error handling
try:
    from backend.models import *
except Exception as e:
    print(f"[create_db] Warning importing models: {e}")

try:
    from backend.models.support_ticket import SupportTicket
except:
    pass

try:
    from backend.models.message_log import MessageLog
except:
    pass


async def create_database():
    """EN"""
    
    database_url = "sqlite+aiosqlite:///./gts_database.db"
    
    print(f"[create_db] EN: {database_url}")
    
    # Create engine
    engine = create_async_engine(
        database_url,
        echo=True,
        future=True
    )
    
    # Create all tables
    async with engine.begin() as conn:
        print("[create_db] EN...")
        await conn.run_sync(Base.metadata.drop_all)
        
        print("[create_db] EN...")
        await conn.run_sync(Base.metadata.create_all)
    
    print("[create_db] ✅ EN!")
    
    # Create admin user
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        print("[create_db] EN admin EN...")
        from backend.security.passwords import hash_password
        
        admin_user = User(
            email="admin@gts.com",
            full_name="System Admin",
            username="admin",
            hashed_password=hash_password("admin123"),
            role="super_admin",
            is_active=True,
            user_type="Admin"
        )
        
        session.add(admin_user)
        await session.commit()
        
        print("[create_db] ✅ EN admin (email: admin@gts.com, password: admin123)")
    
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(create_database())
