"""
RainForge Policy & Compliance Engine
Mandate enforcement, penalty calculation, subsidy eligibility
"""

from typing import Optional, Dict, List
from datetime import datetime
from dataclasses import dataclass
from enum import Enum


class MandateStatus(Enum):
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    EXEMPT = "exempt"
    GRACE_PERIOD = "grace_period"
    GRANDFATHERED = "grandfathered"


class RiskZone(Enum):
    FLOOD_PRONE = "flood_prone"
    WATER_SCARCE = "water_scarce"
    HERITAGE = "heritage"
    SEISMIC = "seismic"
    NORMAL = "normal"


@dataclass
class PolicyInput:
    """Extended inputs for policy compliance check."""
    # Property details
    building_approval_year: Optional[int] = None
    municipal_property_id: Optional[str] = None
    property_tax_id: Optional[str] = None
    land_ownership: str = "owned"  # owned / rented / govt
    existing_rwh_status: str = "none"  # none / partial / non_functional / functional
    
    # Risk & constraints
    flood_prone_zone: bool = False
    roof_load_limit: str = "standard"  # light / standard / reinforced
    heritage_building: bool = False
    water_quality_intent: str = "non_potable"  # potable / non_potable / recharge_only
    
    # Social equity
    income_slab: Optional[str] = None  # APL / BPL / EWS / LIG / MIG / HIG
    slum_classification: bool = False
    ews_classification: bool = False
    institution_type: Optional[str] = None  # school / hospital / anganwadi / community_center


