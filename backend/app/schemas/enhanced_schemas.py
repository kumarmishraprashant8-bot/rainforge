"""
RainForge Enhanced Schemas - Complete Government Platform Edition
All possible user inputs and outputs for comprehensive RWH assessment.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime, date


# ============================================================================
# ENHANCED ENUMS - All possible input categories
# ============================================================================

class PropertyType(str, Enum):
    """Type of property for RWH installation."""
    RESIDENTIAL_INDIVIDUAL = "residential_individual"
    RESIDENTIAL_APARTMENT = "residential_apartment"
    COMMERCIAL = "commercial"
    INDUSTRIAL = "industrial"
    INSTITUTIONAL_SCHOOL = "institutional_school"
    INSTITUTIONAL_HOSPITAL = "institutional_hospital"
    INSTITUTIONAL_GOVT = "institutional_govt"
    RELIGIOUS = "religious"
    AGRICULTURAL = "agricultural"


class OwnershipStatus(str, Enum):
    """Property ownership status."""
    OWNER = "owner"
    TENANT = "tenant"
    SOCIETY = "society"
    GOVERNMENT = "government"
    JOINT_OWNERSHIP = "joint_ownership"


class IncomeCategory(str, Enum):
    """Income category for subsidy calculation."""
    EWS = "ews"  # Economically Weaker Section (<3 LPA)
    LIG = "lig"  # Low Income Group (3-6 LPA)
    MIG_I = "mig_i"  # Middle Income Group I (6-12 LPA)
    MIG_II = "mig_ii"  # Middle Income Group II (12-18 LPA)
    HIG = "hig"  # High Income Group (>18 LPA)
    NOT_DISCLOSED = "not_disclosed"


class EndUseType(str, Enum):
    """Intended end use of harvested rainwater."""
    DRINKING = "drinking"
    NON_POTABLE = "non_potable"  # Toilet, washing, gardening
    RECHARGE_ONLY = "recharge_only"
    MIXED = "mixed"
    INDUSTRIAL_PROCESS = "industrial_process"
    IRRIGATION = "irrigation"


class RoofCondition(str, Enum):
    """Current condition of the roof."""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    NEEDS_REPAIR = "needs_repair"


class RoofType(str, Enum):
    """Roof material type."""
    RCC = "rcc"
    METAL_GI = "metal_gi"
    METAL_ALUMINUM = "metal_aluminum"
    CLAY_TILE = "clay_tile"
    CONCRETE_TILE = "concrete_tile"
    ASBESTOS = "asbestos"
    THATCHED = "thatched"
    POLYCARBONATE = "polycarbonate"
    GREEN_ROOF = "green_roof"


class SoilType(str, Enum):
    """Soil type for recharge assessment."""
    SANDY = "sandy"
    LOAMY = "loamy"
    CLAYEY = "clayey"
    ROCKY = "rocky"
    LATERITE = "laterite"
    BLACK_COTTON = "black_cotton"
    ALLUVIAL = "alluvial"


class WaterSource(str, Enum):
    """Current water source."""
    MUNICIPAL = "municipal"
    BOREWELL = "borewell"
    TANKER = "tanker"
    WELL = "well"
    RIVER = "river"
    POND = "pond"
    NONE = "none"
    MULTIPLE = "multiple"


class StoragePreference(str, Enum):
    """Storage preference for harvested water."""
    UNDERGROUND_TANK = "underground_tank"
    OVERHEAD_TANK = "overhead_tank"
    SURFACE_TANK = "surface_tank"
    RECHARGE_PIT = "recharge_pit"
    RECHARGE_WELL = "recharge_well"
    HYBRID = "hybrid"


class PaymentMode(str, Enum):
    """Preferred payment mode."""
    UPI = "upi"
    NEFT = "neft"
    RTGS = "rtgs"
    CHEQUE = "cheque"
    CASH = "cash"
    DBT = "dbt"  # Direct Benefit Transfer


class Language(str, Enum):
    """Supported languages."""
    ENGLISH = "en"
    HINDI = "hi"
    TAMIL = "ta"
    TELUGU = "te"
    KANNADA = "kn"
    MARATHI = "mr"
    GUJARATI = "gu"
    BENGALI = "bn"
    MALAYALAM = "ml"
    PUNJABI = "pa"
    ODIA = "or"


class ContractorStatus(str, Enum):
    """Contractor status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING_VERIFICATION = "pending_verification"


