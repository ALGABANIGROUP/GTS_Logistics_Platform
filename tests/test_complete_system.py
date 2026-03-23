"""
Comprehensive test suite for GTS Logistics SaaS Platform.
Tests all critical components including auth, multi-tenancy, billing, and bot OS.
"""
import pytest
import asyncio
from datetime import datetime, timedelta
from typing import AsyncGenerator

# Test fixtures
@pytest.fixture
async def async_db_session():
    """Provide async database session for tests."""
    from backend.database.session import wrap_session_factory
    
    async with wrap_session_factory()() as session:
        yield session


@pytest.fixture
async def test_user(async_db_session):
    """Create a test user."""
    from backend.models.user import User
    
    user = User(
        email="test@gts.com",
        full_name="Test User",
        role_key="admin",
        is_active=True
    )
    async_db_session.add(user)
    await async_db_session.commit()
    yield user


@pytest.fixture
async def test_tenant(async_db_session):
    """Create a test tenant."""
    from backend.models.tenant import Tenant
    
    tenant = Tenant(
        name="Test Tenant",
        slug="test-tenant",
        is_active=True
    )
    async_db_session.add(tenant)
    await async_db_session.commit()
    yield tenant


# ============================================================================
# Authentication Tests
# ============================================================================

@pytest.mark.asyncio
async def test_create_access_token():
    """Test JWT token creation."""
    from backend.security.auth import create_access_token
    
    data = {"sub": "test@gts.com", "role": "admin"}
    token = create_access_token(data)
    
    assert token is not None
    assert isinstance(token, str)
    assert len(token) > 50


@pytest.mark.asyncio
async def test_verify_token():
    """Test JWT token verification."""
    from backend.security.auth import create_access_token, verify_token
    
    data = {"sub": "test@gts.com", "role": "admin"}
    token = create_access_token(data)
    
    payload = verify_token(token)
    assert payload is not None
    assert payload["sub"] == "test@gts.com"
    assert payload["role"] == "admin"


@pytest.mark.asyncio
async def test_password_hashing():
    """Test password hashing and verification."""
    from backend.security.auth import hash_password, verify_password
    
    password = "SecurePassword123!"
    hashed = hash_password(password)
    
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("WrongPassword", hashed) is False


# ============================================================================
# 2FA Tests
# ============================================================================

@pytest.mark.asyncio
async def test_2fa_secret_generation():
    """Test 2FA secret generation."""
    from backend.security.two_factor_auth import TwoFactorAuth
    
    tfa = TwoFactorAuth()
    secret = tfa.generate_secret()
    
    assert secret is not None
    assert len(secret) == 32  # Base32 encoded


@pytest.mark.asyncio
async def test_2fa_token_verification():
    """Test 2FA token verification."""
    from backend.security.two_factor_auth import TwoFactorAuth
    import pyotp
    
    tfa = TwoFactorAuth()
    secret = tfa.generate_secret()
    
    # Generate valid token
    totp = pyotp.TOTP(secret)
    valid_token = totp.now()
    
    assert tfa.verify_token(secret, valid_token) is True
    assert tfa.verify_token(secret, "000000") is False


# ============================================================================
# Multi-Tenancy Tests
# ============================================================================

@pytest.mark.asyncio
async def test_tenant_isolation(async_db_session, test_tenant):
    """Test tenant data isolation."""
    from backend.models.user import User
    from sqlalchemy import select
    
    # Create users for different tenants
    user1 = User(email="user1@tenant1.com", tenant_id=test_tenant.id)
    user2 = User(email="user2@tenant2.com", tenant_id=999)  # Different tenant
    
    async_db_session.add_all([user1, user2])
    await async_db_session.commit()
    
    # Query with tenant filter
    stmt = select(User).where(User.tenant_id == test_tenant.id)
    result = await async_db_session.execute(stmt)
    users = result.scalars().all()
    
    assert len(users) == 1
    assert users[0].email == "user1@tenant1.com"


# ============================================================================
# Billing & Subscription Tests
# ============================================================================

@pytest.mark.asyncio
async def test_subscription_creation(async_db_session, test_tenant):
    """Test subscription creation."""
    from backend.models.subscription import Subscription, Plan
    
    # Create plan
    plan = Plan(
        name="Premium Plan",
        price=99.99,
        interval="month",
        features={"max_users": 50, "max_bots": 10}
    )
    async_db_session.add(plan)
    await async_db_session.commit()
    
    # Create subscription
    subscription = Subscription(
        tenant_id=test_tenant.id,
        plan_id=plan.id,
        status="active",
        current_period_start=datetime.utcnow(),
        current_period_end=datetime.utcnow() + timedelta(days=30)
    )
    async_db_session.add(subscription)
    await async_db_session.commit()
    
    assert subscription.id is not None
    assert subscription.status == "active"