class PolicyComplianceEngine:
    """
    Check RWH mandate compliance and calculate penalties/benefits.
    Based on state-wise RWH mandate rules.
    """
    
    # State-wise RWH mandates (building area threshold for mandatory RWH)
    STATE_MANDATES = {
        "Tamil Nadu": {"threshold_sqm": 100, "year": 2003, "penalty_pct": 10},
        "Karnataka": {"threshold_sqm": 100, "year": 2009, "penalty_pct": 5},
        "Maharashtra": {"threshold_sqm": 500, "year": 2007, "penalty_pct": 15},
        "Delhi": {"threshold_sqm": 100, "year": 2001, "penalty_pct": 10},
        "Gujarat": {"threshold_sqm": 500, "year": 2012, "penalty_pct": 5},
        "Rajasthan": {"threshold_sqm": 500, "year": 2011, "penalty_pct": 8},
        "Madhya Pradesh": {"threshold_sqm": 250, "year": 2015, "penalty_pct": 5},
        "Kerala": {"threshold_sqm": 100, "year": 2004, "penalty_pct": 10},
        "Telangana": {"threshold_sqm": 200, "year": 2017, "penalty_pct": 5},
        "Andhra Pradesh": {"threshold_sqm": 200, "year": 2016, "penalty_pct": 5},
        "West Bengal": {"threshold_sqm": 500, "year": 2018, "penalty_pct": 5},
        "Uttar Pradesh": {"threshold_sqm": 300, "year": 2020, "penalty_pct": 5},
    }
    
    # Priority scoring for social equity
    PRIORITY_MULTIPLIERS = {
        "school": 2.0,
        "hospital": 2.5,
        "anganwadi": 2.5,
        "community_center": 1.8,
        "slum": 2.0,
        "ews": 1.8,
        "bpl": 1.5,
    }
    
    def check_mandate_compliance(
        self,
        state: str,
        roof_area_sqm: float,
        building_approval_year: Optional[int],
        existing_rwh_status: str,
        has_functional_rwh: bool
    ) -> Dict:
        """
        Check if building complies with state RWH mandate.
        Returns compliance status and penalty avoided.
        """
        
        mandate = self.STATE_MANDATES.get(state)
        
        if not mandate:
            return {
                "status": MandateStatus.EXEMPT.value,
                "reason": f"No RWH mandate in {state}",
                "penalty_applicable": False,
                "penalty_amount_inr": 0
            }
        
        # Check if building is under threshold
        if roof_area_sqm < mandate["threshold_sqm"]:
            return {
                "status": MandateStatus.EXEMPT.value,
                "reason": f"Building area {roof_area_sqm} sqm below mandate threshold {mandate['threshold_sqm']} sqm",
                "penalty_applicable": False,
                "penalty_amount_inr": 0
            }
        
        # Check if building predates mandate (grandfathered)
        if building_approval_year and building_approval_year < mandate["year"]:
            return {
                "status": MandateStatus.GRANDFATHERED.value,
                "reason": f"Building approved in {building_approval_year}, before {mandate['year']} mandate",
                "penalty_applicable": False,
                "penalty_amount_inr": 0,
                "voluntary_adoption_bonus": True
            }
        
        # Building falls under mandate
        estimated_property_value = roof_area_sqm * 50000  # Rough estimate ₹50k/sqm
        penalty_amount = estimated_property_value * (mandate["penalty_pct"] / 100)
        
        if has_functional_rwh or existing_rwh_status == "functional":
            return {
                "status": MandateStatus.COMPLIANT.value,
                "reason": "Functional RWH system installed - mandate satisfied",
                "penalty_applicable": False,
                "penalty_amount_inr": 0,
                "penalty_avoided_inr": round(penalty_amount, 0),
                "mandate_year": mandate["year"]
            }
        
        return {
            "status": MandateStatus.NON_COMPLIANT.value,
            "reason": f"Building requires RWH per {state} mandate ({mandate['year']})",
            "penalty_applicable": True,
            "penalty_amount_inr": round(penalty_amount, 0),
            "penalty_pct": mandate["penalty_pct"],
            "mandate_year": mandate["year"],
            "action_required": "Install RWH system to avoid penalty and become compliant"
        }
    
    def calculate_priority_score(
        self,
        policy_input: PolicyInput,
        base_score: float = 50
    ) -> Dict:
        """
        Calculate social equity priority score.
        Higher score = higher priority for govt funding.
        """
        
        score = base_score
        factors = []
        
        # Institution multipliers
        if policy_input.institution_type:
            multiplier = self.PRIORITY_MULTIPLIERS.get(policy_input.institution_type, 1.0)
            score *= multiplier
            factors.append({
                "factor": "institution_type",
                "value": policy_input.institution_type,
                "multiplier": multiplier
            })
        
        # Slum/EWS boost
        if policy_input.slum_classification:
            score *= self.PRIORITY_MULTIPLIERS["slum"]
            factors.append({"factor": "slum", "multiplier": 2.0})
        
        if policy_input.ews_classification:
            score *= self.PRIORITY_MULTIPLIERS["ews"]
            factors.append({"factor": "ews", "multiplier": 1.8})
        
        # Income slab
        if policy_input.income_slab == "BPL":
            score *= 1.5
            factors.append({"factor": "income_bpl", "multiplier": 1.5})
        elif policy_input.income_slab == "EWS":
            score *= 1.3
            factors.append({"factor": "income_ews", "multiplier": 1.3})
        
        # Water scarcity zone boost
        if policy_input.flood_prone_zone:
            score *= 1.2
            factors.append({"factor": "flood_zone_mitigation", "multiplier": 1.2})
        
        # Normalize to 0-100
        final_score = min(100, score)
        
        return {
            "priority_score": round(final_score, 1),
            "priority_tier": self._get_tier(final_score),
            "factors": factors,
            "subsidy_eligibility_bonus_pct": min(20, (final_score - 50) / 2.5)
        }
    
    def _get_tier(self, score: float) -> str:
        if score >= 90:
            return "critical_priority"
        elif score >= 70:
            return "high_priority"
        elif score >= 50:
            return "standard"
        return "low_priority"
    
    def check_safety_constraints(
        self,
        policy_input: PolicyInput,
        proposed_tank_liters: float
    ) -> Dict:
        """
        Check if proposed design is safe and legal.
        Returns blocking issues if any.
        """
        
        blockers = []
        warnings = []
        
        # Heritage building check
        if policy_input.heritage_building:
            blockers.append({
                "type": "heritage_restriction",
                "message": "Heritage building - requires Archaeological Survey of India clearance",
                "action": "Obtain ASI approval before proceeding"
            })
        
        # Roof load check
        tank_weight_kg = proposed_tank_liters * 1  # 1 liter = 1 kg
        
        if policy_input.roof_load_limit == "light" and tank_weight_kg > 2000:
            blockers.append({
                "type": "structural_risk",
                "message": f"Tank weight ({tank_weight_kg} kg) exceeds light roof capacity",
                "action": "Structural assessment required or ground-level tank recommended"
            })
        elif policy_input.roof_load_limit == "standard" and tank_weight_kg > 10000:
            warnings.append({
                "type": "structural_warning",
                "message": "Large tank may require structural verification",
                "action": "Recommend structural engineer assessment"
            })
        
        # Flood zone check
        if policy_input.flood_prone_zone and policy_input.water_quality_intent == "recharge_only":
            warnings.append({
                "type": "flood_zone_recharge",
                "message": "Recharge in flood-prone zone may cause waterlogging",
                "action": "Consider storage+use instead of pure recharge"
            })
        
        # Potable water intent
        if policy_input.water_quality_intent == "potable":
            warnings.append({
                "type": "potable_safety",
                "message": "Potable use requires first-flush diverter + filtration + disinfection",
                "action": "Ensure water quality testing post-installation"
            })
        
        return {
            "design_allowed": len(blockers) == 0,
            "blockers": blockers,
            "warnings": warnings,
            "safety_score": 100 - (len(blockers) * 30 + len(warnings) * 10)
        }
    
    def calculate_subsidy_synergy(
        self,
        state: str,
        mandate_status: str,
        priority_score: float,
        base_subsidy_pct: float
    ) -> Dict:
        """
        Calculate combined subsidy + mandate synergy.
        """
        
        synergy_bonus = 0
        
        # Compliance bonus
        if mandate_status == MandateStatus.NON_COMPLIANT.value:
            synergy_bonus += 10  # Extra 10% for becoming compliant
        
        # Priority bonus
        if priority_score >= 70:
            synergy_bonus += 15
        elif priority_score >= 50:
            synergy_bonus += 5
        
        total_subsidy = min(75, base_subsidy_pct + synergy_bonus)  # Cap at 75%
        
        return {
            "base_subsidy_pct": base_subsidy_pct,
            "synergy_bonus_pct": synergy_bonus,
            "total_subsidy_pct": total_subsidy,
            "synergy_score": min(100, priority_score + (synergy_bonus * 2)),
            "funding_priority": "high" if total_subsidy >= 50 else "standard"
        }