class QuoteStatus(str, Enum):
    """Quote request status."""
    PENDING = "pending"
    RECEIVED = "received"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    EXPIRED = "expired"


class WorkOrderStatus(str, Enum):
    """Work order status."""
    CREATED = "created"
    IN_PROGRESS = "in_progress"
    MILESTONE_PENDING = "milestone_pending"
    COMPLETED = "completed"
    DISPUTED = "disputed"
    CANCELLED = "cancelled"


class MilestoneType(str, Enum):
    """Work milestone types."""
    SITE_SURVEY = "site_survey"
    MATERIAL_PROCUREMENT = "material_procurement"
    GUTTER_INSTALLATION = "gutter_installation"
    FILTER_INSTALLATION = "filter_installation"
    TANK_INSTALLATION = "tank_installation"
    PLUMBING = "plumbing"
    RECHARGE_PIT = "recharge_pit"
    TESTING = "testing"
    HANDOVER = "handover"


class AlertType(str, Enum):
    """IoT alert types."""
    TANK_LOW = "tank_low"
    TANK_OVERFLOW = "tank_overflow"
    LEAK_DETECTED = "leak_detected"
    QUALITY_ISSUE = "quality_issue"
    MAINTENANCE_DUE = "maintenance_due"
    SENSOR_OFFLINE = "sensor_offline"
    FIRST_FLUSH_TRIGGERED = "first_flush_triggered"


class CertificateType(str, Enum):
    """Certificate types."""
    INSTALLATION = "installation"
    COMPLIANCE = "compliance"
    WATER_CREDIT = "water_credit"
    MAINTENANCE = "maintenance"
    PERFORMANCE = "performance"


# ============================================================================
# ROOF ZONE MODEL - For multiple roof zones
# ============================================================================

class RoofZone(BaseModel):
    """Single roof zone with specific characteristics."""
    zone_id: str = Field(..., description="Unique zone identifier")
    zone_name: str = Field(..., description="Descriptive name (e.g., 'Main Building')")
    area_sqm: float = Field(..., gt=0, description="Area in square meters")
    roof_type: RoofType = Field(RoofType.RCC)
    roof_condition: RoofCondition = Field(RoofCondition.GOOD)
    slope_degrees: int = Field(5, ge=0, le=45)
    shade_coverage_percent: int = Field(0, ge=0, le=100, description="% of roof under shade")
    
    class Config:
        json_schema_extra = {
            "example": {
                "zone_id": "zone_1",
                "zone_name": "Main Building Terrace",
                "area_sqm": 100,
                "roof_type": "rcc",
                "roof_condition": "good",
                "slope_degrees": 5,
                "shade_coverage_percent": 10
            }
        }


# ============================================================================
# USER PROFILE SCHEMAS
# ============================================================================

