"""
Aadhaar & DigiLocker Integration Service
Deep India Stack integration for government-grade citizen verification.

Features:
- Aadhaar OTP-based eKYC
- DigiLocker document pull API
- eSign for digital signatures
- Auto-populate forms from documents
"""

import logging
import hashlib
import hmac
import base64
import json
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, field
from enum import Enum
import random
import string

logger = logging.getLogger(__name__)


class VerificationStatus(str, Enum):
    """Aadhaar verification status."""
    PENDING = "pending"
    OTP_SENT = "otp_sent"
    VERIFIED = "verified"
    FAILED = "failed"
    EXPIRED = "expired"


class DocumentType(str, Enum):
    """DigiLocker supported document types."""
    PROPERTY_TAX = "PROPTAX"
    ELECTRICITY_BILL = "ELECBILL"
    WATER_BILL = "WATERBILL"
    LAND_RECORD = "LANDREC"
    AADHAR_CARD = "ADHAR"
    PAN_CARD = "PANCR"
    DRIVING_LICENSE = "DRVLC"
    VOTER_ID = "VOTERID"
    BANK_STATEMENT = "BNKSTMT"


@dataclass
class AadhaarProfile:
    """Aadhaar eKYC response profile."""
    aadhaar_number_masked: str  # Last 4 digits visible
    name: str
    date_of_birth: str
    gender: str
    address: Dict[str, str]
    photo_base64: Optional[str] = None
    email_hash: Optional[str] = None
    phone_hash: Optional[str] = None
    verification_timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        return {
            "aadhaar_masked": self.aadhaar_number_masked,
            "name": self.name,
            "dob": self.date_of_birth,
            "gender": self.gender,
            "address": self.address,
            "verified_at": self.verification_timestamp.isoformat()
        }


@dataclass
class DigiLockerDocument:
    """Document fetched from DigiLocker."""
    doc_id: str
    doc_type: DocumentType
    issuer: str
    issue_date: str
    doc_name: str
    uri: str
    extracted_data: Dict[str, Any] = field(default_factory=dict)
    raw_xml: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            "doc_id": self.doc_id,
            "type": self.doc_type.value,
            "issuer": self.issuer,
            "issue_date": self.issue_date,
            "name": self.doc_name,
            "extracted_data": self.extracted_data
        }


@dataclass
class ESignRequest:
    """eSign request for digital signature."""
    request_id: str
    document_hash: str
    signer_name: str
    signer_aadhaar_masked: str
    status: str = "pending"
    signature: Optional[str] = None
    signed_at: Optional[datetime] = None
    certificate: Optional[str] = None


