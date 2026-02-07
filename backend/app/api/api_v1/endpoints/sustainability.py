"""
Sustainability API Endpoints
Water Credits and CSR Integration.
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

from app.services.water_credits_service import get_water_credits_service
from app.services.csr_integration import get_csr_integration_service

router = APIRouter(prefix="/sustainability", tags=["Sustainability"])


# ==================== SCHEMAS ====================

class IssueCreditRequest(BaseModel):
    user_id: str
    project_id: str
    water_saved_liters: float

class ListCreditRequest(BaseModel):
    credit_id: str
    user_id: str
    price_per_unit: float

class BuyCreditRequest(BaseModel):
    order_id: str
    buyer_id: str

class RetireCreditRequest(BaseModel):
    credit_id: str
    user_id: str
    reason: str = ""

class CSRCampaignRequest(BaseModel):
    corporate_id: str
    corporate_name: str
    title: str
    description: str
    target_projects: int
    target_amount: float

class CSRDonationRequest(BaseModel):
    campaign_id: str
    corporate_id: str
    amount: float

class CSRImpactUpdateRequest(BaseModel):
    campaign_id: str
    projects_completed: int
    beneficiaries: int
    water_saved: float
    co2_offset: float


# ==================== WATER CREDITS ====================

@router.post("/water-credits/issue")
async def issue_water_credits(request: IssueCreditRequest):
    """Issue water credits based on verified savings."""
    service = get_water_credits_service()
    return await service.issue_credits(
        request.user_id, request.project_id, request.water_saved_liters
    )

@router.post("/water-credits/list")
async def list_credits_for_sale(request: ListCreditRequest):
    """List water credits for sale."""
    service = get_water_credits_service()
    return await service.list_for_sale(
        request.credit_id, request.user_id, request.price_per_unit
    )

@router.post("/water-credits/buy")
async def buy_water_credits(request: BuyCreditRequest):
    """Purchase water credits."""
    service = get_water_credits_service()
    return await service.buy_credits(request.order_id, request.buyer_id)

@router.post("/water-credits/retire")
async def retire_water_credits(request: RetireCreditRequest):
    """Retire credits for compliance certification."""
    service = get_water_credits_service()
    return await service.retire_credits(
        request.credit_id, request.user_id, request.reason
    )

@router.get("/water-credits/marketplace")
async def get_marketplace_listings(min_units: float = 0, max_price: float = 1000):
    """Get water credits marketplace listings."""
    service = get_water_credits_service()
    return await service.get_marketplace_listings(min_units, max_price)

@router.get("/water-credits/portfolio/{user_id}")
async def get_water_credit_portfolio(user_id: str):
    """Get user's water credit portfolio."""
    service = get_water_credits_service()
    return await service.get_user_portfolio(user_id)


# ==================== CSR ====================

@router.post("/csr/campaigns")
async def create_csr_campaign(request: CSRCampaignRequest):
    """Create a CSR campaign."""
    service = get_csr_integration_service()
    return await service.create_campaign(
        request.corporate_id, request.corporate_name,
        request.title, request.description,
        request.target_projects, request.target_amount
    )

@router.post("/csr/donate")
async def make_csr_donation(request: CSRDonationRequest):
    """Make a donation to a CSR campaign."""
    service = get_csr_integration_service()
    return await service.make_donation(
        request.campaign_id, request.corporate_id, request.amount
    )

@router.post("/csr/impact")
async def update_csr_impact(request: CSRImpactUpdateRequest):
    """Update campaign impact metrics."""
    service = get_csr_integration_service()
    return await service.update_impact(
        request.campaign_id, request.projects_completed,
        request.beneficiaries, request.water_saved, request.co2_offset
    )

@router.get("/csr/campaigns/{campaign_id}")
async def get_csr_dashboard(campaign_id: str):
    """Get CSR campaign dashboard."""
    service = get_csr_integration_service()
    return await service.get_campaign_dashboard(campaign_id)

@router.get("/csr/campaigns")
async def get_public_campaigns():
    """Get public CSR campaigns."""
    service = get_csr_integration_service()
    return await service.get_public_campaigns()

@router.get("/csr/report/{campaign_id}")
async def get_impact_report(campaign_id: str):
    """Generate impact report for a campaign."""
    service = get_csr_integration_service()
    return await service.generate_impact_report(campaign_id)
