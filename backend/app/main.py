from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.core.logger import setup_logging, logger
from app.core.settings import settings
from app.api.v1.api import api_router
from app.middleware import (
    RequestIdMiddleware,
    RequestLoggerMiddleware,
    ExecutionTimeMiddleware,
    GlobalErrorMiddleware,
    RateLimitMiddleware,
    AuditMiddleware,
)
from app.utils.exceptions import FinReliefException
from app.utils.response_utils import error_response
from app.services.scheduler_service import start_scheduler, shutdown_scheduler

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles application startup and shutdown events.
    Initializes logging structures and database tables.
    """
    # Startup Hook
    setup_logging()
    logger.info(f"Starting {settings.APP_NAME} server...")
    logger.info(f"Version: {settings.VERSION} | Environment Settings Loaded Successfully")
    
    # Database initialization
    try:
        from app.database.session import Base, engine
        import app.models  # Registers all tables to Base.metadata
        logger.info("Auto-creating database tables (SQLite)...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables initialized successfully.")
    except Exception as db_err:
        logger.error(f"Database initialization failed: {str(db_err)}", exc_info=True)
        raise db_err

    # Start APScheduler tasks
    try:
        start_scheduler()
    except Exception as sched_err:
        logger.error(f"Scheduler startup failed: {str(sched_err)}", exc_info=True)
        
    yield
    # Shutdown Hook
    try:
        shutdown_scheduler()
    except Exception as sched_err:
        logger.error(f"Scheduler shutdown failed: {str(sched_err)}", exc_info=True)
    logger.info(f"Shutting down {settings.APP_NAME} server...")

# Initialize core FastAPI instance
app = FastAPI(
    title=settings.APP_NAME,
    description="AI Powered Debt Relief & Financial Recovery Platform - Backend Foundation",
    version=settings.VERSION,
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# Exception Handlers configuration
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Captures validation errors (422) and formats them into a clean JSON response.
    """
    # Format and detail error message
    error_details = []
    for err in exc.errors():
        loc = " -> ".join(str(x) for x in err.get("loc", []))
        msg = err.get("msg", "Validation failed")
        error_details.append(f"{loc}: {msg}")
    
    joined_message = " | ".join(error_details)
    request_id = getattr(request.state, "request_id", "N/A")
    
    logger.warning(f"Request Validation Failed on {request.method} {request.url.path}: {joined_message}")
    
    return error_response(
        code="VALIDATION_FAILED",
        message=f"Request verification failed: {joined_message}",
        status_code=422,
        request_id=request_id
    )

@app.exception_handler(FinReliefException)
async def finrelief_exception_handler(request: Request, exc: FinReliefException):
    """
    Captures custom domain-level exceptions and formats them into standard JSON envelopes.
    """
    request_id = getattr(request.state, "request_id", "N/A")
    logger.warning(f"Domain Exception: {exc.message} | Code: {exc.code} | Status: {exc.status_code}")
    
    return error_response(
        code=exc.code,
        message=exc.message,
        status_code=exc.status_code,
        request_id=request_id
    )

# Middleware Stack registration (Executed in reverse order of addition)
# 1. Compress responses
app.add_middleware(GZipMiddleware, minimum_size=1000)

# 2. CORS configurations
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Restrict host domains to prevent HTTP Host Header attacks
# For local dev we allow all hosts. Can be parameterized in settings.
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])

# 4. Process duration timer
app.add_middleware(ExecutionTimeMiddleware)

# 5. API auditing logger
app.add_middleware(RequestLoggerMiddleware)

# 5.5 Audit middleware for mutations
app.add_middleware(AuditMiddleware)

# 6. Request correlation ID generator
app.add_middleware(RequestIdMiddleware)

# 6.5 Rate Limit middleware (100 req/min)
app.add_middleware(RateLimitMiddleware, requests_limit=100, window_seconds=60)

# 7. Outermost unhandled exception boundary
app.add_middleware(GlobalErrorMiddleware)

# Security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer-when-downgrade"
    return response

# Register Version 1 Router under /api/v1 prefix
app.include_router(api_router, prefix="/api/v1")

# Bind root routes at base level as well for easy health checks and monitoring
@app.get("/", summary="Root Status Endpoint")
async def root_redirect() -> dict:
    """
    Serves absolute root path for load balancers.
    """
    return {
        "message": "FinRelief AI Backend Running"
    }

@app.get("/health", summary="Service Health Endpoint")
async def health_check() -> dict:
    """
    Serves absolute health check route.
    """
    return {
        "status": "healthy",
        "version": settings.VERSION
    }
