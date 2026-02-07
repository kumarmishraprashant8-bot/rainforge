"""
Enhanced Features API Endpoints
Comprehensive API for all new RWH platform features.
"""

from fastapi import APIRouter, HTTPException, Query, Path, Body, Depends
from typing import Optional, List
from datetime import date, datetime
from pydantic import BaseModel, Field

# Import services
from app.services.user_profile_service import get_user_profile_service
from app.services.compliance_certificate_service import get_compliance_service
from app.services.contractor_marketplace_service import get_marketplace_service
from app.services.performance_analytics_service import get_performance_service
from app.services.water_quality_service import get_water_quality_service
from app.services.iot_enhanced_service import get_enhanced_iot_service

router = APIRouter()


# ==================== REQUEST/RESPONSE MODELS ====================

# User Profile Models
class ProfileCreateRequest(BaseModel):
    user_id: int
    full_name: str
    phone: str
    email: Optional[str] = None
    preferred_language: str = "en"


class AadhaarVerifyRequest(BaseModel):
    user_id: int
    aadhaar_number: str
    name: str
    dob: Optional[str] = None


class BankAccountRequest(BaseModel):
    user_id: int
    account_holder_name: str
    account_number: str
    ifsc_code: str
    bank_name: str
    branch_name: str
    account_type: str = "savings"


class NotificationPreferencesRequest(BaseModel):
    email: bool = True
    sms: bool = True
    whatsapp: bool = False
    push: bool = True


# Compliance Models
class ComplianceRequirementsRequest(BaseModel):
    state: str
    city: Optional[str] = None
    roof_area_sqm: float


class InstallationCertificateRequest(BaseModel):
    project_id: int
    owner_name: str
    property_address: str
    city: str
    state: str
    tank_capacity_liters: int
    installation_date: date
    installer_name: str
    installer_license: Optional[str] = None
    language: str = "en"


class ComplianceCertificateRequest(BaseModel):
    project_id: int
    owner_name: str
    property_address: str
    city: str
    state: str
    roof_area_sqm: float
    tank_capacity_liters: int
    has_recharge: bool = False
    recharge_capacity_liters: int = 0


class PermitApplicationRequest(BaseModel):
    project_id: int
    owner_name: str
    property_address: str
    city: str
    state: str
    roof_area_sqm: float
    proposed_tank_capacity: int
    property_documents: List[str] = []
    contact_phone: str
    contact_email: Optional[str] = None


# Marketplace Models
class QuoteRequestCreate(BaseModel):
    project_id: int
    user_id: int
    property_address: str
    city: str
    state: str
    roof_area_sqm: float
    tank_capacity_liters: int
    includes_recharge: bool = False
    requirements_description: str
    contact_name: str
    contact_phone: str
    preferred_start_date: Optional[date] = None
    budget_min: Optional[float] = None
    budget_max: Optional[float] = None


class QuoteSubmit(BaseModel):
    quote_request_id: str
    contractor_id: str
    material_cost: float
    labor_cost: float
    estimated_days: int
    proposed_start_date: date
    scope_of_work: str
    materials_included: List[str]
    warranty_months: int = 12
    payment_terms: str = "20% advance, 80% on completion"


class MilestoneUpdateRequest(BaseModel):
    status: str
    photos: List[str] = []
    notes: str = ""


class ReviewSubmit(BaseModel):
    contractor_id: str
    project_id: int
    work_order_id: str
    user_id: int
    overall_rating: int = Field(..., ge=1, le=5)
    quality_rating: int = Field(..., ge=1, le=5)
    timeliness_rating: int = Field(..., ge=1, le=5)
    communication_rating: int = Field(..., ge=1, le=5)
    value_rating: int = Field(..., ge=1, le=5)
    review_text: str
    would_recommend: bool = True
    photos: List[str] = []


class DefectReportRequest(BaseModel):
    project_id: int
    work_order_id: str
    user_id: int
    defect_type: str
    defect_description: str
    defect_location: str
    severity: str = "medium"
    photos: List[str] = []
    detected_date: Optional[date] = None


