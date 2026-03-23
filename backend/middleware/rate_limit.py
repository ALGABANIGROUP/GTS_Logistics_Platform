"""
Rate limiting middleware for FastAPI
Enforces per-IP and per-tenant rate limits
"""

import logging
import time
from datetime import datetime, timedelta
from typing import Dict, Tuple
from collections import defaultdict

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)


class RateLimitStore:
    """In-memory rate limit store (use Redis for production)"""
    
    def __init__(self):
        self.requests: Dict[str, list] = defaultdict(list)  # key -> [timestamp, timestamp, ...]
        self.cleanup_interval = 300  # Clean old entries every 5 minutes
        self.last_cleanup = time.time()
    
    def _cleanup(self):
        """Remove old entries (> 1 hour old)"""
        now = time.time()
        if now - self.last_cleanup < self.cleanup_interval:
            return
        
        cutoff = now - 3600  # 1 hour
        for key in list(self.requests.keys()):
            self.requests[key] = [ts for ts in self.requests[key] if ts > cutoff]
            if not self.requests[key]:
                del self.requests[key]
        
        self.last_cleanup = now
    
    def check_limit(self, key: str, limit: int, window_seconds: int) -> Tuple[bool, int]:
        """
        Check if key is within rate limit
        
        Returns:
            (is_allowed, requests_remaining)
        """
        self._cleanup()
        
        now = time.time()
        cutoff = now - window_seconds
        
        # Remove old requests
        requests = [ts for ts in self.requests[key] if ts > cutoff]
        self.requests[key] = requests
        
        is_allowed = len(requests) < limit
        remaining = max(0, limit - len(requests) - 1)
        
        if is_allowed:
            self.requests[key].append(now)
        
        return is_allowed, remaining


# Global rate limit store
rate_limit_store = RateLimitStore()

# Default limits (can be customized)
DEFAULT_LIMITS = {
    "/api/v1/signup/register": (3, 86400),  # 3 per day per IP
    "/api/v1/commands/human": (60, 60),  # 60 per minute per tenant
    "default": (100, 60),  # 100 per minute per IP (default)
}


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware"""
    
    def __init__(self, app, limits: Dict = None, requests_per_minute: int = 100):
        super().__init__(app)
        self.limits = limits or DEFAULT_LIMITS
        self.default_limit = (requests_per_minute, 60)
    
    async def dispatch(self, request: Request, call_next):
        """Check rate limit before processing request"""
        
        # Skip rate limiting for health checks and public endpoints
        if request.url.path in ["/health", "/docs", "/openapi.json"]:
            return await call_next(request)
        
        # Get rate limit for this endpoint
        endpoint = request.url.path
        limit_info = self.limits.get(endpoint, self.default_limit)
        limit, window = limit_info if isinstance(limit_info, tuple) else self.default_limit
        
        # Determine rate limit key
        if "/api/v1/signup/" in endpoint:
            # Rate limit by IP
            key = f"ip:{self._get_client_ip(request)}"
        elif "/api/v1/commands/" in endpoint:
            # Rate limit by tenant
            try:
                tenant_id = request.headers.get("X-Tenant-ID") or "default"
                key = f"tenant:{tenant_id}"
            except:
                key = f"ip:{self._get_client_ip(request)}"
        else:
            # Default: rate limit by IP
            key = f"ip:{self._get_client_ip(request)}"
        
        # Check rate limit
        is_allowed, remaining = rate_limit_store.check_limit(key, limit, window)
        
        if not is_allowed:
            logger.warning(f"Rate limit exceeded for {key} on {endpoint}")
            return JSONResponse(
                status_code=429,
                content={
                    "error": "rate_limit_exceeded",
                    "message": f"Rate limit exceeded ({limit} requests per {window} seconds)"
                },
                headers={
                    "X-RateLimit-Limit": str(limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Window": str(window),
                }
            )
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Window"] = str(window)
        
        return response
    
    @staticmethod
    def _get_client_ip(request: Request) -> str:
        """Get client IP, handling proxies"""
        if forwarded := request.headers.get("x-forwarded-for"):
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"