class KYCDetails(BaseModel):
    """KYC verification details."""
    aadhaar_number: Optional[str] = Field(None, min_length=12, max_length=12)
    aadhaar_verified: bool = False
    pan_number: Optional[str] = Field(None, pattern=r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$')
    voter_id: Optional[str] = None
    driving_license: Optional[str] = None
    verification_date: Optional[datetime] = None
    verification_status: str = "pending"


class BankDetails(BaseModel):
    """Bank account details for subsidy disbursement."""
    account_holder_name: str
    account_number: str = Field(..., min_length=9, max_length=18)
    ifsc_code: str = Field(..., pattern=r'^[A-Z]{4}0[A-Z0-9]{6}$')
    bank_name: str
    branch_name: str
    account_type: str = "savings"  # savings, current
    upi_id: Optional[str] = None
    verified: bool = False


class UserProfileInput(BaseModel):
    """Complete user profile input."""
    # Basic Info
    full_name: str = Field(..., min_length=2, max_length=100)
    email: Optional[str] = None
    phone: str = Field(..., pattern=r'^\+?[0-9]{10,13}$')
    alternate_phone: Optional[str] = None
    
    # Address
    address_line1: str
    address_line2: Optional[str] = None
    city: str
    district: str
    state: str
    pincode: str = Field(..., pattern=r'^[0-9]{6}$')
    
    # KYC
    kyc: Optional[KYCDetails] = None
    
    # Bank
    bank_details: Optional[BankDetails] = None
    
    # Preferences
    preferred_language: Language = Language.ENGLISH
    preferred_payment_mode: PaymentMode = PaymentMode.UPI
    
    # Notifications
    email_notifications: bool = True
    sms_notifications: bool = True
    whatsapp_notifications: bool = False
    push_notifications: bool = True


# ============================================================================
# PROPERTY DETAILS SCHEMAS
# ============================================================================

class PropertyDetailsInput(BaseModel):
    """Complete property details input."""
    # Property Type
    property_type: PropertyType = PropertyType.RESIDENTIAL_INDIVIDUAL
    ownership_status: OwnershipStatus = OwnershipStatus.OWNER
    
    # Registration
    property_registration_number: Optional[str] = None
    property_tax_id: Optional[str] = None
    electricity_consumer_number: Optional[str] = None
    water_connection_number: Optional[str] = None
    
    # Building Details
    building_name: Optional[str] = None
    plot_number: Optional[str] = None
    ward_number: Optional[str] = None
    gram_panchayat: Optional[str] = None  # For rural areas
    
    # Existing Infrastructure
    existing_rwh_system: bool = False
    existing_rwh_type: Optional[str] = None
    existing_rwh_capacity: Optional[float] = None
    
    # Area Details
    plot_area_sqm: float = Field(..., gt=0)
    built_up_area_sqm: float = Field(..., gt=0)
    open_area_sqm: float = Field(0, ge=0)
    
    # Building Specifics
    num_floors: int = Field(1, ge=1, le=50)
    building_age_years: int = Field(0, ge=0, le=200)
    construction_year: Optional[int] = None


# ============================================================================
# FINANCIAL DETAILS SCHEMAS
# ============================================================================

class SubsidyHistory(BaseModel):
    """Previous subsidy availed."""
    scheme_name: str
    amount_received: float
    year_availed: int
    certificate_number: Optional[str] = None


class FinancialDetailsInput(BaseModel):
    """Complete financial details input."""
    # Income
    income_category: IncomeCategory = IncomeCategory.NOT_DISCLOSED
    annual_income_range: Optional[str] = None
    
    # BPL Status
    is_bpl: bool = False
    bpl_card_number: Optional[str] = None
    apl_card_number: Optional[str] = None
    ration_card_number: Optional[str] = None
    
    # Previous Subsidies
    previous_subsidies: List[SubsidyHistory] = []
    
    # Budget
    budget_min_inr: Optional[float] = None
    budget_max_inr: Optional[float] = None
    
    # Financing
    needs_financing: bool = False
    emi_preference: bool = False
    preferred_emi_tenure_months: Optional[int] = None
    
    # Insurance
    wants_insurance: bool = False
    
    # Current Water Expenses
    monthly_water_bill_inr: float = Field(500, ge=0)
    monthly_tanker_expense_inr: float = Field(0, ge=0)


# ============================================================================
# ADVANCED TECHNICAL INPUT SCHEMAS
# ============================================================================

class PollutionSource(BaseModel):
    """Nearby pollution source."""
    source_type: str  # factory, traffic, construction, etc.
    distance_meters: float
    direction: str  # N, S, E, W, NE, etc.
    severity: str = "low"  # low, medium, high


class AdvancedTechnicalInput(BaseModel):
    """Advanced technical assessment inputs."""
    # Multiple Roof Zones
    roof_zones: List[RoofZone] = []
    
    # Location Precision
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    elevation_m: Optional[float] = None
    
    # Ground Conditions
    soil_type: SoilType = SoilType.LOAMY
    groundwater_depth_m: float = Field(10, ge=0)
    groundwater_quality: str = "unknown"  # good, moderate, poor, unknown
    water_table_trend: str = "stable"  # rising, stable, falling
    
    # Available Space
    available_ground_area_sqm: float = Field(10, ge=0)
    available_terrace_area_sqm: float = Field(0, ge=0)
    basement_available: bool = False
    
    # Environmental Factors
    pollution_sources: List[PollutionSource] = []
    industrial_area: bool = False
    traffic_density: str = "low"  # low, medium, high
    nearby_trees: bool = False
    bird_activity: str = "low"  # low, medium, high
    
    # Climate Zone
    climate_zone: str = "tropical"  # tropical, subtropical, arid, etc.
    monsoon_type: str = "southwest"  # southwest, northeast, both
    
    # Water Details
    current_water_sources: List[WaterSource] = [WaterSource.MUNICIPAL]
    daily_water_demand_liters: float = Field(500, gt=0)
    seasonal_demand_variation: bool = False
    peak_demand_months: List[str] = []
    
    # End Use
    end_use: EndUseType = EndUseType.NON_POTABLE
    drinking_water_required: bool = False
    
    # Preferences
    storage_preference: StoragePreference = StoragePreference.UNDERGROUND_TANK
    aesthetic_preference: str = "functional"  # functional, aesthetic, hidden


# ============================================================================
# COMPLETE ENHANCED ASSESSMENT REQUEST
# ============================================================================

class CompleteEnhancedAssessmentRequest(BaseModel):
    """Complete assessment request with all possible inputs."""
    
    # User Profile
    user_profile: Optional[UserProfileInput] = None
    
    # Property Details
    property_details: PropertyDetailsInput
    
    # Financial Details
    financial_details: Optional[FinancialDetailsInput] = None
    
    # Technical Details
    technical_details: AdvancedTechnicalInput
    
    # Quick Assessment Flag
    is_quick_assessment: bool = False
    
    # Metadata
    source: str = "web"  # web, mobile, api, offline
    referral_code: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "property_details": {
                    "property_type": "residential_individual",
                    "ownership_status": "owner",
                    "plot_area_sqm": 200,
                    "built_up_area_sqm": 150,
                    "num_floors": 2
                },
                "technical_details": {
                    "roof_zones": [
                        {
                            "zone_id": "main",
                            "zone_name": "Main Terrace",
                            "area_sqm": 100,
                            "roof_type": "rcc",
                            "roof_condition": "good",
                            "slope_degrees": 5
                        }
                    ],
                    "latitude": 12.9716,
                    "longitude": 77.5946,
                    "soil_type": "loamy",
                    "daily_water_demand_liters": 600,
                    "end_use": "mixed"
                }
            }
        }


