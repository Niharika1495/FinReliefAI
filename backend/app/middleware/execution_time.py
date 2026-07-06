import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

class ExecutionTimeMiddleware(BaseHTTPMiddleware):
    """
    Middleware that measures the processing duration of incoming HTTP requests
    and appends the duration in the 'X-Process-Time' header of the response.
    """
    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.perf_counter()
        
        response: Response = await call_next(request)
        
        process_time = time.perf_counter() - start_time
        # Attach processing time in seconds to the response headers
        response.headers["X-Process-Time"] = f"{process_time:.6f}s"
        
        return response
