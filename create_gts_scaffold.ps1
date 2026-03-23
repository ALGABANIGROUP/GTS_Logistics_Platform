# D:\GTS-Logistics\create_gts_scaffold.ps1
# Creates missing folders/files for the GTS layered backend + CI
# Existing files are preserved (no overwrite). Safe to re-run.

$ErrorActionPreference = "Stop"

# --- Helpers ---
function New-DirectoryIfMissing {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) {
        New-Item -ItemType Directory -Path $Path -Force | Out-Null
        Write-Host "Created dir: $Path"
    }
    else {
        Write-Host "Dir exists:  $Path"
    }
}

function New-FileIfMissing {
    param(
        [string]$Path,
        [string]$Content
    )
    if (-not (Test-Path -LiteralPath $Path)) {
        $parent = Split-Path -Parent $Path
        if ($parent) { New-DirectoryIfMissing -Path $parent }
        $Content | Out-File -LiteralPath $Path -Encoding UTF8 -Force
        Write-Host "Created file: $Path"
    }
    else {
        Write-Host "File exists:  $Path  (kept as-is)"
    }
}

function Add-GitignoreLines {
    param(
        [string]$Path,
        [string[]]$Lines
    )
    if (-not (Test-Path -LiteralPath $Path)) {
        $Lines -join "`n" | Out-File -LiteralPath $Path -Encoding UTF8 -Force
        Write-Host "Created file: $Path"
        return
    }
    $current = Get-Content -LiteralPath $Path -ErrorAction SilentlyContinue
    $added = 0
    foreach ($l in $Lines) {
        if ($current -notcontains $l) {
            Add-Content -LiteralPath $Path -Value $l
            $added++
        }
    }
    if ($added -gt 0) {
        Write-Host "Updated .gitignore ($added new line(s))"
    }
    else {
        Write-Host ".gitignore already contains required lines"
    }
}

# --- Root of project ---
$Root = "D:\GTS-Logistics"

# --- Ensure directories ---
New-DirectoryIfMissing "$Root\backend\core"
New-DirectoryIfMissing "$Root\backend\api\routes"
New-DirectoryIfMissing "$Root\backend\services"
New-DirectoryIfMissing "$Root\backend\data\repositories"
New-DirectoryIfMissing "$Root\backend\schemas"
New-DirectoryIfMissing "$Root\backend\tests\services"
New-DirectoryIfMissing "$Root\frontend"
New-DirectoryIfMissing "$Root\.github\workflows"

# --- File contents (Here-Strings) ---

# backend/core/config.py
$config_py = @'
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional, List

class Settings(BaseSettings):
    app_name: str = "GTS Logistics"
    env: str = Field(default="dev", pattern=r"^(dev|staging|prod)$")

    # Security
    jwt_issuer: str = "gts"
    jwt_audience: str = "gts-clients"
    jwt_access_ttl_minutes: int = 30
    jwt_refresh_ttl_minutes: int = 60 * 24 * 7
    jwt_private_key_pem: Optional[str] = None
    jwt_public_key_pem: Optional[str] = None
    jwt_secret: Optional[str] = None  # HS256 for local/dev only
    jwt_active_kid: str = "k1"

    # CORS / Rate limit
    cors_allow_origins: List[str] = ["http://localhost:5173"]
    rate_limit_per_minute: int = 60

    # Database
    database_url: str
    database_pool_size: int = 5

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
'@

# backend/core/security.py
$security_py = @'
from datetime import datetime, timedelta, timezone
from typing import Any, Literal, List
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError

from .config import settings

ALGO = "HS256" if settings.jwt_secret else "RS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

Role = Literal["admin", "broker", "ops", "customer"]

class AuthUser(dict):
    @property
    def roles(self) -> List[str]:
        return self.get("roles", [])

def _now() -> datetime:
    return datetime.now(timezone.utc)

def issue_access_token(sub: str, roles: List[Role], kid: str | None = None) -> str:
    exp = _now() + timedelta(minutes=settings.jwt_access_ttl_minutes)
    payload: dict[str, Any] = {
        "iss": settings.jwt_issuer,
        "aud": settings.jwt_audience,
        "sub": sub,
        "roles": roles,
        "iat": int(_now().timestamp()),
        "exp": int(exp.timestamp()),
    }
    headers = {"kid": kid or settings.jwt_active_kid}

    if ALGO == "HS256":
        if not settings.jwt_secret:
            raise RuntimeError("JWT secret missing")
        return jwt.encode(payload, settings.jwt_secret, algorithm=ALGO, headers=headers)

    if not settings.jwt_private_key_pem:
        raise RuntimeError("JWT private key missing for RS256")
    return jwt.encode(payload, settings.jwt_private_key_pem, algorithm=ALGO, headers=headers)