# ============================================================================
# CONTRACTOR / MARKETPLACE SCHEMAS
# ============================================================================

class ContractorProfile(BaseModel):
    """Contractor profile."""
    id: str
    company_name: str
    owner_name: str
    phone: str
    email: Optional[str] = None
    
    # Registration
    gst_number: Optional[str] = None
    license_number: Optional[str] = None
    
    # Location
    city: str
    state: str
    service_areas: List[str] = []
    
    # Experience
    years_experience: int = 0
    projects_completed: int = 0
    
    # Ratings
    average_rating: float = 0.0
    total_reviews: int = 0
    
    # Certifications
    certifications: List[str] = []
    
    # Status
    status: ContractorStatus = ContractorStatus.ACTIVE
    verified: bool = False


class QuoteRequest(BaseModel):
    """Quote request from user."""
    project_id: int
    property_address: str
    city: str
    state: str
    
    # Scope
    roof_area_sqm: float
    tank_capacity_liters: int
    includes_recharge: bool = False
    
    # Requirements
    requirements_description: str
    preferred_start_date: Optional[date] = None
    budget_range_min: Optional[float] = None
    budget_range_max: Optional[float] = None
    
    # Contact
    contact_name: str
    contact_phone: str
    preferred_contact_time: str = "anytime"


