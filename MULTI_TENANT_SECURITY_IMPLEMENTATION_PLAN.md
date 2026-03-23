# Multi-Tenant Security Implementation Plan
**Status: IN PROGRESS** | **Date: January 8, 2026**

## 🎯 Goal
Implement secure multi-tenant system with:
- ✅ Subscription plans (FREE_TRIAL default)
- ✅ Quotas/Limits to prevent abuse
- ⚠️ Fail Closed (reject any request without clear tenant)
- ⚠️ Protected public signup (email verification + rate limiting)
- ⚠️ Smoke tests for data isolation

---

## ✅ Completed

### 1. Tenant Model - Subscription Fields
**File:** `backend/models/tenant.py`

```python
class TenantPlan(str, enum.Enum):
    FREE_TRIAL = "free_trial"  # Default for new tenants
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"

class TenantStatus(str, enum.Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    TRIAL_EXPIRED = "trial_expired"
    PENDING_VERIFICATION = "pending_verification"  # Before email verified

class BillingStatus(str, enum.Enum):
    NOT_REQUIRED = "not_required"  # For FREE_TRIAL
    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELLED = "cancelled"
```

**New Fields Added:**
- `plan`: Enum (default: FREE_TRIAL)
- `trial_ends_at`: Optional datetime
- `billing_status`: Enum (default: NOT_REQUIRED)
- `status`: Enum (default: ACTIVE)
- `owner_email`: String (unique)
- `owner_user_id`: Integer (FK to users.id)
- `quotas`: JSON (flexible quota storage)
- `settings_json`: JSON (tenant settings)
- `email_verified_at`: Optional datetime

### 2. Migration Generated
**File:** `backend/alembic_migrations/versions/faab766d1a0f_add_tenant_subscription_and_quotas.py`

⚠️ **NOT APPLIED YET** - Migration is large and includes cleanup of old tables.

---

## 🚧 Remaining Tasks

### Task 3: Quotas System Implementation

#### 3.1 Create Quota Constants
**File:** `backend/security/quotas.py` (NEW)

```python
"""
Tenant Quota System
Prevents abuse with per-tenant limits
"""

from typing import Dict, Optional
from datetime import datetime, timedelta
from backend.models.tenant import TenantPlan

# Default Quotas by Plan
DEFAULT_QUOTAS = {
    TenantPlan.FREE_TRIAL: {
        "max_users": 3,
        "max_tickets_per_day": 10,
        "max_shipments_per_day": 20,
        "max_file_upload_mb": 10,
        "max_api_calls_per_minute": 10,
        "max_storage_mb": 100,
        "max_exports_per_day": 5,
        "features": {
            "social_media": False,
            "webhooks": False,
            "api_access": False,
            "advanced_reports": False
        }
    },
    TenantPlan.BASIC: {
        "max_users": 10,
        "max_tickets_per_day": 100,
        "max_shipments_per_day": 200,
        "max_file_upload_mb": 50,
        "max_api_calls_per_minute": 60,
        "max_storage_mb": 1000,
        "max_exports_per_day": 50,
        "features": {
            "social_media": True,
            "webhooks": True,
            "api_access": True,
            "advanced_reports": False
        }
    },
    TenantPlan.PROFESSIONAL: {
        "max_users": 50,
        "max_tickets_per_day": 1000,
        "max_shipments_per_day": 2000,
        "max_file_upload_mb": 200,
        "max_api_calls_per_minute": 300,
        "max_storage_mb": 10000,
        "max_exports_per_day": 500,
        "features": {
            "social_media": True,
            "webhooks": True,
            "api_access": True,
            "advanced_reports": True
        }
    },
    TenantPlan.ENTERPRISE: {
        "max_users": -1,  # Unlimited
        "max_tickets_per_day": -1,
        "max_shipments_per_day": -1,
        "max_file_upload_mb": 1000,
        "max_api_calls_per_minute": -1,
        "max_storage_mb": -1,
        "max_exports_per_day": -1,
        "features": {
            "social_media": True,
            "webhooks": True,
            "api_access": True,
            "advanced_reports": True
        }
    }
}


class QuotaChecker:
    """Check and enforce tenant quotas"""
    
    def __init__(self, tenant):
        self.tenant = tenant
        self.quotas = tenant.quotas or DEFAULT_QUOTAS.get(tenant.plan, DEFAULT_QUOTAS[TenantPlan.FREE_TRIAL])
    
    def check_user_limit(self, current_count: int) -> bool:
        """Check if tenant can add more users"""
        max_users = self.quotas.get("max_users", 3)
        if max_users == -1:
            return True  # Unlimited
        return current_count < max_users
    
    def check_daily_limit(self, resource: str, count_today: int) -> bool:
        """Check daily resource limit (tickets, shipments, exports)"""
        limit_key = f"max_{resource}_per_day"
        max_limit = self.quotas.get(limit_key, 10)
        if max_limit == -1:
            return True  # Unlimited
        return count_today < max_limit
    
    def check_feature_access(self, feature_name: str) -> bool:
        """Check if tenant has access to a feature"""
        features = self.quotas.get("features", {})
        return features.get(feature_name, False)
    
    def check_file_size(self, file_size_mb: float) -> bool:
        """Check if file size is within limit"""
        max_mb = self.quotas.get("max_file_upload_mb", 10)
        return file_size_mb <= max_mb
    
    def check_storage(self, current_storage_mb: float, new_file_mb: float) -> bool:
        """Check if adding new file exceeds storage limit"""
        max_storage = self.quotas.get("max_storage_mb", 100)
        if max_storage == -1:
            return True
        return (current_storage_mb + new_file_mb) <= max_storage
```

