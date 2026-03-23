"""
Scope-based dependency injection for authorization
Provides scope requirements for API endpoints
"""

from fastapi import HTTPException, Depends
from typing import List, Optional
from backend.security.auth import get_current_user


def require_scope(required_scope: str):
    """
    Dependency to require specific scope for an endpoint
    
    Usage:
        @router.get("/endpoint", dependencies=[require_scope("resource:read")])
        async def my_endpoint():
            ...
    """
    async def _check_scope(user = Depends(get_current_user)):
        if not user:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        # Extract scopes from user
        user_scopes = getattr(user, 'scopes', []) if hasattr(user, 'scopes') else []
        if isinstance(user, dict):
            user_scopes = user.get('scopes', [])
        
        # Check if user has required scope
        if required_scope not in user_scopes and '*' not in user_scopes:
            # Fallback: check role-based access
            role = _get_user_role(user)
            if not _has_role_access(role, required_scope):
                raise HTTPException(
                    status_code=403,
                    detail=f"Insufficient permissions: required scope '{required_scope}'"
                )
        
        return user
    
    return _check_scope


def require_scopes(required_scopes: List[str]):
    """
    Dependency to require any of multiple scopes
    """
    async def _check_scopes(user = Depends(get_current_user)):
        if not user:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        # Extract scopes from user
        user_scopes = getattr(user, 'scopes', []) if hasattr(user, 'scopes') else []
        if isinstance(user, dict):
            user_scopes = user.get('scopes', [])
        
        # Check if user has any required scope
        has_scope = any(s in user_scopes for s in required_scopes)
        if not has_scope and '*' not in user_scopes:
            # Fallback: check role-based access
            role = _get_user_role(user)
            has_role = any(_has_role_access(role, s) for s in required_scopes)
            if not has_role:
                raise HTTPException(
                    status_code=403,
                    detail=f"Insufficient permissions: required one of {required_scopes}"
                )
        
        return user
    
    return _check_scopes


def _get_user_role(user) -> str:
    """Extract role from user object or dict"""
    if isinstance(user, dict):
        return user.get('role', user.get('user_type', 'user')).lower()
    
    role = getattr(user, 'role', getattr(user, 'user_type', 'user'))
    return (role or 'user').lower()


def _has_role_access(role: str, required_scope: str) -> bool:
    """
    Check if role has access to required scope
    This is a fallback role-based access control
    """
    role = role.lower()
    
    # Admin has access to everything
    if role in ('admin', 'system', 'superuser'):
        return True
    
    # Parse scope format: "resource:action"
    resource, _, action = required_scope.partition(':')
    resource = resource.lower()
    action = action.lower()
    
    # Role-based scope mappings
    role_scope_map = {
        'admin': ['*'],
        'system': ['*'],
        'superuser': ['*'],
        'manager': [
            'users:read',
            'users:write',
            'reports:read',
            'reports:write',
            'bots:read',
            'teams:read',
            'teams:write',
        ],
        'user': [
            'profile:read',
            'profile:write',
            'bots:read',
            'reports:read',
        ],
        'guest': [
            'profile:read',
            'reports:read',
        ],
    }
    
    allowed_scopes = role_scope_map.get(role, [])
    
    # Check exact match or wildcard
    if '*' in allowed_scopes:
        return True
    
    if required_scope in allowed_scopes:
        return True
    
    # Check resource:* pattern
    if f'{resource}:*' in allowed_scopes:
        return True
    
    return False