class QuoteResponse(BaseModel):
    """Quote response from contractor."""
    quote_id: str
    contractor_id: str
    project_id: int
    
    # Pricing
    material_cost: float
    labor_cost: float
    total_cost: float
    
    # Timeline
    estimated_days: int
    proposed_start_date: date
    
    # Details
    scope_of_work: str
    materials_included: List[str]
    warranty_months: int = 12
    
    # Terms
    payment_terms: str
    validity_days: int = 15
    
    # Status
    status: QuoteStatus = QuoteStatus.PENDING
    created_at: datetime


class WorkOrderCreate(BaseModel):
    """Create work order after accepting quote."""
    quote_id: str
    contractor_id: str
    project_id: int
    agreed_amount: float
    
    # Milestones
    milestones: List[Dict[str, Any]] = []
    
    # Terms
    advance_percent: int = 20
    retention_percent: int = 10


class MilestoneUpdate(BaseModel):
    """Update milestone status."""
    milestone_id: str
    work_order_id: str
    status: str  # pending, in_progress, completed, verified
    completion_date: Optional[datetime] = None
    
    # Verification
    photos: List[str] = []  # Photo URLs
    notes: str = ""
    verified_by: Optional[str] = None


class ContractorReview(BaseModel):
    """Review for contractor."""
    contractor_id: str
    project_id: int
    work_order_id: str
    
    # Ratings
    overall_rating: int = Field(..., ge=1, le=5)
    quality_rating: int = Field(..., ge=1, le=5)
    timeliness_rating: int = Field(..., ge=1, le=5)
    communication_rating: int = Field(..., ge=1, le=5)
    value_rating: int = Field(..., ge=1, le=5)
    
    # Feedback
    review_text: str
    would_recommend: bool = True
    
    # Media
    photos: List[str] = []


class DefectReport(BaseModel):
    """Report defect in installation."""
    project_id: int
    work_order_id: str
    
    # Defect Details
    defect_type: str  # leak, crack, blockage, malfunction, etc.
    defect_description: str
    severity: str = "medium"  # low, medium, high, critical
    
    # Evidence
    photos: List[str] = []
    video_url: Optional[str] = None
    
    # Location
    defect_location: str
    
    # Dates
    detected_date: date
    reported_date: datetime


# ============================================================================
# COMPLIANCE & CERTIFICATE SCHEMAS
# ============================================================================

class ComplianceRequirement(BaseModel):
    """Compliance requirement for a state/city."""
    state: str
    city: Optional[str] = None
    
    # Thresholds
    mandatory_above_sqm: float
    permit_required_above_sqm: float
    
    # Authority
    permit_authority: str
    permit_fee_inr: float
    estimated_days: int
    
    # Documents
    required_documents: List[str]
    
    # Subsidy
    subsidy_available: bool
    subsidy_percent: float
    max_subsidy_inr: float


class ComplianceCertificateRequest(BaseModel):
    """Request for compliance certificate."""
    project_id: int
    certificate_type: CertificateType
    
    # Project Details
    owner_name: str
    property_address: str
    city: str
    state: str
    
    # Installation Details
    tank_capacity_liters: int
    installation_date: date
    installer_name: str
    installer_license: Optional[str] = None
    
    # Verification
    verification_date: Optional[date] = None
    verified_by: Optional[str] = None
    
    # Optional
    include_qr_code: bool = True
    language: Language = Language.ENGLISH


class ComplianceCertificateResponse(BaseModel):
    """Compliance certificate response."""
    certificate_id: str
    certificate_number: str
    project_id: int
    
    # Validity
    issue_date: date
    valid_until: date
    
    # Certificate
    certificate_type: CertificateType
    certificate_url: str
    qr_code_url: Optional[str] = None
    
    # Verification
    verification_url: str


# ============================================================================
# PERFORMANCE TRACKING SCHEMAS
# ============================================================================

class MonthlyPerformanceData(BaseModel):
    """Monthly performance data."""
    month: str
    year: int
    
    # Actual
    actual_rainfall_mm: float
    actual_collection_liters: float
    actual_usage_liters: float
    
    # Projected
    projected_collection_liters: float
    
    # Efficiency
    collection_efficiency_percent: float
    
    # IoT Readings
    avg_tank_level_percent: float
    days_data_available: int


