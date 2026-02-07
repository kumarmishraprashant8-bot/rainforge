"""
Financial Services API Endpoints
Credit, Insurance, and Subsidy management.
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List

from app.services.credit_service import get_credit_service
from app.services.insurance_service import get_insurance_service

router = APIRouter(prefix="/finance", tags=["Financial Services"])


# ==================== SCHEMAS ====================

class EligibilityCheckRequest(BaseModel):
    user_id: str
    requested_amount: float
    monthly_income: float = 50000

class LoanApplicationRequest(BaseModel):
    user_id: str
    partner: str
    amount: float
    tenure_months: int
    purpose: str = "RWH Installation"

class InsuranceQuoteRequest(BaseModel):
    project_id: str
    coverage_amount: float

class InsurancePurchaseRequest(BaseModel):
    user_id: str
    project_id: str
    insurance_type: str
    coverage: float

class ClaimRequest(BaseModel):
    policy_id: str
    claim_type: str
    amount: float
    description: str


# ==================== CREDIT ====================

@router.post("/credit/check-eligibility")
async def check_loan_eligibility(request: EligibilityCheckRequest):
    """Check loan eligibility across NBFC partners."""
    service = get_credit_service()
    return await service.check_eligibility(
        request.user_id, request.requested_amount, request.monthly_income
    )

@router.post("/credit/apply")
async def apply_for_loan(request: LoanApplicationRequest):
    """Submit loan application."""
    service = get_credit_service()
    return await service.apply_for_loan(
        request.user_id, request.partner, request.amount,
        request.tenure_months, request.purpose
    )

@router.get("/credit/dashboard/{user_id}")
async def get_loan_dashboard(user_id: str):
    """Get user's loan dashboard."""
    service = get_credit_service()
    return await service.get_loan_dashboard(user_id)


# ==================== INSURANCE ====================

@router.post("/insurance/quotes")
async def get_insurance_quotes(request: InsuranceQuoteRequest):
    """Get insurance quotes for a project."""
    service = get_insurance_service()
    return await service.get_quotes(request.project_id, request.coverage_amount)

@router.post("/insurance/purchase")
async def purchase_insurance(request: InsurancePurchaseRequest):
    """Purchase insurance policy."""
    service = get_insurance_service()
    return await service.purchase_policy(
        request.user_id, request.project_id,
        request.insurance_type, request.coverage
    )

@router.post("/insurance/claim")
async def file_claim(request: ClaimRequest):
    """File an insurance claim."""
    service = get_insurance_service()
    return await service.file_claim(
        request.policy_id, request.claim_type,
        request.amount, request.description
    )

@router.post("/insurance/weather-trigger")
async def check_weather_trigger(
    project_id: str,
    actual_rainfall_mm: float,
    expected_rainfall_mm: float
):
    """Check if weather parametric trigger is met."""
    service = get_insurance_service()
    return await service.check_weather_trigger(
        project_id, actual_rainfall_mm, expected_rainfall_mm
    )
