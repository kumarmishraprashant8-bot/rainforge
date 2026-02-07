"""
RainForge success features API: leaderboard, crisis mode, impact, badges.
Makes the app grand-success ready: sticky, shareable, trustworthy.
"""

from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Optional, List

from app.services.success_features import (
    get_crisis_alert,
    set_crisis_alert,
    get_leaderboard_wards,
    compute_water_security_index,
    compute_water_credits,
    get_impact_summary,
    get_badges_for_assessment,
)

router = APIRouter(prefix="/success", tags=["Success features", "Engagement"])


# ---------- Crisis mode (water alert banner) ----------

@router.get("/crisis")
def get_crisis():
    """
    Active water crisis / alert for global banner.
    Returns empty when no alert. Used by frontend to show "Save water" banner.
    """
    return get_crisis_alert() or {"active": False}


class CrisisUpdate(BaseModel):
    active: bool = True
    title: str = "Water alert"
    message: str = "Use water wisely. Check your tank level."
    severity: str = Field("info", pattern="^(info|warning|critical)$")


@router.post("/crisis")
def update_crisis(payload: CrisisUpdate):
    """Set or clear crisis alert (admin / system)."""
    set_crisis_alert(
        active=payload.active,
        title=payload.title,
        message=payload.message,
        severity=payload.severity,
    )
    return get_crisis_alert()


# ---------- Leaderboard (wards by adoption) ----------

@router.get("/leaderboard")
def leaderboard():
    """
    Ward leaderboard: rank by systems installed and water captured.
    Drives gamification: "Your ward is #3 in Delhi."
    """
    return {
        "city": "New Delhi",
        "wards": get_leaderboard_wards(),
        "description": "Top wards by RWH adoption and water captured",
    }


# ---------- Impact calculator (for share cards) ----------

@router.get("/impact")
def compute_impact(
    annual_yield_liters: float,
    tank_liters: int = 10000,
    roi_years: float = 4.0,
    subsidy_inr: float = 0,
    daily_demand: float = 540,
):
    """
    Compute water security index + credits + share message for a given yield.
    Used by frontend for "Share my impact" without re-running assessment.
    """
    wsi = compute_water_security_index(
        annual_yield_liters=annual_yield_liters,
        recommended_tank_liters=tank_liters,
        roi_years=roi_years,
        subsidy_amount_inr=subsidy_inr,
        daily_demand_liters=daily_demand,
    )
    credits = compute_water_credits(annual_yield_liters)
    co2 = (annual_yield_liters / 1000) * 0.255
    impact = get_impact_summary(annual_yield_liters, wsi, credits, co2)
    return {"water_security_index": wsi, "water_credits": credits, "impact": impact}


# ---------- Badges (gamification) ----------

@router.get("/badges")
def badges_for_yield(
    water_credits: int = 0,
    water_security_index: int = 0,
    is_first: bool = False,
):
    """Badges earned for given metrics (for display after assessment)."""
    return {
        "badges": get_badges_for_assessment(
            is_first=is_first,
            water_credits=water_credits,
            water_security_index=water_security_index,
        ),
    }
