from fastapi import APIRouter
from app.api.api_v1.endpoints import (
    assessments, bulk, monitoring, verification, policy,
    allocation, payments, verification_api, public
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
