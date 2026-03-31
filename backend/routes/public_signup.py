# backend/routes/public_signup.py
"""
Public signup endpoint with email verification
Multi-tenant registration system
"""
import logging
import secrets
import os
from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel, EmailStr

from fastapi import APIRouter, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database.session import wrap_session_factory, get_async_session
from backend.models.tenant import Tenant, TenantPlan, TenantStatus, BillingStatus
from backend.models.user import User
from backend.security.auth import get_password_hash
from backend.services.email_service import send_email_verification

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/signup", tags=["public-signup"])

# Toggle signup
SIGNUP_DISABLED = False
SIGNUP_DISABLED_DETAIL = "Public signup is temporarily closed. Please contact the administrator."

# hCaptcha config (optional)
HCAPTCHA_SECRET = os.getenv("HCAPTCHA_SECRET", "").strip()
HCAPTCHA_ENABLED = bool(HCAPTCHA_SECRET)

# In-memory IP rate limiter (replace with Redis in production)
IP_SIGNUP_ATTEMPTS = {}
SIGNUP_RATE_LIMIT = 3  # signups per day per IP


class SignupRequest(BaseModel):
    """Public signup request"""
    company_name: str  # 2-100 chars
    subdomain: str  # 3-20 chars, alphanumeric+hyphen only, unique
    owner_email: EmailStr
    owner_name: str  # 2-100 chars
    owner_password: str  # 8+ chars


class SignupResponse(BaseModel):
    """Signup response"""
    success: bool
    tenant_id: Optional[str] = None
    message: str


class VerifyEmailRequest(BaseModel):
    """Email verification request"""
    verification_token: str


def validate_subdomain(subdomain: str) -> bool:
    """Validate subdomain format"""
    if not subdomain:
        return False
    if len(subdomain) < 3 or len(subdomain) > 20:
        return False
    # Alphanumeric and hyphen only
    if not all(c.isalnum() or c == "-" for c in subdomain):
        return False
    # No leading/trailing hyphen
    if subdomain.startswith("-") or subdomain.endswith("-"):
        return False
    # No reserved words
    reserved = {"www", "app", "api", "admin", "mail", "ftp", "localhost", "example"}
    if subdomain.lower() in reserved:
        return False
    return True


def check_ip_rate_limit(ip: str) -> bool:
    """Check if IP has exceeded signup rate limit"""
    today = datetime.utcnow().date().isoformat()
    key = f"{ip}:{today}"
    
    attempts = IP_SIGNUP_ATTEMPTS.get(key, 0)
    if attempts >= SIGNUP_RATE_LIMIT:
        return False
    
    # Increment attempts
    IP_SIGNUP_ATTEMPTS[key] = attempts + 1
    
    # Clean old entries (keep only last 7 days)
    cutoff_date = (datetime.utcnow() - timedelta(days=7)).date().isoformat()
    keys_to_delete = [k for k in IP_SIGNUP_ATTEMPTS.keys() if k.split(":")[1] < cutoff_date]
    for k in keys_to_delete:
        del IP_SIGNUP_ATTEMPTS[k]
    
    return True


