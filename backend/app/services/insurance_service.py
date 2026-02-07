"""
Insurance Service
Weather-indexed parametric insurance and equipment protection.
"""

import logging
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, field
from enum import Enum
import random

logger = logging.getLogger(__name__)


class InsuranceType(str, Enum):
    WEATHER_INDEXED = "weather_indexed"
    EQUIPMENT_PROTECTION = "equipment_protection"
    PERFORMANCE_GUARANTEE = "performance_guarantee"


class ClaimStatus(str, Enum):
    FILED = "filed"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    PAID = "paid"


@dataclass
class InsurancePolicy:
    policy_id: str
    user_id: str
    project_id: str
    insurance_type: InsuranceType
    premium_annual: float
    coverage_amount: float
    start_date: datetime
    end_date: datetime
    status: str = "active"
    
    def to_dict(self) -> Dict:
        return {
            "policy_id": self.policy_id,
            "type": self.insurance_type.value,
            "premium": self.premium_annual,
            "coverage": self.coverage_amount,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "status": self.status
        }


@dataclass
class InsuranceClaim:
    claim_id: str
    policy_id: str
    claim_type: str
    amount: float
    description: str
    status: ClaimStatus
    filed_at: datetime
    
    def to_dict(self) -> Dict:
        return {
            "claim_id": self.claim_id,
            "policy_id": self.policy_id,
            "amount": self.amount,
            "status": self.status.value,
            "filed_at": self.filed_at.isoformat()
        }


class InsuranceService:
    """Weather-indexed and equipment insurance for RWH systems."""
    
    def __init__(self):
        self._policies: Dict[str, InsurancePolicy] = {}
        self._claims: Dict[str, InsuranceClaim] = {}
        
        self._products = {
            InsuranceType.WEATHER_INDEXED: {
                "name": "Monsoon Shield",
                "description": "Auto-payout if rainfall <50% of normal",
                "premium_rate": 0.02,  # 2% of coverage
                "max_coverage": 50000
            },
            InsuranceType.EQUIPMENT_PROTECTION: {
                "name": "Equipment Guard",
                "description": "Covers IoT sensors, pumps, and filters",
                "premium_rate": 0.03,
                "max_coverage": 25000
            },
            InsuranceType.PERFORMANCE_GUARANTEE: {
                "name": "Yield Protect",
                "description": "Payout if yield <80% of prediction",
                "premium_rate": 0.025,
                "max_coverage": 30000
            }
        }
        logger.info("🛡️ Insurance Service initialized")
    
    async def get_quotes(self, project_id: str, coverage_amount: float) -> Dict[str, Any]:
        quotes = []
        for ins_type, product in self._products.items():
            coverage = min(coverage_amount, product["max_coverage"])
            premium = coverage * product["premium_rate"]
            quotes.append({
                "type": ins_type.value,
                "name": product["name"],
                "description": product["description"],
                "coverage": coverage,
                "premium_annual": premium,
                "premium_monthly": premium / 12
            })
        return {"success": True, "quotes": quotes}
    
    async def purchase_policy(self, user_id: str, project_id: str,
                             insurance_type: str, coverage: float) -> Dict[str, Any]:
        ins_type = InsuranceType(insurance_type)
        product = self._products[ins_type]
        premium = min(coverage, product["max_coverage"]) * product["premium_rate"]
        
        policy_id = f"POL-{uuid.uuid4().hex[:10].upper()}"
        policy = InsurancePolicy(
            policy_id=policy_id, user_id=user_id, project_id=project_id,
            insurance_type=ins_type, premium_annual=premium, coverage_amount=coverage,
            start_date=datetime.now(), end_date=datetime.now() + timedelta(days=365)
        )
        self._policies[policy_id] = policy
        return {"success": True, "policy": policy.to_dict()}
    
    async def file_claim(self, policy_id: str, claim_type: str,
                        amount: float, description: str) -> Dict[str, Any]:
        policy = self._policies.get(policy_id)
        if not policy:
            return {"success": False, "error": "Policy not found"}
        
        claim_id = f"CLM-{uuid.uuid4().hex[:10].upper()}"
        claim = InsuranceClaim(
            claim_id=claim_id, policy_id=policy_id, claim_type=claim_type,
            amount=min(amount, policy.coverage_amount), description=description,
            status=ClaimStatus.FILED, filed_at=datetime.now()
        )
        self._claims[claim_id] = claim
        
        # Auto-approve for demo
        if random.random() < 0.85:
            claim.status = ClaimStatus.APPROVED
        return {"success": True, "claim": claim.to_dict()}
    
    async def check_weather_trigger(self, project_id: str, 
                                    actual_rainfall_mm: float,
                                    expected_rainfall_mm: float) -> Dict[str, Any]:
        """Check if weather parametric trigger is met."""
        if actual_rainfall_mm < expected_rainfall_mm * 0.5:
            return {
                "triggered": True,
                "actual": actual_rainfall_mm,
                "expected": expected_rainfall_mm,
                "shortfall_percent": (1 - actual_rainfall_mm/expected_rainfall_mm) * 100,
                "message": "Parametric trigger met. Auto-claim initiated."
            }
        return {"triggered": False, "message": "Rainfall within normal range"}


_service: Optional[InsuranceService] = None

def get_insurance_service() -> InsuranceService:
    global _service
    if _service is None:
        _service = InsuranceService()
    return _service
