from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from starlette.status import HTTP_401_UNAUTHORIZED
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.models.user import User
from backend.database.config import get_db
from backend.core.settings import settings
import os
DEFAULT_SECRET_KEY = 'dev-secret-change-me'
JWT_SECRET_KEY = settings.JWT_SECRET_KEY or settings.SECRET_KEY or os.getenv('JWT_SECRET_KEY', DEFAULT_SECRET_KEY)
JWT_ALGORITHM = 'HS256'

class JWTBearer(HTTPBearer):

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials:
        credentials = await super().__call__(request)
        if credentials is None or credentials.scheme.lower() != 'bearer':
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail='Invalid authentication scheme.')
        return credentials

async def get_current_user(token: str=Depends(JWTBearer()), db: AsyncSession=Depends(get_db)) -> User:
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_id_raw = payload.get('sub')
        if user_id_raw is None:
            raise HTTPException(status_code=401, detail='Token missing subject (sub)')
        user_id = int(user_id_raw)
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if user is None:
            raise HTTPException(status_code=404, detail='User not found')
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail='Invalid token')
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail='Token validation failed')
