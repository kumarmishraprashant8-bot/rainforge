"""
Credit (Microloan) Service
Embedded finance for RWH installations via NBFC partnerships.
"""

import logging
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, field
from enum import Enum
import random
import math

logger = logging.getLogger(__name__)


class LoanStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    DISBURSED = "disbursed"
    ACTIVE = "active"
    CLOSED = "closed"


class NBFCPartner(str, Enum):
    CAPITAL_FLOAT = "capital_float"
    KISETSU = "kisetsu"
    BAJAJ_FINSERV = "bajaj_finserv"


@dataclass
class LoanProduct:
    partner: NBFCPartner
    product_name: str
    min_amount: float
    max_amount: float
    interest_rate_annual: float
    min_tenure_months: int
    max_tenure_months: int
    processing_fee_percent: float
    
    def calculate_emi(self, principal: float, tenure_months: int) -> float:
        monthly_rate = self.interest_rate_annual / 12 / 100
        if monthly_rate == 0:
            return principal / tenure_months
        emi = principal * monthly_rate * math.pow(1 + monthly_rate, tenure_months)
        emi /= (math.pow(1 + monthly_rate, tenure_months) - 1)
        return round(emi, 2)


@dataclass
class LoanApplication:
    application_id: str
    user_id: str
    partner: NBFCPartner
    amount: float
    tenure_months: int
    emi: float
    interest_rate: float
    purpose: str
    status: LoanStatus
    applied_at: datetime
    total_payable: float = 0
    total_paid: float = 0
    emis_paid: int = 0
    emis_remaining: int = 0
    
    def to_dict(self) -> Dict:
        return {
            "application_id": self.application_id,
            "partner": self.partner.value,
            "amount": self.amount,
            "tenure_months": self.tenure_months,
            "emi": self.emi,
            "status": self.status.value,
            "total_payable": self.total_payable,
            "total_paid": self.total_paid
        }


class CreditService:
    """Embedded Finance Service for RWH Microloans."""
    
    def __init__(self):
        self._applications: Dict[str, LoanApplication] = {}
        self._user_loans: Dict[str, List[str]] = {}
        
        self._products = {
            NBFCPartner.CAPITAL_FLOAT: LoanProduct(
                partner=NBFCPartner.CAPITAL_FLOAT,
                product_name="RainForge Green Loan",
                min_amount=10000, max_amount=200000,
                interest_rate_annual=14.5,
                min_tenure_months=6, max_tenure_months=36,
                processing_fee_percent=2.0
            ),
            NBFCPartner.BAJAJ_FINSERV: LoanProduct(
                partner=NBFCPartner.BAJAJ_FINSERV,
                product_name="Bajaj EMI Card - RWH",
                min_amount=15000, max_amount=500000,
                interest_rate_annual=12.0,
                min_tenure_months=6, max_tenure_months=48,
                processing_fee_percent=2.5
            )
        }
        logger.info("💳 Credit Service initialized")
    
    async def check_eligibility(self, user_id: str, requested_amount: float, 
                                monthly_income: float = 50000) -> Dict[str, Any]:
        credit_score = random.randint(650, 850)
        max_emi = monthly_income * 0.5
        max_amount = max_emi * 20
        eligible = credit_score >= 650 and requested_amount <= max_amount
        
        offers = []
        for partner, product in self._products.items():
            if product.min_amount <= requested_amount <= product.max_amount:
                for tenure in [12, 18, 24]:
                    emi = product.calculate_emi(requested_amount, tenure)
                    offers.append({
                        "partner": partner.value,
                        "amount": requested_amount,
                        "tenure_months": tenure,
                        "interest_rate": product.interest_rate_annual,
                        "emi": emi,
                        "total_payable": emi * tenure
                    })
        offers.sort(key=lambda x: x["emi"])
        
        return {"success": True, "eligible": eligible, "max_amount": max_amount,
                "credit_score_range": f"{credit_score-50}-{credit_score+50}", "offers": offers[:6]}
    
    async def apply_for_loan(self, user_id: str, partner: str, amount: float,
                            tenure_months: int, purpose: str = "RWH Installation") -> Dict[str, Any]:
        nbfc = NBFCPartner(partner)
        product = self._products[nbfc]
        emi = product.calculate_emi(amount, tenure_months)
        
        app_id = f"LOAN-{uuid.uuid4().hex[:10].upper()}"
        app = LoanApplication(
            application_id=app_id, user_id=user_id, partner=nbfc,
            amount=amount, tenure_months=tenure_months, emi=emi,
            interest_rate=product.interest_rate_annual, purpose=purpose,
            status=LoanStatus.ACTIVE, applied_at=datetime.now(),
            total_payable=emi * tenure_months, emis_remaining=tenure_months
        )
        self._applications[app_id] = app
        self._user_loans.setdefault(user_id, []).append(app_id)
        
        return {"success": True, "application": app.to_dict()}
    
    async def get_loan_dashboard(self, user_id: str) -> Dict[str, Any]:
        loan_ids = self._user_loans.get(user_id, [])
        loans = [self._applications[lid].to_dict() for lid in loan_ids]
        return {"success": True, "loans": loans, "total_loans": len(loans)}


_service: Optional[CreditService] = None

def get_credit_service() -> CreditService:
    global _service
    if _service is None:
        _service = CreditService()
    return _service
