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
import ipaddress
import re

log = logging.getLogger("gts.security")


class HTTPSRedirectMiddleware(BaseHTTPMiddleware):
    """
    Redirect HTTP to HTTPS in production
    Preserve x-forwarded-proto from load balancers
    """

    @staticmethod
    def _is_local_host(hostname: str | None) -> bool:
        if not hostname:
            return False

        normalized = hostname.strip().lower()
        if normalized in {"localhost", "127.0.0.1", "::1"}:
            return True

        try:
            return ipaddress.ip_address(normalized).is_loopback
        except ValueError:
            return normalized.endswith(".local")

    async def dispatch(self, request: Request, call_next):
        forwarded_host = request.headers.get("x-forwarded-host", "")
        host = request.url.hostname or ""
        effective_host = (forwarded_host.split(",")[0].strip() or host)

        # Check if we should redirect to HTTPS
        should_redirect = (
            getattr(settings, "ENFORCE_HTTPS", False) and
            not settings.DEBUG and
            request.url.scheme == "http" and
            request.headers.get("x-forwarded-proto") != "https" and
            not self._is_local_host(effective_host)
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
        forwarded_proto = request.headers.get("x-forwarded-proto", "")
        is_https = request.url.scheme == "https" or forwarded_proto == "https"
        if getattr(settings, "ENFORCE_HTTPS", False) and is_https:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
        
        # Content Security Policy (CSP)
        # Prevent XSS attacks by controlling where resources can load from
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "img-src 'self' data: https: http:; "
            "font-src 'self' https://fonts.googleapis.com; "
            "connect-src 'self' https://api.sentry.io http: https: ws: wss:; "
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
            expired_keys = []
            for k in list(self.requests.keys()):
                try:
                    timestamp_str = k.split(":")[1] if ":" in k else ""
                    if timestamp_str:
                        # Handle both formats: with and without minutes
                        if len(timestamp_str.split()) == 2 and len(timestamp_str.split()[1].split(":")) == 1:
                            # Format is "2026-04-08 21" - add :00 for minutes
                            timestamp_str += ":00"
                        parsed_time = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M").timestamp()
                        if parsed_time < cutoff_time:
                            expired_keys.append(k)
                except (ValueError, IndexError):
                    # If parsing fails, consider it expired
                    expired_keys.append(k)
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


class SecurityMiddleware(BaseHTTPMiddleware):
    """Priority 1 security middleware"""

    async def dispatch(self, request: Request, call_next):
        # Add security headers
        response = await call_next(request)

        # Security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'

        # CSP header (adjust for your needs)
        if not request.url.path.startswith('/admin'):
            response.headers['Content-Security-Policy'] = "default-src 'self'"

        # SQL Injection detection (basic)
        if self._has_sql_injection_pattern(request):
            return Response(
                content='{"error":"Invalid request pattern"}',
                status_code=400,
                media_type='application/json'
            )

        return response

    def _has_sql_injection_pattern(self, request: Request) -> bool:
        """Basic SQL injection pattern detection"""
        sql_patterns = [
            r"(\%27)|(\')|(\-\-)|(\%23)|(#)",
            r"((\%3D)|(=))[^\n]*((\%27)|(\')|(\-\-)|(\%3B)|(;))",
            r"\w*((\%27)|(\'))((\%6F)|o|(\%4F))((\%72)|r|(\%52))",
            r"((\%27)|(\'))union",
            r"exec(\s|\+)+(s|x)p\w+",
        ]

        # Check query parameters
        for param in request.query_params.values():
            for pattern in sql_patterns:
                if re.search(pattern, str(param), re.IGNORECASE):
                    return True

        return False
