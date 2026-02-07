"""
Compliance Certificate Service
Government compliance certificates, permits, and legal requirements.
"""

import io
from datetime import datetime, date, timedelta
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
import logging
import hashlib
import qrcode
from io import BytesIO
import base64

logger = logging.getLogger(__name__)


@dataclass
class ComplianceRequirement:
    """Compliance requirement for a state/city."""
    state: str
    mandatory_threshold_sqm: float
    permit_threshold_sqm: float
    permit_authority: str
    permit_fee_inr: float
    processing_days: int
    required_documents: List[str]
    subsidy_available: bool
    subsidy_percent: float
    max_subsidy_inr: float


# State-wise compliance requirements
STATE_COMPLIANCE = {
    "Tamil Nadu": ComplianceRequirement(
        state="Tamil Nadu",
        mandatory_threshold_sqm=100,
        permit_threshold_sqm=200,
        permit_authority="Tamil Nadu Water Supply and Drainage Board",
        permit_fee_inr=500,
        processing_days=15,
        required_documents=[
            "Property ownership proof",
            "Building plan approval",
            "Site plan with RWH system",
            "Technical specifications",
            "Contractor registration"
        ],
        subsidy_available=True,
        subsidy_percent=50,
        max_subsidy_inr=20000
    ),
    "Karnataka": ComplianceRequirement(
        state="Karnataka",
        mandatory_threshold_sqm=60,
        permit_threshold_sqm=100,
        permit_authority="Bangalore Water Supply and Sewerage Board / Local Municipality",
        permit_fee_inr=750,
        processing_days=21,
        required_documents=[
            "Property tax receipt",
            "Sanctioned building plan",
            "RWH system design",
            "NOC from water authority"
        ],
        subsidy_available=True,
        subsidy_percent=50,
        max_subsidy_inr=25000
    ),
    "Maharashtra": ComplianceRequirement(
        state="Maharashtra",
        mandatory_threshold_sqm=300,
        permit_threshold_sqm=500,
        permit_authority="Maharashtra Jeevan Pradhikaran / Municipal Corporation",
        permit_fee_inr=1000,
        processing_days=30,
        required_documents=[
            "Property registration",
            "IOD/CC copy",
            "Architect certificate",
            "RWH system specification"
        ],
        subsidy_available=True,
        subsidy_percent=30,
        max_subsidy_inr=15000
    ),
    "Delhi": ComplianceRequirement(
        state="Delhi",
        mandatory_threshold_sqm=100,
        permit_threshold_sqm=200,
        permit_authority="Delhi Jal Board",
        permit_fee_inr=500,
        processing_days=15,
        required_documents=[
            "Property ownership document",
            "Water connection receipt",
            "Building plan",
            "RWH design by registered plumber"
        ],
        subsidy_available=True,
        subsidy_percent=50,
        max_subsidy_inr=50000
    ),
    "Rajasthan": ComplianceRequirement(
        state="Rajasthan",
        mandatory_threshold_sqm=300,
        permit_threshold_sqm=500,
        permit_authority="Public Health Engineering Department",
        permit_fee_inr=300,
        processing_days=20,
        required_documents=[
            "Property document",
            "Plot plan",
            "RWH structure plan"
        ],
        subsidy_available=True,
        subsidy_percent=60,
        max_subsidy_inr=30000
    ),
    "Gujarat": ComplianceRequirement(
        state="Gujarat",
        mandatory_threshold_sqm=500,
        permit_threshold_sqm=1000,
        permit_authority="Gujarat Water Supply and Sewerage Board",
        permit_fee_inr=800,
        processing_days=25,
        required_documents=[
            "Property card",
            "Building permission",
            "RWH technical drawing"
        ],
        subsidy_available=True,
        subsidy_percent=40,
        max_subsidy_inr=20000
    ),
}

# Default for states not explicitly listed
DEFAULT_COMPLIANCE = ComplianceRequirement(
    state="Default",
    mandatory_threshold_sqm=500,
    permit_threshold_sqm=1000,
    permit_authority="Local Municipal Authority",
    permit_fee_inr=500,
    processing_days=30,
    required_documents=[
        "Property ownership proof",
        "Building plan",
        "RWH system design"
    ],
    subsidy_available=False,
    subsidy_percent=0,
    max_subsidy_inr=0
)


