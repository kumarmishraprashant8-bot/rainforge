"""
RainForge Assessment API Endpoints - Enhanced
"""

from fastapi import APIRouter, Depends, HTTPException, Response
from typing import Any
from app.schemas.schemas import (
    QuickAssessmentRequest, FullAssessmentResponse, ScenarioMode,
    RainfallData, ScenarioComparison
)
from app.services.hydrology import HydrologyEngine, ScenarioMode as HydroScenario
from app.services.weather import WeatherService
from app.services.report import ReportGenerator
from app.services.policy import PolicyService
from app.services.recharge import RechargeService, SoilType
from shapely.geometry import shape

router = APIRouter()


@router.post("/quick")
def run_quick_assessment(request: QuickAssessmentRequest) -> Any:
    """
    Run quick assessment with scenario comparison.
    """
    # Get area from polygon or use provided value
    try:
        if request.polygon_geojson:
            geom = shape(request.polygon_geojson)
            area_sqm = geom.area * 111000 * 111000  # Rough deg to m conversion
            area_sqm = min(area_sqm, 500)  # Cap for demo
        else:
            area_sqm = request.roof_area_sqm or 120.0
    except Exception:
        area_sqm = request.roof_area_sqm or 100.0

    # Get weather data
    weather = WeatherService.get_historical_rainfall(0, 0)
    
    # Calculate for all scenarios
    scenarios = []
    for scenario in [HydroScenario.COST_OPTIMIZED, HydroScenario.MAX_CAPTURE, HydroScenario.DRY_SEASON]:
        simulation = HydrologyEngine.simulate_yearly_yield(
            area_sqm=area_sqm,
            monthly_rainfall=weather["monthly_mm"],
            surface_type=request.roof_material,
            scenario=scenario,
            explain=True
        )
        
        storage = HydrologyEngine.calculate_storage_requirement(
            monthly_yield=simulation["monthly_yield_liters"],
            daily_demand_liters=request.daily_demand_liters,
            scenario=scenario,
            explain=True
        )
        
        # Water balance simulation
        balance = HydrologyEngine.water_balance_simulation(
            monthly_yield=simulation["monthly_yield_liters"],
            daily_demand_liters=request.daily_demand_liters,
            tank_capacity=storage["recommended_capacity_liters"]
        )
        
        scenarios.append({
            "scenario": scenario.value,
            "tank_size_liters": storage["recommended_capacity_liters"],
            "estimated_cost_inr": storage["estimated_cost_inr"],
            "annual_savings_inr": storage["annual_savings_inr"],
            "payback_years": storage["payback_years"],
            "reliability_percent": balance["reliability_percent"],
            "total_yield_liters": simulation["total_yield_liters"]
        })
    
    # Get recharge suitability if soil type provided
    recharge = None
    if request.soil_type and request.groundwater_depth_m:
        soil = SoilType(request.soil_type.value)
        recharge = RechargeService.calculate_suitability(
            soil_type=soil,
            groundwater_depth_m=request.groundwater_depth_m,
            catchment_area_sqm=area_sqm,
            annual_rainfall_mm=weather["annual_mm"]
        )
    
    # Get policy/subsidy info
    policy = PolicyService.calculate_net_cost(
        system_cost_inr=scenarios[0]["estimated_cost_inr"],
        state="delhi"
    )
    
    # Use primary scenario for main response
    primary = next(s for s in scenarios if s["scenario"] == request.scenario.value)
    primary_sim = HydrologyEngine.simulate_yearly_yield(
        area_sqm=area_sqm,
        monthly_rainfall=weather["monthly_mm"],
        surface_type=request.roof_material,
        scenario=HydroScenario(request.scenario.value)
    )
    
    return {
        "project_id": 123,
        "address": request.address,
        "roof_area_sqm": area_sqm,
        "roof_material": request.roof_material,
        
        "rainfall_stats": {
            "monthly_mm": weather["monthly_mm"],
            "annual_mm": weather["annual_mm"]
        },
        
        "runoff_potential_liters": primary["total_yield_liters"],
        "recommended_tank_size": primary["tank_size_liters"],
        "monthly_breakdown": primary_sim["monthly_yield_liters"],
        
        "scenarios": scenarios,
        "selected_scenario": request.scenario.value,
        
        "dry_season_yield": primary_sim.get("dry_season_yield", 0),
        "wet_season_yield": primary_sim.get("wet_season_yield", 0),
        
        "recharge_suitability": recharge,
        
        "subsidy_eligible": policy["subsidy_amount_inr"] > 0,
        "estimated_subsidy_inr": policy["subsidy_amount_inr"],
        "net_cost_inr": policy["net_cost_inr"],
        
        "message": "Assessment complete"
    }


@router.get("/{project_id}/report", response_class=Response)
def generate_report(project_id: int):
    """
    Generate and download PDF report.
    """
    mock_project = {
        "address": "123 Demo St, New Delhi",
        "created_at": "2024-01-24",
        "roof_area_sqm": 120,
        "roof_material": "concrete"
    }
    mock_assessment = {
        "rainfall_stats": {"annual_mm": 850},
        "runoff_potential_liters": 95000,
        "recommended_tank_size": 15000,
        "estimated_cost_inr": 96000,
        "subsidy_amount_inr": 48000,
        "net_cost_inr": 48000
    }
    
    pdf_bytes = ReportGenerator.generate_pdf(mock_project, mock_assessment)
    
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=RainForge_Report_{project_id}.pdf"}
    )


@router.get("/{project_id}/explain/{kpi}")
def get_explanation(project_id: int, kpi: str):
    """
    Get detailed explanation for a specific KPI.
    """
    explanations = {
        "yield": {
            "title": "Annual Yield Calculation",
            "formula": "Q = C × I × A × η",
            "variables": {
                "C": "Runoff coefficient (0.85 for concrete)",
                "I": "Rainfall in mm",
                "A": "Catchment area in m²",
                "η": "Collection efficiency (0.90)"
            },
            "reference": "IS 15797:2008"
        },
        "tank": {
            "title": "Storage Sizing",
            "formula": "Capacity = Monthly Demand × Carryover Factor",
            "methods": {
                "cost_optimized": "2-month carryover",
                "max_capture": "Peak 3-month storage",
                "dry_season": "4-month buffer"
            },
            "reference": "CPWD Manual"
        },
        "recharge": {
            "title": "Recharge Suitability",
            "formula": "Score = 0.6×Permeability + 0.4×Depth",
            "reference": "CGWB Manual on Artificial Recharge"
        }
    }
    
    return explanations.get(kpi, {"error": "Unknown KPI"})