@router.post("/register", response_model=SignupResponse)
async def register(
    req: SignupRequest,
    request: Request,
    db: AsyncSession = __import__("fastapi").Depends(get_async_session)
):
    """
    Register new tenant with email verification
    """
    if SIGNUP_DISABLED:
        raise HTTPException(status_code=403, detail=SIGNUP_DISABLED_DETAIL)
    
    # hCaptcha server-side verification (optional)
    if HCAPTCHA_ENABLED:
        # Accept token in header X-HCAPTCHA-TOKEN or in JSON body 'h-captcha-response'
        token = request.headers.get("X-HCAPTCHA-TOKEN")
        if not token:
            try:
                body = await request.json()
                token = body.get("h-captcha-response")
            except Exception:
                token = None

        if not token:
            raise HTTPException(status_code=400, detail="hCaptcha token missing")

        # Verify using hCaptcha API
        import aiohttp
        try:
            async with aiohttp.ClientSession() as session:
                payload = {"secret": HCAPTCHA_SECRET, "response": token}
                async with session.post("https://hcaptcha.com/siteverify", data=payload) as resp:
                    data = await resp.json()
                    if not data.get("success", False):
                        raise HTTPException(status_code=400, detail="Captcha verification failed")
        except HTTPException:
            raise
        except Exception as e:
            logger.exception("hCaptcha verification error: %s", e)
            raise HTTPException(status_code=500, detail="Captcha verification failed")

    async with wrap_session_factory(get_async_session) as session:
        # Get client IP (handle proxies)
        client_ip = (
            request.headers.get("x-forwarded-for", "").split(",")[0].strip()
            or request.client.host
        )
        
        # Check rate limit
        if not check_ip_rate_limit(client_ip):
            logger.warning(f"IP rate limit exceeded for {client_ip}")
            raise HTTPException(
                status_code=429,
                detail="Too many signup attempts from this IP (limit: 3/day)"
            )
        
        # Validate input
        if len(req.company_name) < 2 or len(req.company_name) > 100:
            raise HTTPException(status_code=400, detail="Company name must be 2-100 characters")
        
        if len(req.owner_name) < 2 or len(req.owner_name) > 100:
            raise HTTPException(status_code=400, detail="Owner name must be 2-100 characters")
        
        if len(req.owner_password) < 8:
            raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
        
        if not validate_subdomain(req.subdomain):
            raise HTTPException(
                status_code=400,
                detail="Subdomain must be 3-20 characters (alphanumeric + hyphens only)"
            )
        
        # Check subdomain uniqueness
        existing = await session.execute(
            select(Tenant).where(Tenant.subdomain == req.subdomain.lower())
        )
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Subdomain already taken")
        
        # Check email uniqueness
        existing_user = await session.execute(
            select(User).where(User.email == req.owner_email.lower())
        )
        if existing_user.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Email already registered")
        
        try:
            # Create tenant
            tenant = Tenant(
                subdomain=req.subdomain.lower(),
                company_name=req.company_name,
                plan=TenantPlan.FREE_TRIAL,
                billing_status=BillingStatus.NOT_REQUIRED,
                status=TenantStatus.PENDING_VERIFICATION,
                owner_email=req.owner_email.lower(),
                trial_ends_at=datetime.utcnow() + timedelta(days=30),
                quotas={
                    "max_users": 3,
                    "max_tickets_per_day": 10,
                    "max_storage_mb": 100,
                },
            )
            session.add(tenant)
            await session.flush()  # Get tenant.id
            
            # Create owner user (inactive until email verified)
            owner_user = User(
                email=req.owner_email.lower(),
                full_name=req.owner_name,
                hashed_password=get_password_hash(req.owner_password),
                tenant_id=tenant.id,
                role="tenant_admin",
                is_active=False,  # Inactive until email verification
            )
            session.add(owner_user)
            
            # Generate verification token
            verification_token = secrets.token_urlsafe(32)
            tenant.email_verification_token = verification_token
            tenant.email_verification_expires_at = datetime.utcnow() + timedelta(hours=24)
            
            await session.commit()
            
            # Send verification email
            try:
                await send_email_verification(
                    email=req.owner_email,
                    company_name=req.company_name,
                    subdomain=req.subdomain,
                    verification_link=f"https://{req.subdomain.lower()}.gtsdispatcher.com/verify?token={verification_token}",
                    owner_name=req.owner_name
                )
            except Exception as e:
                logger.error(f"Failed to send verification email: {str(e)}")
                # Don't fail signup, but log the error
            
            logger.info(f"New tenant registered: {tenant.id} ({req.company_name})")
            
            return SignupResponse(
                success=True,
                tenant_id=tenant.id,
                message=f"Registration successful! Check {req.owner_email} to verify your account."
            )
        
        except Exception as e:
            await session.rollback()
            logger.exception(f"Signup registration failed: {str(e)}")
            raise HTTPException(status_code=500, detail="Registration failed")


@router.post("/verify-email", response_model=SignupResponse)
async def verify_email(
    req: VerifyEmailRequest,
    db: AsyncSession = __import__("fastapi").Depends(get_async_session)
):
    """
    Verify email and activate tenant
    """
    
    async with wrap_session_factory(get_async_session) as session:
        try:
            # Find tenant by verification token
            stmt = select(Tenant).where(
                Tenant.email_verification_token == req.verification_token
            )
            result = await session.execute(stmt)
            tenant = result.scalar_one_or_none()
            
            if not tenant:
                raise HTTPException(status_code=400, detail="Invalid verification token")
            
            # Check if token expired
            if tenant.email_verification_expires_at and datetime.utcnow() > tenant.email_verification_expires_at:
                raise HTTPException(status_code=400, detail="Verification token expired")
            
            # Activate tenant and owner user
            tenant.status = TenantStatus.ACTIVE
            tenant.email_verified_at = datetime.utcnow()
            tenant.email_verification_token = None
            tenant.email_verification_expires_at = None
            
            # Activate owner user
            owner_user = await session.execute(
                select(User).where(
                    (User.tenant_id == tenant.id) &
                    (User.role == "tenant_admin")
                )
            )
            user = owner_user.scalar_one_or_none()
            if user:
                user.is_active = True
            
            await session.commit()
            
            logger.info(f"Tenant activated after email verification: {tenant.id}")
            
            return SignupResponse(
                success=True,
                tenant_id=tenant.id,
                message="Email verified! Your account is now active. You can now login."
            )
        
        except HTTPException:
            raise
        except Exception as e:
            await session.rollback()
            logger.exception(f"Email verification failed: {str(e)}")
            raise HTTPException(status_code=500, detail="Verification failed")


@router.get("/status/{subdomain}")
async def check_subdomain_availability(
    subdomain: str,
    db: AsyncSession = __import__("fastapi").Depends(get_async_session)
):
    """Check if subdomain is available"""
    
    if not validate_subdomain(subdomain):
        return {"available": False, "message": "Invalid subdomain format"}
    
    async with wrap_session_factory(get_async_session) as session:
        existing = await session.execute(
            select(Tenant).where(Tenant.subdomain == subdomain.lower())
        )
        is_available = existing.scalar_one_or_none() is None
        
        return {
            "subdomain": subdomain.lower(),
            "available": is_available,
            "message": "Available" if is_available else "Already taken"
        }
