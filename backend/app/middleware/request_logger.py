import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from app.core.logger import logger

class RequestLoggerMiddleware(BaseHTTPMiddleware):
    """
    Middleware that records audit logs for all incoming HTTP requests
    and outgoing HTTP responses, including HTTP methods, paths, status codes,
    client host IPs, and processing durations.
    """
    async def dispatch(self, request: Request, call_next) -> Response:
        client_ip = request.client.host if request.client else "unknown"
        path = request.url.path
        if request.url.query:
            path = f"{path}?{request.url.query}"

        logger.info(f"Incoming: {request.method} {path} | Client IP: {client_ip}")
        
        start_time = time.perf_counter()
        try:
            response: Response = await call_next(request)
            process_time = time.perf_counter() - start_time
            
            # Log info or warning depending on status code
            log_msg = f"Outgoing: {request.method} {request.url.path} | Status: {response.status_code} | Duration: {process_time:.4f}s"
            if response.status_code >= 400:
                logger.warning(log_msg)
            else:
                logger.info(log_msg)
                
            return response
        except Exception as e:
            process_time = time.perf_counter() - start_time
            logger.error(
                f"Failure: {request.method} {request.url.path} | Exception: {type(e).__name__}: {str(e)} | Duration: {process_time:.4f}s",
                exc_info=True
            )
            raise e
