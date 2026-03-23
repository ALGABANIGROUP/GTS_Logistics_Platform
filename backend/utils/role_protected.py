from __future__ import annotations

from typing import Any, Callable, List, Dict

from fastapi import Depends, HTTPException, status

from backend.security.auth import get_current_user


def RoleChecker(allowed_roles: List[str]) -> Callable:
    def role_dependency(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
        role = str(current_user.get("effective_role") or current_user.get("role") or "").strip()
        if not role or role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this resource",
            )
        return current_user

    return role_dependency
