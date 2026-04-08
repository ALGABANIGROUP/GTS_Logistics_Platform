# backend/middleware/upload.py
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import os

class MaxUploadSizeMiddleware(BaseHTTPMiddleware):
    """Middleware to limit upload file size"""

    def __init__(self, app, max_upload_size: int = 50 * 1024 * 1024):  # 50MB default
        super().__init__(app)
        self.max_upload_size = max_upload_size

    async def dispatch(self, request: Request, call_next):
        # Only check upload endpoints
        upload_paths = ['/upload', '/uploads', '/api/v1/uploads', '/documents/upload']

        if any(request.url.path.startswith(path) for path in upload_paths):
            content_length = request.headers.get('content-length')

            if content_length and int(content_length) > self.max_upload_size:
                return Response(
                    content=f'{{"error":"File too large","max_size":{self.max_upload_size}}}',
                    status_code=413,
                    media_type='application/json'
                )

        return await call_next(request)