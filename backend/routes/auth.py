"""
Authentication Routes for GTS Logistics
Simplified version to avoid circular imports
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import jwt, JWTError
from passlib.hash import pbkdf2_sha256 as hasher
import os
from backend.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-key-change-in-production")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

# In-memory user store (for development - replace with database)
# This is a fallback; in production, you should use the database
USERS_DB = {
    "admin@example.com": {
        "id": 1,
        "email": "admin@example.com",
        "username": "admin",
        "password_hash": "$pbkdf2-sha256$29000$dummy$hash$placeholder",  # Will be replaced at runtime
        "role": "super_admin",
        "is_active": True,
    }
}


# Initialize the admin password hash on first access
def _init_admin_hash():
    if USERS_DB["admin@example.com"]["password_hash"] == "$pbkdf2-sha256$29000$dummy$hash$placeholder":
        USERS_DB["admin@example.com"]["password_hash"] = hasher.hash("admin123")


# Call it once to initialize
_init_admin_hash()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password"""
    return hasher.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password using PBKDF2-SHA256"""
    return hasher.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """Get current user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        email: str = payload.get("email")
        role: str = payload.get("role", "user")

        if user_id is None or email is None:
            raise credentials_exception

        return {
            "id": int(user_id),
            "email": email,
            "role": role,
            "username": payload.get("username", email.split("@")[0]),
        }
    except JWTError:
        raise credentials_exception


@router.post("/token", response_model=Dict[str, Any])
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Login endpoint - returns access token
    """
    # Try to find user by email or username
    user = None
    for email, user_data in USERS_DB.items():
        if user_data["email"] == form_data.username or user_data["username"] == form_data.username:
            user = user_data
            break

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    if not verify_password(form_data.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": str(user["id"]),
            "email": user["email"],
            "username": user["username"],
            "role": user["role"],
        },
        expires_delta=access_token_expires,
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": {
            "id": user["id"],
            "email": user["email"],
            "username": user["username"],
            "role": user["role"],
        }
    }


@router.post("/register", response_model=Dict[str, Any])
async def register(email: str, password: str, username: Optional[str] = None):
    """
    Register a new user
    """
    # Check if user already exists
    if email in USERS_DB:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Create new user
    new_user = {
        "id": len(USERS_DB) + 1,
        "email": email,
        "username": username or email.split("@")[0],
        "password_hash": get_password_hash(password),
        "role": "user",
        "is_active": True,
    }
    USERS_DB[email] = new_user

    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": str(new_user["id"]),
            "email": new_user["email"],
            "username": new_user["username"],
            "role": new_user["role"],
        },
        expires_delta=access_token_expires,
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": new_user["id"],
            "email": new_user["email"],
            "username": new_user["username"],
            "role": new_user["role"],
        }
    }


@router.get("/me", response_model=Dict[str, Any])
async def get_me(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get current user information"""
    return {
        "id": current_user["id"],
        "email": current_user["email"],
        "username": current_user["username"],
        "role": current_user["role"],
    }


@router.get("/registration-status")
async def get_registration_status():
    """Get registration status"""
    return {
        "enabled": not settings.REGISTRATION_DISABLED,
        "disabled_detail": settings.REGISTRATION_DISABLED_DETAIL,
        "reopen_date": settings.REGISTRATION_REOPEN_DATE,
        "contact_email": settings.REGISTRATION_CONTACT_EMAIL
    }


__all__ = ["router"]