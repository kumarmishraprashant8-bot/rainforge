"""
RainForge Assessment API Endpoints - Enhanced with P0 Features
"""

from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from typing import Any, Dict, Optional
import uuid
from datetime import datetime

from app.schemas.schemas import (
    QuickAssessmentRequest, FullAssessmentResponse, ScenarioMode,
    RainfallData, ScenarioComparison
)
from app.services.calculation_engine import calculation_engine
from app.services.hydrology import HydrologyEngine, ScenarioMode as HydroScenario
from app.services.weather import WeatherService
from app.services.report import ReportGenerator
from app.services.policy import PolicyService
from app.services.recharge import RechargeService, SoilType
from app.services.pdf_generator import get_pdf_generator
from app.models.database import get_db, Assessment
from shapely.geometry import shape

router = APIRouter()


class MultimodalAssessmentRequest(BaseModel):
    """Optional mode and fields for Feature A - multi-modal assessment."""
    address: str = Field(..., example="123 Gandhi Road, New Delhi")
    mode: Optional[str] = Field(None, description="address | satellite-only | photo")
    lat: Optional[float] = Field(None, ge=-90, le=90)
    lng: Optional[float] = Field(None, ge=-180, le=180)
    roof_area_sqm: Optional[float] = Field(None, gt=0)
    roof_material: Optional[str] = Field(None)
    state: Optional[str] = Field(None)
    city: Optional[str] = Field(None)
    people: int = Field(4, ge=1)
    floors: int = Field(1, ge=1)
    site_id: Optional[str] = Field(None)