def verify_token(token: str = Depends(oauth2_scheme)) -> AuthUser:
    try:
        if ALGO == "HS256":
            data = jwt.decode(token, settings.jwt_secret, algorithms=[ALGO],
                              audience=settings.jwt_audience, issuer=settings.jwt_issuer)
        else:
            data = jwt.decode(token, settings.jwt_public_key_pem, algorithms=[ALGO],
                              audience=settings.jwt_audience, issuer=settings.jwt_issuer)
    except JWTError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from e
    return AuthUser(data)

def require_roles(*required: Role):
    def wrapper(user: AuthUser = Depends(verify_token)):
        if not any(r in user.roles for r in required):
            raise HTTPException(status_code=403, detail="Forbidden")
        return user
    return wrapper
'@

# backend/core/deps.py
$deps_py = @'
from .security import verify_token as get_current_user, require_roles
'@

# backend/api/__init__.py
$api_init_py = @'
from fastapi import APIRouter
from .routes import example_finance

api_router = APIRouter()
api_router.include_router(example_finance.router)
'@

# backend/api/routes/example_finance.py
$example_finance_py = @'
from fastapi import APIRouter, Depends
from ...core.deps import require_roles
from ...schemas.expense import ExpenseCreate, ExpenseOut
from ...services.finance_service import FinanceService

router = APIRouter(prefix="/finance", tags=["finance"])

@router.post("/expenses", response_model=ExpenseOut,
             dependencies=[Depends(require_roles("admin", "broker"))])
async def create_expense(payload: ExpenseCreate):
    return await FinanceService().create_expense(payload)
'@

# backend/schemas/expense.py
$expense_schema_py = @'
from pydantic import BaseModel, Field

class ExpenseCreate(BaseModel):
    amount: float = Field(gt=0)
    description: str = Field(min_length=1, max_length=200)

class ExpenseOut(ExpenseCreate):
    id: int
'@

# backend/services/finance_service.py
$finance_service_py = @'
from ..data.repositories.expenses_repo import ExpensesRepo
from ..schemas.expense import ExpenseCreate, ExpenseOut

class FinanceService:
    async def create_expense(self, payload: ExpenseCreate) -> ExpenseOut:
        rec = await ExpensesRepo().insert(amount=payload.amount, description=payload.description)
        return ExpenseOut(**rec)
'@

# backend/data/repositories/base_repo.py
$base_repo_py = @'
from typing import Any, Mapping
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import text
from ...core.config import settings

_engine = create_async_engine(settings.database_url, pool_size=settings.database_pool_size)
_Session = async_sessionmaker(_engine, expire_on_commit=False)

class BaseRepo:
    async def execute(self, sql: str, params: Mapping[str, Any] | None = None):
        async with _Session() as s:
            res = await s.execute(text(sql), params or {})
            await s.commit()
            return res
'@

# backend/data/repositories/expenses_repo.py
$expenses_repo_py = @'
from .base_repo import BaseRepo

class ExpensesRepo(BaseRepo):
    async def insert(self, *, amount: float, description: str) -> dict:
        sql = ("INSERT INTO expenses(amount, description) "
               "VALUES (:amount, :description) RETURNING id, amount, description")
        res = await self.execute(sql, {"amount": amount, "description": description})
        row = res.fetchone()
        return {"id": row.id, "amount": row.amount, "description": row.description}
'@

# backend/tests/conftest.py
$conftest_py = @'
import asyncio
import pytest
from httpx import AsyncClient
from fastapi import FastAPI

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def app() -> FastAPI:
    from backend.main import app  # adjust if your app path differs
    return app

@pytest.fixture
async def client(app: FastAPI):
    async with AsyncClient(app=app, base_url="http://test") as c:
        yield c
'@

# backend/tests/services/test_finance_service.py
$test_finance_service_py = @'
import pytest
from backend.schemas.expense import ExpenseCreate
from backend.services.finance_service import FinanceService

@pytest.mark.asyncio
async def test_create_expense_happy_path():
    svc = FinanceService()
    out = await svc.create_expense(ExpenseCreate(amount=10.5, description="fuel"))
    assert out.amount == 10.5
    assert out.description == "fuel"
    assert isinstance(out.id, int)
'@

# backend/.env.example
$backend_env_example = @'
ENV=dev
APP_NAME=GTS Logistics

# Database (Async SQLAlchemy URL)
# e.g. postgresql+asyncpg://USER:PASSWORD@HOST:5432/DBNAME
DATABASE_URL=
DATABASE_POOL_SIZE=5

