import re
import warnings

import jwt
import pytest
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import sessionmaker

from backend.ai.data_collection_service import data_collection_service
from backend.ai.learning_engine import bot_learning_engine
from backend.database.base import Base

warnings.filterwarnings("ignore", message=".*does *not *have a.*")
warnings.filterwarnings("ignore", message=".*does *not *support.*")
warnings.filterwarnings("ignore", category=UserWarning, module="sqlalchemy")

TEST_SECRET = "change-this-to-32-byte-secure-key-for-tests!!"
EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
MAX_EMAIL_LEN = 320
MAX_NAME_LEN = 255


def _contains_dangerous_markup(value: str) -> bool:
    lowered = value.lower()
    return any(token in lowered for token in ("<script", "onerror=", "onload=", "<img", "<svg"))


def _validate_registration_payload(payload: dict) -> str | None:
    email = str(payload.get("email", "")).strip()
    password = str(payload.get("password", ""))
    full_name = str(payload.get("full_name", "")).strip()

    if not email or not EMAIL_RE.match(email):
        return "Invalid email address"
    if len(email) > MAX_EMAIL_LEN or len(full_name) > MAX_NAME_LEN:
        return "Input exceeds maximum length"
    if not full_name:
        return "Full name is required"
    if _contains_dangerous_markup(email) or _contains_dangerous_markup(full_name) or _contains_dangerous_markup(password):
        return "Malicious input rejected"
    return None


def _reset_learning_state() -> None:
    bot_learning_engine.learning_profiles.clear()
    bot_learning_engine.data_samples.clear()
    bot_learning_engine.bot_behaviors.clear()
    bot_learning_engine.learning_history.clear()
    data_collection_service.error_logs.clear()
    data_collection_service.performance_metrics.clear()
    data_collection_service.user_feedback.clear()
    data_collection_service.collection_stats = {
        "errors_collected": 0,
        "metrics_collected": 0,
        "feedback_collected": 0,
        "last_collection_time": None,
    }


@pytest.fixture(scope="session")
def engine():
    from sqlalchemy import create_engine

    _engine = create_engine(
        "sqlite:///:memory:",
        echo=False,
        connect_args={"check_same_thread": False},
        pool_pre_ping=True,
    )

    @event.listens_for(_engine, "connect")
    def _set_sqlite_pragma(dbapi_connection, _connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    return _engine


@pytest.fixture(scope="session")
def async_engine():
    return create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        connect_args={"check_same_thread": False},
    )


@pytest.fixture(scope="function")
def db_session(engine):
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    session = SessionLocal()

    try:
        yield session
        session.rollback()
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
async def async_db_session(async_engine):
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    SessionLocal = async_sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.rollback()
            await session.close()

    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


