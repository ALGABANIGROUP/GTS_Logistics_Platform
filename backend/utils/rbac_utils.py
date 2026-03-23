from fastapi import Depends, HTTPException, status
from typing import List
from backend.utils.auth_utils import get_current_user
from backend.utils.roles import ROLES

def require_roles(allowed_roles: List[str]):

    async def role_checker(user=Depends(get_current_user)):
        if user.role not in allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Access denied')
        return user
    return Depends(role_checker)