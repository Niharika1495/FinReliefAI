from app.dependencies.db import get_db
from app.dependencies.settings import get_settings
from app.dependencies.logger import get_logger
from app.dependencies.auth import get_current_user
from app.dependencies.admin_auth import get_current_admin

__all__ = [
    "get_db",
    "get_settings",
    "get_logger",
    "get_current_user",
    "get_current_admin",
]