#### 3.2 Create Quota Dependency
**File:** `backend/security/quota_dependency.py` (NEW)

```python
"""
FastAPI dependencies for quota enforcement
"""

from fastapi import Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timedelta

from backend.database.session import wrap_session_factory, get_db_async
from backend.security.auth import get_current_user
from backend.security.quotas import QuotaChecker
from backend.models.tenant import Tenant
from backend.models.support_ticket import SupportTicket


async def enforce_quota(
    request: Request,
    quota_type: str,  # "users", "tickets", "shipments", "exports", "storage"
    increment: int = 1,
    db: AsyncSession = Depends(wrap_session_factory(get_db_async)),
    current_user = Depends(get_current_user)
):
    """
    Enforce quota limits before allowing action
    
    Usage:
        @router.post("/tickets")
        async def create_ticket(
            ...,
            _quota = Depends(lambda: enforce_quota(quota_type="tickets"))
        ):
    """
    
    # Get tenant from request state (set by TenantResolver)
    tenant_id = getattr(request.state, "tenant_id", None)
    if not tenant_id:
        raise HTTPException(status_code=400, detail="Tenant not identified")
    
    # Load tenant
    result = await db.execute(select(Tenant).where(Tenant.id == tenant_id))
    tenant = result.scalar_one_or_none()
    
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    # Check tenant status
    if tenant.status != "active":
        raise HTTPException(
            status_code=403,
            detail=f"Tenant is {tenant.status}. Contact support."
        )
    
    # Check trial expiration
    if tenant.plan == "free_trial" and tenant.trial_ends_at:
        if datetime.utcnow() > tenant.trial_ends_at:
            # Auto-update status
            tenant.status = "trial_expired"
            await db.commit()
            raise HTTPException(
                status_code=402,
                detail="Free trial expired. Please upgrade your plan."
            )
    
    # Initialize quota checker
    checker = QuotaChecker(tenant)
    
    # Check quota based on type
    if quota_type == "users":
        # Count current users in tenant
        count_result = await db.execute(
            select(func.count()).select_from(User).where(User.tenant_id == tenant_id)
        )
        current_count = count_result.scalar()
        
        if not checker.check_user_limit(current_count):
            raise HTTPException(
                status_code=429,
                detail=f"User limit reached ({checker.quotas['max_users']} users). Upgrade your plan."
            )
    
    elif quota_type in ["tickets", "shipments", "exports"]:
        # Count today's resources
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Map quota_type to model
        model_map = {
            "tickets": SupportTicket,
            # "shipments": Shipment,  # Add when model exists
            # "exports": Export  # Add when model exists
        }
        
        model = model_map.get(quota_type)
        if model:
            count_result = await db.execute(
                select(func.count()).select_from(model).where(
                    model.tenant_id == tenant_id,
                    model.created_at >= today_start
                )
            )
            count_today = count_result.scalar()
            
            if not checker.check_daily_limit(quota_type, count_today):
                max_limit = checker.quotas[f"max_{quota_type}_per_day"]
                raise HTTPException(
                    status_code=429,
                    detail=f"Daily {quota_type} limit reached ({max_limit}). Try again tomorrow or upgrade."
                )
    
    # If we got here, quota check passed
    return True


def check_feature_access(feature: str):
    """
    Dependency to check feature access
    
    Usage:
        @router.get("/social-media")
        async def social_endpoint(
            _feature = Depends(check_feature_access("social_media"))
        ):
    """
    async def dependency(
        request: Request,
        db: AsyncSession = Depends(wrap_session_factory(get_db_async))
    ):
        tenant_id = getattr(request.state, "tenant_id", None)
        if not tenant_id:
            raise HTTPException(status_code=400, detail="Tenant not identified")
        
        result = await db.execute(select(Tenant).where(Tenant.id == tenant_id))
        tenant = result.scalar_one_or_none()
        
        if not tenant:
            raise HTTPException(status_code=404, detail="Tenant not found")
        
        checker = QuotaChecker(tenant)
        
        if not checker.check_feature_access(feature):
            raise HTTPException(
                status_code=403,
                detail=f"Feature '{feature}' not available in your plan. Please upgrade."
            )
        
        return True
    
    return dependency
```

