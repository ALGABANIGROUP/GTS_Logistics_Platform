"""
Authentication Routes - Login, Register, Token
"""

from fastapi import APIRouter, HTTPException, Depends, status, Body
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import datetime, timedelta
from typing import Optional
import importlib
import jwt
import bcrypt


def _import_attr(module_names: tuple[str, ...], attr_name: str):
    for module_name in module_names:
        try:
            module = importlib.import_module(module_name)
            return getattr(module, attr_name)
        except Exception:
            continue
    return None


if __name__.startswith("routes."):
    _db_modules = ("database.session", "backend.database.session")
    _config_modules = ("config", "backend.config")
else:
    _db_modules = ("backend.database.session", "database.session")
    _config_modules = ("backend.config", "config")

get_async_session = _import_attr(_db_modules, "get_async_session")
Settings = _import_attr(_config_modules, "Settings")

settings = Settings()

router = APIRouter(prefix="/auth", tags=["Authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


async def _fetch_user_by_login(session: AsyncSession, login: str) -> Optional[dict]:
    result = await session.execute(
        text(
            """
            SELECT
                id,
                email,
                username,
                role,
                is_active,
                created_at,
                hashed_password,
                token_version
            FROM users
            WHERE lower(email) = :login OR lower(username) = :login
            LIMIT 1
            """
        ),
        {"login": login.strip().lower()},
    )
    row = result.mappings().first()
    return dict(row) if row else None


async def _fetch_user_by_id(session: AsyncSession, user_id: int) -> Optional[dict]:
    result = await session.execute(
        text(
            """
            SELECT
                id,
                email,
                username,
                role,
                is_active,
                created_at,
                hashed_password,
                token_version
            FROM users
            WHERE id = :user_id
            LIMIT 1
            """
        ),
        {"user_id": user_id},
    )
    row = result.mappings().first()
    return dict(row) if row else None


async def get_current_user(token: str = Depends(oauth2_scheme), session: AsyncSession = Depends(get_async_session)):
    if get_async_session is None:
        raise HTTPException(status_code=500, detail="Database not available")

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    user = await _fetch_user_by_id(session, int(user_id))
    if user is None:
        raise credentials_exception
    return user


@router.post("/login")
async def login_json(
    credentials: dict = Body(...),
    session: AsyncSession = Depends(get_async_session)
):
    """Login endpoint - accepts JSON credentials"""
    if get_async_session is None:
        raise HTTPException(status_code=500, detail="Database not available")
    
    email = credentials.get("email")
    password = credentials.get("password")
    
    if not email or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email and password are required"
        )
    
    user = await _fetch_user_by_login(session, email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify password
    hashed_password = str(user.get("hashed_password") or "")
    if not hashed_password or not bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token = create_access_token(
        data={
            "sub": str(user["id"]),
            "email": user["email"],
            "role": user.get("role") or "user",
            "tv": int(user.get("token_version") or 0),
        }
    )

    # Create refresh token
    refresh_token = create_access_token(
        data={
            "sub": str(user["id"]),
            "type": "refresh",
            "tv": int(user.get("token_version") or 0),
        },
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


@router.post("/token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_async_session)
):
    """Login endpoint - returns access token"""
    if get_async_session is None:
        raise HTTPException(status_code=500, detail="Database not available")
    user = await _fetch_user_by_login(session, form_data.username)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify password
    hashed_password = str(user.get("hashed_password") or "")
    if not hashed_password or not bcrypt.checkpw(form_data.password.encode('utf-8'), hashed_password.encode('utf-8')):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token = create_access_token(
        data={
            "sub": str(user["id"]),
            "email": user["email"],
            "role": user.get("role") or "user",
            "tv": int(user.get("token_version") or 0),
        }
    )

    # Create refresh token
    refresh_token = create_access_token(
        data={
            "sub": str(user["id"]),
            "type": "refresh",
            "tv": int(user.get("token_version") or 0),
        },
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


@router.get("/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user info"""
    return {
        "id": current_user.get("id"),
        "email": current_user.get("email"),
        "username": current_user.get("username"),
        "role": current_user.get("role"),
        "is_active": current_user.get("is_active"),
        "created_at": current_user["created_at"].isoformat() if current_user.get("created_at") else None
    }


@router.post("/refresh")
async def refresh_token(
    refresh_token: Optional[str] = Body(default=None, embed=True),
    session: AsyncSession = Depends(get_async_session),
):
    """Refresh access token"""
    try:
        if not refresh_token:
            raise HTTPException(status_code=400, detail="refresh_token is required")

        payload = jwt.decode(refresh_token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid refresh token type")
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")

        user = await _fetch_user_by_id(session, int(user_id))
        if not user:
            raise HTTPException(status_code=401, detail="User not found")

        new_access_token = create_access_token(
            data={
                "sub": str(user["id"]),
                "email": user["email"],
                "role": user.get("role") or "user",
                "tv": int(user.get("token_version") or 0),
            }
        )

        return {
            "access_token": new_access_token,
            "token_type": "bearer"
        }

    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