class ComplianceCertificateService:
    """
    Service for generating compliance certificates and managing permits.
    
    Certificate Types:
    - Installation Certificate
    - Compliance Certificate (State PWD format)
    - Water Credit Certificate
    - Maintenance Certificate
    - Performance Certificate
    """
    
    def __init__(self):
        self.certificates: Dict[str, Dict] = {}
        self.permit_applications: Dict[str, Dict] = {}
    
    # ==================== REQUIREMENTS ====================
    
    def get_requirements(
        self,
        state: str,
        city: Optional[str] = None,
        roof_area_sqm: float = 0
    ) -> Dict[str, Any]:
        """Get compliance requirements for a state/city."""
        
        req = STATE_COMPLIANCE.get(state, DEFAULT_COMPLIANCE)
        
        mandatory = roof_area_sqm >= req.mandatory_threshold_sqm
        permit_required = roof_area_sqm >= req.permit_threshold_sqm
        
        return {
            "state": state,
            "city": city,
            "roof_area_sqm": roof_area_sqm,
            "mandatory": mandatory,
            "permit_required": permit_required,
            "permit_authority": req.permit_authority,
            "permit_fee_inr": req.permit_fee_inr if permit_required else 0,
            "processing_days": req.processing_days if permit_required else 0,
            "required_documents": req.required_documents if permit_required else [],
            "subsidy": {
                "available": req.subsidy_available,
                "percent": req.subsidy_percent,
                "max_amount_inr": req.max_subsidy_inr
            },
            "message": self._get_compliance_message(mandatory, permit_required, state)
        }
    
    def _get_compliance_message(
        self,
        mandatory: bool,
        permit_required: bool,
        state: str
    ) -> str:
        """Generate compliance message."""
        if mandatory and permit_required:
            return f"RWH is mandatory in {state} for your property size. Permit required before installation."
        elif mandatory:
            return f"RWH is mandatory in {state} for your property size. No permit required."
        elif permit_required:
            return f"RWH is optional but permit required for your property size in {state}."
        else:
            return f"RWH is optional and no permit required in {state} for your property size."
    
    # ==================== CERTIFICATE GENERATION ====================
    
    def generate_installation_certificate(
        self,
        project_id: int,
        owner_name: str,
        property_address: str,
        city: str,
        state: str,
        tank_capacity_liters: int,
        installation_date: date,
        installer_name: str,
        installer_license: Optional[str] = None,
        verification_date: Optional[date] = None,
        verified_by: Optional[str] = None,
        language: str = "en"
    ) -> Dict[str, Any]:
        """Generate installation certificate."""
        
        certificate_number = self._generate_certificate_number(
            "INST", state, project_id
        )
        
        # Generate QR code for verification
        qr_data = {
            "cert_no": certificate_number,
            "project_id": project_id,
            "capacity": tank_capacity_liters,
            "date": installation_date.isoformat()
        }
        qr_code_base64 = self._generate_qr_code(str(qr_data))
        
        certificate = {
            "certificate_id": f"cert_{project_id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            "certificate_number": certificate_number,
            "certificate_type": "installation",
            "project_id": project_id,
            
            # Owner Details
            "owner_name": owner_name,
            "property_address": property_address,
            "city": city,
            "state": state,
            
            # Installation Details
            "tank_capacity_liters": tank_capacity_liters,
            "installation_date": installation_date.isoformat(),
            "installer_name": installer_name,
            "installer_license": installer_license,
            
            # Verification
            "verification_date": verification_date.isoformat() if verification_date else None,
            "verified_by": verified_by,
            "verification_status": "verified" if verification_date else "pending",
            
            # Certificate
            "issue_date": date.today().isoformat(),
            "valid_until": (date.today() + timedelta(days=365)).isoformat(),
            "qr_code": qr_code_base64,
            
            # URLs (would be generated in production)
            "certificate_url": f"/api/v1/compliance/certificate/{certificate_number}/download",
            "verification_url": f"/verify/{certificate_number}",
            
            "language": language,
            "created_at": datetime.utcnow().isoformat()
        }
        
        self.certificates[certificate_number] = certificate
        logger.info(f"Generated installation certificate: {certificate_number}")
        
        return certificate
    
    def generate_compliance_certificate(
        self,
        project_id: int,
        owner_name: str,
        property_address: str,
        city: str,
        state: str,
        roof_area_sqm: float,
        tank_capacity_liters: int,
        has_recharge: bool = False,
        recharge_capacity_liters: int = 0,
        inspection_date: Optional[date] = None,
        inspector_name: Optional[str] = None,
        inspector_designation: Optional[str] = None,
        language: str = "en"
    ) -> Dict[str, Any]:
        """Generate state compliance certificate in PWD format."""
        
        certificate_number = self._generate_certificate_number(
            "COMP", state, project_id
        )
        
        # Calculate compliance score
        compliance_score = self._calculate_compliance_score(
            roof_area_sqm, tank_capacity_liters, has_recharge
        )
        
        # Get state requirements
        req = STATE_COMPLIANCE.get(state, DEFAULT_COMPLIANCE)
        
        certificate = {
            "certificate_id": f"comp_{project_id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            "certificate_number": certificate_number,
            "certificate_type": "compliance",
            "project_id": project_id,
            
            # Header (State specific)
            "issuing_authority": req.permit_authority,
            "state_emblem": f"/assets/emblems/{state.lower().replace(' ', '_')}.png",
            
            # Owner Details
            "owner_name": owner_name,
            "property_address": property_address,
            "city": city,
            "state": state,
            
            # Property Details
            "roof_area_sqm": roof_area_sqm,
            "tank_capacity_liters": tank_capacity_liters,
            "has_recharge": has_recharge,
            "recharge_capacity_liters": recharge_capacity_liters,
            
            # Compliance
            "compliance_score": compliance_score,
            "compliant": compliance_score >= 80,
            "annual_collection_potential_liters": self._estimate_annual_collection(
                roof_area_sqm, state
            ),
            
            # Inspection
            "inspection_date": inspection_date.isoformat() if inspection_date else None,
            "inspector_name": inspector_name,
            "inspector_designation": inspector_designation,
            
            # Certificate
            "issue_date": date.today().isoformat(),
            "valid_until": (date.today() + timedelta(days=365)).isoformat(),
            "qr_code": self._generate_qr_code(certificate_number),
            
            "language": language,
            "created_at": datetime.utcnow().isoformat()
        }
        
        self.certificates[certificate_number] = certificate
        logger.info(f"Generated compliance certificate: {certificate_number}")
        
        return certificate
    
    def generate_water_credit_certificate(
        self,
        project_id: int,
        owner_name: str,
        city: str,
        state: str,
        water_harvested_liters: float,
        period_start: date,
        period_end: date,
        carbon_offset_kg: float
    ) -> Dict[str, Any]:
        """Generate water credit certificate (tradeable)."""
        
        certificate_number = self._generate_certificate_number(
            "WC", state, project_id
        )
        
        # Calculate water credits (1 credit = 1000 liters)
        water_credits = water_harvested_liters / 1000
        
        certificate = {
            "certificate_id": f"wc_{project_id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            "certificate_number": certificate_number,
            "certificate_type": "water_credit",
            "project_id": project_id,
            
            # Owner
            "owner_name": owner_name,
            "city": city,
            "state": state,
            
            # Credits
            "water_harvested_liters": water_harvested_liters,
            "water_credits": round(water_credits, 2),
            "carbon_offset_kg": carbon_offset_kg,
            
            # Period
            "period_start": period_start.isoformat(),
            "period_end": period_end.isoformat(),
            
            # Value (indicative)
            "credit_value_inr_per_unit": 10,  # ₹10 per 1000L credit
            "total_value_inr": round(water_credits * 10, 2),
            
            # Certificate
            "issue_date": date.today().isoformat(),
            "tradeable": True,
            "blockchain_hash": self._generate_blockchain_hash(certificate_number),
            
            "created_at": datetime.utcnow().isoformat()
        }
        
        self.certificates[certificate_number] = certificate
        logger.info(f"Generated water credit certificate: {certificate_number}")
        
        return certificate
    
    # ==================== PERMIT APPLICATION ====================
    
    def create_permit_application(
        self,
        project_id: int,
        owner_name: str,
        property_address: str,
        city: str,
        state: str,
        roof_area_sqm: float,
        proposed_tank_capacity: int,
        property_documents: List[str],
        contact_phone: str,
        contact_email: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create pre-filled permit application."""
        
        req = STATE_COMPLIANCE.get(state, DEFAULT_COMPLIANCE)
        application_id = f"PERMIT-{state[:2].upper()}-{project_id}-{datetime.utcnow().strftime('%Y%m%d')}"
        
        application = {
            "application_id": application_id,
            "project_id": project_id,
            "status": "draft",
            
            # Authority Details
            "authority": req.permit_authority,
            "state": state,
            "city": city,
            
            # Applicant Details (Pre-filled)
            "applicant_name": owner_name,
            "property_address": property_address,
            "contact_phone": contact_phone,
            "contact_email": contact_email,
            
            # Property Details (Pre-filled)
            "roof_area_sqm": roof_area_sqm,
            "proposed_tank_capacity_liters": proposed_tank_capacity,
            
            # Documents Required
            "required_documents": req.required_documents,
            "uploaded_documents": property_documents,
            "documents_pending": [
                doc for doc in req.required_documents
                if doc not in property_documents
            ],
            
            # Fees
            "permit_fee_inr": req.permit_fee_inr,
            "fee_paid": False,
            
            # Timeline
            "estimated_processing_days": req.processing_days,
            "created_at": datetime.utcnow().isoformat(),
            
            # Form Data (Pre-filled based on project)
            "form_data": {
                "section_a_applicant": {
                    "name": owner_name,
                    "address": property_address,
                    "phone": contact_phone,
                    "email": contact_email
                },
                "section_b_property": {
                    "total_plot_area_sqm": roof_area_sqm * 1.5,  # Estimate
                    "built_up_area_sqm": roof_area_sqm,
                    "roof_area_sqm": roof_area_sqm,
                    "num_floors": 2,
                    "building_use": "Residential"
                },
                "section_c_rwh_system": {
                    "storage_tank_capacity_liters": proposed_tank_capacity,
                    "tank_type": "Underground",
                    "has_recharge_pit": False,
                    "has_filter": True
                }
            }
        }
        
        self.permit_applications[application_id] = application
        logger.info(f"Created permit application: {application_id}")
        
        return application
    
    def submit_permit_application(self, application_id: str) -> Dict[str, Any]:
        """Submit permit application."""
        
        if application_id not in self.permit_applications:
            raise ValueError(f"Application not found: {application_id}")
        
        application = self.permit_applications[application_id]
        
        # Check all documents uploaded
        if application["documents_pending"]:
            return {
                "success": False,
                "message": f"Missing documents: {', '.join(application['documents_pending'])}"
            }
        
        # Submit
        application["status"] = "submitted"
        application["submitted_at"] = datetime.utcnow().isoformat()
        application["expected_completion"] = (
            datetime.utcnow() + timedelta(days=application["estimated_processing_days"])
        ).isoformat()
        
        return {
            "success": True,
            "application_id": application_id,
            "status": "submitted",
            "message": f"Application submitted successfully. Expected processing time: {application['estimated_processing_days']} days"
        }
    
    # ==================== HELPERS ====================
    
    def _generate_certificate_number(
        self,
        cert_type: str,
        state: str,
        project_id: int
    ) -> str:
        """Generate unique certificate number."""
        state_code = state[:2].upper()
        year = datetime.utcnow().strftime("%Y")
        timestamp = datetime.utcnow().strftime("%m%d%H%M")
        return f"RF-{cert_type}-{state_code}-{year}-{project_id:06d}-{timestamp}"
    
    def _generate_qr_code(self, data: str) -> str:
        """Generate QR code as base64 string."""
        try:
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(data)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            return base64.b64encode(buffer.getvalue()).decode()
        except Exception as e:
            logger.warning(f"QR generation failed: {e}")
            return ""
    
    def _generate_blockchain_hash(self, certificate_number: str) -> str:
        """Generate mock blockchain hash for water credits."""
        data = f"{certificate_number}-{datetime.utcnow().isoformat()}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    def _calculate_compliance_score(
        self,
        roof_area_sqm: float,
        tank_capacity_liters: int,
        has_recharge: bool
    ) -> int:
        """Calculate compliance score 0-100."""
        score = 50  # Base score
        
        # Tank sizing (should be at least 100L per sqm)
        ratio = tank_capacity_liters / roof_area_sqm if roof_area_sqm > 0 else 0
        if ratio >= 100:
            score += 25
        elif ratio >= 50:
            score += 15
        elif ratio >= 25:
            score += 5
        
        # Recharge component
        if has_recharge:
            score += 15
        
        # Minimum area threshold
        if roof_area_sqm >= 100:
            score += 10
        
        return min(100, score)
    
    def _estimate_annual_collection(self, roof_area_sqm: float, state: str) -> float:
        """Estimate annual collection potential."""
        # State-wise average rainfall (mm)
        rainfall = {
            "Tamil Nadu": 1200,
            "Karnataka": 1000,
            "Maharashtra": 1100,
            "Delhi": 800,
            "Rajasthan": 500,
            "Gujarat": 800,
            "Kerala": 3000,
            "West Bengal": 1800,
        }
        
        avg_rainfall = rainfall.get(state, 1000)
        runoff_coef = 0.85
        
        return roof_area_sqm * avg_rainfall * runoff_coef


# Singleton instance
_compliance_service: Optional[ComplianceCertificateService] = None


def get_compliance_service() -> ComplianceCertificateService:
    """Get or create compliance certificate service instance."""
    global _compliance_service
    if _compliance_service is None:
        _compliance_service = ComplianceCertificateService()
    return _compliance_service