---

### Task 4: Update Tenant Resolver - Fail Closed

**File:** `backend/security/tenant_resolver.py` (UPDATE)

```python
# Current code allows fallback to default tenant
# CHANGE THIS TO FAIL CLOSED

class TenantResolver:
    """SECURE Multi-source tenant resolution - FAIL CLOSED"""
    
    async def resolve_tenant(self, request: Request) -> Optional[Tenant]:
        """
        Resolve tenant from multiple sources with conflict detection.
        
        **FAIL CLOSED**: Returns None if no clear tenant found.
        Caller MUST handle None and reject request.
        """
        
        tenant_candidates = []
        
        # 1. Subdomain (highest priority for web requests)
        if subdomain := self._extract_subdomain(request):
            tenant = await self._get_tenant_by_subdomain(subdomain)
            if tenant:
                tenant_candidates.append(("subdomain", tenant))
        
        # 2. X-Tenant-ID header (for API integrations only)
        if tenant_id_header := request.headers.get("X-Tenant-ID"):
            tenant = await self._get_tenant_by_id(tenant_id_header)
            if tenant:
                tenant_candidates.append(("header", tenant))
        
        # 3. JWT token (if authenticated)
        try:
            token = request.headers.get("Authorization", "").replace("Bearer ", "")
            if token:
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
                tenant_id = payload.get("tenant_id")
                if tenant_id:
                    tenant = await self._get_tenant_by_id(tenant_id)
                    if tenant:
                        tenant_candidates.append(("jwt", tenant))
        except Exception:
            pass  # Invalid/expired token - no tenant from JWT
        
        # CONFLICT DETECTION
        if len(tenant_candidates) > 1:
            # Check if all candidates agree
            tenant_ids = [t.id for _, t in tenant_candidates]
            if len(set(tenant_ids)) > 1:
                # CONFLICT: Different tenants from different sources
                logger.error(
                    f"Tenant conflict detected! Sources: {tenant_candidates}",
                    extra={"path": request.url.path, "method": request.method}
                )
                return None  # FAIL CLOSED - reject conflicting request
        
        # NO DEFAULT TENANT - FAIL CLOSED
        if not tenant_candidates:
            # Log for debugging but don't expose details
            logger.warning(
                f"No tenant identified for request",
                extra={"path": request.url.path, "host": request.headers.get("host")}
            )
            return None  # FAIL CLOSED
        
        # Return the one agreed-upon tenant
        return tenant_candidates[0][1]


async def get_tenant(request: Request) -> Tenant:
    """
    FastAPI dependency - FAIL CLOSED enforcement
    
    Raises HTTPException if no tenant can be identified.
    """
    resolver = TenantResolver()
    tenant = await resolver.resolve_tenant(request)
    
    if tenant is None:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "tenant_not_identified",
                "message": "Request must include valid tenant identification",
                "help": "Provide subdomain (gtsdispatcher.com), X-API-Key (api.gtsdispatcher.com), or authenticated JWT"
            }
        )
    
    # Attach to request state for downstream use
    request.state.tenant = tenant
    request.state.tenant_id = tenant.id
    
    return tenant


async def get_tenant_id(request: Request) -> str:
    """Shortcut dependency to get just tenant ID"""
    tenant = await get_tenant(request)
    return tenant.id
```