@router.post("", response_model=None)
def create_multimodal_assessment(
    request: MultimodalAssessmentRequest, db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Create assessment with optional input mode: address | satellite-only | photo.
    Returns pdf_url and confidence score (Feature A). Does not change existing /assess.
    """
    from app.services.assessment_pipeline import select_pipeline, run_pipeline
    mode = select_pipeline(request.mode)
    return run_pipeline(
        mode=mode,
        address=request.address,
        lat=request.lat,
        lng=request.lng,
        roof_area_sqm=request.roof_area_sqm,
        roof_material=request.roof_material,
        state=request.state,
        city=request.city,
        people=request.people,
        floors=request.floors,
        site_id=request.site_id,
        db_session=db,
        pdf_base_path="assessments",
    )


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
def generate_report(project_id: str):
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


@router.post("/assess")
def create_assessment(
    site_id: str,
    address: str,
    lat: float,
    lng: float,
    roof_area_sqm: float,
    roof_material: str = "concrete",
    floors: int = 1,
    people: int = 4,
    state: str = "Delhi",
    city: str = "New Delhi",
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    P0 Enhanced Assessment Endpoint:
    - Returns 3 scenarios (cost_optimized, max_capture, dry_season)
    - Includes P10/P50/P90 confidence intervals
    - Stores to database with QR code
    - Returns data sources
    """
    try:
        # Get rainfall data
        weather = WeatherService.get_historical_rainfall(lat, lng)
        monthly_rainfall = weather["monthly_mm"]
        
        # Generate all 3 scenarios
        scenarios_results = calculation_engine.generate_all_scenarios(
            roof_area_sqm=roof_area_sqm,
            roof_material=roof_material,
            city=city,
            state=state,
            floors=floors,
            people=people,
            monthly_rainfall=monthly_rainfall
        )
        
        # Calculate confidence intervals
        p10, p50, p90, data_sources = calculation_engine.calculate_confidence_intervals(
            roof_area_sqm=roof_area_sqm,
            monthly_rainfall=monthly_rainfall,
            roof_material=roof_material
        )
        
        # Generate verification code for QR
        qr_code = str(uuid.uuid4())
        
        # Prepare scenarios for response
        scenarios_data = {}
        for scenario_name, result in scenarios_results.items():
            scenarios_data[scenario_name] = {
                "tank_liters": result.tank_recommendation_l,
                "cost_inr": result.gross_cost,
                "net_cost_inr": result.net_cost,
                "subsidy_inr": result.subsidy_amount,
                "annual_yield_l": result.annual_yield_l,
                "roi_years": result.roi_years,
                "reliability_pct": result.reliability_pct,
                "co2_offset_kg": result.co2_offset_kg
            }
        
        # Store to database
        assessment = Assessment(
            assessment_id=f"ASM-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}",
            site_id=site_id,
            address=address,
            lat=lat,
            lng=lng,
            roof_area_sqm=roof_area_sqm,
            roof_material=roof_material,
            floors=floors,
            people=people,
            state=state,
            city=city,
            scenarios=scenarios_data,
            annual_rainfall_mm=weather["annual_mm"],
            annual_yield_liters=scenarios_results["cost_optimized"].annual_yield_l,
            recommended_tank_liters=int(scenarios_results["cost_optimized"].tank_recommendation_l),
            total_cost_inr=scenarios_results["cost_optimized"].gross_cost,
            subsidy_amount_inr=scenarios_results["cost_optimized"].subsidy_amount,
            net_cost_inr=scenarios_results["cost_optimized"].net_cost,
            roi_years=scenarios_results["cost_optimized"].roi_years,
            co2_avoided_kg=scenarios_results["cost_optimized"].co2_offset_kg,
            confidence_p10=p10,
            confidence_p50=p50,
            confidence_p90=p90,
            data_sources=data_sources,
            qr_verification_code=qr_code,
            scenarios_data=scenarios_data
        )
        
        db.add(assessment)
        db.commit()
        db.refresh(assessment)
        
        return {
            "assessment_id": assessment.assessment_id,
            "site_id": site_id,
            "annual_rainfall_mm": weather["annual_mm"],
            "scenarios": scenarios_data,
            "recommended_scenario": "cost_optimized",
            "confidence": {
                "p10": round(p10, 2),
                "p50": round(p50, 2),
                "p90": round(p90, 2),
                "confidence_percent": 80
            },
            "data_sources": data_sources,
            "pdf_url": f"/api/v1/assessments/{assessment.assessment_id}/pdf",
            "verify_url": f"/api/v1/verify/{qr_code}",
            "created_at": assessment.created_at.isoformat() if assessment.created_at else datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Assessment failed: {str(e)}")


@router.get("/verify/{qr_code}")
def verify_assessment(qr_code: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Verify assessment via QR code - shows assessment details and audit trail.
    """
    assessment = db.query(Assessment).filter(
        Assessment.qr_verification_code == qr_code
    ).first()
    
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found or invalid QR code")
    
    return {
        "verified": True,
        "assessment_id": assessment.assessment_id,
        "site_id": assessment.site_id,
        "address": assessment.address,
        "created_at": assessment.created_at.isoformat() if assessment.created_at else None,
        "roof_area_sqm": assessment.roof_area_sqm,
        "annual_yield_liters": assessment.annual_yield_liters,
        "recommended_tank_liters": assessment.recommended_tank_liters,
        "scenarios": assessment.scenarios_data,
        "confidence": {
            "p10": assessment.confidence_p10,
            "p50": assessment.confidence_p50,
            "p90": assessment.confidence_p90
        },
        "data_sources": assessment.data_sources,
        "audit_trail": [
            {
                "timestamp": assessment.created_at.isoformat() if assessment.created_at else None,
                "action": "assessment_created",
                "actor": "system"
            }
        ]
    }


@router.get("/{assessment_id}/pdf", response_class=Response)
def download_assessment_pdf(assessment_id: str, db: Session = Depends(get_db)) -> Response:
    """
    Download P0-enhanced PDF with QR code and digital signature.
    """
    assessment = db.query(Assessment).filter(
        Assessment.assessment_id == assessment_id
    ).first()
    
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    # Prepare data for PDF
    pdf_data = {
        "assessment_id": assessment.assessment_id,
        "site_id": assessment.site_id,
        "address": assessment.address,
        "roof_area_sqm": assessment.roof_area_sqm,
        "roof_material": assessment.roof_material,
        "annual_rainfall_mm": assessment.annual_rainfall_mm,
        "scenarios": assessment.scenarios_data or {},
        "confidence": {
            "p10": assessment.confidence_p10,
            "p50": assessment.confidence_p50,
            "p90": assessment.confidence_p90
        },
        "data_sources": assessment.data_sources or []
    }
    
    # Generate PDF
    pdf_gen = get_pdf_generator()
    pdf_bytes = pdf_gen.generate_p0_assessment_pdf(
        assessment_data=pdf_data,
        qr_verification_code=assessment.qr_verification_code
    )
    
    # Update PDF URL in database
    pdf_path = f"/generated_pdfs/{assessment.assessment_id}.pdf"
    assessment.pdf_url = pdf_path
    db.commit()
    
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=RainForge_{assessment.assessment_id}.pdf"}
    )