class WaterSecurityCalculator:
    """
    Long-term water security metrics.
    5-year projections, aquifer impact, flood mitigation.
    """
    
    def calculate_long_term_metrics(
        self,
        annual_yield_liters: float,
        daily_demand_liters: float,
        ward_total_demand_kl_day: float = 5000,
        years: int = 5
    ) -> Dict:
        """
        Calculate long-term water security metrics.
        """
        
        # 5-year cumulative
        five_year_capture = annual_yield_liters * years
        
        # Self-sufficiency
        annual_demand = daily_demand_liters * 365
        self_sufficiency_pct = min(100, (annual_yield_liters / annual_demand) * 100)
        
        # Ward contribution
        ward_daily_kl = ward_total_demand_kl_day
        site_daily_kl = annual_yield_liters / 365 / 1000
        ward_contribution_pct = (site_daily_kl / ward_daily_kl) * 100
        
        # Aquifer impact (simplified)
        recharge_fraction = 0.3  # 30% goes to groundwater
        annual_recharge_kl = (annual_yield_liters * recharge_fraction) / 1000
        aquifer_stress_reduction = min(10, annual_recharge_kl / 10)  # Max 10% reduction
        
        # Flood mitigation
        peak_rainfall_mm = 100  # Assume 100mm/hr peak event
        roof_area_sqm = annual_yield_liters / 800 / 0.85  # Back-calculate
        peak_runoff_liters = roof_area_sqm * peak_rainfall_mm * 0.9
        peak_runoff_reduction_pct = min(90, 70)  # Tank captures up to 70%
        
        return {
            "short_term": {
                "annual_yield_liters": round(annual_yield_liters, 0),
                "self_sufficiency_pct": round(self_sufficiency_pct, 1),
                "days_of_water_security": round(annual_yield_liters / daily_demand_liters, 0)
            },
            "long_term": {
                "five_year_capture_liters": round(five_year_capture, 0),
                "five_year_capture_kl": round(five_year_capture / 1000, 1)
            },
            "aquifer_impact": {
                "annual_recharge_kl": round(annual_recharge_kl, 1),
                "aquifer_stress_reduction_pct": round(aquifer_stress_reduction, 2),
                "rating": "positive" if annual_recharge_kl > 20 else "moderate"
            },
            "flood_mitigation": {
                "peak_runoff_reduced_liters": round(peak_runoff_liters * 0.7, 0),
                "peak_flow_reduction_pct": peak_runoff_reduction_pct,
                "urban_flooding_benefit": "high" if peak_runoff_liters > 5000 else "moderate"
            },
            "ward_contribution": {
                "ward_self_sufficiency_contribution_pct": round(ward_contribution_pct, 4),
                "cumulative_impact_if_replicated": "significant"
            },
            "climate_resilience_score": min(100, self_sufficiency_pct + peak_runoff_reduction_pct / 2)
        }


