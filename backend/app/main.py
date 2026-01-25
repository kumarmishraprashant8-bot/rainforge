from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.api_v1.api import api_router

app = FastAPI(
    title="RainForge API",
    description="Backend API for RainForge Rainwater Harvesting Platform",
    version="0.1.0"
)

# CORS Configuration - Allow all origins for demo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Welcome to RainForge API", "status": "active"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
