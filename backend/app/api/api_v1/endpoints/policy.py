"""
RainForge Policy API Endpoints
Subsidy eligibility and policy compliance.
"""

from fastapi import APIRouter
from app.services.policy import PolicyService

router = APIRouter()


@router.get("/schemes/{state}")
async def get_subsidy_schemes(state: str, building_type: str = "residential"):
    """
    Get available subsidy schemes for a state.
    """
    schemes = PolicyService.get_eligible_schemes(state, building_type)
    return {"state": state, "schemes": schemes, "count": len(schemes)}


@router.get("/calculate-net-cost")
async def calculate_net_cost(
    system_cost: float,
    state: str,
    building_type: str = "residential"
):
    """
    Calculate net cost after applying best subsidy.
    """
    result = PolicyService.calculate_net_cost(system_cost, state, building_type)
    return result


@router.get("/compliance/{state}")
async def get_compliance_status(
    state: str,
    roof_area_sqm: float,
    has_rwh: bool = False,
    building_type: str = "residential"
):
    """
    Check policy compliance for a property.
    """
    result = PolicyService.get_policy_compliance_score(
        roof_area_sqm=roof_area_sqm,
        has_rwh=has_rwh,
        state=state,
        building_type=building_type
    )
    return result


@router.get("/all-states")
async def get_all_states():
    """
    Get list of states with RWH schemes.
    """
    return {
        "states": [
            {"code": "delhi", "name": "Delhi", "mandatory_threshold_sqm": 100},
            {"code": "karnataka", "name": "Karnataka", "mandatory_threshold_sqm": 100},
            {"code": "tamil_nadu", "name": "Tamil Nadu", "mandatory_threshold_sqm": 100},
            {"code": "rajasthan", "name": "Rajasthan", "mandatory_threshold_sqm": 300},
            {"code": "maharashtra", "name": "Maharashtra", "mandatory_threshold_sqm": 300},
        ]
    }
