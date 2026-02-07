"""
RainForge success features: Water Security Index, credits, leaderboard, crisis mode.
Makes the app sticky, shareable, and grand-success ready.
"""

from typing import Dict, Any, List


def compute_water_security_index(
    annual_yield_liters: float,
    recommended_tank_liters: int,
    roi_years: float,
    subsidy_amount_inr: float,
    daily_demand_liters: float = 540,
    has_recharge: bool = False,
) -> int:
    """
    Single 0-100 score: how secure is this site's water future?
    Factors: yield, storage coverage, payback, subsidy uptake, recharge.
    """
    score = 0.0
    # Yield score (max 30): more yield = better
    if annual_yield_liters >= 100000:
        score += 30
    elif annual_yield_liters >= 50000:
        score += 22
    elif annual_yield_liters >= 20000:
        score += 15
    else:
        score += min(14, annual_yield_liters / 2000)
    # Coverage days (max 25): tank vs demand
    if daily_demand_liters and daily_demand_liters > 0:
        coverage_days = recommended_tank_liters / daily_demand_liters
        if coverage_days >= 90:
            score += 25
        elif coverage_days >= 60:
            score += 20
        elif coverage_days >= 30:
            score += 14
        else:
            score += min(13, coverage_days)
    # ROI score (max 25): faster payback = better
    if roi_years <= 3:
        score += 25
    elif roi_years <= 5:
        score += 18
    elif roi_years <= 8:
        score += 10
    else:
        score += max(0, 8 - roi_years)
    # Subsidy uptake (max 10)
    if subsidy_amount_inr and subsidy_amount_inr > 0:
        score += 10
    else:
        score += 4
    # Recharge bonus (max 10)
    score += 10 if has_recharge else 0
    return min(100, int(round(score)))


def compute_water_credits(annual_yield_liters: float) -> int:
    """Impact currency: 1 credit per 1000 L potential annual capture."""
    return max(0, int(annual_yield_liters / 1000))


def get_impact_summary(
    annual_yield_liters: float,
    water_security_index: int,
    water_credits: int,
    co2_avoided_kg: float,
) -> Dict[str, Any]:
    """Human-readable impact for share cards and dashboards."""
    showers = int(annual_yield_liters / 50)  # ~50 L per shower
    return {
        "water_saved_liters_year": int(annual_yield_liters),
        "water_security_index": water_security_index,
        "water_credits": water_credits,
        "co2_avoided_kg": round(co2_avoided_kg, 1),
        "equivalent_showers_per_year": showers,
        "share_message": f"I'm harvesting {int(annual_yield_liters):,} L of rainwater/year with RainForge. Water Security Index: {water_security_index}/100. Join the movement.",
    }


# In-memory crisis state (in production: Redis or DB)
_crisis_alert: Dict[str, Any] = {}


def get_crisis_alert() -> Dict[str, Any]:
    return _crisis_alert


def set_crisis_alert(active: bool, title: str = "", message: str = "", severity: str = "info") -> None:
    global _crisis_alert
    _crisis_alert = {
        "active": active,
        "title": title or "Water alert",
        "message": message or "Use water wisely.",
        "severity": severity,
    } if active else {}


def get_leaderboard_wards() -> List[Dict[str, Any]]:
    """Ward leaderboard: rank by systems + water captured (demo data)."""
    wards = [
        {"ward_id": "NDMC-14", "ward_name": "Connaught Place", "systems": 312, "captured": 18400000, "rank": 1},
        {"ward_id": "NDMC-28", "ward_name": "Rohini Sector 5", "systems": 276, "captured": 15200000, "rank": 2},
        {"ward_id": "SDMC-07", "ward_name": "Saket", "systems": 245, "captured": 12800000, "rank": 3},
        {"ward_id": "SDMC-15", "ward_name": "Dwarka Sector 12", "systems": 198, "captured": 11200000, "rank": 4},
        {"ward_id": "EDMC-03", "ward_name": "Shahdara", "systems": 189, "captured": 9500000, "rank": 5},
    ]
    return wards


def get_badges_for_assessment(
    is_first: bool = False,
    water_credits: int = 0,
    water_security_index: int = 0,
) -> List[Dict[str, str]]:
    """Badges earned from this assessment (gamification)."""
    badges = []
    if is_first:
        badges.append({"id": "first_assessment", "name": "First Drop", "description": "Completed your first assessment"})
    if water_credits >= 50:
        badges.append({"id": "water_champion", "name": "Water Champion", "description": f"{water_credits}+ water credits"})
    elif water_credits >= 20:
        badges.append({"id": "water_saver", "name": "Water Saver", "description": f"{water_credits} water credits"})
    if water_security_index >= 80:
        badges.append({"id": "high_security", "name": "High Security", "description": "Water Security Index 80+"})
    return badges
