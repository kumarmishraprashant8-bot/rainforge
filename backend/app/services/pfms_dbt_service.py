"""
PFMS Direct Benefit Transfer Service
Integration with Public Financial Management System for subsidy disbursement.

Features:
- Beneficiary registration with Aadhaar-linked bank accounts
- Direct Benefit Transfer (DBT) initiation
- Payment status tracking
- Jal Shakti Abhiyan subsidy automation
"""

import logging
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, field
from enum import Enum
import random

logger = logging.getLogger(__name__)


class PaymentStatus(str, Enum):
    """DBT payment status."""
    INITIATED = "initiated"
    PENDING_VALIDATION = "pending_validation"
    VALIDATED = "validated"
    PROCESSING = "processing"
    TRANSFERRED = "transferred"
    CREDITED = "credited"
    FAILED = "failed"
    RETURNED = "returned"


class SubsidyScheme(str, Enum):
    """Government subsidy schemes for RWH."""
    JAL_SHAKTI_ABHIYAN = "jsa_2024"
    AMRUT_2 = "amrut_2.0"
    PMAY_URBAN = "pmay_u"
    STATE_RWH_SUBSIDY = "state_rwh"
    SMART_CITY = "smart_city_rwh"


@dataclass
class BankDetails:
    """Beneficiary bank account details."""
    account_number: str
    ifsc_code: str
    bank_name: str
    branch_name: str
    account_holder_name: str
    account_type: str = "savings"
    is_verified: bool = False
    verified_via: Optional[str] = None  # "npci" or "penny_drop"


@dataclass
class Beneficiary:
    """DBT beneficiary record."""
    beneficiary_id: str
    user_id: str
    aadhaar_number_masked: str
    name: str
    bank_details: BankDetails
    registered_at: datetime
    schemes: List[SubsidyScheme] = field(default_factory=list)
    total_disbursed: float = 0.0
    
    def to_dict(self) -> Dict:
        return {
            "beneficiary_id": self.beneficiary_id,
            "name": self.name,
            "aadhaar_masked": self.aadhaar_number_masked,
            "bank_account_masked": f"XXXX{self.bank_details.account_number[-4:]}",
            "bank_name": self.bank_details.bank_name,
            "registered_at": self.registered_at.isoformat(),
            "eligible_schemes": [s.value for s in self.schemes],
            "total_disbursed": self.total_disbursed
        }


@dataclass
class DBTTransaction:
    """Direct Benefit Transfer transaction."""
    transaction_id: str
    beneficiary_id: str
    scheme: SubsidyScheme
    amount: float
    purpose: str
    status: PaymentStatus
    initiated_at: datetime
    status_history: List[Dict] = field(default_factory=list)
    utr_number: Optional[str] = None
    credited_at: Optional[datetime] = None
    failure_reason: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            "transaction_id": self.transaction_id,
            "beneficiary_id": self.beneficiary_id,
            "scheme": self.scheme.value,
            "amount": self.amount,
            "purpose": self.purpose,
            "status": self.status.value,
            "initiated_at": self.initiated_at.isoformat(),
            "utr_number": self.utr_number,
            "credited_at": self.credited_at.isoformat() if self.credited_at else None
        }


@dataclass
class SubsidyEligibility:
    """Subsidy eligibility result."""
    scheme: SubsidyScheme
    eligible: bool
    max_amount: float
    coverage_percent: float
    conditions: List[str]
    documents_required: List[str]


