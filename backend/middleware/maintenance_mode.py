# backend/middleware/maintenance.py
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Optional
import os

class MaintenanceModeMiddleware(BaseHTTPMiddleware):
    """Middleware to handle maintenance mode"""

    def __init__(self, app, maintenance_mode: bool = False):
        super().__init__(app)
        self.maintenance_mode = maintenance_mode or os.getenv('MAINTENANCE_MODE', 'false').lower() == 'true'
        self.allowed_ips = os.getenv('MAINTENANCE_ALLOWED_IPS', '').split(',')
        self.admin_paths = ['/admin', '/api/v1/admin', '/healthz', '/readiness']

    async def dispatch(self, request: Request, call_next):
        # Skip maintenance check for admin paths and health checks
        if any(request.url.path.startswith(path) for path in self.admin_paths):
            return await call_next(request)

        # Skip for allowed IPs
        client_ip = request.client.host if request.client else None
        if client_ip and client_ip in self.allowed_ips:
            return await call_next(request)

        # Check maintenance mode
        if self.maintenance_mode:
            return Response(
                content='{"status":"maintenance","message":"System is under maintenance. Please try again later."}',
                status_code=503,
                media_type='application/json'
            )

        return await call_next(request)