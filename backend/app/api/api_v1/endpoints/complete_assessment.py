"""
Complete Assessment API Endpoint
Enhanced assessment with all inputs and outputs
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum

router = APIRouter()


class RoofTypeEnum(str, Enum):
    rcc = "rcc"
    metal = "metal"
    tile = "tile"
    asbestos = "asbestos"
    thatched = "thatched"


class SoilTypeEnum(str, Enum):
    sandy = "sandy"
    loamy = "loamy"
    clayey = "clayey"
    rocky = "rocky"


class WaterSourceEnum(str, Enum):
    municipality = "municipality"
    borewell = "borewell"
    tanker = "tanker"
    well = "well"
    none = "none"


class StoragePreference(str, Enum):
    tank = "tank"
    recharge = "recharge"
    hybrid = "hybrid"


class CompleteAssessmentRequest(BaseModel):
    """All possible inputs for RWH assessment."""
    
    # Required
    roof_area_sqm: float = Field(..., gt=0, description="Roof catchment area in square meters")
    city: str = Field(..., description="City name")
    state: str = Field(..., description="State name")
    
    # Location
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    
    # Roof details
    roof_type: RoofTypeEnum = Field(RoofTypeEnum.rcc, description="Type of roof material")
    roof_slope_degrees: int = Field(0, ge=0, le=60, description="Roof slope in degrees")
    num_floors: int = Field(1, ge=1, le=20, description="Number of floors in building")
    
    # Building details  
    num_people: int = Field(4, ge=1, description="Number of people in household")
    existing_plumbing: bool = Field(False, description="Does building have existing rainwater plumbing?")
    building_age_years: int = Field(5, ge=0, description="Age of building in years")
    
    # Water details
    current_water_source: WaterSourceEnum = Field(WaterSourceEnum.municipality)
    monthly_water_bill: float = Field(500, ge=0, description="Monthly water bill in INR")
    daily_water_usage_liters: Optional[float] = Field(None, gt=0, description="Known daily water usage")
    
    # Ground conditions
    soil_type: SoilTypeEnum = Field(SoilTypeEnum.loamy, description="Type of soil at site")
    ground_water_depth_m: float = Field(10, gt=0, description="Depth to groundwater in meters")
    available_ground_area_sqm: float = Field(10, ge=0, description="Ground area available for recharge pit")
    
    # Preferences
    storage_preference: StoragePreference = Field(StoragePreference.tank)
    budget_inr: Optional[float] = Field(None, gt=0, description="Maximum budget in INR")

    class Config:
        json_schema_extra = {
            "example": {
                "roof_area_sqm": 150,
                "city": "Mumbai",
                "state": "Maharashtra",
                "roof_type": "rcc",
                "roof_slope_degrees": 5,
                "num_floors": 2,
                "num_people": 4,
                "current_water_source": "municipality",
                "monthly_water_bill": 800,
                "soil_type": "loamy",
                "storage_preference": "hybrid"
            }
        }


class MaterialItem(BaseModel):
    name: str
    quantity: int
    unit: str
    unit_cost: float
    total_cost: float
    category: str


class MonthlyBreakdown(BaseModel):
    month: str
    rainfall_mm: float
    collection_liters: float
    demand_liters: float
    surplus_deficit: float


class MaintenanceTask(BaseModel):
    task: str
    frequency: str
    estimated_cost: float
    next_due: str


class CompleteAssessmentResponse(BaseModel):
    """Complete assessment output with all details."""
    
    # Basic outputs
    annual_rainfall_mm: float
    annual_collection_liters: float
    recommended_tank_liters: int
    roi_years: float
    carbon_offset_kg: float
    
    # Financial
    total_system_cost: float
    material_cost: float
    labor_cost: float
    annual_savings: float
    payback_months: int
    lifetime_savings_20yr: float
    
    # Subsidy
    subsidy_available: bool
    subsidy_percent: int
    subsidy_amount: float
    net_cost_after_subsidy: float
    
    # Coverage
    daily_demand_liters: float
    days_of_coverage: int
    monsoon_collection_liters: float
    dry_season_deficit_liters: float
    
    # Monthly breakdown
    monthly_breakdown: List[MonthlyBreakdown]
    
    # Bill of materials
    materials: List[MaterialItem]
    
    # Maintenance
    maintenance_schedule: List[MaintenanceTask]
    annual_maintenance_cost: float
    
    # System design
    pipe_diameter_mm: int
    filter_type: str
    first_flush_liters: int
    tank_dimensions: Dict[str, float]
    recharge_pit_required: bool
    recharge_pit_dimensions: Optional[Dict[str, float]]
    
    # Water quality
    water_quality_grade: str
    suitable_uses: List[str]
    treatment_required: bool
    treatment_recommendations: List[str]
    
    # Compliance
    permit_required: bool
    permit_authority: str
    estimated_permit_time_days: int
    mandatory_by_law: bool
    
    # Environmental
    groundwater_recharge_potential: float
    flood_mitigation_liters: float
    
    # Scores
    rpi_score: int
    feasibility_score: int
    priority_score: int


@router.post("/complete", response_model=CompleteAssessmentResponse)
async def complete_assessment(request: CompleteAssessmentRequest):
    """
    Run complete RWH assessment with all inputs and outputs.
    
    This endpoint provides:
    - Monthly rainfall breakdown
    - Complete bill of materials
    - Cost breakdown with subsidies
    - Maintenance schedule
    - System design specifications
    - Water quality assessment
    - Legal compliance check
    - Environmental impact
    """
    from app.services.complete_assessment import (
        CompleteAssessmentInput, RoofType, SoilType, WaterSource,
        calculate_complete_assessment
    )
    
    # Map request to service input
    input_data = CompleteAssessmentInput(
        roof_area_sqm=request.roof_area_sqm,
        city=request.city,
        state=request.state,
        latitude=request.latitude,
        longitude=request.longitude,
        roof_type=RoofType(request.roof_type.value),
        roof_slope_degrees=request.roof_slope_degrees,
        num_floors=request.num_floors,
        num_people=request.num_people,
        existing_plumbing=request.existing_plumbing,
        building_age_years=request.building_age_years,
        current_water_source=WaterSource(request.current_water_source.value),
        monthly_water_bill=request.monthly_water_bill,
        daily_water_usage_liters=request.daily_water_usage_liters,
        soil_type=SoilType(request.soil_type.value),
        ground_water_depth_m=request.ground_water_depth_m,
        available_ground_area_sqm=request.available_ground_area_sqm,
        storage_preference=request.storage_preference.value,
        budget_inr=request.budget_inr
    )
    
    # Calculate assessment
    result = calculate_complete_assessment(input_data)
    
    # Convert to response
    return CompleteAssessmentResponse(
        annual_rainfall_mm=result.annual_rainfall_mm,
        annual_collection_liters=result.annual_collection_liters,
        recommended_tank_liters=result.recommended_tank_liters,
        roi_years=result.roi_years,
        carbon_offset_kg=result.carbon_offset_kg,
        
        total_system_cost=result.total_system_cost,
        material_cost=result.material_cost,
        labor_cost=result.labor_cost,
        annual_savings=result.annual_savings,
        payback_months=result.payback_months,
        lifetime_savings_20yr=result.lifetime_savings_20yr,
        
        subsidy_available=result.subsidy_available,
        subsidy_percent=result.subsidy_percent,
        subsidy_amount=result.subsidy_amount,
        net_cost_after_subsidy=result.net_cost_after_subsidy,
        
        daily_demand_liters=result.daily_demand_liters,
        days_of_coverage=result.days_of_coverage,
        monsoon_collection_liters=result.monsoon_collection_liters,
        dry_season_deficit_liters=result.dry_season_deficit_liters,
        
        monthly_breakdown=[
            MonthlyBreakdown(
                month=m.month,
                rainfall_mm=m.rainfall_mm,
                collection_liters=m.collection_liters,
                demand_liters=m.demand_liters,
                surplus_deficit=m.surplus_deficit
            ) for m in result.monthly_breakdown
        ],
        
        materials=[
            MaterialItem(
                name=m.name,
                quantity=m.quantity,
                unit=m.unit,
                unit_cost=m.unit_cost,
                total_cost=m.total_cost,
                category=m.category
            ) for m in result.materials
        ],
        
        maintenance_schedule=[
            MaintenanceTask(
                task=m.task,
                frequency=m.frequency,
                estimated_cost=m.estimated_cost,
                next_due=m.next_due
            ) for m in result.maintenance_schedule
        ],
        annual_maintenance_cost=result.annual_maintenance_cost,
        
        pipe_diameter_mm=result.pipe_diameter_mm,
        filter_type=result.filter_type,
        first_flush_liters=result.first_flush_liters,
        tank_dimensions=result.tank_dimensions,
        recharge_pit_required=result.recharge_pit_required,
        recharge_pit_dimensions=result.recharge_pit_dimensions,
        
        water_quality_grade=result.water_quality_grade,
        suitable_uses=result.suitable_uses,
        treatment_required=result.treatment_required,
        treatment_recommendations=result.treatment_recommendations,
        
        permit_required=result.permit_required,
        permit_authority=result.permit_authority,
        estimated_permit_time_days=result.estimated_permit_time_days,
        mandatory_by_law=result.mandatory_by_law,
        
        groundwater_recharge_potential=result.groundwater_recharge_potential,
        flood_mitigation_liters=result.flood_mitigation_liters,
        
        rpi_score=result.rpi_score,
        feasibility_score=result.feasibility_score,
        priority_score=result.priority_score
    )


@router.get("/subsidies/{state}")
async def get_state_subsidies(state: str):
    """Get RWH subsidy information for a state."""
    from app.services.complete_assessment import STATE_SUBSIDIES
    
    subsidy = STATE_SUBSIDIES.get(state)
    if not subsidy:
        return {
            "state": state,
            "available": False,
            "message": "No subsidy data available for this state"
        }
    
    return {
        "state": state,
        "available": subsidy["applicable"],
        "percent": subsidy["percent"],
        "max_amount": subsidy["max_amount"],
        "notes": f"Up to {subsidy['percent']}% subsidy, maximum ₹{subsidy['max_amount']}"
    }


@router.get("/rainfall/{city}")
async def get_city_rainfall(city: str):
    """Get rainfall data for a city."""
    from app.services.complete_assessment import get_annual_rainfall, MONTHLY_DISTRIBUTION
    
    annual = get_annual_rainfall(city, "")
    monthly = {
        month: round(annual * pct / 100, 1) 
        for month, pct in MONTHLY_DISTRIBUTION.items()
    }
    
    return {
        "city": city,
        "annual_mm": annual,
        "monthly_mm": monthly,
        "monsoon_months": ["June", "July", "August", "September"],
        "peak_month": "July"
    }
