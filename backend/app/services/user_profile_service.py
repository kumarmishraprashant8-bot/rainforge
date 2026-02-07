"""
User Profile Service
KYC verification, bank account management, and user preferences.
"""

import hashlib
import re
from datetime import datetime
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class KYCResult:
    """KYC verification result."""
    verified: bool
    status: str
    message: str
    verification_id: Optional[str] = None
    verified_at: Optional[datetime] = None


@dataclass
class BankVerificationResult:
    """Bank account verification result."""
    verified: bool
    account_holder_name: Optional[str] = None
    message: str = ""


class UserProfileService:
    """
    Service for managing user profiles, KYC, and preferences.
    
    Features:
    - Aadhaar verification (mock/real API integration)
    - PAN verification
    - Bank account verification (penny drop)
    - Language preferences
    - Notification preferences
    """
    
    # Supported languages
    LANGUAGES = {
        "en": "English",
        "hi": "हिंदी (Hindi)",
        "ta": "தமிழ் (Tamil)",
        "te": "తెలుగు (Telugu)",
        "kn": "ಕನ್ನಡ (Kannada)",
        "mr": "मराठी (Marathi)",
        "gu": "ગુજરાતી (Gujarati)",
        "bn": "বাংলা (Bengali)",
        "ml": "മലയാളം (Malayalam)",
        "pa": "ਪੰਜਾਬੀ (Punjabi)",
        "or": "ଓଡ଼ିଆ (Odia)",
    }
    
    # State-wise income limits for categories (₹ LPA)
    INCOME_LIMITS = {
        "ews": (0, 300000),      # Up to 3 LPA
        "lig": (300000, 600000),  # 3-6 LPA
        "mig_i": (600000, 1200000),  # 6-12 LPA
        "mig_ii": (1200000, 1800000),  # 12-18 LPA
        "hig": (1800000, float('inf')),  # Above 18 LPA
    }
    
    def __init__(self):
        self.profiles: Dict[int, Dict] = {}
        self.bank_details: Dict[int, Dict] = {}
    
    # ==================== PROFILE MANAGEMENT ====================
    
    def create_profile(
        self,
        user_id: int,
        full_name: str,
        phone: str,
        email: Optional[str] = None,
        address: Optional[Dict] = None,
        preferred_language: str = "en"
    ) -> Dict[str, Any]:
        """Create a new user profile."""
        
        profile = {
            "user_id": user_id,
            "full_name": full_name,
            "phone": phone,
            "email": email,
            "address": address or {},
            "preferred_language": preferred_language,
            "kyc_status": "pending",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        
        self.profiles[user_id] = profile
        
        logger.info(f"Created profile for user {user_id}")
        return profile
    
    def get_profile(self, user_id: int) -> Optional[Dict]:
        """Get user profile."""
        return self.profiles.get(user_id)
    
    def update_profile(self, user_id: int, **kwargs) -> Dict[str, Any]:
        """Update user profile."""
        if user_id not in self.profiles:
            raise ValueError(f"Profile not found for user {user_id}")
        
        profile = self.profiles[user_id]
        for key, value in kwargs.items():
            if key in profile:
                profile[key] = value
        
        profile["updated_at"] = datetime.utcnow()
        return profile
    
    # ==================== KYC VERIFICATION ====================
    
    def verify_aadhaar(
        self,
        user_id: int,
        aadhaar_number: str,
        name: str,
        dob: Optional[str] = None
    ) -> KYCResult:
        """
        Verify Aadhaar number.
        In production, this would integrate with UIDAI APIs.
        """
        
        # Validate Aadhaar format (12 digits)
        if not re.match(r'^\d{12}$', aadhaar_number):
            return KYCResult(
                verified=False,
                status="invalid_format",
                message="Aadhaar number must be 12 digits"
            )
        
        # Verhoeff checksum validation (simplified)
        if not self._validate_aadhaar_checksum(aadhaar_number):
            return KYCResult(
                verified=False,
                status="invalid_checksum",
                message="Invalid Aadhaar number"
            )
        
        # Mock verification (in production, call UIDAI API)
        # For demo, accept all valid format Aadhaar numbers
        
        # Store hashed Aadhaar (never store plain text)
        aadhaar_hash = hashlib.sha256(aadhaar_number.encode()).hexdigest()
        
        if user_id in self.profiles:
            self.profiles[user_id]["aadhaar_hash"] = aadhaar_hash
            self.profiles[user_id]["aadhaar_last_four"] = aadhaar_number[-4:]
            self.profiles[user_id]["aadhaar_verified"] = True
            self.profiles[user_id]["kyc_status"] = "verified"
            self.profiles[user_id]["kyc_verified_at"] = datetime.utcnow()
        
        logger.info(f"Aadhaar verified for user {user_id}")
        
        return KYCResult(
            verified=True,
            status="verified",
            message="Aadhaar verification successful",
            verification_id=f"AADHAAR-{user_id}-{datetime.utcnow().strftime('%Y%m%d')}",
            verified_at=datetime.utcnow()
        )
    
    def verify_pan(self, user_id: int, pan_number: str, name: str) -> KYCResult:
        """Verify PAN number."""
        
        # Validate PAN format
        pan_pattern = r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$'
        if not re.match(pan_pattern, pan_number.upper()):
            return KYCResult(
                verified=False,
                status="invalid_format",
                message="Invalid PAN format. Expected: ABCDE1234F"
            )
        
        # Mock verification
        if user_id in self.profiles:
            self.profiles[user_id]["pan_number"] = pan_number.upper()
            self.profiles[user_id]["pan_verified"] = True
        
        return KYCResult(
            verified=True,
            status="verified",
            message="PAN verification successful",
            verification_id=f"PAN-{user_id}-{datetime.utcnow().strftime('%Y%m%d')}"
        )
    
    def _validate_aadhaar_checksum(self, aadhaar: str) -> bool:
        """Validate Aadhaar using Verhoeff algorithm (simplified)."""
        # Simplified validation - just check it's not all same digits
        if len(set(aadhaar)) == 1:
            return False
        # Check first digit is not 0 or 1
        if aadhaar[0] in ('0', '1'):
            return False
        return True
    
    # ==================== BANK VERIFICATION ====================
    
    def add_bank_account(
        self,
        user_id: int,
        account_holder_name: str,
        account_number: str,
        ifsc_code: str,
        bank_name: str,
        branch_name: str,
        account_type: str = "savings"
    ) -> Dict[str, Any]:
        """Add bank account details."""
        
        # Validate IFSC format
        if not re.match(r'^[A-Z]{4}0[A-Z0-9]{6}$', ifsc_code.upper()):
            raise ValueError("Invalid IFSC code format")
        
        # Validate account number (9-18 digits)
        if not re.match(r'^\d{9,18}$', account_number):
            raise ValueError("Account number must be 9-18 digits")
        
        # Encrypt account number (in production, use proper encryption)
        account_encrypted = self._encrypt_account_number(account_number)
        
        bank_detail = {
            "user_id": user_id,
            "account_holder_name": account_holder_name,
            "account_number_encrypted": account_encrypted,
            "account_last_four": account_number[-4:],
            "ifsc_code": ifsc_code.upper(),
            "bank_name": bank_name,
            "branch_name": branch_name,
            "account_type": account_type,
            "verified": False,
            "created_at": datetime.utcnow(),
        }
        
        self.bank_details[user_id] = bank_detail
        return bank_detail
    
    def verify_bank_account(self, user_id: int) -> BankVerificationResult:
        """
        Verify bank account using penny drop.
        In production, this would use a payment gateway.
        """
        
        if user_id not in self.bank_details:
            return BankVerificationResult(
                verified=False,
                message="Bank account not found"
            )
        
        bank = self.bank_details[user_id]
        
        # Mock penny drop verification
        # In production, initiate ₹1 transfer and verify name match
        
        bank["verified"] = True
        bank["verified_at"] = datetime.utcnow()
        bank["penny_drop_status"] = "success"
        
        return BankVerificationResult(
            verified=True,
            account_holder_name=bank["account_holder_name"],
            message="Bank account verified successfully"
        )
    
    def _encrypt_account_number(self, account_number: str) -> str:
        """Encrypt account number (simplified - use proper encryption in production)."""
        return hashlib.sha256(account_number.encode()).hexdigest()
    
    # ==================== PREFERENCES ====================
    
    def update_language_preference(self, user_id: int, language: str) -> bool:
        """Update user's preferred language."""
        if language not in self.LANGUAGES:
            raise ValueError(f"Unsupported language: {language}")
        
        if user_id in self.profiles:
            self.profiles[user_id]["preferred_language"] = language
            return True
        return False
    
    def update_notification_preferences(
        self,
        user_id: int,
        email: bool = True,
        sms: bool = True,
        whatsapp: bool = False,
        push: bool = True
    ) -> Dict[str, bool]:
        """Update notification preferences."""
        
        preferences = {
            "email_notifications": email,
            "sms_notifications": sms,
            "whatsapp_notifications": whatsapp,
            "push_notifications": push,
        }
        
        if user_id in self.profiles:
            self.profiles[user_id].update(preferences)
        
        return preferences
    
    # ==================== INCOME CATEGORY ====================
    
    def determine_income_category(self, annual_income: float) -> str:
        """Determine income category based on annual income."""
        for category, (min_income, max_income) in self.INCOME_LIMITS.items():
            if min_income <= annual_income < max_income:
                return category
        return "not_disclosed"
    
    def get_subsidy_eligibility(
        self,
        user_id: int,
        state: str
    ) -> Dict[str, Any]:
        """Get subsidy eligibility based on profile."""
        
        profile = self.profiles.get(user_id, {})
        financial = profile.get("financial_details", {})
        
        income_category = financial.get("income_category", "not_disclosed")
        is_bpl = financial.get("is_bpl", False)
        
        # Base subsidy percentages by income category
        subsidy_rates = {
            "ews": 90,  # 90% for EWS
            "lig": 75,  # 75% for LIG
            "mig_i": 50,  # 50% for MIG-I
            "mig_ii": 30,  # 30% for MIG-II
            "hig": 0,  # No subsidy for HIG
            "not_disclosed": 0,
        }
        
        base_percent = subsidy_rates.get(income_category, 0)
        
        # BPL gets additional 10%
        if is_bpl:
            base_percent = min(100, base_percent + 10)
        
        return {
            "eligible": base_percent > 0,
            "subsidy_percent": base_percent,
            "income_category": income_category,
            "is_bpl": is_bpl,
            "message": f"Eligible for {base_percent}% subsidy under {income_category.upper()} category"
        }


# Singleton instance
_user_profile_service: Optional[UserProfileService] = None


def get_user_profile_service() -> UserProfileService:
    """Get or create user profile service instance."""
    global _user_profile_service
    if _user_profile_service is None:
        _user_profile_service = UserProfileService()
    return _user_profile_service
