"""
Multi-modal assessment pipeline for RainForge Feature A.
Selects address, satellite-only, or photo pipeline and returns
assessment with PDF URL and confidence score.
Self-contained calculation to avoid circular imports.
"""

from enum import Enum
from typing import Any, Dict, Optional
from datetime import datetime
import uuid

# Demo-style constants (mirrored for pipeline independence)
_RUNOFF = {
    "concrete": 0.85, "rcc": 0.85, "metal": 0.90, "tiles": 0.75,
    "tile": 0.75, "thatched": 0.60, "asbestos": 0.80,
}
_CITY_RAINFALL = {
    "delhi": 700, "new delhi": 700, "mumbai": 2200, "bangalore": 970,
    "chennai": 1400, "hyderabad": 800, "kolkata": 1600, "pune": 1100,
    "goa": 3000, "panaji": 3000, "default": 1000,
}
_STATE_SUBSIDIES = {
    "delhi": {"pct": 50, "max": 50000}, "maharashtra": {"pct": 35, "max": 75000},
    "karnataka": {"pct": 40, "max": 40000}, "goa": {"pct": 50, "max": 50000},
}


class AssessmentMode(str, Enum):
    ADDRESS = "address"
    SATELLITE_ONLY = "satellite-only"
    SATELLITE = "satellite"  # alias
    PHOTO = "photo"


DEFAULT_ROOF_AREA_SQM = 120.0
DEFAULT_ROOF_MATERIAL = "concrete"
DEFAULT_LAT = 28.6139
DEFAULT_LNG = 77.2090
DEFAULT_STATE = "Delhi"
DEFAULT_CITY = "New Delhi"
DEFAULT_PEOPLE = 4
DEFAULT_FLOORS = 1


def select_pipeline(mode: Optional[str]) -> AssessmentMode:
    """
    Resolve request mode to pipeline enum.
    Returns address when mode is None or unknown (backwards compatible).
    """
    if not mode:
        return AssessmentMode.ADDRESS
    m = (mode or "").strip().lower().replace(" ", "_")
    if m in ("satellite_only", "satellite-only", "satellite"):
        return AssessmentMode.SATELLITE_ONLY
    if m == "photo":
        return AssessmentMode.PHOTO
    return AssessmentMode.ADDRESS


def get_confidence_for_mode(mode: AssessmentMode) -> float:
    """Return confidence score 0-100 for the given mode."""
    if mode == AssessmentMode.ADDRESS:
        return 85.0
    if mode == AssessmentMode.SATELLITE_ONLY:
        return 72.0
    if mode == AssessmentMode.PHOTO:
        return 65.0
    return 70.0


def _generate_id(prefix: str) -> str:
    date_part = datetime.utcnow().strftime("%Y%m%d")
    random_part = uuid.uuid4().hex[:6].upper()
    return f"{prefix}-{date_part}-{random_part}"


def _get_rainfall(city: str, state: str) -> float:
    c = (city or "").lower()
    return _CITY_RAINFALL.get(c, _CITY_RAINFALL.get("default", 1000))


def _get_subsidy(state: str) -> Dict[str, Any]:
    s = (state or "").lower()
    return _STATE_SUBSIDIES.get(s, {"pct": 0, "max": 0})


def _calculate_yield(roof_area_sqm: float, rainfall_mm: float, material: str) -> float:
    coeff = _RUNOFF.get((material or "concrete").lower(), 0.85)
    return roof_area_sqm * (rainfall_mm / 1000) * coeff * 1000