# Quality Models
class SensorReadingRequest(BaseModel):
    project_id: int
    device_id: str
    ph: Optional[float] = Field(None, ge=0, le=14)
    tds_ppm: Optional[float] = Field(None, ge=0)
    turbidity_ntu: Optional[float] = Field(None, ge=0)
    temperature_c: Optional[float] = None
    dissolved_oxygen_ppm: Optional[float] = None


class LabTestUploadRequest(BaseModel):
    project_id: int
    test_date: date
    lab_name: str
    ph: float = Field(..., ge=0, le=14)
    tds_ppm: float = Field(..., ge=0)
    turbidity_ntu: float = Field(..., ge=0)
    hardness_ppm: Optional[float] = None
    chloride_ppm: Optional[float] = None
    nitrate_ppm: Optional[float] = None
    fluoride_ppm: Optional[float] = None
    iron_ppm: Optional[float] = None
    coliform_present: Optional[bool] = None
    e_coli_present: Optional[bool] = None
    report_url: Optional[str] = None


# IoT Models
class DevicePairRequest(BaseModel):
    project_id: int
    device_type: str
    device_serial: str
    device_name: Optional[str] = None


class CalibrationStartRequest(BaseModel):
    device_id: str
    tank_capacity_liters: int
    tank_shape: str = "cylindrical"


class CalibrationPointRequest(BaseModel):
    calibration_id: str
    step: int
    sensor_reading: float
    known_volume_liters: float = 0


class OverflowPredictionRequest(BaseModel):
    project_id: int
    current_level_percent: float
    tank_capacity_liters: int
    expected_rainfall_mm: float
    roof_area_sqm: float
    runoff_coefficient: float = 0.85


# ==================== USER PROFILE ENDPOINTS ====================

@router.post("/profile/create")
async def create_profile(request: ProfileCreateRequest):
    """Create a new user profile."""
    service = get_user_profile_service()
    return service.create_profile(
        user_id=request.user_id,
        full_name=request.full_name,
        phone=request.phone,
        email=request.email,
        preferred_language=request.preferred_language
    )


