from fastapi import APIRouter
from app.api.api_v1.endpoints import (
    assessments, bulk, monitoring, verification, policy,
    allocation, payments, verification_api, public, auth, features,
    advanced, utils, complete_assessment, community, carbon_nft,
    devices, enhanced_features, success,
    # Unbeatable Platform Features
    india_stack, copilot, finance, academy, sustainability
)

api_router = APIRouter()


# Status endpoint
@api_router.get("/status")
def status():
    return {
        "status": "ok", 
        "version": "v3.0", 
        "platform": "Government Marketplace Edition",
        "features": [
            "smart_allocation",
            "competitive_bidding", 
            "rpi_scoring",
            "escrow_payments",
            "fraud_detection",
            "outcome_contracts"
        ]
    }

# Health check for Docker/Kubernetes
@api_router.get("/health")
def health():
    return {"status": "healthy", "version": "3.0.0"}

# Core Assessment Routes
api_router.include_router(assessments.router, prefix="/assessments", tags=["assessments"])
api_router.include_router(bulk.router, prefix="/bulk", tags=["bulk"])
api_router.include_router(monitoring.router, prefix="/monitoring", tags=["monitoring"])
api_router.include_router(verification.router, prefix="/verification", tags=["verification"])
api_router.include_router(policy.router, prefix="/policy", tags=["policy"])

# Marketplace Routes (NEW)
api_router.include_router(allocation.router, prefix="/marketplace", tags=["marketplace", "allocation", "bidding"])
api_router.include_router(payments.router, prefix="/payments", tags=["payments", "escrow"])
api_router.include_router(verification_api.router, prefix="/verify", tags=["verification", "fraud"])
api_router.include_router(public.router, prefix="/public", tags=["public", "dashboard", "amc"])

# Authentication Routes
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])

# Advanced Features Routes (NEW - Beast Mode)
api_router.include_router(features.router, prefix="/features", tags=["weather", "carbon", "government", "satellite", "notifications"])

# God Mode Advanced Features (FULL UPGRADE)
api_router.include_router(advanced.router, tags=["advanced", "forecasting", "analytics", "sso", "lorawan", "chatbot"])

# Free Utility Features (PDF, QR, Export, Import, Health, Gamification)
api_router.include_router(utils.router, tags=["utilities", "pdf", "qr", "export", "health", "gamification"])

# Complete Assessment (All Inputs/Outputs)
api_router.include_router(complete_assessment.router, prefix="/assessment", tags=["complete-assessment", "materials", "subsidies", "compliance"])

# Community Features (Water Sharing, Maintenance, Satellite, Notifications)
api_router.include_router(community.router, tags=["community", "water-sharing", "maintenance", "satellite", "notifications"])

# Carbon NFT Marketplace
# IoT Device Provisioning
api_router.include_router(devices.router, prefix="/devices", tags=["iot", "devices", "provisioning"])

# Enhanced Features (Full Government-Grade RWH Platform)
api_router.include_router(
    enhanced_features.router, 
    prefix="/enhanced", 
    tags=["user-profile", "compliance", "marketplace", "performance", "quality", "iot-enhanced"]
)

# Success features (Water Security Index, leaderboard, crisis, badges, impact)
api_router.include_router(success.router, tags=["success", "engagement", "gamification"])

# ==================== UNBEATABLE PLATFORM FEATURES ====================

# India Stack Integration (Aadhaar, DigiLocker, PFMS DBT)
api_router.include_router(india_stack.router, tags=["india-stack", "aadhaar", "digilocker", "dbt"])

# AI Copilot (GPT-4 powered assistant)
api_router.include_router(copilot.router, tags=["ai", "copilot", "nlp"])

# Financial Services (Microloans, Insurance)
api_router.include_router(finance.router, tags=["finance", "credit", "insurance"])

# Installer Academy (Training & Certifications)
api_router.include_router(academy.router, tags=["academy", "training", "certification"])

# Sustainability Ecosystem (Water Credits, CSR)
api_router.include_router(sustainability.router, tags=["sustainability", "water-credits", "csr"])
