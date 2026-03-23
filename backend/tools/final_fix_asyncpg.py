# backend/tools/final_fix_asyncpg.py
import os
import re
from pathlib import Path

def fix_all_files_for_asyncpg():
    """Fix all files to use asyncpg only"""
    backend_path = Path(__file__).parent.parent

    print("🔧 Final fix to use asyncpg only...")

    # 1. Fix config.py

    config_content = '''import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

# PostgreSQL database connection - Render.com with asyncpg only
DATABASE_URL = "postgresql+asyncpg://gabani_transport_solutions_user:__SET_IN_SECRET_MANAGER__@dpg-cuicq2qj1k6c73asm5c0-a.oregon-postgres.render.com:5432/gabani_transport_solutions?sslmode=require"
ASYNC_DATABASE_URL = DATABASE_URL

print(f"[db] DSN -> {DATABASE_URL.replace('__SET_IN_SECRET_MANAGER__', '****')}")

# Create async database engine only
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=True,
    future=True,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10
)

print("[db] Using asyncpg with SSL")

# Create async session only
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=True,
    autocommit=False
)

Base = declarative_base()

async def get_db():
    """Get async database session for FastAPI"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
       

async def test_connection():
    """Test database connection"""
    try:
        async with async_engine.connect() as conn:
            result = await conn.execute("SELECT version()")
            version = await result.scalar()
            print(f"✅ Database connection successful: {version}")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

async def database_health():
    """Database health check"""
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute("SELECT 1")
            test_value = await result.scalar()
            return {"status": "healthy", "test_value": test_value}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
'''

    config_path = backend_path / "database" / "config.py"
    with open(config_path, 'w', encoding='utf-8') as f:
        f.write(config_content)
    print("✅ Updated config.py to use asyncpg only")

    # 2. Fix session.py
    session_content = '''from .config import AsyncSessionLocal, async_engine

async def get_db():
    """Get async database session - main dependency for FastAPI"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        

# Export for backward compatibility
get_async_session = get_db
'''

    session_path = backend_path / "database" / "session.py"
    with open(session_path, 'w', encoding='utf-8') as f:
        f.write(session_content)
    print("✅ Updated session.py")

    # 3. Fix all other files to remove psycopg2
    files_to_fix = [
        backend_path / "main.py",
        backend_path / "routes" / "finance_routes.py",
        backend_path / "routes" / "documents_routes.py",
        backend_path / "routes" / "finance_reports.py",
        backend_path / "routes" / "finance_ai_routes.py",
    ]

    for file_path in files_to_fix:
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Remove any reference to psycopg2
                content = content.replace('psycopg2', 'asyncpg')
                content = content.replace('psycopg', 'asyncpg')
                content = re.sub(r'create_engine\([^)]+\)', 'create_async_engine', content)

                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)

                print(f"✅ Fixed: {file_path.name}")

            except Exception as e:
                print(f"⚠️ Could not fix {file_path.name}: {e}")

    print("🎉 Final fix complete! The system now uses asyncpg only.")

if __name__ == "__main__":
    fix_all_files_for_asyncpg()
