import logging
import sys
from contextvars import ContextVar
from app.core.settings import settings

# Thread-safe ContextVar to store the current request's unique ID
request_id_var: ContextVar[str] = ContextVar("request_id", default="N/A")

# Log output format: includes Timestamp, Level, Module Logger Name, request_id context, and the Message
LOG_FORMAT = "%(asctime)s - %(levelname)s - [%(name)s] - [RequestID: %(request_id)s] - %(message)s"

class RequestIdFilter(logging.Filter):
    """
    A filter that injects the active thread-local request correlation ID
    from request_id_var into all log records automatically.
    """
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_var.get("N/A")
        return True

def setup_logging() -> None:
    """
    Configures application-wide logging with handlers, formatters, and filters.
    Sets standard levels based on DEBUG parameters and suppresses excessive library noise.
    """
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO

    # Configure the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Clear pre-existing handlers to prevent duplicated logs
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Configure stdout stream handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    
    # Formatter mapping
    formatter = logging.Formatter(LOG_FORMAT)
    console_handler.setFormatter(formatter)
    
    # Register filter
    console_handler.addFilter(RequestIdFilter())
    
    root_logger.addHandler(console_handler)

    # Configure logs levels for external packages to reduce noise
    logging.getLogger("uvicorn.access").disabled = True
    logging.getLogger("uvicorn.error").setLevel(logging.WARNING)

# Expose package-wide default logger
logger = logging.getLogger("finrelief_ai")
