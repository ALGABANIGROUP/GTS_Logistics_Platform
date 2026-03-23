"""
Max Upload Size Middleware for FastAPI.
Enforces max upload size from platform technical settings.
"""

import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from starlette.requests import Request

log = logging.getLogger("gts.middleware.max_upload_size")


class MaxUploadSizeMiddleware(BaseHTTPMiddleware):
    """
    Middleware to enforce maximum upload size from database settings.
    Checks Content-Length header against maxUploadSize from platform_settings.
    """
    
    async def dispatch(self, request: Request, call_next):
        # Only check for requests with body (POST, PUT, PATCH)
        if request.method not in ("POST", "PUT", "PATCH"):
            return await call_next(request)
        
        # Get max upload size from technical settings
        try:
            from backend.utils.technical_settings import get_max_upload_size_mb
            max_size_mb = await get_max_upload_size_mb()
            max_size_bytes = max_size_mb * 1024 * 1024  # Convert MB to bytes
        except Exception as e:
            log.error(f"Failed to get max upload size: {e}")
            # Default to 10MB if unable to fetch
            max_size_bytes = 10 * 1024 * 1024
        
        # Check Content-Length header
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                content_length_bytes = int(content_length)
                if content_length_bytes > max_size_bytes:
                    return JSONResponse(
                        status_code=413,
                        content={
                            "error": "Request entity too large",
                            "detail": f"Upload size ({content_length_bytes / (1024*1024):.2f} MB) exceeds maximum allowed size ({max_size_mb} MB)",
                            "max_upload_mb": max_size_mb
                        }
                    )
            except ValueError:
                log.warning(f"Invalid Content-Length header: {content_length}")
        
        return await call_next(request)
