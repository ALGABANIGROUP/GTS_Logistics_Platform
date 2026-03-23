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

def get_current_user(user: AuthUser = Depends(verify_token)) -> AuthUser:
    return user

def require_roles(*required: Role):
    def wrapper(user: AuthUser = Depends(verify_token)):
        if not any(r in user.roles for r in required):
            raise HTTPException(status_code=403, detail="Forbidden")
        return user
    return wrapper
