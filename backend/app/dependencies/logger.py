import logging
from app.core.logger import logger

def get_logger() -> logging.Logger:
    """
    Dependency injection provider returning the preconfigured application logger
    for runtime auditing in services and controllers.
    """
    return logger
