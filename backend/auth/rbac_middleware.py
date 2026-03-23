from __future__ import annotations

from typing import Any, Callable, Dict, Iterable

from fastapi import Depends, HTTPException, status

from backend.security.auth import get_current_user


def _user_is_global(user: Dict[str, Any]) -> bool:
    perms = set(
        (user.get("permissions") or [])
        if isinstance(user.get("permissions"), list)
        else []
    )
    role = str(user.get("role") or "").strip()
    roles = set(
        (user.get("roles") or [])
        if isinstance(user.get("roles"), list)
        else []
    )
    return (
        "system.full_access" in perms
        or "*" in perms
        or role in ("super_admin", "owner")
        or bool({"super_admin", "owner"} & roles)
    )


def require_permission(permission: str) -> Callable[..., Any]:
    async def _dep(user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
        if _user_is_global(user):
            return user
        perms = set(
            (user.get("permissions") or [])
            if isinstance(user.get("permissions"), list)
            else []
        )
        if permission not in perms:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: Permission '{permission}' required",
            )
        return user

    return _dep


def require_any_permission(permissions: Iterable[str]) -> Callable[..., Any]:
    wanted = [p for p in (permissions or []) if p]

    async def _dep(user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
        if _user_is_global(user):
            return user
        perms = set(
            (user.get("permissions") or [])
            if isinstance(user.get("permissions"), list)
            else []
        )
        if not any(p in perms for p in wanted):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Missing required permission",
            )
        return user

    return _dep


def require_roles(roles: Iterable[str]) -> Callable[..., Any]:
    wanted = {str(r).strip().lower() for r in (roles or []) if r}

    async def _dep(user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
        if _user_is_global(user):
            return user
        role = str(user.get("role") or "").strip().lower()
        user_roles = {str(r).strip().lower() for r in (user.get("roles") or []) if r}
        if role not in wanted and not (user_roles & wanted):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
        return user

    return _dep


__all__ = [
    "require_permission",
    "require_any_permission",
    "require_roles",
]
