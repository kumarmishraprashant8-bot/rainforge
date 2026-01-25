"""
RainForge Policy & Subsidy Service
State-wise subsidy information and policy compliance.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class SubsidyScheme:
    state: str
    scheme_name: str
    subsidy_percent: float
    max_amount_inr: float
    eligibility: List[str]
    ministry: str
    application_link: str


class PolicyService:
    """
    Service for subsidy eligibility and policy compliance calculations.
    """
    
    # State-wise RWH subsidy schemes (Mock data - real integration with state portals needed)
    SUBSIDY_SCHEMES = {
        "delhi": [
            SubsidyScheme(
                state="Delhi",
                scheme_name="DJB Rainwater Harvesting Rebate",
                subsidy_percent=50,
                max_amount_inr=50000,
                eligibility=["Residential property", "Plot > 100 sqm", "New construction or retrofit"],
                ministry="Delhi Jal Board",
                application_link="https://delhijalboard.nic.in/rwh"
            )
        ],
        "karnataka": [
            SubsidyScheme(
                state="Karnataka",
                scheme_name="Neeru Bhaghya RWH Scheme",
                subsidy_percent=75,
                max_amount_inr=75000,
                eligibility=["BPL families", "Rural areas", "First-time installation"],
                ministry="Rural Development & Panchayat Raj",
                application_link="https://rdpr.karnataka.gov.in"
            )
        ],
        "tamil_nadu": [
            SubsidyScheme(
                state="Tamil Nadu",
                scheme_name="CMDA RWH Incentive",
                subsidy_percent=100,  # Property tax rebate
                max_amount_inr=25000,
                eligibility=["Chennai Metropolitan Area", "Mandatory for plots > 200 sqm"],
                ministry="Chennai Metro Water",
                application_link="https://chennaimetrowater.tn.gov.in"
            )
        ],
        "rajasthan": [
            SubsidyScheme(
                state="Rajasthan",
                scheme_name="Mukhya Mantri Jal Swavalamban Abhiyan",
                subsidy_percent=60,
                max_amount_inr=100000,
                eligibility=["Government buildings", "Schools", "Hospitals", "Community centers"],
                ministry="Water Resources Department",
                application_link="https://water.rajasthan.gov.in"
            )
        ],
        "maharashtra": [
            SubsidyScheme(
                state="Maharashtra",
                scheme_name="Jalyukt Shivar Abhiyan",
                subsidy_percent=40,
                max_amount_inr=30000,
                eligibility=["Rural areas", "Agricultural land", "Drought-prone districts"],
                ministry="Soil & Water Conservation",
                application_link="https://mrsac.gov.in"
            )
        ],
        "default": [
            SubsidyScheme(
                state="Central",
                scheme_name="Jal Shakti Abhiyan RWH",
                subsidy_percent=30,
                max_amount_inr=25000,
                eligibility=["Any state", "Residential or institutional", "New installation"],
                ministry="Ministry of Jal Shakti",
                application_link="https://jalshakti.gov.in"
            )
        ]
    }
    
    @staticmethod
    def get_eligible_schemes(
        state: str,
        building_type: str = "residential",
        roof_area_sqm: float = 100,
        is_rural: bool = False
    ) -> List[Dict]:
        """
        Get list of applicable subsidy schemes.
        """
        state_key = state.lower().replace(" ", "_")
        schemes = PolicyService.SUBSIDY_SCHEMES.get(state_key, [])
        
        # Add central scheme as fallback
        schemes.extend(PolicyService.SUBSIDY_SCHEMES["default"])
        
        eligible = []
        for scheme in schemes:
            eligible.append({
                "state": scheme.state,
                "scheme_name": scheme.scheme_name,
                "subsidy_percent": scheme.subsidy_percent,
                "max_amount_inr": scheme.max_amount_inr,
                "eligibility_criteria": scheme.eligibility,
                "ministry": scheme.ministry,
                "application_link": scheme.application_link
            })
        
        return eligible
    
    @staticmethod
    def calculate_net_cost(
        system_cost_inr: float,
        state: str,
        building_type: str = "residential"
    ) -> Dict:
        """
        Calculate net cost after applying best available subsidy.
        """
        schemes = PolicyService.get_eligible_schemes(state, building_type)
        
        if not schemes:
            return {
                "gross_cost_inr": system_cost_inr,
                "subsidy_amount_inr": 0,
                "net_cost_inr": system_cost_inr,
                "applied_scheme": None
            }
        
        # Find best subsidy
        best_subsidy = 0
        best_scheme = None
        
        for scheme in schemes:
            subsidy = min(
                system_cost_inr * scheme["subsidy_percent"] / 100,
                scheme["max_amount_inr"]
            )
            if subsidy > best_subsidy:
                best_subsidy = subsidy
                best_scheme = scheme
        
        return {
            "gross_cost_inr": round(system_cost_inr),
            "subsidy_amount_inr": round(best_subsidy),
            "net_cost_inr": round(system_cost_inr - best_subsidy),
            "applied_scheme": best_scheme["scheme_name"] if best_scheme else None,
            "scheme_details": best_scheme
        }
    
    @staticmethod
    def get_policy_compliance_score(
        roof_area_sqm: float,
        has_rwh: bool,
        state: str,
        building_type: str = "residential"
    ) -> Dict:
        """
        Calculate policy compliance score based on state regulations.
        """
        # State-wise mandatory RWH thresholds (sqm)
        MANDATORY_THRESHOLDS = {
            "tamil_nadu": 100,
            "karnataka": 100,
            "delhi": 100,
            "rajasthan": 300,
            "maharashtra": 300,
            "default": 500
        }
        
        state_key = state.lower().replace(" ", "_")
        threshold = MANDATORY_THRESHOLDS.get(state_key, MANDATORY_THRESHOLDS["default"])
        
        is_mandatory = roof_area_sqm >= threshold
        is_compliant = has_rwh or not is_mandatory
        
        # Score calculation
        if has_rwh:
            score = 100
            status = "Compliant"
        elif is_mandatory:
            score = 0
            status = "Non-Compliant (Mandatory)"
        else:
            score = 50
            status = "Not Required (Voluntary)"
        
        return {
            "compliance_score": score,
            "status": status,
            "is_mandatory": is_mandatory,
            "mandatory_threshold_sqm": threshold,
            "your_roof_area_sqm": roof_area_sqm,
            "recommendation": "Excellent - System installed" if has_rwh else 
                            "Action Required - RWH is mandatory" if is_mandatory else
                            "Consider RWH for water savings and tax benefits"
        }
