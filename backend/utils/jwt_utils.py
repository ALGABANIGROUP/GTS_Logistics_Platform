# backend/auth/jwt_utils.py
import os
import jwt
from fastapi import HTTPException, status

JWT_SECRET = os.getenv("JWT_SECRET", "change-this-to-32-byte-secure-key-for-jwt!!")
JWT_ALG = os.getenv("JWT_ALG", "HS256")

def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
