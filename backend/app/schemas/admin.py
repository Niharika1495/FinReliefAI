from pydantic import BaseModel
from typing import Dict, Any

class AdminLoginRequest(BaseModel):
    username: str
    password: str

class AdminTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class SystemHealth(BaseModel):
    cpu_usage_percent: float
    memory_usage_percent: float
    disk_usage_percent: float
    db_latency_ms: float

class AdminDashboardMetrics(BaseModel):
    total_users: int
    total_active_loans: int
    total_ai_queries: int
    system_health: SystemHealth
