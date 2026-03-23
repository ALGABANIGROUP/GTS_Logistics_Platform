"""
Security Headers Middleware for GTS Platform
Implements security best practices and hardening
"""
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import logging
from typing import Callable
import os

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Add security headers to all responses
    Implements OWASP security best practices
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.is_production = os.getenv("APP_ENV", "development").lower() == "production"
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Security Headers (OWASP Recommendations)
        
        # 1. Strict-Transport-Security (HSTS)
        # Force HTTPS for 1 year, include subdomains
        if self.is_production:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
        
        # 2. X-Content-Type-Options
        # Prevent MIME-sniffing attacks
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # 3. X-Frame-Options
        # Prevent clickjacking attacks
        response.headers["X-Frame-Options"] = "DENY"
        
        # 4. X-XSS-Protection
        # Enable XSS filtering (legacy support)
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # 5. Content-Security-Policy (CSP)
        # Prevent XSS, injection attacks
        csp_policy = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://unpkg.com https://js.stripe.com https://hcaptcha.com https://*.hcaptcha.com; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.jsdelivr.net; "
            "font-src 'self' https://fonts.gstatic.com data:; "
            "img-src 'self' data: https: blob:; "
            "connect-src 'self' http: https: ws: wss: https://api.stripe.com https://hcaptcha.com https://*.hcaptcha.com; "
            "frame-src 'self' https://hcaptcha.com https://*.hcaptcha.com https://js.stripe.com; "
            "object-src 'none'; "
            "base-uri 'self'; "
            "form-action 'self'; "
            "frame-ancestors 'none'; "
            "upgrade-insecure-requests;"
        )
        response.headers["Content-Security-Policy"] = csp_policy
        
        # 6. Referrer-Policy
        # Control referrer information
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # 7. Permissions-Policy (formerly Feature-Policy)
        # Restrict browser features
        permissions = (
            "geolocation=(), "
            "microphone=(), "
            "camera=(), "
            "payment=(self), "
            "usb=(), "
            "magnetometer=(), "
            "accelerometer=(), "
            "gyroscope=()"
        )
        response.headers["Permissions-Policy"] = permissions
        
        # 8. Remove server identification headers
        if "Server" in response.headers:
            del response.headers["Server"]
        if "X-Powered-By" in response.headers:
            del response.headers["X-Powered-By"]
        
        # 9. Cache control for sensitive endpoints
        if any(path in request.url.path for path in ["/auth/", "/api/v1/admin/", "/api/v1/user/"]):
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, private"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
        
        return response


class HTTPSRedirectMiddleware(BaseHTTPMiddleware):
    """
    Redirect HTTP to HTTPS in production
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.is_production = os.getenv("APP_ENV", "development").lower() == "production"
        self.enforce_https = os.getenv("ENFORCE_HTTPS", "true").lower() == "true"
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Only redirect in production
        if self.is_production and self.enforce_https:
            # Check if request is HTTP
            if request.url.scheme == "http":
                # Build HTTPS URL
                https_url = request.url.replace(scheme="https")
                logger.warning(f"Redirecting HTTP to HTTPS: {request.url} -> {https_url}")
                return JSONResponse(
                    status_code=301,
                    content={"detail": "Redirecting to HTTPS"},
                    headers={"Location": str(https_url)}
                )
        
        return await call_next(request)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Simple in-memory rate limiting
    For production, use Redis-based rate limiting
    """
    
    def __init__(self, app: ASGIApp, requests_per_minute: int = 120):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.request_counts = {}  # IP -> (count, timestamp)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/api/v1/health", "/api/v1/monitoring/health"]:
            return await call_next(request)
        
        # Check rate limit (simple implementation)
        # TODO: Replace with Redis-based rate limiting in production
        import time
        current_time = int(time.time())
        
        if client_ip in self.request_counts:
            count, timestamp = self.request_counts[client_ip]
            
            # Reset counter if minute has passed
            if current_time - timestamp >= 60:
                self.request_counts[client_ip] = (1, current_time)
            else:
                # Increment counter
                count += 1
                self.request_counts[client_ip] = (count, timestamp)
                
                # Check if limit exceeded
                if count > self.requests_per_minute:
                    logger.warning(f"Rate limit exceeded for IP: {client_ip}")
                    return JSONResponse(
                        status_code=429,
                        content={
                            "detail": "Too many requests. Please try again later.",
                            "retry_after": 60 - (current_time - timestamp)
                        },
                        headers={"Retry-After": str(60 - (current_time - timestamp))}
                    )
        else:
            self.request_counts[client_ip] = (1, current_time)
        
        # Clean up old entries periodically
        if len(self.request_counts) > 10000:
            # Remove entries older than 2 minutes
            self.request_counts = {
                ip: (count, ts) 
                for ip, (count, ts) in self.request_counts.items() 
                if current_time - ts < 120
            }
        
        return await call_next(request)