class AnnualPerformanceReport(BaseModel):
    """Annual performance report."""
    project_id: int
    year: int
    
    # Summary
    total_rainfall_mm: float
    total_collection_liters: float
    total_usage_liters: float
    total_overflow_liters: float
    
    # Comparison
    projected_collection_liters: float
    actual_vs_projected_percent: float
    
    # Savings
    water_bill_savings_inr: float
    tanker_savings_inr: float
    total_savings_inr: float
    
    # Environmental
    carbon_offset_kg: float
    groundwater_recharged_liters: float
    
    # Monthly Breakdown
    monthly_data: List[MonthlyPerformanceData]
    
    # Maintenance
    maintenance_completed: int
    maintenance_pending: int
    
    # Scores
    performance_score: int  # 0-100
    reliability_score: int  # 0-100


class NeighborComparison(BaseModel):
    """Comparison with neighbors."""
    project_id: int
    
    # Your Stats
    your_collection_liters: float
    your_efficiency_percent: float
    your_savings_inr: float
    
    # Area Stats
    area_average_collection: float
    area_average_efficiency: float
    area_average_savings: float
    
    # Ranking
    area_rank: int
    total_in_area: int
    percentile: int
    
    # Leaderboard
    top_performers: List[Dict[str, Any]]


# ============================================================================
# IOT & MONITORING SCHEMAS
# ============================================================================

class WaterQualityReading(BaseModel):
    """Water quality sensor reading."""
    project_id: int
    timestamp: datetime
    
    # Readings
    ph: Optional[float] = Field(None, ge=0, le=14)
    tds_ppm: Optional[float] = Field(None, ge=0)
    turbidity_ntu: Optional[float] = Field(None, ge=0)
    temperature_c: Optional[float] = None
    dissolved_oxygen_ppm: Optional[float] = None
    
    # Status
    overall_quality: str = "unknown"  # good, acceptable, poor, unsafe
    potable: bool = False


class WaterQualityTestUpload(BaseModel):
    """Upload water quality test results."""
    project_id: int
    test_date: date
    lab_name: str
    
    # Results
    ph: float
    tds_ppm: float
    turbidity_ntu: float
    hardness_ppm: Optional[float] = None
    chloride_ppm: Optional[float] = None
    nitrate_ppm: Optional[float] = None
    fluoride_ppm: Optional[float] = None
    iron_ppm: Optional[float] = None
    coliform_present: Optional[bool] = None
    e_coli_present: Optional[bool] = None
    
    # Report
    report_url: Optional[str] = None
    
    # Recommendation
    suitable_for_drinking: bool
    treatment_required: List[str] = []


class DevicePairingRequest(BaseModel):
    """Request to pair IoT device."""
    project_id: int
    device_type: str  # tank_sensor, flow_meter, quality_sensor, rain_gauge
    device_serial: str
    
    # Optional
    device_name: Optional[str] = None
    installation_location: str = ""


class DeviceCalibration(BaseModel):
    """Device calibration data."""
    device_id: str
    project_id: int
    
    # Tank Calibration
    tank_capacity_liters: Optional[int] = None
    tank_height_cm: Optional[float] = None
    tank_shape: str = "cylindrical"  # cylindrical, rectangular, custom
    
    # Custom Shape
    volume_at_levels: Optional[Dict[int, float]] = None  # {level_cm: volume_liters}
    
    # Flow Meter
    pulses_per_liter: Optional[float] = None


class IoTAlert(BaseModel):
    """IoT alert."""
    alert_id: str
    project_id: int
    device_id: str
    
    # Alert Details
    alert_type: AlertType
    severity: str  # info, warning, critical
    message: str
    
    # Data
    trigger_value: Optional[float] = None
    threshold_value: Optional[float] = None
    
    # Timestamps
    triggered_at: datetime
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    
    # Actions
    action_taken: Optional[str] = None


