"""Maintenance Mode Middleware"""
import logging
from typing import Callable

from fastapi import Request, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from backend.security.auth import _decode_token

logger = logging.getLogger(__name__)

class MaintenanceModeMiddleware(BaseHTTPMiddleware):
    """Middleware to check if system is in maintenance mode"""
    
    # Paths that are allowed even in maintenance mode
    ALLOWED_PATHS = [
        "/api/v1/auth/token",
        "/api/v1/platform-settings/branding",
        "/healthz",
        "/health",
        "/docs",
        "/openapi.json",
        "/api/v1/admin/platform-settings"  # Admin can access settings to disable maintenance
    ]
    
    async def dispatch(self, request: Request, call_next: Callable):
        # Skip check for allowed paths
        if any(request.url.path.startswith(path) for path in self.ALLOWED_PATHS):
            return await call_next(request)
        
        # Check if maintenance mode is enabled
        try:
            from backend.utils.technical_settings import is_maintenance_mode
            
            if await is_maintenance_mode():
                # Check if user is admin (they can bypass maintenance mode)
                auth_header = request.headers.get("Authorization", "")
                if auth_header.startswith("Bearer "):
                    token = auth_header.replace("Bearer ", "", 1).strip()
                    if token:
                        try:
                            claims = _decode_token(token)
                            role = str(
                                claims.get("effective_role")
                                or claims.get("role")
                                or ""
                            ).strip().lower()
                            if role in {"admin", "super_admin", "owner", "system_admin"}:
                                return await call_next(request)
                        except Exception as exc:
                            logger.debug("Maintenance auth bypass rejected: %s", exc)
                
                return JSONResponse(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    content={
                        "error": "Service Unavailable",
                        "detail": "System is currently under maintenance. Please try again later.",
                        "maintenance": True
                    }
                )
        except Exception as e:
            logger.warning(f"Failed to check maintenance mode: {e}")
        
        return await call_next(request)
