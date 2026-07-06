from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from app.core.logger import logger
from app.core.settings import settings

class GlobalErrorMiddleware(BaseHTTPMiddleware):
    """
    Middleware serving as the outermost safety net to intercept any unexpected,
    unhandled exceptions occurring during request execution.
    Logs standard tracebacks and structures standard error response payloads.
    """
    async def dispatch(self, request: Request, call_next) -> JSONResponse:
        try:
            return await call_next(request)
        except Exception as exc:
            # Audit trace log
            logger.error(
                f"Unhandled Exception in request pipeline: {type(exc).__name__}: {str(exc)}",
                exc_info=True
            )
            
            # Get Correlation ID if set
            request_id = getattr(request.state, "request_id", "N/A")
            
            content = {
                "success": False,
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected server error occurred.",
                    "request_id": request_id
                }
            }
            
            # Expose stack details if running under local DEBUG mode
            if settings.DEBUG:
                content["error"]["debug_message"] = str(exc)
                content["error"]["debug_type"] = type(exc).__name__
                
            return JSONResponse(
                status_code=500,
                content=content
            )