def _calculate_scenarios(
    annual_yield: float, daily_demand: float, total_cost_base: float
) -> Dict[str, Dict]:
    cost_tank = max(1000, int(annual_yield * 0.08))
    cost_tank = (cost_tank // 500) * 500
    max_tank = max(2000, int(annual_yield * 0.25))
    max_tank = (max_tank // 1000) * 1000
    dry_tank = max(1500, int(daily_demand * 60))
    dry_tank = (dry_tank // 500) * 500

    def tank_cost(liters: int) -> float:
        per_liter = max(15, min(25, 20 - (liters / 10000) * 5))
        return liters * per_liter + total_cost_base * 0.3

    def coverage_days(tank: int, demand: float) -> int:
        return min(365, int(tank / demand)) if demand > 0 else 365

    def roi_years(cost: float, annual_savings: float) -> float:
        return round(cost / annual_savings, 1) if annual_savings > 0 else 99.0

    annual_savings = (annual_yield / 1000) * 50
    return {
        "cost_optimized": {
            "name": "Cost Optimized",
            "tank_liters": cost_tank,
            "cost_inr": round(tank_cost(cost_tank), 0),
            "capture_liters": int(annual_yield * 0.6),
            "coverage_days": coverage_days(cost_tank, daily_demand),
            "roi_years": roi_years(tank_cost(cost_tank), annual_savings * 0.6),
        },
        "max_capture": {
            "name": "Maximum Capture",
            "tank_liters": max_tank,
            "cost_inr": round(tank_cost(max_tank), 0),
            "capture_liters": int(annual_yield * 0.95),
            "coverage_days": coverage_days(max_tank, daily_demand),
            "roi_years": roi_years(tank_cost(max_tank), annual_savings),
        },
        "dry_season": {
            "name": "Dry Season",
            "tank_liters": dry_tank,
            "cost_inr": round(tank_cost(dry_tank), 0),
            "capture_liters": int(annual_yield * 0.7),
            "coverage_days": coverage_days(dry_tank, daily_demand),
            "roi_years": roi_years(tank_cost(dry_tank), annual_savings * 0.8),
        },
    }


def run_pipeline(
    mode: AssessmentMode,
    address: str,
    lat: Optional[float] = None,
    lng: Optional[float] = None,
    roof_area_sqm: Optional[float] = None,
    roof_material: Optional[str] = None,
    state: Optional[str] = None,
    city: Optional[str] = None,
    people: int = DEFAULT_PEOPLE,
    floors: int = DEFAULT_FLOORS,
    site_id: Optional[str] = None,
    db_session: Any = None,
    pdf_base_path: str = "assessments",
) -> Dict[str, Any]:
    """
    Run the assessment pipeline for the given mode.
    Persists Assessment and returns response with pdf_url and confidence.
    pdf_base_path: "assessments" for full app (PDF at /api/v1/assessments/{id}/pdf),
                   "assess" for demo (PDF at /api/v1/assess/{id}/pdf).
    """
    if db_session is None:
        raise ValueError("db_session is required")

    if mode == AssessmentMode.SATELLITE_ONLY or mode == AssessmentMode.PHOTO:
        lat = lat or DEFAULT_LAT
        lng = lng or DEFAULT_LNG
        roof_area_sqm = roof_area_sqm or DEFAULT_ROOF_AREA_SQM
        roof_material = roof_material or DEFAULT_ROOF_MATERIAL
        state = state or DEFAULT_STATE
        city = city or DEFAULT_CITY
        if mode == AssessmentMode.PHOTO and not address:
            address = "Photo-based assessment (image analysis)"

    address = address or "Unknown address"
    lat = lat or DEFAULT_LAT
    lng = lng or DEFAULT_LNG
    roof_area_sqm = roof_area_sqm or DEFAULT_ROOF_AREA_SQM
    roof_material = (roof_material or DEFAULT_ROOF_MATERIAL).lower()
    state = state or DEFAULT_STATE
    city = city or DEFAULT_CITY
    site_id = site_id or f"SITE-{uuid.uuid4().hex[:8].upper()}"

    annual_rainfall = _get_rainfall(city, state)
    annual_yield = _calculate_yield(roof_area_sqm, annual_rainfall, roof_material)
    daily_demand = people * 135
    base_cost = roof_area_sqm * 150
    scenarios = _calculate_scenarios(annual_yield, daily_demand, base_cost)
    subsidy_info = _get_subsidy(state)
    recommended = scenarios["max_capture"]
    subsidy_amount = min(
        recommended["cost_inr"] * subsidy_info["pct"] / 100,
        subsidy_info["max"],
    )
    co2_avoided = (annual_yield / 1000) * 0.255
    confidence = get_confidence_for_mode(mode)

    from app.models.database import Assessment, Job, AssessmentStatus, JobStatus

    assessment_id = _generate_id("ASM")
    qr_code = str(uuid.uuid4())

    assessment = Assessment(
        assessment_id=assessment_id,
        site_id=site_id,
        address=address,
        lat=lat,
        lng=lng,
        roof_area_sqm=roof_area_sqm,
        roof_material=roof_material,
        demand_l_per_day=daily_demand,
        floors=floors,
        people=people,
        state=state,
        city=city,
        scenarios=scenarios,
        annual_rainfall_mm=annual_rainfall,
        annual_yield_liters=annual_yield,
        recommended_tank_liters=recommended["tank_liters"],
        total_cost_inr=recommended["cost_inr"],
        subsidy_pct=subsidy_info["pct"],
        subsidy_amount_inr=subsidy_amount,
        net_cost_inr=recommended["cost_inr"] - subsidy_amount,
        roi_years=recommended["roi_years"],
        co2_avoided_kg=co2_avoided,
        status=AssessmentStatus.COMPLETED,
        qr_verification_code=qr_code,
    )
    db_session.add(assessment)
    db_session.commit()
    db_session.refresh(assessment)

    job = Job(
        job_id=_generate_id("JOB"),
        assessment_id=assessment.id,
        status=JobStatus.PENDING,
    )
    db_session.add(job)
    db_session.commit()

    from app.services.success_features import (
        compute_water_security_index,
        compute_water_credits,
        get_impact_summary,
        get_badges_for_assessment,
    )
    daily_demand = people * 135
    water_security_index = compute_water_security_index(
        annual_yield_liters=annual_yield,
        recommended_tank_liters=recommended["tank_liters"],
        roi_years=recommended["roi_years"],
        subsidy_amount_inr=subsidy_amount,
        daily_demand_liters=daily_demand,
        has_recharge=False,
    )
    water_credits = compute_water_credits(annual_yield)
    impact = get_impact_summary(annual_yield, water_security_index, water_credits, co2_avoided)
    badges = get_badges_for_assessment(water_credits=water_credits, water_security_index=water_security_index)

    pdf_url = f"/api/v1/{pdf_base_path.strip('/')}/{assessment_id}/pdf"
    return {
        "assessment_id": assessment_id,
        "site_id": site_id,
        "address": address,
        "mode": mode.value,
        "annual_rainfall_mm": annual_rainfall,
        "annual_yield_liters": annual_yield,
        "scenarios": scenarios,
        "recommended_scenario": "max_capture",
        "confidence": round(confidence, 1),
        "water_security_index": water_security_index,
        "water_credits": water_credits,
        "impact": impact,
        "badges": badges,
        "pdf_url": pdf_url,
        "verify_url": f"/api/v1/verify/{qr_code}",
        "created_at": assessment.created_at.isoformat() if assessment.created_at else datetime.utcnow().isoformat(),
    }
