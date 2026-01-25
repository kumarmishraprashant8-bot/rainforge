"""
RainForge Hydrology Engine - Government Platform Edition
Implements scenario-based assessment, water balance simulation, and explainable calculations.
"""

from enum import Enum
from typing import Dict, List, Tuple
import math

class ScenarioMode(str, Enum):
    COST_OPTIMIZED = "cost_optimized"
    MAX_CAPTURE = "max_capture"
    DRY_SEASON = "dry_season"

class SoilType(str, Enum):
    SANDY = "sandy"
    LOAMY = "loamy"
    CLAY = "clay"
    ROCKY = "rocky"

class HydrologyEngine:
    """
    Core hydrology calculations for rainwater harvesting assessment.
    All formulas are based on Indian Standard IS 15797:2008 and CPWD guidelines.
    """
    
    # Runoff coefficients by surface type (dimensionless, 0-1)
    RUNOFF_COEFFICIENTS = {
        "concrete": 0.85,
        "metal": 0.90,
        "tiles": 0.80,
        "asbestos": 0.85,
        "thatched": 0.60,
        "gravel": 0.70,
    }
    
    # Tank costs per liter (INR) by capacity range
    TANK_COSTS = {
        "small": {"max_liters": 5000, "cost_per_liter": 8},      # < 5kL
        "medium": {"max_liters": 20000, "cost_per_liter": 6},    # 5-20kL
        "large": {"max_liters": 100000, "cost_per_liter": 4},    # 20-100kL
        "bulk": {"max_liters": float('inf'), "cost_per_liter": 3} # > 100kL
    }
    
    # Soil permeability coefficients (m/day)
    SOIL_PERMEABILITY = {
        SoilType.SANDY: 5.0,
        SoilType.LOAMY: 1.0,
        SoilType.CLAY: 0.05,
        SoilType.ROCKY: 0.01,
    }
    
    @staticmethod
    def calculate_runoff(
        area_sqm: float, 
        rainfall_mm: float, 
        surface_type: str = "concrete",
        explain: bool = False
    ) -> Dict:
        """
        Calculate runoff volume using Rational Method.
        Formula: Q = C × I × A × η
        
        Where:
            Q = Harvested runoff (Liters)
            C = Runoff Coefficient (0-1)
            I = Rainfall (mm)
            A = Catchment Area (m²)
            η = Collection efficiency (0.85-0.90)
        """
        c = HydrologyEngine.RUNOFF_COEFFICIENTS.get(surface_type.lower(), 0.80)
        efficiency = 0.90  # First flush + filter losses
        
        runoff_liters = area_sqm * rainfall_mm * c * efficiency
        
        result = {"runoff_liters": round(runoff_liters, 2)}
        
        if explain:
            result["explanation"] = {
                "formula": "Q = C × I × A × η",
                "variables": {
                    "C (Runoff Coefficient)": c,
                    "I (Rainfall in mm)": rainfall_mm,
                    "A (Area in m²)": area_sqm,
                    "η (Collection Efficiency)": efficiency
                },
                "calculation": f"{area_sqm} × {rainfall_mm} × {c} × {efficiency} = {round(runoff_liters, 2)} L",
                "reference": "IS 15797:2008, CPWD RWH Manual"
            }
        
        return result
    
    @staticmethod
    def simulate_yearly_yield(
        area_sqm: float,
        monthly_rainfall: List[float],
        surface_type: str = "concrete",
        scenario: ScenarioMode = ScenarioMode.COST_OPTIMIZED,
        explain: bool = False
    ) -> Dict:
        """
        Simulate yearly water yield with scenario-based optimization.
        
        Scenarios:
        - COST_OPTIMIZED: Minimize tank size while meeting 80% demand
        - MAX_CAPTURE: Capture maximum possible rainfall
        - DRY_SEASON: Prioritize storage for dry months (Oct-Mar in India)
        """
        monthly_yield = []
        
        for rain_mm in monthly_rainfall:
            result = HydrologyEngine.calculate_runoff(area_sqm, rain_mm, surface_type)
            monthly_yield.append(round(result["runoff_liters"], 2))
        
        total_yield = sum(monthly_yield)
        avg_monthly = total_yield / 12
        
        # Scenario-specific adjustments
        scenario_multiplier = {
            ScenarioMode.COST_OPTIMIZED: 0.8,    # 80% capture target
            ScenarioMode.MAX_CAPTURE: 1.0,        # 100% capture
            ScenarioMode.DRY_SEASON: 0.9,         # Focus on Nov-Apr storage
        }
        
        effective_yield = total_yield * scenario_multiplier[scenario]
        
        # Calculate dry season metrics (Oct-Mar in India)
        dry_months = [9, 10, 11, 0, 1, 2]  # Oct-Mar indices
        dry_season_yield = sum(monthly_yield[i] for i in dry_months if i < len(monthly_yield))
        wet_season_yield = total_yield - dry_season_yield
        
        result = {
            "total_yield_liters": round(effective_yield, 2),
            "monthly_yield_liters": monthly_yield,
            "avg_monthly_liters": round(avg_monthly, 2),
            "scenario": scenario.value,
            "dry_season_yield": round(dry_season_yield, 2),
            "wet_season_yield": round(wet_season_yield, 2),
            "capture_efficiency": scenario_multiplier[scenario]
        }
        
        if explain:
            result["explanation"] = {
                "method": "Monthly Runoff Summation with Scenario Optimization",
                "scenario_description": {
                    "cost_optimized": "Targets 80% capture to reduce storage costs",
                    "max_capture": "Maximizes all available rainfall capture",
                    "dry_season": "Optimizes for Nov-Apr water security"
                }[scenario.value],
                "formula": "Σ(C × Iₘ × A × η) for m=1 to 12",
                "reference": "CGWB Technical Manual on Artificial Recharge"
            }
        
        return result
    
    @staticmethod
    def water_balance_simulation(
        monthly_yield: List[float],
        daily_demand_liters: float,
        tank_capacity: float,
        initial_level: float = 0.5,  # 50% full
        explain: bool = False
    ) -> Dict:
        """
        Monthly water balance simulation.
        Tracks: Supply, Demand, Storage, Overflow, Deficit
        """
        monthly_demand = daily_demand_liters * 30
        
        balance = []
        tank_level = tank_capacity * initial_level
        total_overflow = 0
        total_deficit = 0
        
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
                  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        
        for i, supply in enumerate(monthly_yield):
            # Add supply
            available = tank_level + supply
            
            # Subtract demand
            if available >= monthly_demand:
                used = monthly_demand
                deficit = 0
            else:
                used = available
                deficit = monthly_demand - available
                total_deficit += deficit
            
            remaining = available - used
            
            # Calculate overflow
            if remaining > tank_capacity:
                overflow = remaining - tank_capacity
                tank_level = tank_capacity
                total_overflow += overflow
            else:
                overflow = 0
                tank_level = remaining
            
            balance.append({
                "month": months[i],
                "supply": round(supply, 0),
                "demand": round(monthly_demand, 0),
                "tank_level": round(tank_level, 0),
                "overflow": round(overflow, 0),
                "deficit": round(deficit, 0),
                "utilization_pct": round((used / monthly_demand) * 100 if monthly_demand > 0 else 100, 1)
            })
        
        # Calculate reliability metrics
        months_met = sum(1 for b in balance if b["deficit"] == 0)
        reliability = (months_met / 12) * 100
        
        result = {
            "monthly_balance": balance,
            "total_overflow_liters": round(total_overflow, 0),
            "total_deficit_liters": round(total_deficit, 0),
            "reliability_percent": round(reliability, 1),
            "months_demand_met": months_met,
            "recommended_action": "Adequate" if reliability >= 80 else "Increase storage" if total_overflow > 0 else "Reduce demand"
        }
        
        if explain:
            result["explanation"] = {
                "method": "Monthly Mass Balance with Carryover",
                "formula": "Sₜ = Sₜ₋₁ + Qₜ - Dₜ (bounded by 0 and capacity)",
                "variables": {
                    "Sₜ": "Tank level at month t",
                    "Qₜ": "Inflow (rainfall capture)",
                    "Dₜ": "Demand (consumption)"
                },
                "reliability_definition": "% of months where demand is fully met",
                "reference": "FAO Irrigation & Drainage Paper 56"
            }
        
        return result
    
    @staticmethod
    def calculate_storage_requirement(
        monthly_yield: List[float],
        daily_demand_liters: float,
        scenario: ScenarioMode = ScenarioMode.COST_OPTIMIZED,
        explain: bool = False
    ) -> Dict:
        """
        Calculate optimal storage capacity based on scenario.
        """
        monthly_demand = daily_demand_liters * 30
        annual_demand = monthly_demand * 12
        total_yield = sum(monthly_yield)
        
        # Scenario-based sizing
        if scenario == ScenarioMode.COST_OPTIMIZED:
            # Size for 2-month carryover
            capacity = monthly_demand * 2
        elif scenario == ScenarioMode.MAX_CAPTURE:
            # Size to capture peak 3-month rainfall
            peak_3_months = max(sum(monthly_yield[i:i+3]) for i in range(10))
            capacity = peak_3_months
        else:  # DRY_SEASON
            # Size for 4-month dry season buffer
            capacity = monthly_demand * 4
        
        # Apply practical limits
        capacity = max(1000, min(capacity, 100000))  # 1kL to 100kL
        
        # Calculate cost
        cost = HydrologyEngine._calculate_tank_cost(capacity)
        
        # ROI calculation
        water_saved_value = total_yield * 0.05  # ₹0.05/L saved
        payback_years = cost / water_saved_value if water_saved_value > 0 else float('inf')
        
        result = {
            "recommended_capacity_liters": round(capacity, 0),
            "scenario": scenario.value,
            "estimated_cost_inr": round(cost, 0),
            "annual_savings_inr": round(water_saved_value, 0),
            "payback_years": round(payback_years, 1),
            "demand_coverage_percent": round((total_yield / annual_demand) * 100 if annual_demand > 0 else 100, 1)
        }
        
        if explain:
            result["explanation"] = {
                "sizing_method": {
                    "cost_optimized": "2-month carryover capacity",
                    "max_capture": "Peak 3-month rainfall storage",
                    "dry_season": "4-month buffer for Oct-Mar"
                }[scenario.value],
                "cost_basis": "CPWD Schedule of Rates 2024",
                "roi_assumption": "₹0.05/L municipal water replacement value"
            }
        
        return result
    
    @staticmethod
    def calculate_recharge_suitability(
        soil_type: SoilType,
        groundwater_depth_m: float,
        area_sqm: float,
        explain: bool = False
    ) -> Dict:
        """
        Calculate groundwater recharge suitability score.
        Based on CGWB guidelines for artificial recharge.
        """
        # Get permeability
        permeability = HydrologyEngine.SOIL_PERMEABILITY[soil_type]
        
        # Score components (0-100)
        permeability_score = min(100, permeability * 20)
        depth_score = min(100, max(0, (groundwater_depth_m - 3) * 10))  # Better if > 3m
        
        # Combined suitability
        suitability = (permeability_score * 0.6 + depth_score * 0.4)
        
        # Recommended recharge structure
        if suitability >= 70:
            structure = "Recharge Well"
            pit_size = "1.5m × 1.5m × 3m"
        elif suitability >= 40:
            structure = "Recharge Pit with Filter"
            pit_size = "2m × 2m × 2m"
        else:
            structure = "Storage Tank (Recharge not recommended)"
            pit_size = "N/A"
        
        # Potential recharge rate
        daily_recharge = permeability * area_sqm * 0.001  # m³/day to kL/day
        
        result = {
            "suitability_score": round(suitability, 1),
            "suitability_grade": "Excellent" if suitability >= 70 else "Good" if suitability >= 50 else "Moderate" if suitability >= 30 else "Poor",
            "recommended_structure": structure,
            "recommended_pit_size": pit_size,
            "potential_recharge_kld": round(daily_recharge, 2),
            "soil_permeability_m_per_day": permeability
        }
        
        if explain:
            result["explanation"] = {
                "scoring_method": "Weighted average of permeability (60%) and depth (40%)",
                "permeability_scores": {s.value: HydrologyEngine.SOIL_PERMEABILITY[s] for s in SoilType},
                "depth_criteria": "Optimal: >10m, Minimum: 3m below surface",
                "reference": "CGWB Manual on Artificial Recharge, 2007"
            }
        
        return result
    
    @staticmethod
    def _calculate_tank_cost(capacity_liters: float) -> float:
        """Calculate estimated tank cost based on capacity."""
        for tier, data in HydrologyEngine.TANK_COSTS.items():
            if capacity_liters <= data["max_liters"]:
                return capacity_liters * data["cost_per_liter"]
        return capacity_liters * 3  # Bulk rate
    
    @staticmethod
    def generate_bom(
        tank_capacity: float,
        roof_area: float,
        include_recharge: bool = False
    ) -> List[Dict]:
        """
        Generate Bill of Materials for RWH system.
        """
        bom = [
            {"item": "Storage Tank (PVC/Ferrocement)", "quantity": 1, "unit": "nos", 
             "specification": f"{int(tank_capacity)}L capacity", "est_cost": HydrologyEngine._calculate_tank_cost(tank_capacity)},
            {"item": "First Flush Diverter", "quantity": 1, "unit": "nos",
             "specification": "20L capacity, auto-reset", "est_cost": 1500},
            {"item": "PVC Pipe 110mm", "quantity": max(10, roof_area ** 0.5), "unit": "m",
             "specification": "Class 4, ISI marked", "est_cost": 150 * max(10, roof_area ** 0.5)},
            {"item": "Mesh Filter", "quantity": 2, "unit": "nos",
             "specification": "Stainless steel, 1mm mesh", "est_cost": 800 * 2},
            {"item": "Float Valve", "quantity": 1, "unit": "nos",
             "specification": "1 inch, brass", "est_cost": 450},
            {"item": "Overflow Pipe", "quantity": 3, "unit": "m",
             "specification": "PVC 110mm with mosquito mesh", "est_cost": 150 * 3},
        ]
        
        if include_recharge:
            bom.extend([
                {"item": "Recharge Pit Excavation", "quantity": 6, "unit": "m³",
                 "specification": "2m × 2m × 1.5m", "est_cost": 500 * 6},
                {"item": "Filter Media (Gravel)", "quantity": 2, "unit": "m³",
                 "specification": "20-40mm graded", "est_cost": 1200 * 2},
                {"item": "Filter Media (Sand)", "quantity": 1, "unit": "m³",
                 "specification": "Coarse river sand", "est_cost": 800},
            ])
        
        total = sum(item["est_cost"] for item in bom)
        bom.append({"item": "TOTAL", "quantity": "-", "unit": "-", 
                    "specification": "-", "est_cost": total})
        
        return bom
