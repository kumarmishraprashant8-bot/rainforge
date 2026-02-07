"""
Complete RWH Assessment Service
All possible inputs and outputs for rainwater harvesting
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum
import math


class RoofType(str, Enum):
    RCC = "rcc"
    METAL = "metal"
    TILE = "tile"
    ASBESTOS = "asbestos"
    THATCHED = "thatched"


class SoilType(str, Enum):
    SANDY = "sandy"
    LOAMY = "loamy"
    CLAYEY = "clayey"
    ROCKY = "rocky"


class WaterSource(str, Enum):
    MUNICIPALITY = "municipality"
    BOREWELL = "borewell"
    TANKER = "tanker"
    WELL = "well"
    NONE = "none"


# Runoff coefficients by roof type and slope
RUNOFF_COEFFICIENTS = {
    RoofType.RCC: {0: 0.85, 10: 0.88, 20: 0.90, 30: 0.92},
    RoofType.METAL: {0: 0.90, 10: 0.92, 20: 0.94, 30: 0.95},
    RoofType.TILE: {0: 0.75, 10: 0.78, 20: 0.80, 30: 0.82},
    RoofType.ASBESTOS: {0: 0.80, 10: 0.83, 20: 0.85, 30: 0.87},
    RoofType.THATCHED: {0: 0.60, 10: 0.62, 20: 0.65, 30: 0.68},
}

# Percolation rates by soil type (mm/hour)
PERCOLATION_RATES = {
    SoilType.SANDY: 50,
    SoilType.LOAMY: 25,
    SoilType.CLAYEY: 5,
    SoilType.ROCKY: 2,
}

# Water cost by source (₹ per 1000 liters)
WATER_COSTS = {
    WaterSource.MUNICIPALITY: 20,
    WaterSource.BOREWELL: 5,
    WaterSource.TANKER: 150,
    WaterSource.WELL: 10,
    WaterSource.NONE: 200,
}

# State-wise subsidies (as of 2024)
STATE_SUBSIDIES = {
    "Tamil Nadu": {"percent": 50, "max_amount": 20000, "applicable": True},
    "Karnataka": {"percent": 50, "max_amount": 25000, "applicable": True},
    "Maharashtra": {"percent": 30, "max_amount": 15000, "applicable": True},
    "Gujarat": {"percent": 40, "max_amount": 20000, "applicable": True},
    "Rajasthan": {"percent": 60, "max_amount": 30000, "applicable": True},
    "Delhi": {"percent": 50, "max_amount": 50000, "applicable": True},
    "Haryana": {"percent": 50, "max_amount": 25000, "applicable": True},
    "Kerala": {"percent": 25, "max_amount": 10000, "applicable": True},
    "Andhra Pradesh": {"percent": 50, "max_amount": 20000, "applicable": True},
    "Telangana": {"percent": 50, "max_amount": 25000, "applicable": True},
    "Madhya Pradesh": {"percent": 40, "max_amount": 15000, "applicable": True},
    "Uttar Pradesh": {"percent": 30, "max_amount": 10000, "applicable": True},
    "West Bengal": {"percent": 25, "max_amount": 10000, "applicable": True},
    "Punjab": {"percent": 50, "max_amount": 20000, "applicable": True},
    "Odisha": {"percent": 50, "max_amount": 15000, "applicable": True},
}

# Monthly rainfall distribution (% of annual) - India average
MONTHLY_DISTRIBUTION = {
    "January": 2, "February": 2, "March": 3, "April": 4,
    "May": 5, "June": 15, "July": 25, "August": 22,
    "September": 14, "October": 5, "November": 2, "December": 1
}


@dataclass
class CompleteAssessmentInput:
    """All possible inputs for RWH assessment."""
    # Required
    roof_area_sqm: float
    city: str
    state: str
    
    # Location (optional but recommended)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    
    # Roof details
    roof_type: RoofType = RoofType.RCC
    roof_slope_degrees: int = 0
    num_floors: int = 1
    
    # Building details
    num_people: int = 4
    existing_plumbing: bool = False
    building_age_years: int = 5
    
    # Water details
    current_water_source: WaterSource = WaterSource.MUNICIPALITY
    monthly_water_bill: float = 500
    daily_water_usage_liters: Optional[float] = None
    
    # Ground conditions
    soil_type: SoilType = SoilType.LOAMY
    ground_water_depth_m: float = 10
    available_ground_area_sqm: float = 10
    
    # Preferences
    storage_preference: str = "tank"  # tank, recharge, hybrid
    budget_inr: Optional[float] = None


@dataclass
class MaterialItem:
    """Bill of materials item."""
    name: str
    quantity: int
    unit: str
    unit_cost: float
    total_cost: float
    category: str


@dataclass
class MonthlyBreakdown:
    """Monthly rainfall and collection data."""
    month: str
    rainfall_mm: float
    collection_liters: float
    demand_liters: float
    surplus_deficit: float


@dataclass
class MaintenanceTask:
    """Maintenance schedule item."""
    task: str
    frequency: str
    estimated_cost: float
    next_due: str


@dataclass
class CompleteAssessmentOutput:
    """All possible outputs from RWH assessment."""
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
    water_quality_grade: str  # A, B, C
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
    rpi_score: int  # RainForge Performance Index
    feasibility_score: int
    priority_score: int


def calculate_complete_assessment(input: CompleteAssessmentInput) -> CompleteAssessmentOutput:
    """Calculate complete RWH assessment with all inputs/outputs."""
    
    # Get rainfall data (mock - would use weather API)
    annual_rainfall = get_annual_rainfall(input.city, input.state)
    
    # Calculate runoff coefficient based on roof type and slope
    runoff_coef = get_runoff_coefficient(input.roof_type, input.roof_slope_degrees)
    
    # First flush deduction (first 1-2mm of each rainfall event)
    first_flush_loss = 0.10  # 10% loss
    effective_coef = runoff_coef * (1 - first_flush_loss)
    
    # Annual collection
    annual_collection = input.roof_area_sqm * annual_rainfall * effective_coef
    
    # Daily water demand
    if input.daily_water_usage_liters:
        daily_demand = input.daily_water_usage_liters
    else:
        daily_demand = input.num_people * 135  # 135 lpcd India average
    
    annual_demand = daily_demand * 365
    
    # Monthly breakdown
    monthly_breakdown = calculate_monthly_breakdown(
        annual_rainfall, annual_collection, daily_demand * 30, input.city
    )
    
    # Tank sizing (store 15-20 days of demand or 2 months of monsoon collection)
    recommended_tank = calculate_tank_size(daily_demand, annual_collection)
    
    # Days of coverage
    days_coverage = int(recommended_tank / daily_demand) if daily_demand > 0 else 0
    
    # Bill of materials
    materials = calculate_materials(
        input.roof_area_sqm, recommended_tank, input.num_floors,
        input.existing_plumbing, input.storage_preference
    )
    
    material_cost = sum(m.total_cost for m in materials)
    labor_cost = material_cost * 0.30  # 30% of material cost
    total_cost = material_cost + labor_cost
    
    # Subsidy calculation
    subsidy_info = STATE_SUBSIDIES.get(input.state, {"percent": 0, "max_amount": 0, "applicable": False})
    subsidy_amount = min(total_cost * subsidy_info["percent"] / 100, subsidy_info["max_amount"])
    net_cost = total_cost - subsidy_amount
    
    # Savings calculation
    water_rate = WATER_COSTS[input.current_water_source]
    annual_savings = (annual_collection / 1000) * water_rate
    if input.monthly_water_bill > 0:
        # More accurate: use actual bill
        annual_savings = min(annual_savings, input.monthly_water_bill * 12 * 0.6)
    
    # ROI
    roi_years = net_cost / annual_savings if annual_savings > 0 else 99
    payback_months = int(roi_years * 12)
    lifetime_savings = (annual_savings * 20) - net_cost
    
    # Maintenance schedule
    maintenance = get_maintenance_schedule(input.storage_preference)
    annual_maintenance = sum(m.estimated_cost for m in maintenance if m.frequency == "Annual")
    
    # System design
    pipe_diameter = calculate_pipe_diameter(input.roof_area_sqm)
    first_flush = int(input.roof_area_sqm * 2)  # 2L per sqm
    tank_dims = calculate_tank_dimensions(recommended_tank)
    
    # Recharge pit (if hybrid or recharge only)
    recharge_required = input.storage_preference in ["recharge", "hybrid"]
    recharge_dims = None
    if recharge_required:
        recharge_dims = calculate_recharge_pit(
            annual_collection, input.soil_type, input.available_ground_area_sqm
        )
    
    # Water quality assessment
    quality_grade, uses, treatment_needed, treatments = assess_water_quality(input.roof_type)
    
    # Compliance
    permit_required, authority, permit_days, mandatory = check_compliance(
        input.state, input.roof_area_sqm, input.city
    )
    
    # Environmental benefits
    carbon_offset = (annual_collection / 1000) * 0.5  # 0.5 kg CO2 per 1000L saved
    groundwater_recharge = annual_collection * 0.3 if recharge_required else 0
    flood_mitigation = annual_collection * 0.8  # Reduces urban flooding
    
    # Scores
    rpi_score = calculate_rpi_score(annual_collection, recommended_tank, roi_years)
    feasibility = calculate_feasibility_score(input, annual_collection)
    priority = calculate_priority_score(input, annual_savings)
    
    return CompleteAssessmentOutput(
        # Basic
        annual_rainfall_mm=annual_rainfall,
        annual_collection_liters=annual_collection,
        recommended_tank_liters=recommended_tank,
        roi_years=round(roi_years, 1),
        carbon_offset_kg=round(carbon_offset, 1),
        
        # Financial
        total_system_cost=round(total_cost),
        material_cost=round(material_cost),
        labor_cost=round(labor_cost),
        annual_savings=round(annual_savings),
        payback_months=payback_months,
        lifetime_savings_20yr=round(lifetime_savings),
        
        # Subsidy
        subsidy_available=subsidy_info["applicable"],
        subsidy_percent=subsidy_info["percent"],
        subsidy_amount=round(subsidy_amount),
        net_cost_after_subsidy=round(net_cost),
        
        # Coverage
        daily_demand_liters=daily_demand,
        days_of_coverage=days_coverage,
        monsoon_collection_liters=annual_collection * 0.76,  # June-Sept
        dry_season_deficit_liters=max(0, annual_demand - annual_collection),
        
        # Monthly
        monthly_breakdown=monthly_breakdown,
        
        # Materials
        materials=materials,
        
        # Maintenance
        maintenance_schedule=maintenance,
        annual_maintenance_cost=round(annual_maintenance),
        
        # System design
        pipe_diameter_mm=pipe_diameter,
        filter_type="Mesh + Charcoal" if recommended_tank > 5000 else "Basic Mesh",
        first_flush_liters=first_flush,
        tank_dimensions=tank_dims,
        recharge_pit_required=recharge_required,
        recharge_pit_dimensions=recharge_dims,
        
        # Water quality
        water_quality_grade=quality_grade,
        suitable_uses=uses,
        treatment_required=treatment_needed,
        treatment_recommendations=treatments,
        
        # Compliance
        permit_required=permit_required,
        permit_authority=authority,
        estimated_permit_time_days=permit_days,
        mandatory_by_law=mandatory,
        
        # Environmental
        groundwater_recharge_potential=groundwater_recharge,
        flood_mitigation_liters=flood_mitigation,
        
        # Scores
        rpi_score=rpi_score,
        feasibility_score=feasibility,
        priority_score=priority
    )


# Helper functions

def get_annual_rainfall(city: str, state: str) -> float:
    """Get annual rainfall for location."""
    # City-specific data (mm)
    CITY_RAINFALL = {
        "Mumbai": 2200, "Chennai": 1400, "Kolkata": 1600, "Delhi": 800,
        "Bangalore": 970, "Hyderabad": 800, "Pune": 720, "Ahmedabad": 780,
        "Jaipur": 650, "Lucknow": 900, "Chandigarh": 1100, "Bhopal": 1150,
        "Kochi": 3000, "Guwahati": 1800, "Bhubaneswar": 1500,
    }
    return CITY_RAINFALL.get(city, 1000)  # Default 1000mm


def get_runoff_coefficient(roof_type: RoofType, slope: int) -> float:
    """Get runoff coefficient based on roof type and slope."""
    slopes = RUNOFF_COEFFICIENTS.get(roof_type, RUNOFF_COEFFICIENTS[RoofType.RCC])
    # Find closest slope
    closest = min(slopes.keys(), key=lambda x: abs(x - slope))
    return slopes[closest]


def calculate_monthly_breakdown(
    annual_rainfall: float, 
    annual_collection: float,
    monthly_demand: float,
    city: str
) -> List[MonthlyBreakdown]:
    """Calculate month-by-month rainfall and collection."""
    breakdown = []
    for month, percent in MONTHLY_DISTRIBUTION.items():
        rain = annual_rainfall * percent / 100
        collection = annual_collection * percent / 100
        surplus = collection - monthly_demand
        breakdown.append(MonthlyBreakdown(
            month=month,
            rainfall_mm=round(rain, 1),
            collection_liters=round(collection),
            demand_liters=monthly_demand,
            surplus_deficit=round(surplus)
        ))
    return breakdown


def calculate_tank_size(daily_demand: float, annual_collection: float) -> int:
    """Calculate recommended tank size."""
    # Option 1: 15 days of demand
    by_demand = daily_demand * 15
    
    # Option 2: Store monsoon surplus
    monsoon_monthly = annual_collection * 0.25 / 4  # July peak
    dry_monthly_demand = daily_demand * 30
    by_surplus = monsoon_monthly * 2  # Store 2 months
    
    # Take the more practical size
    recommended = max(by_demand, min(by_surplus, by_demand * 3))
    
    # Round to standard sizes
    standard_sizes = [500, 1000, 2000, 3000, 5000, 7500, 10000, 15000, 20000, 25000, 30000]
    return min(standard_sizes, key=lambda x: abs(x - recommended) if x >= recommended * 0.8 else float('inf'))


def calculate_materials(
    roof_area: float, 
    tank_size: int, 
    floors: int,
    existing_plumbing: bool,
    storage_type: str
) -> List[MaterialItem]:
    """Calculate bill of materials."""
    materials = []
    
    # Gutters
    gutter_length = math.sqrt(roof_area) * 4  # Perimeter estimate
    materials.append(MaterialItem(
        name="PVC Gutter (110mm)",
        quantity=int(gutter_length / 3) + 1,  # 3m pieces
        unit="pieces",
        unit_cost=450,
        total_cost=int(gutter_length / 3 + 1) * 450,
        category="Collection"
    ))
    
    # Downpipes
    pipe_length = floors * 3.5  # 3.5m per floor
    materials.append(MaterialItem(
        name="PVC Downpipe (90mm)",
        quantity=int(pipe_length / 3) + 1,
        unit="pieces",
        unit_cost=380,
        total_cost=int(pipe_length / 3 + 1) * 380,
        category="Collection"
    ))
    
    # First flush diverter
    materials.append(MaterialItem(
        name="First Flush Diverter",
        quantity=1,
        unit="unit",
        unit_cost=1200,
        total_cost=1200,
        category="Filtration"
    ))
    
    # Filter
    filter_cost = 2500 if tank_size > 5000 else 1500
    materials.append(MaterialItem(
        name="Rainwater Filter",
        quantity=1,
        unit="unit",
        unit_cost=filter_cost,
        total_cost=filter_cost,
        category="Filtration"
    ))
    
    # Tank
    if storage_type in ["tank", "hybrid"]:
        # Cost varies by size (₹ per liter decreases with size)
        cost_per_liter = 8 if tank_size < 5000 else 6 if tank_size < 10000 else 5
        tank_cost = tank_size * cost_per_liter
        materials.append(MaterialItem(
            name=f"Storage Tank ({tank_size}L)",
            quantity=1,
            unit="unit",
            unit_cost=tank_cost,
            total_cost=tank_cost,
            category="Storage"
        ))
    
    # Recharge pit materials
    if storage_type in ["recharge", "hybrid"]:
        materials.append(MaterialItem(
            name="Recharge Pit Rings",
            quantity=5,
            unit="rings",
            unit_cost=800,
            total_cost=4000,
            category="Recharge"
        ))
        materials.append(MaterialItem(
            name="Gravel & Sand",
            quantity=2,
            unit="cubic meters",
            unit_cost=1500,
            total_cost=3000,
            category="Recharge"
        ))
    
    # Pipes and fittings
    if not existing_plumbing:
        materials.append(MaterialItem(
            name="PVC Pipes & Fittings",
            quantity=1,
            unit="set",
            unit_cost=3500,
            total_cost=3500,
            category="Plumbing"
        ))
    
    # Pump (if multi-story)
    if floors > 1:
        materials.append(MaterialItem(
            name="Submersible Pump (0.5HP)",
            quantity=1,
            unit="unit",
            unit_cost=4500,
            total_cost=4500,
            category="Pumping"
        ))
    
    return materials


def get_maintenance_schedule(storage_type: str) -> List[MaintenanceTask]:
    """Get maintenance schedule."""
    tasks = [
        MaintenanceTask("Clean gutters", "Quarterly", 0, "Before monsoon"),
        MaintenanceTask("Clean filter", "Monthly", 0, "1st of month"),
        MaintenanceTask("Empty first flush", "After each rain", 0, "After rain"),
        MaintenanceTask("Inspect tank", "Annually", 500, "Post-monsoon"),
        MaintenanceTask("Clean tank", "Annually", 1500, "March"),
        MaintenanceTask("Check pipes for leaks", "Quarterly", 0, "Every 3 months"),
    ]
    
    if storage_type in ["recharge", "hybrid"]:
        tasks.append(MaintenanceTask("Clean recharge pit", "Annually", 2000, "Pre-monsoon"))
    
    return tasks


def calculate_pipe_diameter(roof_area: float) -> int:
    """Calculate required pipe diameter based on roof area."""
    if roof_area < 50:
        return 75
    elif roof_area < 100:
        return 90
    elif roof_area < 200:
        return 110
    else:
        return 160


def calculate_tank_dimensions(capacity_liters: int) -> Dict[str, float]:
    """Calculate tank dimensions for given capacity."""
    # Assume cylindrical tank with height = 1.5 * diameter
    volume_m3 = capacity_liters / 1000
    # V = π * r² * h, where h = 1.5 * 2r = 3r
    # V = π * r² * 3r = 3π * r³
    # r = (V / 3π)^(1/3)
    r = (volume_m3 / (3 * math.pi)) ** (1/3)
    diameter = round(r * 2, 2)
    height = round(r * 3, 2)
    
    return {
        "diameter_m": diameter,
        "height_m": height,
        "footprint_sqm": round(math.pi * r * r, 2)
    }


def calculate_recharge_pit(
    annual_collection: float, 
    soil_type: SoilType,
    available_area: float
) -> Dict[str, float]:
    """Calculate recharge pit dimensions."""
    percolation_rate = PERCOLATION_RATES[soil_type]
    
    # Monsoon daily max (25% of annual in 120 days = peak day)
    peak_daily_liters = annual_collection * 0.02  # 2% on peak day
    
    # Required percolation area
    # Percolation = rate * area * time
    # Area = volume / (rate * time)
    required_area = peak_daily_liters / (percolation_rate * 24)  # 24 hours
    
    # Limit to available area
    actual_area = min(required_area, available_area)
    
    # Pit dimensions (circular)
    diameter = math.sqrt(actual_area * 4 / math.pi)
    depth = 3.0  # Standard 3m depth
    
    return {
        "diameter_m": round(diameter, 2),
        "depth_m": depth,
        "area_sqm": round(actual_area, 2)
    }


def assess_water_quality(roof_type: RoofType) -> tuple:
    """Assess water quality based on roof type."""
    quality_map = {
        RoofType.RCC: ("B", ["Gardening", "Toilet flushing", "Washing", "Groundwater recharge"], True, ["Basic filtration", "First flush diversion"]),
        RoofType.METAL: ("A", ["Gardening", "Toilet flushing", "Washing", "Bathing", "Cooking (with treatment)"], True, ["Sediment filter", "UV treatment for drinking"]),
        RoofType.TILE: ("B", ["Gardening", "Toilet flushing", "Groundwater recharge"], True, ["Coarse filter", "Settling tank"]),
        RoofType.ASBESTOS: ("C", ["Groundwater recharge only"], False, ["Do not use for domestic purposes", "Only recharge"]),
        RoofType.THATCHED: ("C", ["Gardening only"], True, ["Multiple stage filtration"]),
    }
    return quality_map.get(roof_type, ("B", ["General use"], True, ["Basic filtration"]))


def check_compliance(state: str, roof_area: float, city: str) -> tuple:
    """Check legal compliance requirements."""
    # States with mandatory RWH
    mandatory_states = {
        "Tamil Nadu": 100,  # >100 sqm plots
        "Karnataka": 60,   # >60x40 plots
        "Maharashtra": 300,
        "Delhi": 100,
        "Gujarat": 500,
        "Rajasthan": 300,
    }
    
    threshold = mandatory_states.get(state, 0)
    mandatory = roof_area >= threshold if threshold > 0 else False
    permit_required = roof_area > 200
    authority = f"{city} Municipal Corporation"
    days = 15 if permit_required else 0
    
    return permit_required, authority, days, mandatory


def calculate_rpi_score(collection: float, tank: int, roi: float) -> int:
    """Calculate RainForge Performance Index."""
    # Score components
    collection_score = min(30, int(collection / 10000))  # Max 30 for 300K+ liters
    tank_score = min(25, int(tank / 400))  # Max 25 for 10K+ tank
    roi_score = max(0, 25 - int(roi * 5))  # Better ROI = higher score
    feasibility_score = 20  # Base score
    
    return min(100, collection_score + tank_score + roi_score + feasibility_score)


def calculate_feasibility_score(input: CompleteAssessmentInput, collection: float) -> int:
    """Calculate feasibility score 0-100."""
    score = 50  # Base
    
    if collection > 100000:
        score += 20
    if input.ground_water_depth_m > 5:
        score += 10
    if input.soil_type in [SoilType.SANDY, SoilType.LOAMY]:
        score += 10
    if input.existing_plumbing:
        score += 5
    if input.available_ground_area_sqm > 5:
        score += 5
    
    return min(100, score)


def calculate_priority_score(input: CompleteAssessmentInput, savings: float) -> int:
    """Calculate priority score for government schemes."""
    score = 50
    
    if input.current_water_source == WaterSource.TANKER:
        score += 30
    elif input.current_water_source == WaterSource.NONE:
        score += 40
    
    if savings > 10000:
        score += 10
    
    return min(100, score)