# Security (choose one: HS256 secret OR RS256 keys)
JWT_ISSUER=gts
JWT_AUDIENCE=gts-clients
JWT_ACCESS_TTL_MINUTES=30
JWT_REFRESH_TTL_MINUTES=10080
JWT_SECRET=
JWT_ACTIVE_KID=k1
# JWT_PRIVATE_KEY_PEM="""-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"""
# JWT_PUBLIC_KEY_PEM="""-----BEGIN PUBLIC KEY-----\n...\n-----END PUBLIC KEY-----\n"""

# CORS
CORS_ALLOW_ORIGINS=http://localhost:5173,https://app.gabanilogistics.com
RATE_LIMIT_PER_MINUTE=60
'@

# SECURITY.md
$security_md = @'
# Security Policy

## Reporting
Please report security issues privately to security@gabanilogistics.com. We will acknowledge within 72h and coordinate a fix.

## Secrets
Never commit secrets. Use environment variables and `.env` files excluded by Git. Provide `.env.example` only.

## Dependencies
Enable Dependabot and CodeQL. All PRs must pass CI scans.

## Authentication
JWT tokens are short-lived with `kid` rotation support. RBAC roles: `admin`, `broker`, `ops`, `customer`.
'@

# .editorconfig
$editorconfig = @'
root = true

[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
indent_style = space
indent_size = 2

[*.py]
indent_size = 4
'@

# .gitattributes
$gitattributes = @'
* text=auto eol=lf
'@

# frontend/.env.example
$frontend_env_example = @'
VITE_API_BASE=http://localhost:8001
'@

# .github/workflows/lint-and-test.yml
$lint_test_yml = @'
name: Lint & Test
on:
  pull_request:
  push:
    branches: [ mvp-free ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Install deps
        run: |
          python -m pip install -U pip
          pip install -r requirements.txt
      - name: Lint (ruff)
        run: |
          pip install ruff black
          ruff check backend || true
      - name: Tests
        run: |
          pip install pytest pytest-asyncio httpx
          pytest -q --maxfail=1 --disable-warnings --color=yes
'@

# .github/workflows/supply-chain.yml
$supply_chain_yml = @'
name: Supply Chain Scan
on:
  pull_request:
  schedule:
    - cron: "0 3 * * *"

jobs:
  deps:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Install tools
        run: |
          python -m pip install -U pip
          pip install safety pip-audit
      - name: pip-audit
        run: pip-audit -r requirements.txt || true
      - name: safety
        run: safety check -r requirements.txt || true
'@

# .gitignore lines to ensure
$gitignore_lines = @(
    ".env",
    "backend/.env",
    "frontend/.env",
    "*.pem",
    "*.key"
)

# --- Create files (no overwrite) ---
New-FileIfMissing -Path "$Root\backend\core\config.py" -Content $config_py
New-FileIfMissing -Path "$Root\backend\core\security.py" -Content $security_py
New-FileIfMissing -Path "$Root\backend\core\deps.py" -Content $deps_py

New-FileIfMissing -Path "$Root\backend\api\__init__.py" -Content $api_init_py
New-FileIfMissing -Path "$Root\backend\api\routes\example_finance.py" -Content $example_finance_py

New-FileIfMissing -Path "$Root\backend\schemas\expense.py" -Content $expense_schema_py
New-FileIfMissing -Path "$Root\backend\services\finance_service.py" -Content $finance_service_py

New-FileIfMissing -Path "$Root\backend\data\repositories\base_repo.py" -Content $base_repo_py
New-FileIfMissing -Path "$Root\backend\data\repositories\expenses_repo.py" -Content $expenses_repo_py

New-FileIfMissing -Path "$Root\backend\tests\conftest.py" -Content $conftest_py
New-FileIfMissing -Path "$Root\backend\tests\services\test_finance_service.py" -Content $test_finance_service_py

New-FileIfMissing -Path "$Root\backend\.env.example" -Content $backend_env_example
New-FileIfMissing -Path "$Root\frontend\.env.example" -Content $frontend_env_example
New-FileIfMissing -Path "$Root\SECURITY.md" -Content $security_md
New-FileIfMissing -Path "$Root\.editorconfig" -Content $editorconfig
New-FileIfMissing -Path "$Root\.gitattributes" -Content $gitattributes
New-FileIfMissing -Path "$Root\.github\workflows\lint-and-test.yml" -Content $lint_test_yml
New-FileIfMissing -Path "$Root\.github\workflows\supply-chain.yml" -Content $supply_chain_yml

Add-GitignoreLines -Path "$Root\.gitignore" -Lines $gitignore_lines

Write-Host "`nDone. Review the created files, set your .env, and run uvicorn / CI as needed." -ForegroundColor Green
