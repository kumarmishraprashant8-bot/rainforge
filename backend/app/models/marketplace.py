"""
RainForge Marketplace Database Models
Core models for allocation, bidding, payments, verification, and AMC.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from enum import Enum


# ============== ENUMS ==============

class AllocationMode(str, Enum):
    USER_CHOICE = "user_choice"
    GOV_OPTIMIZED = "gov_optimized"
    EQUITABLE = "equitable"


class BidStatus(str, Enum):
    PENDING = "pending"
    AWARDED = "awarded"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


class PaymentStatus(str, Enum):
    PENDING = "pending"
    ESCROW = "escrow"
    PARTIAL_RELEASED = "partial_released"
    RELEASED = "released"
    REFUNDED = "refunded"


class MilestoneStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    VERIFIED = "verified"
    RELEASED = "released"


class VerificationStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    FLAGGED = "flagged"
    REWORK = "rework"


class CertLevel(str, Enum):
    BASIC = "basic"
    CERTIFIED = "certified"
    ADVANCED = "advanced"
    MASTER = "master"


class AMCTier(str, Enum):
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"


# ============== INSTALLER MODELS ==============

class InstallerBase(BaseModel):
    id: int
    name: str
    company: str
    phone: str
    email: str
    address: str
    lat: float
    lng: float
    service_radius_km: float = 50.0
    is_verified: bool = False
    is_blacklisted: bool = False


class InstallerRPI(BaseModel):
    installer_id: int
    rpi_score: float = Field(ge=0, le=100)
    design_match_pct: float = 0.0
    yield_accuracy_pct: float = 0.0
    timeliness_score: float = 0.0
    complaint_rate: float = 0.0
    maintenance_compliance: float = 0.0
    calculated_at: datetime = Field(default_factory=datetime.utcnow)


class InstallerProfile(InstallerBase):
    rpi_score: float = 0.0
    rpi_components: Optional[Dict[str, float]] = None
    cert_level: CertLevel = CertLevel.BASIC
    capacity_estimate: int = 10  # jobs per month
    jobs_completed: int = 0
    avg_rating: float = 0.0
    total_water_captured: int = 0  # liters


# ============== JOB MODELS ==============

class JobBase(BaseModel):
    id: int
    project_id: int
    address: str
    lat: float
    lng: float
    roof_area_sqm: float
    estimated_yield_liters: int
    tank_size_liters: int
    estimated_cost_inr: float


class JobAllocation(BaseModel):
    job_id: int
    allocation_mode: AllocationMode = AllocationMode.USER_CHOICE
    bid_status: str = "closed"
    assigned_installer_id: Optional[int] = None
    allocation_score: Optional[float] = None
    allocation_reason: Optional[str] = None


class JobCreate(BaseModel):
    project_id: int
    address: str
    lat: float = 28.6139
    lng: float = 77.2090
    roof_area_sqm: float
    roof_material: str = "concrete"
    estimated_yield_liters: int
    tank_size_liters: int
    estimated_cost_inr: float
    allocation_mode: AllocationMode = AllocationMode.USER_CHOICE


# ============== BID MODELS ==============

class BidCreate(BaseModel):
    job_id: int
    installer_id: int
    price: float
    timeline_days: int
    warranty_months: int = 12
    notes: Optional[str] = None


class BidResponse(BaseModel):
    id: int
    job_id: int
    installer_id: int
    installer_name: str
    installer_rpi: float
    price: float
    timeline_days: int
    warranty_months: int
    score: float
    status: BidStatus
    created_at: datetime


class BidScoreWeights(BaseModel):
    price_weight: float = 0.35
    timeline_weight: float = 0.20
    warranty_weight: float = 0.15
    rpi_weight: float = 0.30


# ============== ALLOCATION MODELS ==============

class AllocationWeights(BaseModel):
    capacity_weight: float = 0.20
    rpi_weight: float = 0.30
    cost_band_weight: float = 0.20
    distance_weight: float = 0.15
    sla_history_weight: float = 0.15


class AllocationResult(BaseModel):
    job_id: int
    recommended_installer_id: int
    installer_name: str
    score: float
    score_breakdown: Dict[str, float]
    alternatives: List[Dict[str, Any]]


class AllocationRequest(BaseModel):
    job_id: int
    mode: AllocationMode = AllocationMode.GOV_OPTIMIZED
    weights: Optional[AllocationWeights] = None
    force_installer_id: Optional[int] = None


# ============== PAYMENT MODELS ==============

class MilestoneType(str, Enum):
    DESIGN_APPROVAL = "design_approval"
    INSTALLATION_COMPLETE = "installation_complete"
    VERIFICATION_PASSED = "verification_passed"
    POST_PERFORMANCE = "post_performance"


class MilestoneCreate(BaseModel):
    name: str
    amount: float
    sequence: int


class MilestoneResponse(BaseModel):
    id: int
    payment_id: int
    name: str
    amount: float
    status: MilestoneStatus
    sequence: int
    completed_at: Optional[datetime] = None


class PaymentCreate(BaseModel):
    job_id: int
    total_amount: float
    milestones: List[MilestoneCreate]


class PaymentResponse(BaseModel):
    id: int
    job_id: int
    total_amount: float
    escrow_amount: float
    released_amount: float
    status: PaymentStatus
    provider: str
    provider_ref: Optional[str] = None
    milestones: List[MilestoneResponse]
    created_at: datetime


# ============== VERIFICATION MODELS ==============

class VerificationSubmit(BaseModel):
    job_id: int
    photo_url: str
    geo_lat: float
    geo_lng: float
    notes: Optional[str] = None


class VerificationResponse(BaseModel):
    id: int
    job_id: int
    photo_url: str
    geo_lat: float
    geo_lng: float
    geo_distance_m: float
    status: VerificationStatus
    fraud_flags: Optional[Dict[str, Any]] = None
    verifier_notes: Optional[str] = None
    created_at: datetime


class FraudFlag(BaseModel):
    type: str  # photo_reuse, geo_mismatch, timestamp_anomaly
    severity: str  # low, medium, high
    details: str


# ============== AMC & WARRANTY MODELS ==============

class AMCPackage(BaseModel):
    id: int
    name: str
    tier: AMCTier
    price_yearly: float
    features: List[str]
    is_active: bool = True


class WarrantyCreate(BaseModel):
    job_id: int
    amc_package_id: Optional[int] = None
    start_date: date
    duration_months: int = 12
    auto_renew: bool = False


class WarrantyResponse(BaseModel):
    id: int
    job_id: int
    amc_package: Optional[AMCPackage] = None
    start_date: date
    end_date: date
    status: str
    auto_renew: bool


# ============== OUTCOME CONTRACT MODELS ==============

class OutcomeContractCreate(BaseModel):
    job_id: int
    target_capture_liters: int
    monitoring_months: int = 12


class OutcomeContractResponse(BaseModel):
    id: int
    job_id: int
    target_capture_liters: int
    actual_capture_liters: int
    monitoring_start: date
    monitoring_end: date
    achievement_pct: float
    status: str
    final_payment_released: bool


# ============== PUBLIC DASHBOARD MODELS ==============

class WardStats(BaseModel):
    ward_id: str
    ward_name: str
    total_systems: int
    active_systems: int
    total_captured_liters: int
    co2_avoided_kg: float
    funds_spent_inr: float
    beneficiaries: int


class CityExport(BaseModel):
    format: str  # csv, geojson
    data: Any


# ============== AUDIT MODELS ==============

class AuditTrigger(str, Enum):
    RANDOM = "random"
    FRAUD_FLAG = "fraud_flag"
    COMPLAINT = "complaint"
    MANUAL = "manual"


class AuditRecord(BaseModel):
    id: int
    job_id: int
    verification_id: Optional[int] = None
    trigger_type: AuditTrigger
    findings: Dict[str, Any]
    resolution: Optional[str] = None
    auditor_id: Optional[int] = None
    created_at: datetime


# ============== CERTIFICATION MODELS ==============

class CertificationModule(BaseModel):
    module_name: str
    quiz_questions: List[Dict[str, Any]]
    passing_score: int = 70


class CertificationResult(BaseModel):
    installer_id: int
    module_name: str
    quiz_score: int
    passed: bool
    completed_at: datetime