**Update all routers:**
```python
# Add to ALL /api/v1/* routers that touch tenant-scoped data

from backend.security.tenant_resolver import get_tenant_id

@router.post("/tickets")
async def create_ticket(
    ticket_data: TicketCreate,
    tenant_id: str = Depends(get_tenant_id),  # ← ADD THIS
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    # Now tenant_id is guaranteed to exist or request was rejected
    new_ticket = SupportTicket(
        tenant_id=tenant_id,  # ← USE IT
        ...
    )
```

---

### Task 5: Public Signup Endpoint

**File:** `backend/routes/public_signup.py` (NEW)

```python
"""
Public Tenant Signup with Security
"""

import secrets
import hashlib
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Request, Depends, BackgroundTasks
from pydantic import BaseModel, EmailStr, validator
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.database.session import wrap_session_factory, get_db_async
from backend.models.tenant import Tenant, TenantPlan, TenantStatus, BillingStatus
from backend.models.user import User  # Assuming User model exists
from backend.security.password import hash_password
from backend.services.email import send_verification_email  # You'll need to implement
from backend.security.quotas import DEFAULT_QUOTAS


router = APIRouter(prefix="/api/v1/signup", tags=["Public Signup"])


# In-memory rate limiting (replace with Redis in production)
SIGNUP_RATE_LIMIT = {}  # {ip: [timestamps]}
MAX_SIGNUPS_PER_IP_PER_DAY = 3


class SignupRequest(BaseModel):
    company_name: str
    subdomain: str
    owner_email: EmailStr
    owner_name: str
    owner_password: str
    
    @validator("subdomain")
    def validate_subdomain(cls, v):
        """Ensure subdomain is safe"""
        if not v.isalnum() or len(v) < 3 or len(v) > 20:
            raise ValueError("Subdomain must be 3-20 alphanumeric characters")
        
        # Reserved subdomains
        reserved = {"www", "api", "admin", "app", "dashboard", "mail", "ftp", "blog", "docs"}
        if v.lower() in reserved:
            raise ValueError(f"Subdomain '{v}' is reserved")
        
        return v.lower()
    
    @validator("owner_password")
    def validate_password(cls, v):
        """Basic password strength"""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class SignupResponse(BaseModel):
    success: bool
    tenant_id: str
    subdomain: str
    message: str
    verification_required: bool


def check_ip_rate_limit(ip: str):
    """Check if IP has exceeded signup limit"""
    now = datetime.utcnow()
    cutoff = now - timedelta(days=1)
    
    # Clean old entries
    if ip in SIGNUP_RATE_LIMIT:
        SIGNUP_RATE_LIMIT[ip] = [ts for ts in SIGNUP_RATE_LIMIT[ip] if ts > cutoff]
    
    # Check limit
    count = len(SIGNUP_RATE_LIMIT.get(ip, []))
    if count >= MAX_SIGNUPS_PER_IP_PER_DAY:
        raise HTTPException(
            status_code=429,
            detail=f"Too many signups from your IP today. Limit: {MAX_SIGNUPS_PER_IP_PER_DAY}/day"
        )
    
    # Record this attempt
    if ip not in SIGNUP_RATE_LIMIT:
        SIGNUP_RATE_LIMIT[ip] = []
    SIGNUP_RATE_LIMIT[ip].append(now)


async def check_subdomain_available(subdomain: str, db: AsyncSession) -> bool:
    """Check if subdomain is not taken"""
    result = await db.execute(
        select(Tenant).where(Tenant.subdomain == subdomain)
    )
    existing = result.scalar_one_or_none()
    return existing is None


async def check_email_available(email: str, db: AsyncSession) -> bool:
    """Check if email is not already used"""
    result = await db.execute(
        select(Tenant).where(Tenant.owner_email == email)
    )
    existing = result.scalar_one_or_none()
    return existing is None


@router.post("/register", response_model=SignupResponse)
async def public_signup(
    signup_data: SignupRequest,
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(wrap_session_factory(get_db_async))
):
    """
    Public tenant signup endpoint - PROTECTED
    
    Security measures:
    - IP rate limiting
    - Subdomain validation
    - Email verification required
    - Free trial auto-assigned
    - Owner user auto-created
    """
    
    # Get client IP
    client_ip = request.client.host
    
    # Rate limiting
    check_ip_rate_limit(client_ip)
    
    # Check subdomain availability
    if not await check_subdomain_available(signup_data.subdomain, db):
        raise HTTPException(
            status_code=409,
            detail=f"Subdomain '{signup_data.subdomain}' is already taken"
        )
    
    # Check email availability
    if not await check_email_available(signup_data.owner_email, db):
        raise HTTPException(
            status_code=409,
            detail="Email already registered. Try logging in instead."
        )
    
    # Generate tenant ID
    tenant_id = secrets.token_urlsafe(16)
    
    # Generate verification token
    verification_token = secrets.token_urlsafe(32)
    
    # Create tenant
    new_tenant = Tenant(
        id=tenant_id,
        subdomain=signup_data.subdomain,
        name=signup_data.company_name,
        owner_email=signup_data.owner_email,
        plan=TenantPlan.FREE_TRIAL,
        billing_status=BillingStatus.NOT_REQUIRED,
        status=TenantStatus.PENDING_VERIFICATION,  # ← Requires email verification
        trial_ends_at=datetime.utcnow() + timedelta(days=14),  # 14-day trial
        quotas=DEFAULT_QUOTAS[TenantPlan.FREE_TRIAL],
        settings_json={"verification_token": verification_token}
    )
    db.add(new_tenant)
    
    # Create owner user
    password_hash = hash_password(signup_data.owner_password)
    owner_user = User(
        tenant_id=tenant_id,
        email=signup_data.owner_email,
        name=signup_data.owner_name,
        hashed_password=password_hash,
        role="tenant_admin",  # Owner gets admin role
        is_active=False  # Activated after email verification
    )
    db.add(owner_user)
    
    await db.commit()
    await db.refresh(new_tenant)
    await db.refresh(owner_user)
    
    # Update tenant with owner_user_id
    new_tenant.owner_user_id = owner_user.id
    await db.commit()
    
    # Send verification email (background task)
    verification_url = f"https://{signup_data.subdomain}.gtsdispatcher.com/verify-email?token={verification_token}"
    background_tasks.add_task(
        send_verification_email,
        to_email=signup_data.owner_email,
        company_name=signup_data.company_name,
        verification_url=verification_url
    )
    
    return SignupResponse(
        success=True,
        tenant_id=tenant_id,
        subdomain=signup_data.subdomain,
        message="Signup successful! Check your email to verify and activate your account.",
        verification_required=True
    )


@router.post("/verify-email")
async def verify_email(
    token: str,
    db: AsyncSession = Depends(wrap_session_factory(get_db_async))
):
    """Verify email and activate tenant"""
    
    # Find tenant by verification token
    result = await db.execute(
        select(Tenant).where(Tenant.settings_json.contains({"verification_token": token}))
    )
    tenant = result.scalar_one_or_none()
    
    if not tenant:
        raise HTTPException(status_code=404, detail="Invalid verification token")
    
    if tenant.email_verified_at:
        return {"success": True, "message": "Email already verified"}
    
    # Activate tenant
    tenant.status = TenantStatus.ACTIVE
    tenant.email_verified_at = datetime.utcnow()
    
    # Activate owner user
    result = await db.execute(
        select(User).where(User.id == tenant.owner_user_id)
    )
    owner = result.scalar_one_or_none()
    if owner:
        owner.is_active = True
    
    await db.commit()
    
    return {
        "success": True,
        "message": "Email verified! Your account is now active.",
        "subdomain": tenant.subdomain,
        "login_url": f"https://{tenant.subdomain}.gtsdispatcher.com/login"
    }
```

