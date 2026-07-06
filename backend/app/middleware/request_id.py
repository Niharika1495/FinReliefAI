import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from app.core.logger import request_id_var

class RequestIdMiddleware(BaseHTTPMiddleware):
    """
    Middleware that assigns a unique UUID to every incoming HTTP request.
    It registers the ID to a ContextVar for logger interpolation, and appends
    the 'X-Request-ID' header to the response.
    """
    async def dispatch(self, request: Request, call_next) -> Response:
        # Check if client provided a correlation ID, else generate one
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        
        # Bind request_id to context variable
        token = request_id_var.set(request_id)
        
        # Attach request_id to request state for routes to access
        request.state.request_id = request_id
        
        try:
            response: Response = await call_next(request)
            # Add correlation ID to response headers
            response.headers["X-Request-ID"] = request_id
            return response
        finally:
            # Safely reset context variable token
            request_id_var.reset(token)
