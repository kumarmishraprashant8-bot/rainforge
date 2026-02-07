"""
India Stack API Endpoints
Aadhaar eKYC, DigiLocker, and PFMS DBT integration.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from app.services.aadhaar_digilocker_service import get_aadhaar_digilocker_service
from app.services.pfms_dbt_service import get_pfms_dbt_service

router = APIRouter(prefix="/india-stack", tags=["India Stack"])


# ==================== SCHEMAS ====================

class AadhaarOTPRequest(BaseModel):
    aadhaar_number: str
    user_id: str

class AadhaarVerifyRequest(BaseModel):
    txn_id: str
    otp: str

class DigiLockerAuthRequest(BaseModel):
    user_id: str
    redirect_uri: str

class BeneficiaryRegisterRequest(BaseModel):
    user_id: str
    aadhaar_masked: str
    name: str
    account_number: str
    ifsc_code: str
    branch_name: Optional[str] = None

class DBTPaymentRequest(BaseModel):
    beneficiary_id: str
    scheme: str
    amount: float
    purpose: str
    project_id: Optional[str] = None

class SubsidyCheckRequest(BaseModel):
    user_id: str
    project_cost: float
    property_type: str = "residential"
    city_tier: str = "tier_2"


# ==================== AADHAAR ====================

@router.post("/aadhaar/send-otp")
async def send_aadhaar_otp(request: AadhaarOTPRequest):
    """Send OTP to Aadhaar-linked mobile."""
    service = get_aadhaar_digilocker_service()
    return await service.send_aadhaar_otp(request.aadhaar_number, request.user_id)

@router.post("/aadhaar/verify-otp")
async def verify_aadhaar_otp(request: AadhaarVerifyRequest):
    """Verify OTP and get eKYC profile."""
    service = get_aadhaar_digilocker_service()
    return await service.verify_aadhaar_otp(request.txn_id, request.otp)

@router.get("/aadhaar/status/{user_id}")
async def get_verification_status(user_id: str):
    """Get user's verification status."""
    service = get_aadhaar_digilocker_service()
    return service.get_user_verification_status(user_id)


# ==================== DIGILOCKER ====================

@router.post("/digilocker/auth")
async def initiate_digilocker(request: DigiLockerAuthRequest):
    """Initiate DigiLocker OAuth flow."""
    service = get_aadhaar_digilocker_service()
    return await service.initiate_digilocker_auth(request.user_id, request.redirect_uri)

@router.post("/digilocker/callback")
async def digilocker_callback(code: str, state: str):
    """Handle DigiLocker OAuth callback."""
    service = get_aadhaar_digilocker_service()
    return await service.complete_digilocker_auth(code, state)

@router.get("/digilocker/documents/{user_id}")
async def get_digilocker_documents(user_id: str):
    """Fetch user's DigiLocker documents."""
    service = get_aadhaar_digilocker_service()
    return await service.fetch_digilocker_documents(user_id)

@router.get("/digilocker/extract/{user_id}")
async def extract_property_data(user_id: str):
    """Extract property data from DigiLocker documents."""
    service = get_aadhaar_digilocker_service()
    return await service.extract_property_data(user_id)


# ==================== PFMS DBT ====================

@router.post("/dbt/register")
async def register_beneficiary(request: BeneficiaryRegisterRequest):
    """Register DBT beneficiary."""
    service = get_pfms_dbt_service()
    return await service.register_beneficiary(
        request.user_id, request.aadhaar_masked, request.name,
        {"account_number": request.account_number, "ifsc_code": request.ifsc_code,
         "branch_name": request.branch_name}
    )

@router.post("/dbt/check-eligibility")
async def check_subsidy_eligibility(request: SubsidyCheckRequest):
    """Check subsidy eligibility across schemes."""
    service = get_pfms_dbt_service()
    return await service.check_subsidy_eligibility(
        request.user_id, request.project_cost, request.property_type, request.city_tier
    )

@router.post("/dbt/initiate")
async def initiate_dbt_payment(request: DBTPaymentRequest):
    """Initiate DBT payment."""
    service = get_pfms_dbt_service()
    from app.services.pfms_dbt_service import SubsidyScheme
    return await service.initiate_dbt_payment(
        request.beneficiary_id, SubsidyScheme(request.scheme),
        request.amount, request.purpose, request.project_id
    )

@router.get("/dbt/status/{transaction_id}")
async def get_dbt_status(transaction_id: str):
    """Check DBT payment status."""
    service = get_pfms_dbt_service()
    return await service.check_payment_status(transaction_id)

@router.get("/dbt/transactions/{user_id}")
async def get_user_transactions(user_id: str, limit: int = 20):
    """Get user's DBT transactions."""
    service = get_pfms_dbt_service()
    return await service.get_user_transactions(user_id, limit)