@router.get("/profile/{user_id}")
async def get_profile(user_id: int):
    """Get user profile."""
    service = get_user_profile_service()
    profile = service.get_profile(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@router.post("/profile/verify-aadhaar")
async def verify_aadhaar(request: AadhaarVerifyRequest):
    """Verify Aadhaar number."""
    service = get_user_profile_service()
    return service.verify_aadhaar(
        user_id=request.user_id,
        aadhaar_number=request.aadhaar_number,
        name=request.name,
        dob=request.dob
    )


@router.post("/profile/verify-pan")
async def verify_pan(user_id: int, pan_number: str, name: str):
    """Verify PAN number."""
    service = get_user_profile_service()
    return service.verify_pan(user_id, pan_number, name)


@router.post("/profile/bank-account")
async def add_bank_account(request: BankAccountRequest):
    """Add bank account details."""
    service = get_user_profile_service()
    try:
        return service.add_bank_account(
            user_id=request.user_id,
            account_holder_name=request.account_holder_name,
            account_number=request.account_number,
            ifsc_code=request.ifsc_code,
            bank_name=request.bank_name,
            branch_name=request.branch_name,
            account_type=request.account_type
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/profile/{user_id}/verify-bank")
async def verify_bank_account(user_id: int):
    """Verify bank account via penny drop."""
    service = get_user_profile_service()
    return service.verify_bank_account(user_id)


@router.put("/profile/{user_id}/language/{language}")
async def update_language(user_id: int, language: str):
    """Update preferred language."""
    service = get_user_profile_service()
    try:
        service.update_language_preference(user_id, language)
        return {"success": True, "language": language}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/profile/{user_id}/notifications")
async def update_notifications(user_id: int, request: NotificationPreferencesRequest):
    """Update notification preferences."""
    service = get_user_profile_service()
    return service.update_notification_preferences(
        user_id=user_id,
        email=request.email,
        sms=request.sms,
        whatsapp=request.whatsapp,
        push=request.push
    )


@router.get("/profile/{user_id}/subsidy-eligibility")
async def get_subsidy_eligibility(user_id: int, state: str):
    """Get subsidy eligibility based on profile."""
    service = get_user_profile_service()
    return service.get_subsidy_eligibility(user_id, state)


# ==================== COMPLIANCE ENDPOINTS ====================

@router.post("/compliance/requirements")
async def get_compliance_requirements(request: ComplianceRequirementsRequest):
    """Get compliance requirements for a state/city."""
    service = get_compliance_service()
    return service.get_requirements(
        state=request.state,
        city=request.city,
        roof_area_sqm=request.roof_area_sqm
    )


@router.post("/compliance/certificate/installation")
async def generate_installation_certificate(request: InstallationCertificateRequest):
    """Generate installation certificate."""
    service = get_compliance_service()
    return service.generate_installation_certificate(
        project_id=request.project_id,
        owner_name=request.owner_name,
        property_address=request.property_address,
        city=request.city,
        state=request.state,
        tank_capacity_liters=request.tank_capacity_liters,
        installation_date=request.installation_date,
        installer_name=request.installer_name,
        installer_license=request.installer_license,
        language=request.language
    )


@router.post("/compliance/certificate/compliance")
async def generate_compliance_certificate(request: ComplianceCertificateRequest):
    """Generate state compliance certificate."""
    service = get_compliance_service()
    return service.generate_compliance_certificate(
        project_id=request.project_id,
        owner_name=request.owner_name,
        property_address=request.property_address,
        city=request.city,
        state=request.state,
        roof_area_sqm=request.roof_area_sqm,
        tank_capacity_liters=request.tank_capacity_liters,
        has_recharge=request.has_recharge,
        recharge_capacity_liters=request.recharge_capacity_liters
    )


@router.post("/compliance/certificate/water-credit")
async def generate_water_credit_certificate(
    project_id: int,
    owner_name: str,
    city: str,
    state: str,
    water_harvested_liters: float,
    period_start: date,
    period_end: date,
    carbon_offset_kg: float = 0
):
    """Generate tradeable water credit certificate."""
    service = get_compliance_service()
    return service.generate_water_credit_certificate(
        project_id=project_id,
        owner_name=owner_name,
        city=city,
        state=state,
        water_harvested_liters=water_harvested_liters,
        period_start=period_start,
        period_end=period_end,
        carbon_offset_kg=carbon_offset_kg
    )


@router.post("/compliance/permit/create")
async def create_permit_application(request: PermitApplicationRequest):
    """Create pre-filled permit application."""
    service = get_compliance_service()
    return service.create_permit_application(
        project_id=request.project_id,
        owner_name=request.owner_name,
        property_address=request.property_address,
        city=request.city,
        state=request.state,
        roof_area_sqm=request.roof_area_sqm,
        proposed_tank_capacity=request.proposed_tank_capacity,
        property_documents=request.property_documents,
        contact_phone=request.contact_phone,
        contact_email=request.contact_email
    )


@router.post("/compliance/permit/{application_id}/submit")
async def submit_permit_application(application_id: str):
    """Submit permit application."""
    service = get_compliance_service()
    try:
        return service.submit_permit_application(application_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==================== MARKETPLACE ENDPOINTS ====================

@router.post("/marketplace/contractor/register")
async def register_contractor(
    company_name: str,
    owner_name: str,
    phone: str,
    email: str,
    city: str,
    state: str,
    years_experience: int = 0,
    certifications: List[str] = [],
    service_areas: List[str] = []
):
    """Register a new contractor."""
    service = get_marketplace_service()
    return service.register_contractor(
        company_name=company_name,
        owner_name=owner_name,
        phone=phone,
        email=email,
        city=city,
        state=state,
        years_experience=years_experience,
        certifications=certifications,
        service_areas=service_areas
    )


@router.get("/marketplace/contractors/search")
async def search_contractors(
    city: Optional[str] = None,
    state: Optional[str] = None,
    min_rating: float = 0,
    verified_only: bool = True
):
    """Search for contractors."""
    service = get_marketplace_service()
    return service.search_contractors(
        city=city,
        state=state,
        min_rating=min_rating,
        verified_only=verified_only
    )


@router.get("/marketplace/contractor/{contractor_id}")
async def get_contractor(contractor_id: str):
    """Get contractor details."""
    service = get_marketplace_service()
    contractor = service.get_contractor(contractor_id)
    if not contractor:
        raise HTTPException(status_code=404, detail="Contractor not found")
    return contractor


@router.post("/marketplace/quote/request")
async def create_quote_request(request: QuoteRequestCreate):
    """Create a quote request."""
    service = get_marketplace_service()
    return service.create_quote_request(
        project_id=request.project_id,
        user_id=request.user_id,
        property_address=request.property_address,
        city=request.city,
        state=request.state,
        roof_area_sqm=request.roof_area_sqm,
        tank_capacity_liters=request.tank_capacity_liters,
        includes_recharge=request.includes_recharge,
        requirements_description=request.requirements_description,
        contact_name=request.contact_name,
        contact_phone=request.contact_phone,
        preferred_start_date=request.preferred_start_date,
        budget_min=request.budget_min,
        budget_max=request.budget_max
    )


@router.post("/marketplace/quote/submit")
async def submit_quote(request: QuoteSubmit):
    """Submit a quote for a request."""
    service = get_marketplace_service()
    try:
        return service.submit_quote(
            quote_request_id=request.quote_request_id,
            contractor_id=request.contractor_id,
            material_cost=request.material_cost,
            labor_cost=request.labor_cost,
            estimated_days=request.estimated_days,
            proposed_start_date=request.proposed_start_date,
            scope_of_work=request.scope_of_work,
            materials_included=request.materials_included,
            warranty_months=request.warranty_months,
            payment_terms=request.payment_terms
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/marketplace/quote/request/{request_id}/quotes")
async def get_quotes_for_request(request_id: str):
    """Get all quotes for a request."""
    service = get_marketplace_service()
    return service.get_quotes_for_request(request_id)


@router.post("/marketplace/quote/{quote_id}/accept")
async def accept_quote(quote_id: str):
    """Accept a quote and create work order."""
    service = get_marketplace_service()
    try:
        return service.accept_quote(quote_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/marketplace/milestone/{milestone_id}")
async def update_milestone(milestone_id: str, request: MilestoneUpdateRequest):
    """Update milestone status."""
    service = get_marketplace_service()
    try:
        return service.update_milestone(
            milestone_id=milestone_id,
            status=request.status,
            photos=request.photos,
            notes=request.notes
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/marketplace/milestone/{milestone_id}/verify")
async def verify_milestone(
    milestone_id: str,
    verified_by: str,
    approved: bool,
    rejection_reason: str = ""
):
    """Verify a completed milestone."""
    service = get_marketplace_service()
    try:
        return service.verify_milestone(
            milestone_id=milestone_id,
            verified_by=verified_by,
            approved=approved,
            rejection_reason=rejection_reason
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/marketplace/review")
async def submit_review(request: ReviewSubmit):
    """Submit a contractor review."""
    service = get_marketplace_service()
    try:
        return service.submit_review(
            contractor_id=request.contractor_id,
            project_id=request.project_id,
            work_order_id=request.work_order_id,
            user_id=request.user_id,
            overall_rating=request.overall_rating,
            quality_rating=request.quality_rating,
            timeliness_rating=request.timeliness_rating,
            communication_rating=request.communication_rating,
            value_rating=request.value_rating,
            review_text=request.review_text,
            would_recommend=request.would_recommend,
            photos=request.photos
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/marketplace/defect/report")
async def report_defect(request: DefectReportRequest):
    """Report a defect in installation."""
    service = get_marketplace_service()
    return service.report_defect(
        project_id=request.project_id,
        work_order_id=request.work_order_id,
        user_id=request.user_id,
        defect_type=request.defect_type,
        defect_description=request.defect_description,
        defect_location=request.defect_location,
        severity=request.severity,
        photos=request.photos,
        detected_date=request.detected_date
    )


# ==================== PERFORMANCE ENDPOINTS ====================

@router.get("/performance/{project_id}/annual/{year}")
async def get_annual_performance(project_id: int, year: int):
    """Get annual performance report."""
    service = get_performance_service()
    return service.get_annual_performance_report(project_id, year)


@router.get("/performance/{project_id}/comparison")
async def get_neighbor_comparison(project_id: int, city: str, year: Optional[int] = None):
    """Get comparison with neighbors."""
    service = get_performance_service()
    return service.get_neighbor_comparison(project_id, city, year)


@router.get("/performance/leaderboard")
async def get_leaderboard(city: str, state: str, limit: int = 10):
    """Get area leaderboard."""
    service = get_performance_service()
    return service.get_leaderboard(city, state, limit)


@router.post("/performance/{project_id}/maintenance/init")
async def init_maintenance_schedule(
    project_id: int,
    installation_date: date,
    has_recharge: bool = False
):
    """Initialize maintenance schedule."""
    service = get_performance_service()
    return service.initialize_maintenance_schedule(project_id, installation_date, has_recharge)


@router.get("/performance/{project_id}/maintenance/reminders")
async def get_maintenance_reminders(project_id: int, days_ahead: int = 30):
    """Get upcoming maintenance reminders."""
    service = get_performance_service()
    return service.get_maintenance_reminders(project_id, days_ahead)


@router.post("/performance/{project_id}/maintenance/{task_id}/complete")
async def complete_maintenance_task(
    project_id: int,
    task_id: str,
    completed_date: Optional[date] = None,
    notes: str = "",
    cost_incurred: float = 0
):
    """Mark maintenance task as completed."""
    service = get_performance_service()
    try:
        return service.complete_maintenance_task(
            project_id, task_id, completed_date, notes, cost_incurred
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/performance/{project_id}/premonsoon-checklist")
async def get_premonsoon_checklist(project_id: int):
    """Get pre-monsoon preparation checklist."""
    service = get_performance_service()
    return service.get_premonsoon_checklist(project_id)


# ==================== WATER QUALITY ENDPOINTS ====================

@router.post("/quality/sensor/reading")
async def record_quality_reading(request: SensorReadingRequest):
    """Record water quality sensor reading."""
    service = get_water_quality_service()
    return service.record_sensor_reading(
        project_id=request.project_id,
        device_id=request.device_id,
        ph=request.ph,
        tds_ppm=request.tds_ppm,
        turbidity_ntu=request.turbidity_ntu,
        temperature_c=request.temperature_c,
        dissolved_oxygen_ppm=request.dissolved_oxygen_ppm
    )


@router.post("/quality/lab-test")
async def upload_lab_test(request: LabTestUploadRequest):
    """Upload lab test results."""
    service = get_water_quality_service()
    return service. upload_lab_test(
        project_id=request.project_id,
        test_date=request.test_date,
        lab_name=request.lab_name,
        ph=request.ph,
        tds_ppm=request.tds_ppm,
        turbidity_ntu=request.turbidity_ntu,
        hardness_ppm=request.hardness_ppm,
        chloride_ppm=request.chloride_ppm,
        nitrate_ppm=request.nitrate_ppm,
        fluoride_ppm=request.fluoride_ppm,
        iron_ppm=request.iron_ppm,
        coliform_present=request.coliform_present,
        e_coli_present=request.e_coli_present,
        report_url=request.report_url
    )


@router.get("/quality/{project_id}/history")
async def get_quality_history(project_id: int, days: int = 30):
    """Get quality history for a project."""
    service = get_water_quality_service()
    return service.get_quality_history(project_id, days)


@router.get("/quality/{project_id}/alerts")
async def get_quality_alerts(project_id: int, unacknowledged_only: bool = True):
    """Get quality alerts."""
    service = get_water_quality_service()
    return service.get_quality_alerts(project_id, unacknowledged_only)


@router.post("/quality/{project_id}/alert/{alert_id}/acknowledge")
async def acknowledge_quality_alert(project_id: int, alert_id: str):
    """Acknowledge a quality alert."""
    service = get_water_quality_service()
    if service.acknowledge_alert(project_id, alert_id):
        return {"success": True}
    raise HTTPException(status_code=404, detail="Alert not found")


# ==================== IOT ENDPOINTS ====================

@router.post("/iot/device/pairing-qr")
async def generate_pairing_qr(project_id: int, device_type: str):
    """Generate QR code for device pairing."""
    service = get_enhanced_iot_service()
    try:
        return service.generate_pairing_qr(project_id, device_type)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/iot/device/pair")
async def pair_device(request: DevicePairRequest):
    """Pair a new IoT device."""
    service = get_enhanced_iot_service()
    try:
        return service.pair_device(
            project_id=request.project_id,
            device_type=request.device_type,
            device_serial=request.device_serial,
            device_name=request.device_name
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/iot/devices/{project_id}")
async def get_project_devices(project_id: int):
    """Get all IoT devices for a project."""
    service = get_enhanced_iot_service()
    return service.get_project_devices(project_id)


@router.post("/iot/calibration/start")
async def start_calibration(request: CalibrationStartRequest):
    """Start calibration wizard."""
    service = get_enhanced_iot_service()
    try:
        return service.start_calibration(
            device_id=request.device_id,
            tank_capacity_liters=request.tank_capacity_liters,
            tank_shape=request.tank_shape
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/iot/calibration/point")
async def record_calibration_point(request: CalibrationPointRequest):
    """Record a calibration point."""
    service = get_enhanced_iot_service()
    try:
        return service.record_calibration_point(
            calibration_id=request.calibration_id,
            step=request.step,
            sensor_reading=request.sensor_reading,
            known_volume_liters=request.known_volume_liters
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/iot/device/{device_id}/convert-reading")
async def convert_sensor_reading(device_id: str, sensor_reading: float):
    """Convert raw sensor reading to volume."""
    service = get_enhanced_iot_service()
    try:
        return service.convert_reading_to_volume(device_id, sensor_reading)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/iot/{project_id}/leak-detection")
async def detect_leak(project_id: int):
    """Run leak detection algorithm."""
    service = get_enhanced_iot_service()
    return service.detect_leak(project_id)


@router.post("/iot/overflow-prediction")
async def predict_overflow(request: OverflowPredictionRequest):
    """Predict tank overflow based on weather."""
    service = get_enhanced_iot_service()
    return service.predict_overflow(
        project_id=request.project_id,
        current_level_percent=request.current_level_percent,
        tank_capacity_liters=request.tank_capacity_liters,
        expected_rainfall_mm=request.expected_rainfall_mm,
        roof_area_sqm=request.roof_area_sqm,
        runoff_coefficient=request.runoff_coefficient
    )


@router.post("/iot/{project_id}/first-flush/log")
async def log_first_flush(
    project_id: int,
    device_id: str,
    diversion_liters: float,
    rainfall_mm: float
):
    """Log first flush trigger event."""
    service = get_enhanced_iot_service()
    return service.log_first_flush_trigger(
        project_id, device_id, diversion_liters, rainfall_mm
    )


@router.get("/iot/{project_id}/first-flush/history")
async def get_first_flush_history(project_id: int, days: int = 30):
    """Get first flush history."""
    service = get_enhanced_iot_service()
    return service.get_first_flush_history(project_id, days)


@router.get("/iot/{project_id}/alerts")
async def get_iot_alerts(
    project_id: int,
    alert_type: Optional[str] = None,
    unacknowledged_only: bool = True
):
    """Get IoT alerts."""
    service = get_enhanced_iot_service()
    return service.get_alerts(project_id, alert_type, unacknowledged_only)


@router.post("/iot/{project_id}/alert/{alert_id}/acknowledge")
async def acknowledge_iot_alert(project_id: int, alert_id: str):
    """Acknowledge an IoT alert."""
    service = get_enhanced_iot_service()
    if service.acknowledge_alert(project_id, alert_id):
        return {"success": True}
    raise HTTPException(status_code=404, detail="Alert not found")
