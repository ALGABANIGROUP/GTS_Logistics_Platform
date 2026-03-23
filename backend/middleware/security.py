"""
Phase 5 Security Middleware
- HTTPS enforcement
- Security headers
- CORS configuration
- Rate limiting
"""

from fastapi import Request, HTTPException
from fastapi.responses import RedirectResponse, Response
from starlette.middleware.base import BaseHTTPMiddleware
from backend.config import settings
import logging
from datetime import datetime

log = logging.getLogger("gts.security")


class HTTPSRedirectMiddleware(BaseHTTPMiddleware):
    """
    Redirect HTTP to HTTPS in production
    Preserve x-forwarded-proto from load balancers
    """
    
    async def dispatch(self, request: Request, call_next):
        # Check if we should redirect to HTTPS
        should_redirect = (
            not settings.DEBUG and
            request.url.scheme == "http" and
            request.headers.get("x-forwarded-proto") != "https"
        )
        
        if should_redirect:
            # Redirect to HTTPS
            https_url = request.url.replace(scheme="https")
            log.warning(f"Redirecting HTTP request to HTTPS: {request.url.path}")
            return RedirectResponse(url=https_url, status_code=301)
        
        response = await call_next(request)
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Add security headers to all responses
    """
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Strict Transport Security (HSTS)
        # Tell browsers to always use HTTPS for this domain
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
        
        # Content Security Policy (CSP)
        # Prevent XSS attacks by controlling where resources can load from
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "img-src 'self' data: https:; "
            "font-src 'self' https://fonts.googleapis.com; "
            "connect-src 'self' https://api.sentry.io; "
            "frame-ancestors 'none';"
        )
        
        # X-Content-Type-Options
        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # X-Frame-Options
        # Prevent clickjacking attacks
        response.headers["X-Frame-Options"] = "DENY"
        
        # X-XSS-Protection
        # Enable browser XSS protection
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Referrer-Policy
        # Control what referrer information is sent
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Permissions-Policy (formerly Feature-Policy)
        # Control which browser features can be used
        response.headers["Permissions-Policy"] = (
            "geolocation=(), "
            "microphone=(), "
            "camera=(), "
            "payment=(), "
            "clipboard-read=(), "
            "clipboard-write=()"
        )
        
        # Remove server header (security through obscurity)
        if "server" in response.headers:
            del response.headers["server"]
        
        return response


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Add request ID to all requests for tracing
    """
    
    async def dispatch(self, request: Request, call_next):
        import uuid
        
        # Get or create request ID
        request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
        request.state.request_id = request_id
        
        response = await call_next(request)
        
        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id
        
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Basic rate limiting middleware
    """
    
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests = {}  # {ip: [(timestamp, count), ...]}
    
    async def dispatch(self, request: Request, call_next):
        if not settings.DEBUG:
            # Get client IP
            client_ip = request.client.host if request.client else "unknown"
            
            # Get current minute
            current_minute = datetime.now().strftime("%Y-%m-%d %H:%M")
            key = f"{client_ip}:{current_minute}"
            
            # Track requests
            if key not in self.requests:
                self.requests[key] = 0
            
            self.requests[key] += 1
            
            # Check rate limit
            if self.requests[key] > self.requests_per_minute:
                log.warning(f"Rate limit exceeded for {client_ip}: {self.requests[key]} requests/minute")
                raise HTTPException(
                    status_code=429,
                    detail="Too many requests. Please try again later."
                )
            
            # Clean old entries (older than 2 minutes)
            import time
            cutoff_time = datetime.now().timestamp() - 120
            expired_keys = [
                k for k, v in self.requests.items()
                if datetime.strptime(k.split(":")[1], "%Y-%m-%d %H:%M").timestamp() < cutoff_time
            ]
            for k in expired_keys:
                del self.requests[k]
        
        response = await call_next(request)
        return response


class AuditLoggingMiddleware(BaseHTTPMiddleware):
    """
    Log all requests and responses for audit trail
    """
    
    async def dispatch(self, request: Request, call_next):
        # Log request
        log.info(
            f"Request: {request.method} {request.url.path} "
            f"from {request.client.host if request.client else 'unknown'}"
        )
        
        response = await call_next(request)
        
        # Log response
        log.info(
            f"Response: {response.status_code} for {request.url.path} "
            f"(Request ID: {request.state.request_id})"
        )
        
        return response


def setup_security_middleware(app):
    """
    Register all security middlewares
    Order matters: execute from bottom to top (reverse registration order)
    """
    # 1. Audit logging (outermost - logs everything)
    app.add_middleware(AuditLoggingMiddleware)
    
    # 2. Rate limiting
    app.add_middleware(RateLimitMiddleware, requests_per_minute=settings.RATE_LIMIT_REQUESTS_PER_MINUTE)
    
    # 3. Request ID tracking
    app.add_middleware(RequestIDMiddleware)
    
    # 4. Security headers
    app.add_middleware(SecurityHeadersMiddleware)
    
    # 5. HTTPS redirect (innermost - redirect before other processing)
    app.add_middleware(HTTPSRedirectMiddleware)
    
    log.info("✅ Security middleware setup completed")
