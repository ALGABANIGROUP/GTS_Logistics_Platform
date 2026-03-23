import datetime
from typing import Optional

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.config import settings  # type: ignore[import]
from backend.database.config import get_db_async  # type: ignore[import]
from backend.models.user import User  # type: ignore[import]
from backend.schemas.token import Token  # type: ignore[import]
from backend.schemas.user import UserCreate  # type: ignore[import]