---

### Task 6: Rate Limiting Middleware

**File:** `backend/middleware/rate_limit.py` (NEW)

```python
"""
Simple in-memory rate limiting
Replace with Redis in production
"""

import time
from collections import defaultdict
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Simple rate limiting middleware
    
    Limits per IP + per Tenant
    """
    
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests = defaultdict(list)  # {ip: [timestamps]}
    
    async def dispatch(self, request: Request, call_next):
        # Get client IP
        client_ip = request.client.host
        
        # Get current time
        now = time.time()
        minute_ago = now - 60
        
        # Clean old requests
        self.requests[client_ip] = [
            ts for ts in self.requests[client_ip] if ts > minute_ago
        ]
        
        # Check limit
        if len(self.requests[client_ip]) >= self.requests_per_minute:
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded: {self.requests_per_minute} requests/minute"
            )
        
        # Record this request
        self.requests[client_ip].append(now)
        
        # Process request
        response = await call_next(request)
        return response
```

**Add to main.py:**
```python
from backend.middleware.rate_limit import RateLimitMiddleware

app.add_middleware(RateLimitMiddleware, requests_per_minute=60)
```

---

### Task 7: Smoke Test - Multi-Tenant Isolation

**File:** `tests/smoke_test_multi_tenant.py` (NEW)

