"""
RainForge Schemas - Government Platform Edition
Pydantic models for API request/response validation.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime


# ============ ENUMS ============

class ScenarioMode(str, Enum):
    COST_OPTIMIZED = "cost_optimized"
    MAX_CAPTURE = "max_capture"
    DRY_SEASON = "dry_season"

class SoilType(str, Enum):
    SANDY = "sandy"
    LOAMY = "loamy"
    CLAY = "clay"
    ROCKY = "rocky"

class VerificationStatus(str, Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"
    INSTALLED = "installed"

class UserRole(str, Enum):
    ADMIN = "admin"
    INSTALLER = "installer"
    VIEWER = "viewer"


# ============ BASE SCHEMAS ============

class RainfallData(BaseModel):
    monthly_mm: List[float]
    annual_mm: float

class ExplanationDetail(BaseModel):
    formula: Optional[str] = None
    variables: Optional[Dict[str, Any]] = None
    calculation: Optional[str] = None
    reference: Optional[str] = None
    method: Optional[str] = None


# ============ ASSESSMENT SCHEMAS ============

class QuickAssessmentRequest(BaseModel):
    address: str
    roof_material: str = "concrete"
    polygon_geojson: Optional[Dict] = None
    roof_area_sqm: Optional[float] = None
    scenario: ScenarioMode = ScenarioMode.COST_OPTIMIZED
    daily_demand_liters: float = 500.0
    include_recharge: bool = False
    soil_type: Optional[SoilType] = None
    groundwater_depth_m: Optional[float] = None

class AssessmentResponse(BaseModel):
    project_id: int
    rainfall_stats: RainfallData
    runoff_potential_liters: float
    recommended_tank_size: float
    monthly_breakdown: List[float]
    message: str
    scenario: Optional[str] = None
    dry_season_yield: Optional[float] = None
    wet_season_yield: Optional[float] = None

class ScenarioComparison(BaseModel):
    scenario: str
    tank_size_liters: float
    estimated_cost_inr: float
    annual_savings_inr: float
    payback_years: float
    reliability_percent: float

class FullAssessmentResponse(BaseModel):
    project_id: int
    address: str
    roof_area_sqm: float
    roof_material: str
    
    # Rainfall
    rainfall_stats: RainfallData
    
    # Yield
    total_yield_liters: float
    monthly_yield: List[float]
    dry_season_yield: float
    wet_season_yield: float
    
    # Scenario comparison
    scenarios: List[ScenarioComparison]
    selected_scenario: str
    
    # Water balance
    water_balance: Optional[Dict] = None
    reliability_percent: float
    
    # Recharge (if applicable)
    recharge_suitability: Optional[Dict] = None
    
    # Costs
    recommended_tank_size: float
    estimated_cost_inr: float
    annual_savings_inr: float
    payback_years: float
    
    # BOM
    bill_of_materials: Optional[List[Dict]] = None
    
    # Policy
    subsidy_eligible: bool = False
    estimated_subsidy_inr: float = 0
    net_cost_inr: float = 0
    
    # Explanations
    explanations: Optional[Dict[str, ExplanationDetail]] = None


# ============ BULK ASSESSMENT SCHEMAS ============

class BulkSiteInput(BaseModel):
    site_id: str
    address: str
    roof_area_sqm: float
    roof_material: str = "concrete"
    lat: Optional[float] = None
    lng: Optional[float] = None

class BulkUploadRequest(BaseModel):
    batch_name: str
    sites: List[BulkSiteInput]
    scenario: ScenarioMode = ScenarioMode.COST_OPTIMIZED

class BulkSiteResult(BaseModel):
    site_id: str
    address: str
    status: str
    annual_yield_liters: float
    tank_size_liters: float
    cost_inr: float
    lat: Optional[float] = None
    lng: Optional[float] = None

class BulkAssessmentResponse(BaseModel):
    batch_id: str
    batch_name: str
    total_sites: int
    processed_sites: int
    failed_sites: int
    
    # Aggregates
    total_capture_liters: float
    total_cost_inr: float
    avg_payback_years: float
    total_beneficiaries: int
    
    # Results
    site_results: List[BulkSiteResult]
    
    # Heatmap data
    heatmap_data: Optional[List[Dict]] = None


# ============ VERIFICATION SCHEMAS ============

class VerificationRequest(BaseModel):
    project_id: int
    photo_url: str
    geo_lat: float
    geo_lng: float
    notes: Optional[str] = None
    installer_id: Optional[int] = None

class VerificationRecord(BaseModel):
    id: int
    project_id: int
    photo_url: str
    geo_lat: float
    geo_lng: float
    timestamp: datetime
    status: VerificationStatus
    verified_by: Optional[int] = None
    notes: Optional[str] = None


# ============ MONITORING SCHEMAS ============

class IoTReading(BaseModel):
    project_id: int
    tank_level_percent: float
    flow_rate_lpm: Optional[float] = None
    rainfall_mm: Optional[float] = None
    timestamp: datetime

class TankStatus(BaseModel):
    project_id: int
    current_level_percent: float
    current_volume_liters: float
    capacity_liters: float
    last_updated: datetime
    predicted_empty_date: Optional[datetime] = None
    maintenance_alerts: List[str] = []

class MonitoringDashboard(BaseModel):
    total_projects: int
    online_projects: int
    total_water_harvested_liters: float
    avg_tank_level_percent: float
    alerts_count: int
    projects: List[TankStatus]


# ============ PORTFOLIO SCHEMAS ============

class ProjectSummary(BaseModel):
    id: int
    address: str
    status: str
    annual_yield_liters: float
    tank_size_liters: float
    installation_date: Optional[datetime] = None
    verification_status: VerificationStatus

class PortfolioStats(BaseModel):
    total_projects: int
    installed_count: int
    pending_count: int
    total_investment_inr: float
    total_water_captured_liters: float
    avg_roi_years: float
    co2_offset_kg: float  # 1L water = 0.7g CO2 saved (pumping)

class PortfolioDashboardResponse(BaseModel):
    stats: PortfolioStats
    projects: List[ProjectSummary]
    monthly_trend: List[Dict]


# ============ SUBSIDY / POLICY SCHEMAS ============

class SubsidyInfo(BaseModel):
    state: str
    scheme_name: str
    subsidy_percent: float
    max_amount_inr: float
    eligibility_criteria: List[str]
    application_link: Optional[str] = None

class PolicyCardResponse(BaseModel):
    eligible_schemes: List[SubsidyInfo]
    total_potential_subsidy_inr: float
    net_cost_after_subsidy_inr: float
    policy_compliance_score: float  # 0-100


# ============ AUDIT SCHEMAS ============

class AuditLogEntry(BaseModel):
    id: int
    entity_type: str
    entity_id: int
    action: str
    old_value: Optional[Dict] = None
    new_value: Optional[Dict] = None
    user_id: int
    timestamp: datetime