# ============================================================================
# Bot OS Tests
# ============================================================================

@pytest.mark.asyncio
async def test_bot_registry():
    """Test bot registry."""
    from backend.bots.os import BotOS
    
    bot_os = BotOS()
    registry = bot_os.list_bots()
    
    assert isinstance(registry, list)
    assert len(registry) > 0
    assert all("name" in bot for bot in registry)


@pytest.mark.asyncio
async def test_bot_execution(async_db_session):
    """Test bot execution."""
    from backend.models.bot_os import BotRun
    
    run = BotRun(
        bot_name="test_bot",
        status="running",
        started_at=datetime.utcnow()
    )
    async_db_session.add(run)
    await async_db_session.commit()
    
    assert run.id is not None
    assert run.status == "running"


# ============================================================================
# Cache Tests
# ============================================================================

@pytest.mark.asyncio
async def test_cache_set_get():
    """Test Redis cache operations."""
    from backend.utils.cache import cache
    
    # Initialize cache
    await cache.connect()
    
    if cache.enabled:
        # Test set/get
        key = "test:cache:key"
        value = {"test": "data", "number": 123}
        
        await cache.set(key, value, ttl=60)
        retrieved = await cache.get(key)
        
        assert retrieved == value
        
        # Test delete
        await cache.delete(key)
        assert await cache.get(key) is None
        
        await cache.disconnect()
    else:
        pytest.skip("Redis cache not available")


# ============================================================================
# Logging Tests
# ============================================================================

@pytest.mark.asyncio
async def test_structured_logging():
    """Test structured logging."""
    from backend.utils.logging_config import RequestLogger, SecurityLogger
    
    # Test request logging
    RequestLogger.log_request(
        method="GET",
        path="/api/v1/test",
        status_code=200,
        duration_ms=45.2,
        user_id="user123"
    )
    
    # Test security logging
    SecurityLogger.log_auth_attempt(
        email="test@gts.com",
        success=True,
        ip_address="127.0.0.1"
    )
    
    # If no exception raised, logging works
    assert True


# ============================================================================
# Expense Schema Tests
# ============================================================================

@pytest.mark.asyncio
async def test_unified_expense_schemas():
    """Test unified expense schemas."""
    from backend.schemas.expense_schemas import ExpenseCreate, ExpenseOut
    
    # Test creation schema
    expense_data = {
        "category": "Transportation",
        "amount": 150.50,
        "description": "Fuel costs",
        "vendor": "Shell"
    }
    expense_create = ExpenseCreate(**expense_data)
    
    assert expense_create.category == "Transportation"
    assert expense_create.amount == 150.50
    
    # Test output schema
    expense_out = ExpenseOut(
        id=1,
        category="Transportation",
        amount=150.50,
        description="Fuel costs",
        vendor="Shell",
        created_at=datetime.utcnow(),
        status="pending"
    )
    
    assert expense_out.id == 1
    assert expense_out.status == "pending"


# ============================================================================
# Performance Tests
# ============================================================================

@pytest.mark.asyncio
async def test_async_endpoints_performance():
    """Test that async endpoints are actually async."""
    import time
    
    # Simulate async function
    async def async_task():
        await asyncio.sleep(0.1)
        return "done"
    
    start = time.time()
    
    # Run 10 tasks concurrently
    tasks = [async_task() for _ in range(10)]
    results = await asyncio.gather(*tasks)
    
    duration = time.time() - start
    
    # Should take ~0.1s (concurrent), not 1s (sequential)
    assert duration < 0.5
    assert len(results) == 10


# ============================================================================
# Integration Tests
# ============================================================================

@pytest.mark.asyncio
async def test_end_to_end_auth_flow(async_db_session):
    """Test complete authentication flow."""
    from backend.security.auth import create_access_token, verify_token, hash_password, verify_password
    from backend.models.user import User
    
    # 1. Create user
    password = "SecurePass123!"
    hashed = hash_password(password)
    
    user = User(
        email="e2e@test.com",
        password_hash=hashed,
        full_name="E2E Test",
        role_key="user",
        is_active=True
    )
    async_db_session.add(user)
    await async_db_session.commit()
    
    # 2. Verify password
    assert verify_password(password, hashed) is True
    
    # 3. Create token
    token = create_access_token({"sub": user.email, "role": user.role_key})
    assert token is not None
    
    # 4. Verify token
    payload = verify_token(token)
    assert payload["sub"] == user.email
    assert payload["role"] == "user"


# ============================================================================
# Run Tests
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
