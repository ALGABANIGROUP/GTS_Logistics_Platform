# backend/routes/auth_secure.py
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field, validator
from backend.security.jwt_security import JWTSecurity
from backend.security.encryption import encryption_service
from backend.security.audit_logger import AuditLogger, AuditEventType
from datetime import datetime
import logging

# Typing
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])

# ============================================================================
# PYDANTIC MODELS - Secure Input Validation
# ============================================================================

class LoginRequest(BaseModel):
    """Login request with validation"""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    
    @validator('password')
    def validate_password(cls, v):
        """Validate password strength"""
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain uppercase letter')
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain digit')
        return v

class TokenResponse(BaseModel):
    """Token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class RegisterRequest(BaseModel):
    """User registration"""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    name: str = Field(..., min_length=2, max_length=100)
    company: str = Field(..., min_length=2, max_length=100)
    
    @validator('password')
    def validate_password_strength(cls, v):
        """Strong password validation"""
        if len(v) < 8:
            raise ValueError('Password too short')
        if not any(char.isupper() for char in v):
            raise ValueError('Need uppercase letter')
        if not any(char.isdigit() for char in v):
            raise ValueError('Need digit')
        if not any(char in "!@#$%^&*" for char in v):
            raise ValueError('Need special character')
        return v

class RefreshTokenRequest(BaseModel):
    """Refresh token request"""
    refresh_token: str

# ============================================================================
# LOGIN ENDPOINT
# ============================================================================

@router.post("/token", response_model=TokenResponse)
async def login(credentials: LoginRequest, request):
    """
    User login endpoint
    Returns access and refresh tokens
    """
    
    client_ip = request.state.client_ip if hasattr(request.state, 'client_ip') else "unknown"
    
    try:
        # Validate credentials (fetch from database)
        user = await authenticate_user(credentials.email, credentials.password)
        
        if not user:
            # Log failed login
            AuditLogger.log_login(
                user_id=credentials.email,
                ip_address=client_ip,
                success=False
            )
            
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Check if user is active
        if not user.get('is_active', False):
            AuditLogger.log_security_alert(
                alert_type="INACTIVE_USER_LOGIN_ATTEMPT",
                details={"user_id": user.get('id'), "ip": client_ip}
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )
        
        # Create tokens
        access_token = JWTSecurity.create_access_token(
            data={
                "sub": user['id'],
                "email": user['email'],
                "role": user.get('role', 'customer'),
                "company_id": user.get('company_id')
            }
        )
        
        refresh_token = JWTSecurity.create_refresh_token(
            data={"sub": user['id']}
        )
        
        # Log successful login
        AuditLogger.log_login(
            user_id=user['id'],
            ip_address=client_ip,
            success=True
        )
        
        logger.info(f"✅ User {user['email']} logged in from {client_ip}")
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=JWTSecurity.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Login error: {str(e)}")
        AuditLogger.log_security_alert(
            alert_type="LOGIN_ERROR",
            details={"error": str(e), "ip": client_ip}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )

# ============================================================================
# REGISTRATION ENDPOINT
# ============================================================================

@router.post("/register", response_model=dict)
async def register(user_data: RegisterRequest):
    """
    User registration endpoint
    """
    
    try:
        # Check if email already exists (async)
        if await email_exists(user_data.email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered"
            )
        
        # Hash password
        hashed_password = encryption_service.hash_password(user_data.password)
        
        # Create user in database (async)
        new_user = await create_user_in_db(
            email=user_data.email,
            password_hash=hashed_password,
            name=user_data.name,
            company=user_data.company
        )
        
        # Log registration
        AuditLogger.log_event(
            event_type=AuditEventType.LOGIN,  # New user
            user_id=new_user['id'],
            action="REGISTER",
            resource="authentication"
        )
        
        logger.info(f"✅ New user registered: {user_data.email}")
        
        return {
            "user_id": new_user['id'],
            "email": user_data.email,
            "message": "Registration successful. Please log in."
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Registration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

# ============================================================================
# REFRESH TOKEN ENDPOINT
# ============================================================================

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshTokenRequest):
    """
    Refresh access token using refresh token
    """
    
    try:
        # Verify refresh token
        payload = JWTSecurity.verify_token(request.refresh_token)
        
        user_id = payload.get('sub')
        
        # Get updated user data (async)
        user = await get_user_by_id(user_id)
        
        if not user or not user.get('is_active'):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Create new access token
        new_access_token = JWTSecurity.create_access_token(
            data={
                "sub": user['id'],
                "email": user['email'],
                "role": user.get('role', 'customer')
            }
        )
        
        logger.info(f"✅ Token refreshed for user {user_id}")
        
        return TokenResponse(
            access_token=new_access_token,
            refresh_token=request.refresh_token,  # Same refresh token
            expires_in=JWTSecurity.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Token refresh error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token refresh failed"
        )

# ============================================================================
# GET CURRENT USER ENDPOINT
# ============================================================================

@router.get("/me")
async def get_current_user_info(current_user = Depends(JWTSecurity.get_current_user)):
    """
    Get current authenticated user's information
    """
    
    user_id = current_user['sub']
    
    # Get full user details (async)
    user = await get_user_by_id(user_id)
    
    # Log access
    AuditLogger.log_data_access(
        user_id=user_id,
        resource='user_profile',
        access_type='VIEW_SELF'
    )
    
    return {
        "id": user['id'],
        "email": user['email'],
        "name": user['name'],
        "company": user.get('company'),
        "role": user.get('role'),
        "is_active": user.get('is_active'),
        "created_at": user.get('created_at').isoformat() if user.get('created_at') else None
    }

# ============================================================================
# LOGOUT ENDPOINT
# ============================================================================

@router.post("/logout")
async def logout(current_user = Depends(JWTSecurity.get_current_user)):
    """
    Logout endpoint - optional, mainly for frontend to clear tokens
    """
    
    user_id = current_user['sub']
    
    # Log logout
    AuditLogger.log_event(
        event_type=AuditEventType.LOGOUT,
        user_id=user_id,
        action="LOGOUT",
        resource="authentication"
    )
    
    logger.info(f"✅ User {user_id} logged out")
    
    return {"message": "Logged out successfully"}

# ============================================================================
# HELPER FUNCTIONS (async versions)
# ============================================================================

async def authenticate_user(email: str, password: str):
    """Authenticate user with email and password (async)"""
    # This function queries the database
    # Implementation depends on your database schema
    
    user = await get_user_by_email(email)
    if not user:
        return None
    
    # Verify password (synchronous call to encryption_service)
    if not encryption_service.verify_password(password, user.get('password_hash') or user.get('hashed_password') or ""):
        return None
    
    return user

async def email_exists(email: str) -> bool:
    """Check if email already exists (async)"""
    return (await get_user_by_email(email)) is not None

# NOTE: The lower part of this file provides DB helper implementations used above.
# Please append or keep these helpers at the end of this file.
# They rely on AsyncSessionLocal and backend.models.user.User.
# Adjust names if your project uses different session factory names or field names.

# -----------------------------------------------------------------------------
# DB helper implementations for auth_secure.py
# Add this block at the end of backend/routes/auth_secure.py
# -----------------------------------------------------------------------------
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from backend.core.db_config import AsyncSessionLocal  # adjust if your session factory has a different name
from backend.models.user import User

async def get_user_by_email(email: str, db: Optional[Any] = None) -> Optional[Dict[str, Any]]:
    """
    Retrieve a user by email and return a normalized dict or None.
    The returned dict uses keys expected by auth code: id, email, role, name, is_active,
    is_deleted, token_version, password_hash, tenant_id, created_at.
    """
    if not email:
        return None
    email_clean = str(email).strip().lower()

    user_obj = None
    try:
        if db is None:
            async with AsyncSessionLocal() as session:
                res = await session.execute(select(User).where(User.email == email_clean))
                user_obj = res.scalar_one_or_none()
        else:
            res = await db.execute(select(User).where(User.email == email_clean))
            user_obj = res.scalar_one_or_none()
    except Exception:
        return None

    if not user_obj:
        return None

    # Map ORM object to simple dict
    return {
        "id": getattr(user_obj, "id", None),
        "email": getattr(user_obj, "email", None),
        "role": getattr(user_obj, "role", None),
        "name": getattr(user_obj, "name", None) or getattr(user_obj, "full_name", None),
        "is_active": getattr(user_obj, "is_active", True),
        "is_deleted": getattr(user_obj, "is_deleted", False),
        "token_version": int(getattr(user_obj, "token_version", 0) or 0),
        # password field name might be password_hash or hashed_password
        "password_hash": getattr(user_obj, "password_hash", None) or getattr(user_obj, "hashed_password", None),
        "tenant_id": getattr(user_obj, "tenant_id", None),
        "created_at": getattr(user_obj, "created_at", None),
    }


async def get_user_by_id(user_id: int, db: Optional[Any] = None) -> Optional[Dict[str, Any]]:
    """
    Retrieve a user by id and return a normalized dict or None.
    """
    if not user_id:
        return None

    user_obj = None
    try:
        if db is None:
            async with AsyncSessionLocal() as session:
                res = await session.execute(select(User).where(User.id == int(user_id)))
                user_obj = res.scalar_one_or_none()
        else:
            res = await db.execute(select(User).where(User.id == int(user_id)))
            user_obj = res.scalar_one_or_none()
    except Exception:
        return None

    if not user_obj:
        return None

    return {
        "id": getattr(user_obj, "id", None),
        "email": getattr(user_obj, "email", None),
        "role": getattr(user_obj, "role", None),
        "name": getattr(user_obj, "name", None) or getattr(user_obj, "full_name", None),
        "is_active": getattr(user_obj, "is_active", True),
        "is_deleted": getattr(user_obj, "is_deleted", False),
        "token_version": int(getattr(user_obj, "token_version", 0) or 0),
        "tenant_id": getattr(user_obj, "tenant_id", None),
        "created_at": getattr(user_obj, "created_at", None),
    }


async def create_user_in_db(
    email: str,
    password_hash: str,
    name: Optional[str] = None,
    company: Optional[str] = None,
    role: str = "customer",
    tenant_id: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Create a new user record in the DB and return a minimal dict with id and email (and optional fields).
    - This function uses AsyncSessionLocal to obtain a session. It commits the new user and returns the persisted values.
    - Caller must pass a password_hash (already hashed) — use your project's hashing helper for that.
    """
    email_clean = str(email).strip().lower()

    async with AsyncSessionLocal() as session:
        try:
            user = User(
                email=email_clean,
                name=name,
                # Depending on your model, the password field might be 'password_hash' or 'hashed_password'.
                # Try to set both if desired or change to the correct one.
                password_hash=password_hash if hasattr(User, "password_hash") or True else None,
                tenant_id=tenant_id,
                role=role,
                is_active=True,
            )
            # If your model uses 'hashed_password' instead of 'password_hash', set attribute accordingly:
            if hasattr(user, "hashed_password") and not hasattr(user, "password_hash"):
                setattr(user, "hashed_password", password_hash)

            session.add(user)
            await session.flush()  # assign id
            await session.commit()
            # refresh to get DB-generated fields
            try:
                await session.refresh(user)
            except Exception:
                pass

            return {
                "id": getattr(user, "id", None),
                "email": getattr(user, "email", None),
                "name": getattr(user, "name", None),
                "role": getattr(user, "role", None),
                "tenant_id": getattr(user, "tenant_id", None),
                "is_active": getattr(user, "is_active", True),
            }
        except IntegrityError:
            await session.rollback()
            # Raise to caller so they can convert to HTTP 409 if required
            raise
        except Exception:
            await session.rollback()
            raise
