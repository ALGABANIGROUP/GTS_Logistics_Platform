# backend/routes/auth.py
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import jwt
import os
import bcrypt

router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])
security = HTTPBearer()

# ==================== Models ====================
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: Dict[str, Any]

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    role: str

# ==================== Mock Database ====================
# Users for production
USERS_DB = {
    "enjoy983@hotmail.com": {
        "id": 1,
        "email": "enjoy983@hotmail.com",
        "full_name": "Admin User",
        "role": "admin",
        "is_active": True
    },
    "admin@gts.com": {
        "id": 2,
        "email": "admin@gts.com",
        "full_name": "System Administrator",
        "role": "admin",
        "is_active": True
    },
    "manager@gts.com": {
        "id": 3,
        "email": "manager@gts.com",
        "full_name": "Operations Manager",
        "role": "manager",
        "is_active": True
    }
}

# Passwords (in production, these should be hashed)
PASSWORDS = {
    "enjoy983@hotmail.com": "Gabani@2026",
    "admin@gts.com": "admin123",
    "manager@gts.com": "manager123"
}

# ==================== Helper Functions ====================
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=30)
    
    to_encode.update({"exp": expire})
    
    secret_key = os.getenv("JWT_SECRET_KEY", "development-secret-key")
    algorithm = os.getenv("JWT_ALGORITHM", "HS256")
    
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
    return encoded_jwt

def verify_password(plain_password: str, email: str) -> bool:
    """Verify password"""
    stored_password = PASSWORDS.get(email)
    if not stored_password:
        return False
    return plain_password == stored_password

# ==================== Endpoints ====================
@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    Login to the system
    
    - **email**: User email address
    - **password**: User password
    """
    
    # Find user
    user = USERS_DB.get(request.email)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    if not verify_password(request.password, request.email):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if account is active
    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled"
        )
    
    # Create token
    access_token = create_access_token(
        data={
            "sub": str(user["id"]),
            "email": user["email"],
            "role": user["role"]
        }
    )
    
    return LoginResponse(
        access_token=access_token,
        expires_in=1800,
        user={
            "id": user["id"],
            "email": user["email"],
            "full_name": user["full_name"],
            "role": user["role"]
        }
    )

@router.get("/me", response_model=UserResponse)
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user information"""
    token = credentials.credentials
    
    try:
        secret_key = os.getenv("JWT_SECRET_KEY", "development-secret-key")
        algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        email = payload.get("email")
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = USERS_DB.get(email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserResponse(
        id=user["id"],
        email=user["email"],
        full_name=user["full_name"],
        role=user["role"]
    )