class SystemDegradationPredictor:
    """
    Predict system failure and degradation over time.
    """
    
    COMPONENT_LIFESPANS = {
        "filter": {"years": 2, "failure_mode": "clogging"},
        "first_flush": {"years": 5, "failure_mode": "valve_failure"},
        "tank_ferrocement": {"years": 25, "failure_mode": "crack_seepage"},
        "tank_plastic": {"years": 15, "failure_mode": "uv_degradation"},
        "pipes_pvc": {"years": 20, "failure_mode": "joint_failure"},
        "pump": {"years": 8, "failure_mode": "motor_burnout"},
        "sensor": {"years": 5, "failure_mode": "calibration_drift"},
    }
    
    def predict_degradation(
        self,
        installation_date: datetime,
        tank_type: str = "ferrocement",
        has_pump: bool = False,
        maintenance_history: Optional[List[Dict]] = None
    ) -> Dict:
        """
        Predict system degradation and failure points.
        """
        
        age_years = (datetime.utcnow() - installation_date).days / 365
        
        predictions = []
        overall_health = 100
        
        for component, config in self.COMPONENT_LIFESPANS.items():
            if component.startswith("tank_"):
                if component != f"tank_{tank_type}":
                    continue
            
            if component == "pump" and not has_pump:
                continue
            
            lifespan = config["years"]
            remaining = max(0, lifespan - age_years)
            health_pct = (remaining / lifespan) * 100
            
            predictions.append({
                "component": component,
                "expected_lifespan_years": lifespan,
                "age_years": round(age_years, 1),
                "remaining_years": round(remaining, 1),
                "health_pct": round(health_pct, 1),
                "failure_mode": config["failure_mode"],
                "replacement_urgency": "critical" if remaining < 0.5 else "soon" if remaining < 1 else "normal"
            })
            
            overall_health = min(overall_health, health_pct)
        
        # Maintenance negligence risk
        if not maintenance_history:
            negligence_risk = "high"
        elif len(maintenance_history) < age_years * 2:  # Expect ~2 maintenance events/year
            negligence_risk = "medium"
        else:
            negligence_risk = "low"
        
        return {
            "installation_date": installation_date.strftime("%Y-%m-%d"),
            "system_age_years": round(age_years, 1),
            "overall_health_pct": round(overall_health, 1),
            "component_predictions": predictions,
            "maintenance_negligence_risk": negligence_risk,
            "next_failure_predicted": min(predictions, key=lambda x: x["remaining_years"]) if predictions else None,
            "action_required": any(p["replacement_urgency"] == "critical" for p in predictions)
        }
