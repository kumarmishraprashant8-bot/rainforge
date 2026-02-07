"""
CSR Integration Hub
Corporate Social Responsibility integration for sponsored RWH projects.
"""

import logging
import uuid
from datetime import datetime
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class CSRCampaign:
    campaign_id: str
    corporate_id: str
    corporate_name: str
    title: str
    description: str
    target_projects: int
    target_amount: float
    funded_amount: float = 0
    projects_completed: int = 0
    beneficiaries: int = 0
    water_saved_liters: float = 0
    co2_offset_kg: float = 0
    start_date: datetime = field(default_factory=datetime.now)
    status: str = "active"
    
    def to_dict(self) -> Dict:
        return {
            "campaign_id": self.campaign_id,
            "corporate_name": self.corporate_name,
            "title": self.title,
            "target_projects": self.target_projects,
            "target_amount": self.target_amount,
            "funded_amount": self.funded_amount,
            "projects_completed": self.projects_completed,
            "beneficiaries": self.beneficiaries,
            "water_saved_liters": self.water_saved_liters,
            "co2_offset_kg": self.co2_offset_kg,
            "progress_percent": (self.projects_completed / self.target_projects * 100) if self.target_projects > 0 else 0,
            "status": self.status
        }


@dataclass
class CSRDonation:
    donation_id: str
    campaign_id: str
    corporate_id: str
    amount: float
    donation_date: datetime
    receipt_number: str
    tax_certificate_url: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            "donation_id": self.donation_id,
            "amount": self.amount,
            "date": self.donation_date.isoformat(),
            "receipt_number": self.receipt_number,
            "tax_certificate": self.tax_certificate_url
        }


class CSRIntegrationService:
    """CSR Hub for corporate-sponsored RWH projects."""
    
    def __init__(self):
        self._campaigns: Dict[str, CSRCampaign] = {}
        self._donations: Dict[str, CSRDonation] = {}
        self._corporate_campaigns: Dict[str, List[str]] = {}
        
        logger.info("🏢 CSR Integration Service initialized")
    
    async def create_campaign(self, corporate_id: str, corporate_name: str,
                             title: str, description: str,
                             target_projects: int, target_amount: float) -> Dict[str, Any]:
        campaign_id = f"CSR-{uuid.uuid4().hex[:10].upper()}"
        
        campaign = CSRCampaign(
            campaign_id=campaign_id,
            corporate_id=corporate_id,
            corporate_name=corporate_name,
            title=title,
            description=description,
            target_projects=target_projects,
            target_amount=target_amount
        )
        
        self._campaigns[campaign_id] = campaign
        self._corporate_campaigns.setdefault(corporate_id, []).append(campaign_id)
        
        return {"success": True, "campaign": campaign.to_dict()}
    
    async def make_donation(self, campaign_id: str, corporate_id: str,
                           amount: float) -> Dict[str, Any]:
        campaign = self._campaigns.get(campaign_id)
        if not campaign:
            return {"success": False, "error": "Campaign not found"}
        
        donation_id = f"DON-{uuid.uuid4().hex[:10].upper()}"
        receipt = f"RCP-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        
        donation = CSRDonation(
            donation_id=donation_id,
            campaign_id=campaign_id,
            corporate_id=corporate_id,
            amount=amount,
            donation_date=datetime.now(),
            receipt_number=receipt,
            tax_certificate_url=f"/api/v1/csr/donations/{donation_id}/80g-certificate"
        )
        
        self._donations[donation_id] = donation
        campaign.funded_amount += amount
        
        return {
            "success": True,
            "donation": donation.to_dict(),
            "message": "Thank you for your contribution!"
        }
    
    async def update_impact(self, campaign_id: str, projects_completed: int,
                           beneficiaries: int, water_saved: float,
                           co2_offset: float) -> Dict[str, Any]:
        campaign = self._campaigns.get(campaign_id)
        if not campaign:
            return {"success": False, "error": "Campaign not found"}
        
        campaign.projects_completed = projects_completed
        campaign.beneficiaries = beneficiaries
        campaign.water_saved_liters = water_saved
        campaign.co2_offset_kg = co2_offset
        
        if projects_completed >= campaign.target_projects:
            campaign.status = "completed"
        
        return {"success": True, "campaign": campaign.to_dict()}
    
    async def get_campaign_dashboard(self, campaign_id: str) -> Dict[str, Any]:
        campaign = self._campaigns.get(campaign_id)
        if not campaign:
            return {"success": False, "error": "Campaign not found"}
        
        donations = [d.to_dict() for d in self._donations.values() 
                    if d.campaign_id == campaign_id]
        
        return {
            "success": True,
            "campaign": campaign.to_dict(),
            "donations": donations,
            "impact_summary": {
                "water_saved_liters": campaign.water_saved_liters,
                "water_saved_kl": campaign.water_saved_liters / 1000,
                "co2_offset_kg": campaign.co2_offset_kg,
                "beneficiaries": campaign.beneficiaries,
                "cost_per_beneficiary": campaign.funded_amount / campaign.beneficiaries if campaign.beneficiaries > 0 else 0
            }
        }
    
    async def get_public_campaigns(self) -> Dict[str, Any]:
        campaigns = [c.to_dict() for c in self._campaigns.values() 
                    if c.status == "active"]
        return {"success": True, "campaigns": campaigns}
    
    async def generate_impact_report(self, campaign_id: str) -> Dict[str, Any]:
        campaign = self._campaigns.get(campaign_id)
        if not campaign:
            return {"success": False, "error": "Campaign not found"}
        
        return {
            "success": True,
            "report": {
                "campaign": campaign.title,
                "corporate": campaign.corporate_name,
                "total_investment": campaign.funded_amount,
                "projects_completed": campaign.projects_completed,
                "beneficiaries": campaign.beneficiaries,
                "environmental_impact": {
                    "water_saved_kl": campaign.water_saved_liters / 1000,
                    "annual_recharge_potential_kl": campaign.water_saved_liters / 1000 * 12,
                    "co2_offset_tonnes": campaign.co2_offset_kg / 1000,
                    "trees_equivalent": int(campaign.co2_offset_kg / 22)
                },
                "social_impact": {
                    "families_benefited": campaign.beneficiaries,
                    "water_security_days": int(campaign.water_saved_liters / 150 / campaign.beneficiaries) if campaign.beneficiaries > 0 else 0
                },
                "sdg_alignment": ["SDG 6: Clean Water", "SDG 13: Climate Action", "SDG 11: Sustainable Cities"],
                "report_url": f"/api/v1/csr/campaigns/{campaign_id}/report.pdf"
            }
        }


_service: Optional[CSRIntegrationService] = None

def get_csr_integration_service() -> CSRIntegrationService:
    global _service
    if _service is None:
        _service = CSRIntegrationService()
    return _service
