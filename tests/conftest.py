"""
pytest configuration and fixtures for GTS test suite
"""
import pytest
import asyncio
from typing import AsyncGenerator, Generator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from httpx import AsyncClient
from fastapi.testclient import TestClient

# Import app and database
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.main import app
from backend.database import Base, get_async_db
from backend.security import create_access_token
from backend.models.unified_models import UnifiedUser

# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_gts.db"

# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    future=True,
)

TestAsyncSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.run_until_complete(test_engine.dispose())

    try:
        from backend.database import config as db_config

        app_engine = getattr(db_config, "_async_engine", None)
        if app_engine is not None:
            loop.run_until_complete(app_engine.dispose())
    except Exception:
        pass

    loop.close()


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create test database session"""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with TestAsyncSessionLocal() as session:
        yield session
        await session.rollback()
    
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create test client with database override"""
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_async_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture
async def test_user(db_session: AsyncSession) -> UnifiedUser:
    """Create test user"""
    from backend.auth import get_password_hash
    
    user = UnifiedUser(
        email="test@gts.local",
        full_name="Test User",
        hashed_password=get_password_hash("testpassword"),
        role="user",
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def admin_user(db_session: AsyncSession) -> UnifiedUser:
    """Create admin test user"""
    from backend.auth import get_password_hash
    
    user = UnifiedUser(
        email="admin@gts.local",
        full_name="Admin User",
        hashed_password=get_password_hash("adminpassword"),
        role="super_admin",
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
def user_token(test_user: UnifiedUser) -> str:
    """Generate JWT token for test user"""
    return create_access_token(
        subject=getattr(test_user, "id", 0),
        email=test_user.email,
        role=getattr(test_user, "role", "user"),
    )


@pytest.fixture
def admin_token(admin_user: UnifiedUser) -> str:
    """Generate JWT token for admin user"""
    return create_access_token(
        subject=getattr(admin_user, "id", 0),
        email=admin_user.email,
        role=getattr(admin_user, "role", "super_admin"),
    )


@pytest.fixture
def auth_headers(user_token: str) -> dict:
    """Generate authorization headers for test user"""
    return {"Authorization": f"Bearer {user_token}"}


@pytest.fixture
def admin_headers(admin_token: str) -> dict:
    """Generate authorization headers for admin user"""
    return {"Authorization": f"Bearer {admin_token}"}
