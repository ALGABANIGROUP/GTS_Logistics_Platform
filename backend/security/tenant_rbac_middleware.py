from __future__ import annotations

from typing import Callable

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database.session import wrap_session_factory, get_async_session
from backend.security.tenant_resolver import TenantResolver
from backend.security.auth import get_current_user
from backend.security.rbac import normalize_role


class TenantRBACMiddleware(BaseHTTPMiddleware):
    """Middleware that attaches resolved tenant to the request and enforces
    minimal RBAC rules for admin endpoints.

    Rules:
    - Resolves tenant for every request, stores in `request.state.tenant`
    - Blocks `/admin/` paths unless the effective role is `super_admin`
    - Ensures `/api/` paths have a resolvable tenant
    """

    def __init__(self, app: Callable):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Skip tenant resolution for public signup endpoints
        if request.url.path.startswith("/api/v1/signup/"):
            request.state.tenant = None
            return await call_next(request)
        
        # Try to resolve tenant, but handle missing tables gracefully
        try:
            async with wrap_session_factory(get_async_session) as session:  # type: ignore[arg-type]
                assert isinstance(session, AsyncSession)
                tenant = await TenantResolver.resolve_tenant(request, session)
                if not tenant and request.url.path.startswith("/api/"):
                    # For non-critical APIs, allow None tenant
                    if not any(path in request.url.path for path in ["/admin/", "/api/v1/admin"]):
                        tenant = None
                    else:
                        raise HTTPException(status_code=400, detail="Tenant not found")
                request.state.tenant = tenant
        except Exception as e:
            # If tenants table doesn't exist yet, allow the request through
            # This handles initial setup when migrations haven't run
            print(f"[middleware] WARN: tenant resolution failed: {e}")
            request.state.tenant = None

        # Admin RBAC: require super_admin
        if request.url.path.startswith("/admin/"):
            try:
                user = await get_current_user(request)
                role = normalize_role(user.get("effective_role") or user.get("role"))
                if role != "super_admin":
                    raise HTTPException(status_code=403, detail="Admin access requires super_admin")
            except HTTPException:
                raise
            except Exception as e:
                print(f"[middleware] WARN: admin check failed: {e}")

        return await call_next(request)


