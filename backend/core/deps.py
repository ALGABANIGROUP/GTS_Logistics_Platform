"""
Lightweight dependency shims for FastAPI with safe editor fallback.

- Re-exports: get_current_user, require_roles, Role, AuthUser
- Provides a minimal Depends() stub if FastAPI is not installed,
  so static analyzers/linters don't explode outside runtime.
"""

from .security import verify_token as get_current_user, require_roles
from .security import Role, AuthUser

try:
    from fastapi import Depends  # real Depends at runtime
except Exception:
    # Fallback stub for environments where FastAPI is not installed (e.g., editors/linters).
    # This lets imports succeed during type-checking or static analysis.
    def Depends(dep=None):  # type: ignore
        return dep

__all__ = [
    "get_current_user",
    "require_roles",
    "Role",
    "AuthUser",
    "Depends",
]
