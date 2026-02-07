"""RainForge API - Main Application Entry Point."""
import logging
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.api.api_v1.api import api_router
from app.core.config import settings
from app.core.middleware import (
    SecurityHeadersMiddleware,
    RateLimitMiddleware,
    RequestLoggingMiddleware
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    logger.info("🌧️ RainForge API starting up...")
    
    # Start MQTT Worker
    from app.worker.mqtt_ingest import get_mqtt_worker
    worker = get_mqtt_worker()
    worker.start()
    
    logger.info(f"Debug mode: {settings.DEBUG}")
    logger.info(f"Allowed origins: {settings.ALLOWED_ORIGINS}")
    
    yield
    
    logger.info("🌧️ RainForge API shutting down...")
    worker.stop()


app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,  # Disable docs in prod
    redoc_url="/redoc" if settings.DEBUG else None,
)

# ============== MIDDLEWARE (order matters - last added = first executed) ==============

# 1. Request logging (outermost)
app.add_middleware(RequestLoggingMiddleware)

# 2. Rate limiting
app.add_middleware(RateLimitMiddleware, requests_per_minute=settings.RATE_LIMIT_PER_MINUTE)

# 3. Security headers
app.add_middleware(SecurityHeadersMiddleware)

# 4. CORS - Production hardened configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=[
        "Authorization",
        "Content-Type",
        "X-Requested-With",
        "X-Device-ID",
        "X-Request-ID",
    ],
    expose_headers=[
        "X-Process-Time",
        "X-Request-ID",
    ],
    max_age=600,  # Cache preflight for 10 minutes
)

# ============== ROUTES ==============

# Include API v1 router
app.include_router(api_router, prefix="/api/v1")


@app.get("/", tags=["Health"])
async def root():
    """Root endpoint - API info."""
    return {
        "name": settings.API_TITLE,
        "version": settings.API_VERSION,
        "status": "active",
        "message": "Welcome to RainForge API - Government-grade Rainwater Harvesting Platform"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for load balancers and monitoring."""
    import redis
    from app.core.config import settings
    
    checks = {"api": "ok"}
    overall_status = "healthy"
    
    # Check Redis connectivity
    try:
        r = redis.from_url(settings.REDIS_URL, socket_connect_timeout=2)
        r.ping()
        checks["redis"] = "ok"
    except Exception as e:
        checks["redis"] = f"error: {str(e)[:50]}"
        overall_status = "degraded"
    
    # Check database connectivity (mock for demo, replace with real check in prod)
    try:
        # In production, uncomment and use:
        # from sqlalchemy import create_engine, text
        # engine = create_engine(settings.DATABASE_URL)
        # with engine.connect() as conn:
        #     conn.execute(text("SELECT 1"))
        checks["database"] = "ok (mock)"
    except Exception as e:
        checks["database"] = f"error: {str(e)[:50]}"
        overall_status = "degraded"
    
    return {
        "status": overall_status,
        "version": settings.API_VERSION,
        "timestamp": datetime.utcnow().isoformat(),
        "checks": checks
    }


@app.get("/ready", tags=["Health"])
async def readiness_check():
    """Readiness check for Kubernetes."""
    from app.core.config import settings
    
    # In production, verify all critical services are ready
    ready = True
    details = {
        "api": True,
        "config_loaded": bool(settings.SECRET_KEY),
    }
    
    return {
        "status": "ready" if ready else "not_ready",
        "details": details
    }

