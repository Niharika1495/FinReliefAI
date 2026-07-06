import time
import psutil
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models.admin import Admin
from app.models.user import User
from app.models.loan import Loan
from app.models.ai_history import AIHistory
from app.auth.password import verify_password
from app.auth.jwt import create_access_token
from app.utils.exceptions import FinReliefException
from fastapi import status

class AdminService:
    """
    Service layer providing administrative authentication 
    and system status dashboard metrics gathering.
    """

    @staticmethod
    def authenticate_admin(db: Session, username: str, password: str) -> str:
        """
        Authenticates an administrator and returns a signed JWT token.
        """
        admin = db.query(Admin).filter(Admin.username == username).first()
        if not admin or not verify_password(password, admin.password_hash):
            raise FinReliefException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                error_code="INVALID_CREDENTIALS",
                message="Invalid administrator username or password."
            )
        
        token = create_access_token(data={"sub": admin.username, "role": "admin"})
        return token

    @staticmethod
    def get_dashboard_metrics(db: Session) -> dict:
        """
        Compiles users metrics, active liabilities, AI usage stats,
        and system metrics like CPU/Memory/Disk and DB latency.
        """
        total_users = db.query(User).count()
        total_loans = db.query(Loan).filter(Loan.is_active == True).count()
        total_ai_queries = db.query(AIHistory).count()
        
        t0 = time.perf_counter()
        try:
            db.execute(text("SELECT 1"))
            db_latency = (time.perf_counter() - t0) * 1000.0
        except Exception:
            db_latency = -1.0
            
        try:
            cpu = psutil.cpu_percent(interval=None)
            mem = psutil.virtual_memory().percent
            disk = psutil.disk_usage('/').percent
        except Exception:
            cpu, mem, disk = 0.0, 0.0, 0.0
            
        return {
            "total_users": total_users,
            "total_active_loans": total_loans,
            "total_ai_queries": total_ai_queries,
            "system_health": {
                "cpu_usage_percent": cpu,
                "memory_usage_percent": mem,
                "disk_usage_percent": disk,
                "db_latency_ms": db_latency
            }
        }