class AadhaarDigiLockerService:
    """
    India Stack Integration Service.
    
    Integrates with:
    - UIDAI Aadhaar eKYC API (OTP-based)
    - DigiLocker Partner API
    - eSign API for digital signatures
    
    Note: This is a mock implementation for demo purposes.
    Production would require UIDAI ASA/KUA license and DigiLocker partnership.
    """
    
    def __init__(self):
        self._otp_sessions: Dict[str, Dict] = {}
        self._verified_users: Dict[str, AadhaarProfile] = {}
        self._digilocker_tokens: Dict[str, Dict] = {}
        self._documents: Dict[str, List[DigiLockerDocument]] = {}
        self._esign_requests: Dict[str, ESignRequest] = {}
        
        # Mock API credentials (would be real in production)
        self._asa_license = "RAINFORGE-ASA-2024"
        self._digilocker_client_id = "rainforge_partner_v1"
        
        logger.info("🔐 Aadhaar & DigiLocker Service initialized")
    
    # ==================== AADHAAR eKYC ====================
    
    async def send_aadhaar_otp(
        self,
        aadhaar_number: str,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Send OTP to Aadhaar-linked mobile number.
        
        In production, this calls UIDAI's OTP API.
        """
        # Validate Aadhaar format (12 digits)
        if not aadhaar_number.isdigit() or len(aadhaar_number) != 12:
            return {
                "success": False,
                "error": "Invalid Aadhaar number format",
                "error_code": "INVALID_AADHAAR"
            }
        
        # Generate transaction ID
        txn_id = f"RF-{uuid.uuid4().hex[:16].upper()}"
        
        # Generate mock OTP (in production, UIDAI sends this)
        mock_otp = ''.join(random.choices(string.digits, k=6))
        
        # Store session
        self._otp_sessions[txn_id] = {
            "aadhaar": aadhaar_number,
            "user_id": user_id,
            "otp": mock_otp,  # In production, we don't store this
            "created_at": datetime.now(),
            "expires_at": datetime.now() + timedelta(minutes=10),
            "attempts": 0,
            "status": VerificationStatus.OTP_SENT
        }
        
        logger.info(f"📱 OTP sent for Aadhaar XXXX-XXXX-{aadhaar_number[-4:]}")
        
        return {
            "success": True,
            "txn_id": txn_id,
            "message": "OTP sent to Aadhaar-linked mobile",
            "expires_in_seconds": 600,
            # For demo only - remove in production!
            "demo_otp": mock_otp
        }
    
    async def verify_aadhaar_otp(
        self,
        txn_id: str,
        otp: str
    ) -> Dict[str, Any]:
        """
        Verify OTP and fetch eKYC data.
        
        Returns citizen profile on success.
        """
        session = self._otp_sessions.get(txn_id)
        
        if not session:
            return {
                "success": False,
                "error": "Invalid or expired transaction",
                "error_code": "INVALID_TXN"
            }
        
        if datetime.now() > session["expires_at"]:
            session["status"] = VerificationStatus.EXPIRED
            return {
                "success": False,
                "error": "OTP expired. Please request a new one.",
                "error_code": "OTP_EXPIRED"
            }
        
        session["attempts"] += 1
        
        if session["attempts"] > 3:
            session["status"] = VerificationStatus.FAILED
            return {
                "success": False,
                "error": "Maximum attempts exceeded",
                "error_code": "MAX_ATTEMPTS"
            }
        
        if otp != session["otp"]:
            return {
                "success": False,
                "error": f"Invalid OTP. {3 - session['attempts']} attempts remaining.",
                "error_code": "INVALID_OTP"
            }
        
        # OTP verified - generate mock eKYC response
        aadhaar = session["aadhaar"]
        
        # Mock profile (in production, this comes from UIDAI)
        profile = AadhaarProfile(
            aadhaar_number_masked=f"XXXX-XXXX-{aadhaar[-4:]}",
            name=self._generate_mock_name(),
            date_of_birth="1985-06-15",
            gender="M",
            address={
                "house": "123",
                "street": "Main Road",
                "landmark": "Near Water Tank",
                "locality": "Sector 5",
                "city": "Jaipur",
                "district": "Jaipur",
                "state": "Rajasthan",
                "pincode": "302001"
            },
            photo_base64=None,  # Would contain photo in production
            verification_timestamp=datetime.now()
        )
        
        # Store verified profile
        self._verified_users[session["user_id"]] = profile
        session["status"] = VerificationStatus.VERIFIED
        
        logger.info(f"✅ Aadhaar verified for user {session['user_id']}")
        
        return {
            "success": True,
            "profile": profile.to_dict(),
            "verification_id": f"EKVC-{uuid.uuid4().hex[:12].upper()}"
        }
    
    def _generate_mock_name(self) -> str:
        """Generate realistic Indian name for demo."""
        first_names = ["Rajesh", "Priya", "Amit", "Sunita", "Vikram", "Anjali", "Suresh", "Kavita"]
        last_names = ["Sharma", "Patel", "Singh", "Kumar", "Verma", "Gupta", "Joshi", "Mishra"]
        return f"{random.choice(first_names)} {random.choice(last_names)}"
    
    # ==================== DIGILOCKER ====================
    
    async def initiate_digilocker_auth(
        self,
        user_id: str,
        redirect_uri: str
    ) -> Dict[str, Any]:
        """
        Initiate DigiLocker OAuth flow.
        
        Returns authorization URL for user consent.
        """
        state = uuid.uuid4().hex
        
        # Store session for callback validation
        self._digilocker_tokens[state] = {
            "user_id": user_id,
            "created_at": datetime.now(),
            "status": "pending"
        }
        
        # Mock OAuth URL (in production, this is DigiLocker's URL)
        auth_url = (
            f"https://digilocker.meripehchaan.gov.in/public/oauth2/1/authorize"
            f"?response_type=code"
            f"&client_id={self._digilocker_client_id}"
            f"&redirect_uri={redirect_uri}"
            f"&state={state}"
            f"&scope=openid+profile+docs"
        )
        
        logger.info(f"🔗 DigiLocker auth initiated for user {user_id}")
        
        return {
            "success": True,
            "auth_url": auth_url,
            "state": state,
            "expires_in_seconds": 300
        }
    
    async def complete_digilocker_auth(
        self,
        authorization_code: str,
        state: str
    ) -> Dict[str, Any]:
        """
        Complete DigiLocker OAuth and get access token.
        """
        session = self._digilocker_tokens.get(state)
        
        if not session:
            return {
                "success": False,
                "error": "Invalid state parameter",
                "error_code": "INVALID_STATE"
            }
        
        # Mock token exchange (in production, call DigiLocker token endpoint)
        access_token = f"dl_access_{uuid.uuid4().hex}"
        refresh_token = f"dl_refresh_{uuid.uuid4().hex}"
        
        session["access_token"] = access_token
        session["refresh_token"] = refresh_token
        session["status"] = "authorized"
        session["authorized_at"] = datetime.now()
        
        # Pre-populate with mock documents
        user_id = session["user_id"]
        self._documents[user_id] = self._generate_mock_documents()
        
        logger.info(f"✅ DigiLocker authorized for user {user_id}")
        
        return {
            "success": True,
            "access_token": access_token,
            "expires_in": 3600,
            "documents_available": len(self._documents[user_id])
        }
    
    async def fetch_digilocker_documents(
        self,
        user_id: str,
        doc_types: Optional[List[DocumentType]] = None
    ) -> Dict[str, Any]:
        """
        Fetch documents from DigiLocker.
        
        Optionally filter by document type.
        """
        documents = self._documents.get(user_id, [])
        
        if doc_types:
            documents = [d for d in documents if d.doc_type in doc_types]
        
        return {
            "success": True,
            "total_documents": len(documents),
            "documents": [d.to_dict() for d in documents]
        }
    
    async def extract_property_data(
        self,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Extract property-related data from DigiLocker documents.
        
        Used to auto-populate RWH assessment forms.
        """
        documents = self._documents.get(user_id, [])
        
        extracted = {
            "address": None,
            "property_area_sqft": None,
            "owner_name": None,
            "property_type": None,
            "utility_account": None,
            "water_connection": None
        }
        
        for doc in documents:
            if doc.doc_type == DocumentType.PROPERTY_TAX:
                extracted.update({
                    "address": doc.extracted_data.get("property_address"),
                    "property_area_sqft": doc.extracted_data.get("built_up_area"),
                    "owner_name": doc.extracted_data.get("owner_name"),
                    "property_type": doc.extracted_data.get("property_type")
                })
            elif doc.doc_type == DocumentType.WATER_BILL:
                extracted.update({
                    "utility_account": doc.extracted_data.get("consumer_number"),
                    "water_connection": doc.extracted_data.get("connection_type")
                })
        
        # Check Aadhaar profile for additional data
        profile = self._verified_users.get(user_id)
        if profile:
            if not extracted["owner_name"]:
                extracted["owner_name"] = profile.name
            if not extracted["address"]:
                addr = profile.address
                extracted["address"] = f"{addr['house']}, {addr['street']}, {addr['locality']}, {addr['city']} - {addr['pincode']}"
        
        return {
            "success": True,
            "extracted_data": extracted,
            "confidence": 0.95 if extracted["address"] else 0.60
        }
    
    def _generate_mock_documents(self) -> List[DigiLockerDocument]:
        """Generate mock DigiLocker documents for demo."""
        return [
            DigiLockerDocument(
                doc_id=f"DOC-{uuid.uuid4().hex[:8].upper()}",
                doc_type=DocumentType.PROPERTY_TAX,
                issuer="Municipal Corporation of Jaipur",
                issue_date="2023-04-01",
                doc_name="Property Tax Receipt 2023-24",
                uri="in.gov.raj.mcj/PROPTAX/2024",
                extracted_data={
                    "property_address": "123, Main Road, Sector 5, Jaipur - 302001",
                    "built_up_area": 2500,  # sqft
                    "plot_area": 3000,  # sqft
                    "owner_name": "Rajesh Sharma",
                    "property_type": "Residential",
                    "tax_paid": 12500.00
                }
            ),
            DigiLockerDocument(
                doc_id=f"DOC-{uuid.uuid4().hex[:8].upper()}",
                doc_type=DocumentType.ELECTRICITY_BILL,
                issuer="Jaipur Vidyut Vitran Nigam Ltd",
                issue_date="2024-01-15",
                doc_name="Electricity Bill - January 2024",
                uri="in.gov.raj.jvvnl/ELECBILL/2024",
                extracted_data={
                    "consumer_number": "JVVNL-1234567890",
                    "connection_type": "Domestic",
                    "sanctioned_load": "5 kW",
                    "units_consumed": 450,
                    "amount_due": 2850.00
                }
            ),
            DigiLockerDocument(
                doc_id=f"DOC-{uuid.uuid4().hex[:8].upper()}",
                doc_type=DocumentType.WATER_BILL,
                issuer="PHED Rajasthan",
                issue_date="2024-01-10",
                doc_name="Water Bill - January 2024",
                uri="in.gov.raj.phed/WATERBILL/2024",
                extracted_data={
                    "consumer_number": "PHED-RAJ-789012",
                    "connection_type": "Domestic",
                    "meter_reading": 15420,
                    "consumption_kl": 18,
                    "amount_due": 540.00
                }
            ),
            DigiLockerDocument(
                doc_id=f"DOC-{uuid.uuid4().hex[:8].upper()}",
                doc_type=DocumentType.LAND_RECORD,
                issuer="Revenue Department, Rajasthan",
                issue_date="2022-08-20",
                doc_name="Jamabandi (Land Record)",
                uri="in.gov.raj.revenue/LANDREC/2022",
                extracted_data={
                    "khasra_number": "123/456",
                    "village": "Sector 5",
                    "tehsil": "Sanganer",
                    "district": "Jaipur",
                    "area_hectare": 0.028,  # ~3000 sqft
                    "land_use": "Residential",
                    "owner_name": "Rajesh Sharma"
                }
            )
        ]
    
    # ==================== eSIGN ====================
    
    async def initiate_esign(
        self,
        user_id: str,
        document_content: bytes,
        document_name: str
    ) -> Dict[str, Any]:
        """
        Initiate eSign for a document.
        
        Requires Aadhaar verification first.
        """
        profile = self._verified_users.get(user_id)
        
        if not profile:
            return {
                "success": False,
                "error": "Aadhaar verification required before eSign",
                "error_code": "AADHAAR_NOT_VERIFIED"
            }
        
        # Create document hash
        doc_hash = hashlib.sha256(document_content).hexdigest()
        
        request_id = f"ESIGN-{uuid.uuid4().hex[:12].upper()}"
        
        esign_request = ESignRequest(
            request_id=request_id,
            document_hash=doc_hash,
            signer_name=profile.name,
            signer_aadhaar_masked=profile.aadhaar_number_masked,
            status="pending"
        )
        
        self._esign_requests[request_id] = esign_request
        
        logger.info(f"📝 eSign initiated for document: {document_name}")
        
        return {
            "success": True,
            "request_id": request_id,
            "document_hash": doc_hash,
            "signer": profile.name,
            "status": "otp_required",
            "message": "Please enter OTP sent to Aadhaar-linked mobile"
        }
    
    async def complete_esign(
        self,
        request_id: str,
        otp: str
    ) -> Dict[str, Any]:
        """
        Complete eSign with OTP verification.
        """
        esign_req = self._esign_requests.get(request_id)
        
        if not esign_req:
            return {
                "success": False,
                "error": "Invalid eSign request",
                "error_code": "INVALID_REQUEST"
            }
        
        # Mock OTP verification (in production, verify with UIDAI)
        if len(otp) != 6 or not otp.isdigit():
            return {
                "success": False,
                "error": "Invalid OTP format",
                "error_code": "INVALID_OTP"
            }
        
        # Generate mock signature
        signature_data = {
            "document_hash": esign_req.document_hash,
            "signer": esign_req.signer_name,
            "timestamp": datetime.now().isoformat(),
            "request_id": request_id
        }
        
        signature = base64.b64encode(
            hashlib.sha512(json.dumps(signature_data).encode()).digest()
        ).decode()
        
        esign_req.signature = signature
        esign_req.signed_at = datetime.now()
        esign_req.status = "signed"
        esign_req.certificate = f"CERT-{uuid.uuid4().hex[:16].upper()}"
        
        logger.info(f"✅ Document signed: {request_id}")
        
        return {
            "success": True,
            "request_id": request_id,
            "signature": signature,
            "certificate_id": esign_req.certificate,
            "signed_at": esign_req.signed_at.isoformat(),
            "signer": esign_req.signer_name,
            "legally_valid": True
        }
    
    # ==================== STATUS & UTILITIES ====================
    
    def get_user_verification_status(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive verification status for a user."""
        profile = self._verified_users.get(user_id)
        documents = self._documents.get(user_id, [])
        
        digilocker_status = "not_connected"
        for state, session in self._digilocker_tokens.items():
            if session.get("user_id") == user_id:
                digilocker_status = session.get("status", "pending")
                break
        
        return {
            "aadhaar_verified": profile is not None,
            "aadhaar_name": profile.name if profile else None,
            "digilocker_status": digilocker_status,
            "documents_available": len(documents),
            "esign_capable": profile is not None
        }


# Singleton instance
_service: Optional[AadhaarDigiLockerService] = None


def get_aadhaar_digilocker_service() -> AadhaarDigiLockerService:
    """Get or create the Aadhaar/DigiLocker service singleton."""
    global _service
    if _service is None:
        _service = AadhaarDigiLockerService()
    return _service
