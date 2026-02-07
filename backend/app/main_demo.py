"""
RainForge Demo Application
Main FastAPI application with all demo endpoints
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.models.database import init_db, SessionLocal
from app.api.api_v1.endpoints.demo_api import router as demo_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    print("🌧️ RainForge Demo Starting...")
    init_db()
    
    # Seed data if database is empty
    from app.seed_data import seed_demo_data
    db = SessionLocal()
    try:
        seed_demo_data(db)
    finally:
        db.close()
    
    print("✅ RainForge Demo Ready!")
    print("📍 API Docs: http://localhost:8000/docs")
    print("📍 Health: http://localhost:8000/api/v1/health")
    
    yield
    
    # Shutdown
    print("👋 RainForge Demo Shutting Down...")


app = FastAPI(
    title="RainForge API",
    description="""
    🌧️ **RainForge** - Complete Rooftop Rainwater Harvesting Platform
    
    ## Features
    - **Assessment**: Instant RWH assessment with 3 scenarios
    - **PDF Generation**: Engineer-signed reports with QR verification
    - **Auction**: Reverse auction for installer bidding
    - **Allocation**: Smart installer allocation (RPI-weighted)
    - **Escrow**: Milestone-based payment release
    - **Verification**: Fraud-resistant geo-verified photo uploads
    - **Monitoring**: Real-time IoT telemetry dashboard
    - **Public Dashboard**: Ward-level transparency reporting
    
    ## Demo Data
    - 6 seeded installers with varied RPI scores
    - 10 state subsidy rules
    - Sample telemetry data
    - Ward boundaries
    
    ## Authentication
    Demo mode - no authentication required.
    Production would use JWT Bearer tokens.
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Demo: allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files for uploads and PDFs
os.makedirs("uploads", exist_ok=True)
os.makedirs("generated_pdfs", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.mount("/pdfs", StaticFiles(directory="generated_pdfs"), name="pdfs")

# API routes
app.include_router(demo_router, prefix="/api/v1")

# Include existing routers if available
try:
    from app.api.api_v1.endpoints.complete_assessment import router as assessment_router
    app.include_router(assessment_router, prefix="/api/v1/assess", tags=["Assessment Extended"])
except ImportError:
    pass

try:
    from app.api.api_v1.endpoints.bulk import router as bulk_router
    app.include_router(bulk_router, prefix="/api/v1/bulk", tags=["Bulk Processing"])
except ImportError:
    pass

try:
    from app.api.api_v1.endpoints.success import router as success_router
    app.include_router(success_router, prefix="/api/v1", tags=["Success features"])
except ImportError:
    pass


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with welcome message."""
    return {
        "message": "🌧️ Welcome to RainForge API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/health",
        "demo": True
    }


@app.get("/api/v1/info", tags=["System"])
async def get_info():
    """Get system information."""
    return {
        "name": "RainForge",
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "demo"),
        "database": "sqlite" if "sqlite" in os.getenv("DATABASE_URL", "sqlite") else "postgres",
        "features": [
            "assessment",
            "pdf_generation",
            "auction",
            "allocation",
            "escrow",
            "verification",
            "fraud_detection",
            "monitoring",
            "public_dashboard"
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main_demo:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=True
    )
