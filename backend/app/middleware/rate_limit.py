import time
from fastapi import status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    In-memory rate limiter applying IP-based limits (default: 100 requests per minute).
    """
    def __init__(self, app, requests_limit: int = 100, window_seconds: int = 60):
        super().__init__(app)
        self.requests_limit = requests_limit
        self.window_seconds = window_seconds
        self.ip_records = {}

    async def dispatch(self, request: Request, call_next) -> Response:
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        
        if client_ip not in self.ip_records:
            self.ip_records[client_ip] = []
            
        timestamps = self.ip_records[client_ip]
        
        # Evict expired timestamps
        cutoff = now - self.window_seconds
        self.ip_records[client_ip] = [ts for ts in timestamps if ts > cutoff]
        
        # Validate limit
        if len(self.ip_records[client_ip]) >= self.requests_limit:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "status": "error",
                    "code": "RATE_LIMIT_EXCEEDED",
                    "message": "Too many requests. Please slow down and try again later."
                }
            )
            
        self.ip_records[client_ip].append(now)
        
        response = await call_next(request)
        return response
