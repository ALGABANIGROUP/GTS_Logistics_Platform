# backend/tests/conftest.py
import asyncio
import sys
import pytest
try:
    from httpx import AsyncClient, ASGITransport
except ImportError:
    # For newer httpx versions
    from httpx import AsyncClient
    from httpx._transports.asgi import ASGITransport

# Import models in correct order to avoid relationship resolution issues
from backend.models import Tenant, User, Document, PasswordResetToken

from backend.main import app
from backend.database.session import async_session, wrap_session_factory


@pytest.fixture(scope="session", autouse=True)
def _windows_event_loop_policy():
    if sys.platform.startswith("win"):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


@pytest.fixture
async def async_client():
    """
    Async HTTP client for testing the FastAPI app.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
async def db_session():
    """
    Database session fixture for tests.
    Uses a transaction that gets rolled back automatically.
    """
    from backend.database.config import _get_async_dsn, _sanitize_async_url
    from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
    from sqlalchemy.pool import NullPool
    import os
    
    # Create test-specific engine with NullPool to avoid connection pooling issues
    dsn = _get_async_dsn()
    if not dsn:
        pytest.skip("No database DSN configured")
    
    test_engine = create_async_engine(
        dsn,
        echo=False,
        future=True,
        poolclass=NullPool,  # Use NullPool to avoid connection pooling and cleanup issues
    )
    
    test_maker = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )
    
    session = test_maker()
    
    # Start a nested transaction for test isolation
    async with session.begin_nested():
        yield session
        # Explicit rollback of nested transaction
        try:
            await session.rollback()
        except Exception:
            pass  # Ignore rollback errors during teardown
    
    # Close the session - with NullPool this is simpler
    try:
        await session.close()
    except Exception:
        pass  # Ignore close errors during teardown
    
    # Dispose of the test engine - NullPool makes this safer
    try:
        await test_engine.dispose()
    except Exception:
        pass  # Ignore dispose errors during teardown