class PFMSDirectBenefitService:
    """
    Public Financial Management System Integration.
    
    Handles:
    - Beneficiary registration with Aadhaar seeding
    - NPCI bank account verification
    - DBT payment initiation via PFMS
    - Real-time payment tracking
    
    Note: Mock implementation for demo. Production requires:
    - PFMS API credentials from Ministry of Finance
    - NPCI Aadhaar Mapper access
    - PFU (PFMS Fund User) registration
    """
    
    def __init__(self):
        self._beneficiaries: Dict[str, Beneficiary] = {}
        self._transactions: Dict[str, DBTTransaction] = {}
        self._user_to_beneficiary: Dict[str, str] = {}
        
        # Mock PFMS credentials
        self._pfu_code = "RAINFORGE-PFU-2024"
        self._scheme_codes = {
            SubsidyScheme.JAL_SHAKTI_ABHIYAN: "JSA-WH-001",
            SubsidyScheme.AMRUT_2: "AMRUT-WH-002",
            SubsidyScheme.PMAY_URBAN: "PMAY-RWH-003",
            SubsidyScheme.STATE_RWH_SUBSIDY: "STATE-RWH-VAR",
            SubsidyScheme.SMART_CITY: "SCM-RWH-005"
        }
        
        # Subsidy limits by scheme
        self._subsidy_limits = {
            SubsidyScheme.JAL_SHAKTI_ABHIYAN: {"max": 50000, "coverage": 0.50},
            SubsidyScheme.AMRUT_2: {"max": 75000, "coverage": 0.60},
            SubsidyScheme.PMAY_URBAN: {"max": 30000, "coverage": 0.40},
            SubsidyScheme.STATE_RWH_SUBSIDY: {"max": 25000, "coverage": 0.35},
            SubsidyScheme.SMART_CITY: {"max": 100000, "coverage": 0.70}
        }
        
        logger.info("💰 PFMS Direct Benefit Service initialized")
    
    # ==================== BENEFICIARY REGISTRATION ====================
    
    async def register_beneficiary(
        self,
        user_id: str,
        aadhaar_masked: str,
        name: str,
        bank_details: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Register a new DBT beneficiary.
        
        Requires Aadhaar verification and bank account validation.
        """
        # Check if already registered
        if user_id in self._user_to_beneficiary:
            existing = self._beneficiaries[self._user_to_beneficiary[user_id]]
            return {
                "success": True,
                "message": "Beneficiary already registered",
                "beneficiary": existing.to_dict(),
                "is_new": False
            }
        
        # Validate bank details
        bank = BankDetails(
            account_number=bank_details["account_number"],
            ifsc_code=bank_details["ifsc_code"],
            bank_name=self._get_bank_name(bank_details["ifsc_code"]),
            branch_name=bank_details.get("branch_name", ""),
            account_holder_name=bank_details.get("account_holder_name", name)
        )
        
        # Mock NPCI verification
        verification_result = await self._verify_bank_account(bank)
        
        if not verification_result["success"]:
            return {
                "success": False,
                "error": verification_result["error"],
                "error_code": "BANK_VERIFICATION_FAILED"
            }
        
        bank.is_verified = True
        bank.verified_via = "npci"
        
        # Generate beneficiary ID (matches PFMS format)
        beneficiary_id = f"BEN-{uuid.uuid4().hex[:12].upper()}"
        
        beneficiary = Beneficiary(
            beneficiary_id=beneficiary_id,
            user_id=user_id,
            aadhaar_number_masked=aadhaar_masked,
            name=name,
            bank_details=bank,
            registered_at=datetime.now(),
            schemes=self._get_eligible_schemes(user_id)
        )
        
        self._beneficiaries[beneficiary_id] = beneficiary
        self._user_to_beneficiary[user_id] = beneficiary_id
        
        logger.info(f"✅ Beneficiary registered: {beneficiary_id}")
        
        return {
            "success": True,
            "beneficiary": beneficiary.to_dict(),
            "is_new": True,
            "bank_verified": True
        }
    
    async def _verify_bank_account(self, bank: BankDetails) -> Dict[str, Any]:
        """
        Verify bank account via NPCI.
        
        In production, this calls NPCI's account verification API.
        """
        # Simulate NPCI verification
        # In production: verify account holder name matches Aadhaar name
        
        if not bank.ifsc_code or len(bank.ifsc_code) != 11:
            return {"success": False, "error": "Invalid IFSC code"}
        
        if not bank.account_number or len(bank.account_number) < 9:
            return {"success": False, "error": "Invalid account number"}
        
        # Mock success (95% success rate in demo)
        if random.random() > 0.95:
            return {"success": False, "error": "Account verification failed. Please check details."}
        
        return {
            "success": True,
            "name_match": True,
            "account_status": "active"
        }
    
    def _get_bank_name(self, ifsc: str) -> str:
        """Get bank name from IFSC code."""
        bank_codes = {
            "SBIN": "State Bank of India",
            "HDFC": "HDFC Bank",
            "ICIC": "ICICI Bank",
            "PUNB": "Punjab National Bank",
            "BARB": "Bank of Baroda",
            "CNRB": "Canara Bank",
            "UBIN": "Union Bank of India",
            "BKID": "Bank of India",
            "UTIB": "Axis Bank",
            "KKBK": "Kotak Mahindra Bank"
        }
        prefix = ifsc[:4]
        return bank_codes.get(prefix, f"{prefix} Bank")
    
    def _get_eligible_schemes(self, user_id: str) -> List[SubsidyScheme]:
        """Determine eligible subsidy schemes for user."""
        # In production, check against scheme criteria
        # For demo, return common schemes
        return [
            SubsidyScheme.JAL_SHAKTI_ABHIYAN,
            SubsidyScheme.STATE_RWH_SUBSIDY
        ]
    
    # ==================== SUBSIDY ELIGIBILITY ====================
    
    async def check_subsidy_eligibility(
        self,
        user_id: str,
        project_cost: float,
        property_type: str = "residential",
        city_tier: str = "tier_2"
    ) -> Dict[str, Any]:
        """
        Check eligibility for all subsidy schemes.
        
        Returns list of eligible schemes with amounts.
        """
        eligibility_results = []
        
        for scheme, limits in self._subsidy_limits.items():
            eligible, conditions = self._check_scheme_eligibility(
                scheme, property_type, city_tier, project_cost
            )
            
            if eligible:
                subsidy_amount = min(
                    project_cost * limits["coverage"],
                    limits["max"]
                )
            else:
                subsidy_amount = 0
            
            eligibility_results.append(SubsidyEligibility(
                scheme=scheme,
                eligible=eligible,
                max_amount=subsidy_amount,
                coverage_percent=limits["coverage"] * 100 if eligible else 0,
                conditions=conditions,
                documents_required=self._get_required_documents(scheme)
            ))
        
        total_eligible = sum(e.max_amount for e in eligibility_results if e.eligible)
        best_scheme = max(
            [e for e in eligibility_results if e.eligible],
            key=lambda x: x.max_amount,
            default=None
        )
        
        return {
            "success": True,
            "project_cost": project_cost,
            "total_eligible_subsidy": total_eligible,
            "best_scheme": best_scheme.scheme.value if best_scheme else None,
            "best_amount": best_scheme.max_amount if best_scheme else 0,
            "schemes": [
                {
                    "scheme": e.scheme.value,
                    "eligible": e.eligible,
                    "amount": e.max_amount,
                    "coverage_percent": e.coverage_percent,
                    "conditions": e.conditions,
                    "documents": e.documents_required
                }
                for e in eligibility_results
            ]
        }
    
    def _check_scheme_eligibility(
        self,
        scheme: SubsidyScheme,
        property_type: str,
        city_tier: str,
        project_cost: float
    ) -> tuple[bool, List[str]]:
        """Check specific scheme eligibility."""
        conditions = []
        eligible = True
        
        if scheme == SubsidyScheme.JAL_SHAKTI_ABHIYAN:
            conditions.append("✓ Residential/Institutional property")
            conditions.append("✓ First-time RWH installation")
            if property_type not in ["residential", "institutional"]:
                eligible = False
                conditions[0] = "✗ Only residential/institutional eligible"
        
        elif scheme == SubsidyScheme.AMRUT_2:
            conditions.append("✓ City covered under AMRUT 2.0")
            if city_tier == "tier_3":
                eligible = False
                conditions[0] = "✗ City not under AMRUT 2.0"
        
        elif scheme == SubsidyScheme.PMAY_URBAN:
            conditions.append("✓ PMAY-U beneficiary")
            conditions.append("✓ EWS/LIG category")
            # Would check against PMAY database in production
        
        elif scheme == SubsidyScheme.SMART_CITY:
            conditions.append("✓ Smart City Mission area")
            if city_tier != "tier_1":
                eligible = False
                conditions[0] = "✗ Not a Smart City"
        
        return eligible, conditions
    
    def _get_required_documents(self, scheme: SubsidyScheme) -> List[str]:
        """Get required documents for scheme application."""
        base_docs = [
            "Aadhaar Card",
            "Property Tax Receipt",
            "Bank Passbook/Statement"
        ]
        
        scheme_specific = {
            SubsidyScheme.JAL_SHAKTI_ABHIYAN: ["RWH Installation Quote", "Site Photos"],
            SubsidyScheme.AMRUT_2: ["Municipal NOC", "RWH Design Approval"],
            SubsidyScheme.PMAY_URBAN: ["PMAY-U Allotment Letter", "Income Certificate"],
            SubsidyScheme.STATE_RWH_SUBSIDY: ["State Domicile", "Utility Bills"],
            SubsidyScheme.SMART_CITY: ["Smart City Area Certificate"]
        }
        
        return base_docs + scheme_specific.get(scheme, [])
    
    # ==================== DBT PAYMENT ====================
    
    async def initiate_dbt_payment(
        self,
        beneficiary_id: str,
        scheme: SubsidyScheme,
        amount: float,
        purpose: str,
        project_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Initiate Direct Benefit Transfer payment.
        
        Creates payment request in PFMS.
        """
        beneficiary = self._beneficiaries.get(beneficiary_id)
        
        if not beneficiary:
            return {
                "success": False,
                "error": "Beneficiary not found",
                "error_code": "BENEFICIARY_NOT_FOUND"
            }
        
        if scheme not in beneficiary.schemes:
            return {
                "success": False,
                "error": f"Beneficiary not eligible for {scheme.value}",
                "error_code": "SCHEME_NOT_ELIGIBLE"
            }
        
        # Check scheme limits
        limits = self._subsidy_limits[scheme]
        if amount > limits["max"]:
            return {
                "success": False,
                "error": f"Amount exceeds scheme limit of ₹{limits['max']}",
                "error_code": "AMOUNT_EXCEEDS_LIMIT"
            }
        
        # Create transaction
        txn_id = f"DBT-{uuid.uuid4().hex[:12].upper()}"
        
        transaction = DBTTransaction(
            transaction_id=txn_id,
            beneficiary_id=beneficiary_id,
            scheme=scheme,
            amount=amount,
            purpose=purpose,
            status=PaymentStatus.INITIATED,
            initiated_at=datetime.now(),
            status_history=[{
                "status": PaymentStatus.INITIATED.value,
                "timestamp": datetime.now().isoformat(),
                "remarks": "Payment request created"
            }]
        )
        
        self._transactions[txn_id] = transaction
        
        # Simulate async processing
        await self._process_payment_async(txn_id)
        
        logger.info(f"💸 DBT initiated: {txn_id} for ₹{amount}")
        
        return {
            "success": True,
            "transaction": transaction.to_dict(),
            "message": "Payment initiated successfully",
            "estimated_credit_time": "2-3 business days"
        }
    
    async def _process_payment_async(self, txn_id: str):
        """
        Simulate PFMS payment processing.
        
        In production, this would be handled by PFMS webhooks.
        """
        txn = self._transactions[txn_id]
        
        # Update to validated
        txn.status = PaymentStatus.VALIDATED
        txn.status_history.append({
            "status": PaymentStatus.VALIDATED.value,
            "timestamp": datetime.now().isoformat(),
            "remarks": "Beneficiary and bank details validated"
        })
        
        # Simulate processing (in production, this happens over hours/days)
        txn.status = PaymentStatus.PROCESSING
        txn.status_history.append({
            "status": PaymentStatus.PROCESSING.value,
            "timestamp": datetime.now().isoformat(),
            "remarks": "Payment being processed by PFMS"
        })
        
        # Simulate transfer (90% success rate)
        if random.random() < 0.90:
            txn.status = PaymentStatus.CREDITED
            txn.utr_number = f"UTR{random.randint(100000000000, 999999999999)}"
            txn.credited_at = datetime.now()
            txn.status_history.append({
                "status": PaymentStatus.CREDITED.value,
                "timestamp": datetime.now().isoformat(),
                "remarks": f"Amount credited. UTR: {txn.utr_number}",
                "utr": txn.utr_number
            })
            
            # Update beneficiary total
            beneficiary = self._beneficiaries[txn.beneficiary_id]
            beneficiary.total_disbursed += txn.amount
        else:
            txn.status = PaymentStatus.FAILED
            txn.failure_reason = "Bank account issue. Please verify details."
            txn.status_history.append({
                "status": PaymentStatus.FAILED.value,
                "timestamp": datetime.now().isoformat(),
                "remarks": txn.failure_reason
            })
    
    async def check_payment_status(
        self,
        transaction_id: str
    ) -> Dict[str, Any]:
        """
        Check DBT payment status.
        
        Returns current status and full history.
        """
        txn = self._transactions.get(transaction_id)
        
        if not txn:
            return {
                "success": False,
                "error": "Transaction not found",
                "error_code": "TXN_NOT_FOUND"
            }
        
        return {
            "success": True,
            "transaction": txn.to_dict(),
            "status_history": txn.status_history,
            "is_completed": txn.status in [PaymentStatus.CREDITED, PaymentStatus.FAILED],
            "is_successful": txn.status == PaymentStatus.CREDITED
        }
    
    async def get_user_transactions(
        self,
        user_id: str,
        limit: int = 20
    ) -> Dict[str, Any]:
        """Get all transactions for a user."""
        beneficiary_id = self._user_to_beneficiary.get(user_id)
        
        if not beneficiary_id:
            return {
                "success": True,
                "transactions": [],
                "total": 0
            }
        
        user_txns = [
            t.to_dict() for t in self._transactions.values()
            if t.beneficiary_id == beneficiary_id
        ]
        
        # Sort by date, newest first
        user_txns.sort(key=lambda x: x["initiated_at"], reverse=True)
        
        return {
            "success": True,
            "transactions": user_txns[:limit],
            "total": len(user_txns),
            "total_credited": sum(
                t.amount for t in self._transactions.values()
                if t.beneficiary_id == beneficiary_id and t.status == PaymentStatus.CREDITED
            )
        }
    
    # ==================== AUTO-APPLICATION ====================
    
    async def auto_apply_subsidy(
        self,
        user_id: str,
        project_id: str,
        project_cost: float,
        scheme: SubsidyScheme
    ) -> Dict[str, Any]:
        """
        Auto-apply for subsidy using DigiLocker documents.
        
        Streamlines the application process by pre-filling forms.
        """
        beneficiary_id = self._user_to_beneficiary.get(user_id)
        
        if not beneficiary_id:
            return {
                "success": False,
                "error": "Please register as beneficiary first",
                "error_code": "NOT_REGISTERED"
            }
        
        # In production: Pull documents from DigiLocker
        # Generate application form
        # Submit to respective government portal
        
        application_id = f"APP-{uuid.uuid4().hex[:10].upper()}"
        
        return {
            "success": True,
            "application_id": application_id,
            "scheme": scheme.value,
            "project_id": project_id,
            "project_cost": project_cost,
            "estimated_subsidy": min(
                project_cost * self._subsidy_limits[scheme]["coverage"],
                self._subsidy_limits[scheme]["max"]
            ),
            "status": "submitted",
            "message": "Application submitted. Track status in scheme portal.",
            "tracking_url": f"https://jaljeevanmission.gov.in/track/{application_id}"
        }


# Singleton instance
_service: Optional[PFMSDirectBenefitService] = None


def get_pfms_dbt_service() -> PFMSDirectBenefitService:
    """Get or create the PFMS DBT service singleton."""
    global _service
    if _service is None:
        _service = PFMSDirectBenefitService()
    return _service
