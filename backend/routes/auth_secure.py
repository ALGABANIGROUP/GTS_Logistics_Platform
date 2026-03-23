from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field, validator
from backend.security.jwt_security import JWTSecurity
from backend.security.encryption import encryption_service
from backend.security.audit_logger import AuditLogger, AuditEventType
from datetime import datetime
import logging

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
        user = authenticate_user(credentials.email, credentials.password)
        
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
                details={"user_id": user['id'], "ip": client_ip}
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
        # Check if email already exists
        if email_exists(user_data.email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered"
            )
        
        # Hash password
        hashed_password = encryption_service.hash_password(user_data.password)
        
        # Create user in database
        new_user = create_user_in_db(
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
        
        # Get updated user data
        user = get_user_by_id(user_id)
        
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
    
    # Get full user details
    user = get_user_by_id(user_id)
    
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
# HELPER FUNCTIONS
# ============================================================================

def authenticate_user(email: str, password: str):
    """Authenticate user with email and password"""
    # This function queries the database
    # Implementation depends on your database schema
    
    user = get_user_by_email(email)
    if not user:
        return None
    
    # Verify password
    if not encryption_service.verify_password(password, user['password_hash']):
        return None
    
    return user

def email_exists(email: str) -> bool:
    """Check if email already exists"""
    return get_user_by_email(email) is not None

# NOTE: These functions need to be implemented based on your database
# get_user_by_email, get_user_by_id, create_user_in_db, etc.