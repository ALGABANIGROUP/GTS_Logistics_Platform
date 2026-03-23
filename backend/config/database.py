import os
from sqlalchemy.pool import QueuePool
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import logging

logger = logging.getLogger(__name__)

# Get database URL from environment
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://user:password@localhost:5432/mydatabase"
)

# Determine if running in development or production
IS_DEVELOPMENT = os.getenv("ENVIRONMENT", "development") == "development"
IS_LOCALHOST = "localhost" in DATABASE_URL or "127.0.0.1" in DATABASE_URL

# Fix SSL handling for local development
def get_async_database_url():
    """Get async database URL with proper SSL handling"""
    
    # Convert to asyncpg
    async_url = DATABASE_URL.replace(
        "postgresql://",
        "postgresql+asyncpg://"
    )
    
    # For local development, disable SSL requirement
    if IS_LOCALHOST and IS_DEVELOPMENT:
        # Remove SSL requirements for localhost
        async_url = async_url.replace("?ssl=require", "")
        async_url = async_url.replace("?sslmode=require", "")
        logger.info("✅ Local development: SSL disabled for localhost")
    else:
        # For production, require SSL
        if "?" not in async_url:
            async_url += "?ssl=require"
        logger.info("✅ Production: SSL required")
    
    return async_url

ASYNC_DATABASE_URL = get_async_database_url()

# Create async engine with optimized pool
engine = create_async_engine(
    ASYNC_DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False,
    connect_args={
        "server_settings": {
            "jit": "off"  # Disable JIT for compatibility
        }
    } if not IS_LOCALHOST else {}
)

# Create async session factory
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

async def get_db_session():
    """Get database session - dependency for FastAPI"""
    async with AsyncSessionLocal() as session:
        yield session

logger.info(f"🔐 Database configured: {ASYNC_DATABASE_URL[:50]}...")