```python
"""
Smoke Test: Multi-Tenant Data Isolation
CRITICAL: Verify no cross-tenant data leakage
"""

import pytest
import httpx
from backend.main import app

BASE_URL = "http://localhost:8000"


async def create_test_tenant(subdomain: str, email: str):
    """Helper to create a test tenant via signup"""
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app)) as client:
        response = await client.post(
            f"{BASE_URL}/api/v1/signup/register",
            json={
                "company_name": f"Test Company {subdomain}",
                "subdomain": subdomain,
                "owner_email": email,
                "owner_name": "Test Owner",
                "owner_password": "testpass123"
            }
        )
        assert response.status_code == 200
        return response.json()


async def login_tenant(email: str, password: str):
    """Login and get token"""
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app)) as client:
        response = await client.post(
            f"{BASE_URL}/auth/token",
            data={"email": email, "password": password}
        )
        assert response.status_code == 200
        return response.json()["access_token"]


@pytest.mark.asyncio
async def test_tenant_isolation_tickets():
    """
    Test: Support tickets are isolated per tenant
    Tenant A cannot see Tenant B's tickets
    """
    
    # Create two tenants
    tenant_a = await create_test_tenant("tenant-a-test", "a@test.com")
    tenant_b = await create_test_tenant("tenant-b-test", "b@test.com")
    
    # Verify both tenants (manually set verified_at in DB for test)
    # ...
    
    # Login as Tenant A
    token_a = await login_tenant("a@test.com", "testpass123")
    
    # Login as Tenant B
    token_b = await login_tenant("b@test.com", "testpass123")
    
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app)) as client:
        # Tenant A creates a ticket
        response_a = await client.post(
            f"{BASE_URL}/api/v1/support/tickets",
            json={
                "subject": "Secret Tenant A Issue",
                "description": "Confidential A data",
                "priority": "high"
            },
            headers={"Authorization": f"Bearer {token_a}"}
        )
        assert response_a.status_code == 201
        ticket_a_id = response_a.json()["id"]
        
        # Tenant B creates a ticket
        response_b = await client.post(
            f"{BASE_URL}/api/v1/support/tickets",
            json={
                "subject": "Secret Tenant B Issue",
                "description": "Confidential B data",
                "priority": "low"
            },
            headers={"Authorization": f"Bearer {token_b}"}
        )
        assert response_b.status_code == 201
        ticket_b_id = response_b.json()["id"]
        
        # Tenant A lists tickets - should only see their own
        response = await client.get(
            f"{BASE_URL}/api/v1/support/tickets",
            headers={"Authorization": f"Bearer {token_a}"}
        )
        assert response.status_code == 200
        tickets_a = response.json()["tickets"]
        ticket_ids_a = [t["id"] for t in tickets_a]
        
        # CRITICAL ASSERTION: Tenant A cannot see Tenant B's ticket
        assert ticket_a_id in ticket_ids_a
        assert ticket_b_id not in ticket_ids_a
        
        # Tenant B lists tickets - should only see their own
        response = await client.get(
            f"{BASE_URL}/api/v1/support/tickets",
            headers={"Authorization": f"Bearer {token_b}"}
        )
        assert response.status_code == 200
        tickets_b = response.json()["tickets"]
        ticket_ids_b = [t["id"] for t in tickets_b]
        
        # CRITICAL ASSERTION: Tenant B cannot see Tenant A's ticket
        assert ticket_b_id in ticket_ids_b
        assert ticket_a_id not in ticket_ids_b
        
        # Tenant A tries to access Tenant B's ticket directly - should fail
        response = await client.get(
            f"{BASE_URL}/api/v1/support/tickets/{ticket_b_id}",
            headers={"Authorization": f"Bearer {token_a}"}
        )
        # Should return 404 or 403 (not 200 with data!)
        assert response.status_code in [403, 404]
    
    print("✅ Ticket isolation verified: No cross-tenant data leakage")


@pytest.mark.asyncio
async def test_tenant_quota_enforcement():
    """
    Test: FREE_TRIAL quota limits are enforced
    """
    
    tenant = await create_test_tenant("quota-test", "quota@test.com")
    token = await login_tenant("quota@test.com", "testpass123")
    
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app)) as client:
        # Try to exceed daily ticket limit (default: 10 for FREE_TRIAL)
        for i in range(15):
            response = await client.post(
                f"{BASE_URL}/api/v1/support/tickets",
                json={
                    "subject": f"Ticket {i}",
                    "description": "Test",
                    "priority": "low"
                },
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if i < 10:
                # First 10 should succeed
                assert response.status_code == 201
            else:
                # 11th+ should fail with quota error
                assert response.status_code == 429
                assert "limit" in response.json()["detail"].lower()
    
    print("✅ Quota enforcement verified: Limits working correctly")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
```

