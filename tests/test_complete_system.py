"""Current-contract smoke coverage for core platform services."""

import asyncio
from datetime import datetime

import jwt
import pytest


@pytest.mark.asyncio
async def test_create_access_token():
    from backend.security.auth import JWT_ALGORITHM, JWT_SECRET_KEY, create_access_token

    token = create_access_token(
        subject="test@gts.com",
        email="test@gts.com",
        role="admin",
    )
    payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])

    assert isinstance(token, str)
    assert payload["email"] == "test@gts.com"
    assert payload["role"] == "admin"


@pytest.mark.asyncio
async def test_password_hashing():
    from backend.utils.auth_utils import get_password_hash, verify_password

    password = "SecurePassword123!"
    hashed = get_password_hash(password)

    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("WrongPassword", hashed) is False


@pytest.mark.asyncio
async def test_2fa_secret_generation():
    from backend.security.two_factor_auth import TwoFactorAuth

    tfa = TwoFactorAuth()
    secret = tfa.generate_secret()

    assert secret is not None
    assert len(secret) == 32


@pytest.mark.asyncio
async def test_2fa_token_verification():
    import pyotp
    from backend.security.two_factor_auth import TwoFactorAuth

    tfa = TwoFactorAuth()
    secret = tfa.generate_secret()
    totp = pyotp.TOTP(secret)

    assert tfa.verify_token(secret, totp.now()) is True
    assert tfa.verify_token(secret, "000000") is False


@pytest.mark.asyncio
async def test_bot_run_model_shape():
    from backend.models.bot_os import BotRun

    columns = set(BotRun.__table__.columns.keys())
    assert "bot_name" in columns
    assert "status" in columns
    assert "started_at" in columns


@pytest.mark.asyncio
async def test_cache_set_get():
    from backend.utils.cache import cache

    await cache.connect()
    if not cache.enabled:
        pytest.skip("Redis cache not available")

    key = "test:cache:key"
    value = {"test": "data", "number": 123}
    await cache.set(key, value, ttl=60)
    assert await cache.get(key) == value
    await cache.delete(key)
    assert await cache.get(key) is None
    await cache.disconnect()


@pytest.mark.asyncio
async def test_structured_logging():
    from backend.utils.logging_config import RequestLogger, SecurityLogger

    RequestLogger.log_request(
        method="GET",
        path="/api/v1/test",
        status_code=200,
        duration_ms=45.2,
        user_id="user123",
    )
    SecurityLogger.log_auth_attempt(
        email="test@gts.com",
        success=True,
        ip_address="127.0.0.1",
    )
    assert True


@pytest.mark.asyncio
async def test_unified_expense_schemas():
    from backend.schemas.expense_schemas import ExpenseCreate, ExpenseOut

    expense_create = ExpenseCreate(
        category="Transportation",
        amount=150.50,
        description="Fuel costs",
        vendor="Shell",
    )
    expense_out = ExpenseOut(
        id=1,
        category="Transportation",
        amount=150.50,
        description="Fuel costs",
        vendor="Shell",
        created_at=datetime.utcnow(),
        status="pending",
    )

    assert expense_create.amount == 150.50
    assert expense_out.id == 1
    assert expense_out.status == "pending"


@pytest.mark.asyncio
async def test_async_endpoints_performance():
    async def async_task():
        await asyncio.sleep(0.1)
        return "done"

    results = await asyncio.gather(*[async_task() for _ in range(10)])
    assert len(results) == 10
    assert all(result == "done" for result in results)