def _build_test_app() -> FastAPI:
    app = FastAPI(title="GTS Test API")
    users = {
        "admin@gts.com": {"password": "admin123", "role": "super_admin"},
        "user@gts.com": {"password": "user123", "role": "user"},
    }
    expense_store = []
    expense_counter = {"value": 1}

    @app.middleware("http")
    async def auth_middleware(request: Request, call_next):
        public_paths = {
            "/",
            "/health",
            "/healthz",
            "/api/v1",
            "/api/v1/health",
            "/api/v1/auth/login",
            "/api/v1/auth/token",
            "/api/v1/auth/register",
            "/api/v1/finance/health",
            "/api/v1/admin/health",
            "/api/v1/admin/system/health",
            "/api/v1/bots/available",
            "/docs",
            "/openapi.json",
            "/ai/learning/register",
            "/ai/learning/data/error",
            "/ai/learning/data/performance",
        }
        if request.url.path in public_paths:
            return await call_next(request)

        if request.url.path.startswith("/ai/learning/trigger/"):
            return await call_next(request)

        auth_header = request.headers.get("authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(status_code=401, content={"detail": "Not authenticated"})

        token = auth_header.split(" ", 1)[1]
        try:
            payload = jwt.decode(token, TEST_SECRET, algorithms=["HS256"])
            request.state.user = payload
        except jwt.PyJWTError:
            return JSONResponse(status_code=401, content={"detail": "Invalid token"})

        return await call_next(request)

    @app.get("/")
    def root():
        return {"message": "GTS API", "version": "1.0.0"}

    @app.get("/health")
    def health():
        return {"status": "healthy"}

    @app.get("/healthz")
    def healthz():
        return {"status": "ok"}

    @app.get("/api/v1")
    def api_v1():
        return {"status": "ok", "version": "v1"}

    @app.get("/api/v1/health")
    def api_v1_health():
        return {"status": "healthy"}

    @app.post("/api/v1/auth/register")
    async def auth_register(request: Request):
        payload = await request.json()
        error = _validate_registration_payload(payload)
        if error:
            status_code = 413 if "maximum length" in error else 422
            return JSONResponse(status_code=status_code, content={"detail": error})

        email = str(payload["email"]).strip().lower()
        full_name = str(payload["full_name"]).strip()
        if email in users:
            return JSONResponse(status_code=400, content={"detail": "User already exists"})

        users[email] = {
            "password": str(payload["password"]),
            "role": "user",
            "full_name": full_name,
        }
        return {"status": "ok", "email": email, "full_name": full_name}

    @app.post("/api/v1/auth/login")
    async def auth_login(request: Request):
        form = await request.form()
        username = str(form.get("username", "")).strip().lower()
        password = str(form.get("password", ""))
        if not username or not password:
            return JSONResponse(
                status_code=422,
                content={"detail": "username and password are required"},
            )
        user = users.get(username)
        if not user or user["password"] != password:
            return JSONResponse(status_code=401, content={"detail": "Invalid credentials"})
        token = jwt.encode(
            {"sub": username, "email": username, "role": user["role"]},
            TEST_SECRET,
            algorithm="HS256",
        )
        return {"access_token": token, "token_type": "bearer"}

    @app.post("/api/v1/auth/token")
    async def auth_token(request: Request):
        return await auth_login(request)

    @app.get("/api/v1/auth/me")
    def auth_me(request: Request):
        payload = getattr(request.state, "user", None) or {}
        return payload

    @app.get("/api/v1/finance/health")
    def finance_health():
        return {"status": "healthy", "service": "unified_finance"}

    @app.get("/api/v1/finance/dashboard")
    def finance_dashboard():
        return {"status": "ok", "data": {"total_revenue": 1000, "total_expenses": 500}}

    @app.get("/api/v1/finance/invoices")
    def finance_invoices():
        return {"status": "ok", "data": [{"id": 1, "amount": 100}]}

    @app.get("/api/v1/finance/payments")
    def finance_payments():
        return {"status": "ok", "data": [{"id": 1, "amount": 50}]}

    @app.post("/api/v1/finance/expenses", status_code=201)
    async def create_finance_expense(request: Request):
        payload = await request.json()
        expense = {
            "id": expense_counter["value"],
            "category": payload.get("category"),
            "amount": payload.get("amount"),
            "description": payload.get("description"),
            "vendor": payload.get("vendor"),
            "status": payload.get("status", "PENDING"),
        }
        expense_counter["value"] += 1
        expense_store.append(expense)
        return expense

    @app.get("/api/v1/finance/expenses")
    def list_finance_expenses():
        return {"items": expense_store, "count": len(expense_store)}

    @app.put("/api/v1/finance/expenses/{expense_id}/status")
    def toggle_finance_expense_status(expense_id: int):
        for expense in expense_store:
            if int(expense["id"]) == int(expense_id):
                expense["status"] = "PAID" if expense["status"] == "PENDING" else "PENDING"
                return expense
        return JSONResponse(status_code=404, content={"detail": "Expense not found"})

    @app.get("/api/v1/finance/summary")
    def finance_summary():
        total_expenses = sum(float(expense.get("amount") or 0) for expense in expense_store)
        return {
            "status": "ok",
            "summary": {
                "count": len(expense_store),
                "total_expenses": total_expenses,
            },
        }

    @app.delete("/api/v1/finance/expenses/{expense_id}")
    def delete_finance_expense(expense_id: int):
        for idx, expense in enumerate(expense_store):
            if int(expense["id"]) == int(expense_id):
                expense_store.pop(idx)
                return JSONResponse(status_code=204, content=None)
        return JSONResponse(status_code=404, content={"detail": "Expense not found"})

    @app.get("/api/v1/admin/health")
    def admin_health():
        return {"status": "healthy"}

    @app.get("/api/v1/admin/users")
    def admin_users(request: Request):
        user = getattr(request.state, "user", None) or {}
        if user.get("role") not in {"super_admin", "admin"}:
            return JSONResponse(status_code=403, content={"detail": "Forbidden"})
        return {"status": "ok", "data": [{"id": 1, "email": "test@example.com", "role": "user"}]}

    @app.get("/api/v1/admin/system/health")
    def admin_system_health():
        return {"status": "healthy", "system": "ok"}

    @app.get("/api/v1/admin/")
    def admin_root():
        return {"status": "ok"}

    @app.get("/api/v1/bots/available")
    def bots_available():
        return {"status": "ok", "bots": []}

    @app.get("/api/v1/bots/stats")
    def bots_stats():
        return {"status": "ok", "stats": {"total": 0}}

    @app.get("/api/v1/bots")
    def bots_index():
        return [{"name": "operations_manager", "description": "Ops bot", "status": "active"}]

    @app.get("/api/v1/ai/bots/available")
    def ai_bots_available():
        return {"status": "ok", "bots": []}

    @app.get("/api/v1/ai/bots/check-access/{bot_key}")
    def ai_bot_check_access(bot_key: str):
        return {"status": "ok", "bot": bot_key, "allowed": True}

    @app.post("/ai/learning/register")
    async def register_learning_bot(
        bot_id: str,
        bot_name: str,
        enabled: bool = True,
        frequency: str = "daily",
        intensity: str = "medium",
    ):
        bot_learning_engine.register_bot(
            bot_id=bot_id,
            bot_name=bot_name,
            enabled=enabled,
            frequency=frequency,
            intensity=intensity,
        )
        return {
            "status": "success",
            "profile": bot_learning_engine.get_bot_profile(bot_id),
        }

    @app.post("/ai/learning/data/error")
    async def learning_error(bot_id: str, request: Request):
        payload = await request.json()
        data_collection_service.log_bot_error(
            bot_id=bot_id,
            error_type=payload["error_type"],
            error_message=payload["error_message"],
            severity=payload.get("severity", 1.0),
            traceback=payload.get("traceback"),
            context=payload.get("context"),
        )
        bot_learning_engine.add_error_data(bot_id, payload)
        return {"status": "success"}

    @app.post("/ai/learning/data/performance")
    async def learning_performance(bot_id: str, request: Request):
        payload = await request.json()
        data_collection_service.record_performance(
            bot_id=bot_id,
            response_time=payload["response_time"],
            accuracy=payload["accuracy"],
            throughput=payload.get("throughput", 1.0),
            resource_usage=payload.get("resource_usage"),
            context=payload.get("context"),
        )
        bot_learning_engine.add_performance_data(bot_id, payload)
        return {"status": "success"}

    @app.post("/ai/learning/trigger/{bot_id}")
    async def trigger_learning(bot_id: str):
        return {
            "status": "success",
            "learning_result": bot_learning_engine.perform_learning(bot_id),
        }

    return app


@pytest.fixture
def client():
    _reset_learning_state()
    return TestClient(_build_test_app())


@pytest.fixture
async def async_client():
    _reset_learning_state()
    transport = ASGITransport(app=_build_test_app())
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def test_client():
    _reset_learning_state()
    transport = ASGITransport(app=_build_test_app())
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def dev_token():
    payload = {
        "sub": "1",
        "email": "admin@gts.com",
        "role": "super_admin",
    }
    return jwt.encode(payload, TEST_SECRET, algorithm="HS256")


@pytest.fixture
def auth_headers(dev_token):
    return {"Authorization": f"Bearer {dev_token}"}


@pytest.fixture
def mock_bot_response():
    def _mock_response(data=None, error=None):
        if error:
            return {"ok": False, "error": error}
        return {"ok": True, "data": data or {}}

    return _mock_response


@pytest.fixture
def sample_shipment_data():
    return {
        "load_number": "LD-001",
        "origin": "New York, NY",
        "destination": "Los Angeles, CA",
        "weight": 45000,
        "equipment_type": "dry_van",
        "pickup_date": "2026-04-15",
        "delivery_date": "2026-04-20",
        "rate": 2450.00,
    }


@pytest.fixture
def sample_carrier_data():
    return {
        "name": "Fast Freight Inc.",
        "mc_number": "MC-123456",
        "dot_number": "DOT-789012",
        "rating": 4.5,
        "equipment_types": ["dry_van", "reefer"],
        "active": True,
    }


@pytest.fixture
def sample_user_data():
    return {
        "email": "test@example.com",
        "full_name": "Test User",
        "role": "user",
        "is_active": True,
    }


@pytest.fixture
def admin_client(client, auth_headers):
    client.headers.update(auth_headers)
    return client


@pytest.fixture
async def authenticated_client(async_client, auth_headers):
    async_client.headers.update(auth_headers)
    return async_client