---

## 📋 Final Deployment Steps

### Step 1: Apply Migrations
```bash
# Review migration first!
code backend/alembic_migrations/versions/faab766d1a0f_add_tenant_subscription_and_quotas.py

# Apply migration (CAREFUL - large changes)
python -m alembic -c backend/alembic.ini upgrade head

# Verify tenant table structure
psql $DATABASE_URL -c "\d tenants;"
```

### Step 2: Update Existing Tenants
```sql
-- Set default values for existing tenants
UPDATE tenants 
SET 
    plan = 'free_trial',
    billing_status = 'not_required',
    status = 'active',
    trial_ends_at = NOW() + INTERVAL '30 days',
    quotas = '{"max_users": 10, "max_tickets_per_day": 100}'::jsonb
WHERE plan IS NULL;
```

### Step 3: Mount New Routes
```python
# In backend/main.py

from backend.routes.public_signup import router as signup_router
app.include_router(signup_router)  # Public - no auth
```

### Step 4: Update Tenant Resolver (CRITICAL!)
```python
# Replace in backend/security/tenant_resolver.py
# Switch from "default tenant fallback" to "FAIL CLOSED"
# (See Task 4 above)
```

### Step 5: Add Quota Enforcement to Routes
```python
# Example: backend/routes/support_routes.py

from backend.security.quota_dependency import enforce_quota

@router.post("/tickets")
async def create_ticket(
    ticket_data: TicketCreate,
    tenant_id: str = Depends(get_tenant_id),
    current_user = Depends(get_current_user),
    _quota = Depends(lambda r: enforce_quota(r, quota_type="tickets")),  # ← ADD
    db: AsyncSession = Depends(get_async_session)
):
    # Quota checked before reaching here
    ...
```

### Step 6: Run Smoke Tests
```bash
# Start backend
python -m uvicorn backend.main:app --reload

# In another terminal
pytest tests/smoke_test_multi_tenant.py -v -s

# Must see:
# ✅ Ticket isolation verified
# ✅ Quota enforcement verified
```

### Step 7: Frontend Updates
```javascript
// frontend/src/api/axiosClient.js
// Add subdomain to all requests
const instance = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL,
    headers: {
        'X-Tenant-Subdomain': window.location.hostname.split('.')[0]
    }
});
```

---

## ⚠️ Pre-Launch Checklist

### Security Checks
- [ ] Tenant resolver returns 400 for unidentified tenants (NO DEFAULT FALLBACK)
- [ ] All tenant-scoped tables have `tenant_id` column
- [ ] All queries filter by `tenant_id`
- [ ] Smoke tests pass (no cross-tenant leakage)
- [ ] Rate limiting enabled (IP + tenant)
- [ ] Email verification required
- [ ] Subdomain validation enforced

### Quota Enforcement
- [ ] FREE_TRIAL limits set and tested
- [ ] Daily limits reset at midnight UTC
- [ ] Feature flags work (social_media, webhooks, etc.)
- [ ] Upgrade paths documented

### Monitoring
- [ ] Error tracking configured (Sentry/similar)
- [ ] Logs include `tenant_id` in all entries
- [ ] Alert on quota abuse attempts
- [ ] Dashboard for tenant metrics

---

## 📞 Support & Next Steps

### If an error occurs
1. Check logs: `tenant_id` missing?
2. Check `request.state.tenant` in middleware
3. Verify migration applied: `SELECT plan FROM tenants LIMIT 1;`

### Additional features (for future)
- Stripe integration for paid plans
- Tenant dashboard (usage metrics)
- Admin panel for super_admin (view all tenants)
- Automated trial expiration emails
- Plan comparison page
- Referral system

---

**End of Implementation Plan**
**Last Updated:** January 8, 2026