class OverflowPrediction(BaseModel):
    """Tank overflow prediction."""
    project_id: int
    current_level_percent: float
    current_volume_liters: float
    tank_capacity_liters: int
    
    # Prediction
    will_overflow: bool
    hours_until_overflow: Optional[float] = None
    predicted_overflow_time: Optional[datetime] = None
    
    # Weather
    expected_rainfall_mm: float
    expected_collection_liters: float
    
    # Recommendation
    recommended_action: str


class LeakDetection(BaseModel):
    """Leak detection alert."""
    project_id: int
    device_id: str
    
    # Detection
    leak_detected: bool
    leak_location: str = "unknown"
    estimated_loss_liters_per_day: float
    
    # Evidence
    consecutive_readings: int
    unexpected_level_drop_cm: float
    
    # Timeline
    detected_at: datetime
    monitoring_since: datetime


# ============================================================================
# EXPORT SCHEMAS
# ============================================================================

class ExportRequest(BaseModel):
    """Export data request."""
    project_id: int
    export_type: str  # csv, excel, pdf
    
    # Data Range
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    
    # Data Types
    include_readings: bool = True
    include_alerts: bool = True
    include_maintenance: bool = True
    
    # Delivery
    delivery_method: str = "download"  # download, email, whatsapp, sms
    delivery_destination: Optional[str] = None  # email/phone
    
    # Language
    language: Language = Language.ENGLISH


class WhatsAppReportRequest(BaseModel):
    """Request to send report via WhatsApp."""
    project_id: int
    phone_number: str
    report_type: str  # daily, weekly, monthly, annual
    include_charts: bool = True
    language: Language = Language.ENGLISH


class SMSReportRequest(BaseModel):
    """Request to send report via SMS."""
    project_id: int
    phone_number: str
    report_type: str  # summary, alert, status
    language: Language = Language.ENGLISH


# ============================================================================
# GOVERNMENT / INSTITUTIONAL SCHEMAS
# ============================================================================

class InstitutionalAssessmentRequest(BaseModel):
    """Assessment request for institutional buildings."""
    institution_type: str  # school, hospital, govt_office, etc.
    institution_name: str
    
    # UDISE/NIN for schools, hospital registration for hospitals
    registration_number: str
    
    # JJM Details (for Jal Jeevan Mission)
    jjm_id: Optional[str] = None
    
    # Location
    address: str
    city: str
    district: str
    state: str
    block: Optional[str] = None
    gram_panchayat: Optional[str] = None
    
    # Building
    total_built_up_sqm: float
    num_buildings: int = 1
    
    # Beneficiaries
    daily_footfall: int
    students_count: Optional[int] = None
    staff_count: Optional[int] = None
    bed_count: Optional[int] = None  # For hospitals
    
    # Water
    daily_water_requirement_liters: float
    current_water_source: WaterSource


class WardHeatmapRequest(BaseModel):
    """Request for ward-level heatmap."""
    city: str
    state: str
    
    # Filters
    property_types: List[PropertyType] = []
    min_roof_area: Optional[float] = None
    
    # Metrics
    metric: str = "potential"  # potential, installed, efficiency, savings


class TankerReductionCalculation(BaseModel):
    """Tanker trip reduction calculation for municipalities."""
    city: str
    state: str
    
    # Current Tanker Usage
    daily_tanker_trips: int
    tanker_capacity_liters: int
    cost_per_trip_inr: float
    
    # RWH Coverage
    total_properties: int
    rwh_installed_count: int
    avg_collection_liters_per_property: float
    
    # Output
    trips_reduced_per_day: int
    daily_savings_inr: float
    annual_savings_inr: float
    water_self_sufficiency_percent: float


class FloodRiskReduction(BaseModel):
    """Flood risk reduction calculation."""
    city: str
    ward: str
    
    # Area Details
    total_roof_area_sqm: float
    impermeable_ground_sqm: float
    
    # RWH Impact
    rwh_coverage_percent: float
    total_storage_liters: float
    total_recharge_liters: float
    
    # Risk Metrics
    reduced_runoff_liters: float
    flood_risk_reduction_percent: float
    peak_discharge_reduction_percent: float
