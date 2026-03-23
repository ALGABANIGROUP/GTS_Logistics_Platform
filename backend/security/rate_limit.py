# backend/security/rate_limit.py
from __future__ import annotations

from typing import Callable

from fastapi import FastAPI, Request, Response
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

# Global limiter instance used across the app
limiter: Limiter = Limiter(key_func=get_remote_address)


def rate_limit_handler(request: Request, exc: Exception) -> Response:
    """
    Wrapper around SlowAPI's _rate_limit_exceeded_handler
    with a signature compatible with FastAPI's ExceptionHandler type.
    """
    if isinstance(exc, RateLimitExceeded):
        return _rate_limit_exceeded_handler(request, exc)
    # Fallback: re-raise if it's not a RateLimitExceeded (should not normally happen)
    raise exc


def init_rate_limiter(app: FastAPI) -> None:
    """
    Initialize SlowAPI rate limiting for the FastAPI app.

    Usage in main.py (example):
        from backend.security.rate_limit import init_rate_limiter

        app = FastAPI()

        @app.on_event("startup")
        async def startup():
            init_rate_limiter(app)
    """
    # Attach limiter to app state so SlowAPI can inject headers
    app.state.limiter = limiter

    # Register the RateLimitExceeded handler via our wrapper
    app.add_exception_handler(RateLimitExceeded, rate_limit_handler)


def rate_limit(limit: str) -> Callable:
    """
    Convenience wrapper so you can write:

        from backend.security.rate_limit import rate_limit

        @router.get("/some-endpoint")
        @rate_limit("5/minute")
        async def some_endpoint(...):
            ...

    """
    return limiter.limit(limit)
