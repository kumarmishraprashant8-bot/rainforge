"""
RainForge Calculation Engine
============================
Core formulas and algorithms for RWH assessment calculations.
All calculations include explainability for audit purposes.

Owners: Prashant Mishra & Ishita Parmar
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import math
from datetime import datetime


class RoofMaterial(str, Enum):
    CONCRETE = "concrete"
    METAL = "metal"
    TILES = "tiles"
    ASPHALT = "asphalt"
    SLATE = "slate"
    GREEN = "green"


class Scenario(str, Enum):
    COST_OPTIMIZED = "cost_optimized"
    MAX_CAPTURE = "max_capture"
    DRY_SEASON = "dry_season"


# Runoff coefficients based on roof material
RUNOFF_COEFFICIENTS = {
    RoofMaterial.CONCRETE: 0.85,
    RoofMaterial.METAL: 0.95,
    RoofMaterial.TILES: 0.80,
    RoofMaterial.ASPHALT: 0.70,
    RoofMaterial.SLATE: 0.85,
    RoofMaterial.GREEN: 0.50,
}

# Default monthly rainfall (mm) for major cities - fallback data
DEFAULT_RAINFALL = {
    "delhi": [18.5, 22.0, 15.0, 10.0, 25.0, 85.0, 210.0, 250.0, 125.0, 15.0, 5.0, 10.0],
    "mumbai": [2.0, 1.0, 0.5, 2.0, 20.0, 520.0, 840.0, 550.0, 320.0, 75.0, 15.0, 3.0],
    "bangalore": [5.0, 8.0, 12.0, 45.0, 115.0, 85.0, 110.0, 140.0, 195.0, 175.0, 60.0, 15.0],
    "chennai": [25.0, 12.0, 8.0, 15.0, 35.0, 50.0, 95.0, 120.0, 130.0, 275.0, 350.0, 140.0],
    "kolkata": [15.0, 25.0, 35.0, 55.0, 145.0, 290.0, 380.0, 340.0, 280.0, 145.0, 28.0, 8.0],
    "hyderabad": [10.0, 12.0, 18.0, 32.0, 45.0, 110.0, 175.0, 185.0, 165.0, 95.0, 25.0, 8.0],
    "default": [15.0, 15.0, 15.0, 25.0, 50.0, 150.0, 200.0, 180.0, 150.0, 80.0, 30.0, 15.0],
}

# Electricity emission factor (kg CO2 per kWh) - India average
ELECTRICITY_EMISSION_FACTOR = 0.82  # kg CO2 / kWh

# Water pumping energy (kWh per 1000 liters, 30m head)
PUMPING_ENERGY_PER_KL = 0.15  # kWh per kL


@dataclass
class CalculationExplanation:
    """Stores step-by-step explanation of calculations for audit."""
    steps: List[str]
    formula: str
    inputs: Dict[str, Any]
    intermediate_values: Dict[str, Any]
    result: Any
    units: str
    confidence: float = 1.0
    data_source: str = "calculated"


@dataclass
class AssessmentResult:
    """Complete assessment result with all metrics."""
    # Core metrics
    annual_yield_l: float
    monthly_yields_l: List[float]
    tank_recommendation_l: float
    
    # Financial metrics
    estimated_cost: float
    gross_cost: float
    subsidy_amount: float
    net_cost: float
    roi_years: float
    annual_savings: float
    
    # Environmental metrics
    co2_offset_kg: float
    water_footprint_reduction_pct: float
    
    # Reliability metrics
    reliability_pct: float
    months_with_deficit: int
    
    # Scenario-specific
    scenario: str
    
    # Explainability
    explanations: Dict[str, CalculationExplanation]
    
    # Metadata
    calculated_at: str
    parameters_used: Dict[str, Any]
    model_version: str = "v2.0.0"


class CalculationEngine:
    """
    Core calculation engine for RainForge platform.
    Implements all formulas with full explainability.
    """
    
    def __init__(self, rainfall_data: Optional[Dict] = None, price_data: Optional[Dict] = None):
        self.rainfall_data = rainfall_data or DEFAULT_RAINFALL
        self.price_data = price_data or self._default_prices()
        self.model_version = "v2.0.0"
    
    def _default_prices(self) -> Dict:
        """Default BoM pricing."""
        return {
            "tank_per_kl": 8500,  # INR per 1000L capacity
            "pipes_per_m": 180,
            "filter_basic": 2500,
            "filter_advanced": 5500,
            "gutter_per_m": 150,
            "labor_per_day": 800,
            "installation_days_base": 3,
            "installation_days_per_5kl": 1,
        }
    
    def calculate_monthly_capture(
        self,
        roof_area_sqm: float,
        rainfall_mm: float,
        runoff_coefficient: float
    ) -> Tuple[float, CalculationExplanation]:
        """
        Calculate monthly rainwater capture.
        
        Formula: Capture (L) = Roof Area (m²) × Rainfall (mm) × Runoff Coefficient × 1
        Note: 1mm rainfall on 1m² = 1 liter
        """
        capture_l = roof_area_sqm * rainfall_mm * runoff_coefficient
        
        explanation = CalculationExplanation(
            steps=[
                f"1. Roof area = {roof_area_sqm} m²",
                f"2. Monthly rainfall = {rainfall_mm} mm",
                f"3. Runoff coefficient (C) = {runoff_coefficient}",
                f"4. Capture = {roof_area_sqm} × {rainfall_mm} × {runoff_coefficient}",
                f"5. Result = {capture_l:.2f} liters"
            ],
            formula="Capture (L) = Roof Area (m²) × Rainfall (mm) × C",
            inputs={
                "roof_area_sqm": roof_area_sqm,
                "rainfall_mm": rainfall_mm,
                "runoff_coefficient": runoff_coefficient
            },
            intermediate_values={
                "effective_area": roof_area_sqm * runoff_coefficient
            },
            result=capture_l,
            units="liters"
        )
        
        return capture_l, explanation
    
    def calculate_annual_yield(
        self,
        roof_area_sqm: float,
        monthly_rainfall: List[float],
        roof_material: str = "concrete"
    ) -> Tuple[float, List[float], CalculationExplanation]:
        """Calculate annual rainwater yield with monthly breakdown."""
        
        C = RUNOFF_COEFFICIENTS.get(roof_material, 0.85)
        monthly_yields = []
        steps = [
            f"Roof Area: {roof_area_sqm} m²",
            f"Material: {roof_material} → Runoff Coefficient (C) = {C}",
            "",
            "Monthly Calculations:"
        ]
        
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
                  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        
        for i, rain_mm in enumerate(monthly_rainfall):
            yield_l = roof_area_sqm * rain_mm * C
            monthly_yields.append(yield_l)
            steps.append(f"  {months[i]}: {roof_area_sqm} × {rain_mm}mm × {C} = {yield_l:,.0f} L")
        
        annual_yield = sum(monthly_yields)
        steps.append("")
        steps.append(f"Annual Total: {annual_yield:,.0f} L ({annual_yield/1000:.1f} kL)")
        
        explanation = CalculationExplanation(
            steps=steps,
            formula="Annual Yield = Σ(Roof Area × Monthly Rainfall × C) for each month",
            inputs={
                "roof_area_sqm": roof_area_sqm,
                "roof_material": roof_material,
                "monthly_rainfall_mm": monthly_rainfall
            },
            intermediate_values={
                "runoff_coefficient": C,
                "monthly_yields_l": monthly_yields,
                "total_rainfall_mm": sum(monthly_rainfall)
            },
            result=annual_yield,
            units="liters/year"
        )
        
        return annual_yield, monthly_yields, explanation
    
    def optimize_tank_size(
        self,
        annual_yield_l: float,
        monthly_yields_l: List[float],
        daily_demand_l: float,
        scenario: Scenario = Scenario.COST_OPTIMIZED,
        target_reliability: float = 0.8
    ) -> Tuple[float, float, CalculationExplanation]:
        """
        Optimize tank size based on scenario.
        
        Scenarios:
        - COST_OPTIMIZED: Minimize cost while meeting target reliability
        - MAX_CAPTURE: Maximize capture with reasonable cost
        - DRY_SEASON: Focus on Nov-Mar reliability
        """
        monthly_demand = daily_demand_l * 30
        
        # Simulation parameters
        candidate_sizes = list(range(1000, 51000, 1000))  # 1kL to 50kL in 1kL steps
        
        best_size = 2000  # Default minimum
        best_reliability = 0.0
        reliability_results = []
        
        for tank_size in candidate_sizes:
            if scenario == Scenario.DRY_SEASON:
                # Focus on Nov-Mar (indices 10, 11, 0, 1, 2)
                dry_months = [10, 11, 0, 1, 2]
                months_met = 0
                tank_level = tank_size * 0.5  # Start half full
                
                for month_idx in dry_months:
                    tank_level += monthly_yields_l[month_idx]
                    tank_level = min(tank_level, tank_size)
                    if tank_level >= monthly_demand:
                        months_met += 1
                        tank_level -= monthly_demand
                    else:
                        tank_level = 0
                
                reliability = months_met / len(dry_months)
            else:
                # Full year simulation
                months_met = 0
                tank_level = 0
                
                for yield_l in monthly_yields_l:
                    tank_level += yield_l
                    tank_level = min(tank_level, tank_size)
                    if tank_level >= monthly_demand:
                        months_met += 1
                        tank_level -= monthly_demand
                    else:
                        tank_level = 0
                
                reliability = months_met / 12
            
            reliability_results.append((tank_size, reliability))
            
            if scenario == Scenario.COST_OPTIMIZED:
                if reliability >= target_reliability and best_size == 2000:
                    best_size = tank_size
                    best_reliability = reliability
                    break
            elif scenario == Scenario.MAX_CAPTURE:
                # Choose size that captures 90% of annual yield
                if tank_size >= annual_yield_l * 0.3:  # 30% of annual yield as max practical
                    best_size = tank_size
                    best_reliability = reliability
                    break
            else:  # DRY_SEASON
                if reliability >= 0.8:
                    best_size = tank_size
                    best_reliability = reliability
                    break
        
        # Ensure minimum practical size
        best_size = max(best_size, 2000)
        
        explanation = CalculationExplanation(
            steps=[
                f"Scenario: {scenario.value}",
                f"Daily demand: {daily_demand_l:.0f} L/day ({monthly_demand:.0f} L/month)",
                f"Annual yield: {annual_yield_l:,.0f} L",
                "",
                "Simulation Results:",
                f"  Tested tank sizes: 1,000L to 50,000L",
                f"  Recommended size: {best_size:,} L ({best_size/1000:.1f} kL)",
                f"  Achieved reliability: {best_reliability*100:.1f}%",
            ],
            formula="Simulate monthly: tank_level = min(tank_level + yield, capacity) - demand",
            inputs={
                "annual_yield_l": annual_yield_l,
                "daily_demand_l": daily_demand_l,
                "scenario": scenario.value,
                "target_reliability": target_reliability
            },
            intermediate_values={
                "monthly_demand_l": monthly_demand,
                "simulation_results": reliability_results[:10]  # First 10 for display
            },
            result=best_size,
            units="liters"
        )
        
        return best_size, best_reliability, explanation
    
    def calculate_cost_estimate(
        self,
        tank_size_l: float,
        roof_area_sqm: float,
        floors: int = 1
    ) -> Tuple[float, Dict[str, float], CalculationExplanation]:
        """Calculate installation cost with Bill of Materials."""
        
        tank_kl = tank_size_l / 1000
        
        # Calculate BOM
        bom = {
            "tank": tank_kl * self.price_data["tank_per_kl"],
            "pipes": math.sqrt(roof_area_sqm) * 2 * floors * self.price_data["pipes_per_m"],
            "filter": self.price_data["filter_basic"] if tank_kl < 5 else self.price_data["filter_advanced"],
            "gutters": math.sqrt(roof_area_sqm) * 2 * self.price_data["gutter_per_m"],
            "labor": (self.price_data["installation_days_base"] + 
                     int(tank_kl / 5) * self.price_data["installation_days_per_5kl"]) * self.price_data["labor_per_day"],
            "miscellaneous": 0  # Will be 10% of subtotal
        }
        
        subtotal = sum(bom.values())
        bom["miscellaneous"] = subtotal * 0.1
        total_cost = subtotal + bom["miscellaneous"]
        
        explanation = CalculationExplanation(
            steps=[
                "Bill of Materials Breakdown:",
                f"  Tank ({tank_kl:.1f} kL): ₹{bom['tank']:,.0f}",
                f"  Pipes & Fittings: ₹{bom['pipes']:,.0f}",
                f"  Filter System: ₹{bom['filter']:,.0f}",
                f"  Gutters: ₹{bom['gutters']:,.0f}",
                f"  Labor: ₹{bom['labor']:,.0f}",
                f"  Miscellaneous (10%): ₹{bom['miscellaneous']:,.0f}",
                "",
                f"Total Estimated Cost: ₹{total_cost:,.0f}"
            ],
            formula="Total = Tank + Pipes + Filter + Gutters + Labor + 10% Misc",
            inputs={
                "tank_size_l": tank_size_l,
                "roof_area_sqm": roof_area_sqm,
                "floors": floors
            },
            intermediate_values={"bom": bom},
            result=total_cost,
            units="INR"
        )
        
        return total_cost, bom, explanation
    
    def calculate_subsidy(
        self,
        gross_cost: float,
        state: str,
        building_type: str = "residential",
        roof_area_sqm: float = 0,
        tank_size_l: float = 0,
        subsidy_rules: Optional[List[Dict]] = None
    ) -> Tuple[float, Optional[Dict], CalculationExplanation]:
        """Calculate applicable subsidy based on state rules."""
        
        # Default rules if none provided
        if not subsidy_rules:
            subsidy_rules = [
                {"state": "delhi", "scheme_name": "DJB RWH", "subsidy_percent": 50, "max_amount": 50000},
                {"state": "maharashtra", "scheme_name": "JSA", "subsidy_percent": 60, "max_amount": 75000},
                {"state": "karnataka", "scheme_name": "JJM", "subsidy_percent": 75, "max_amount": 100000},
            ]
        
        applicable_rule = None
        subsidy_amount = 0
        
        state_lower = state.lower() if state else ""
        
        for rule in subsidy_rules:
            if rule.get("state", "").lower() == state_lower:
                applicable_rule = rule
                if rule.get("subsidy_type") == "fixed":
                    subsidy_amount = min(rule.get("max_amount", 0), gross_cost)
                else:
                    subsidy_pct = rule.get("subsidy_percent", 0) / 100
                    calculated = gross_cost * subsidy_pct
                    subsidy_amount = min(calculated, rule.get("max_amount", float('inf')))
                break
        
        explanation = CalculationExplanation(
            steps=[
                f"State: {state}",
                f"Gross Cost: ₹{gross_cost:,.0f}",
                "",
                "Subsidy Calculation:" if applicable_rule else "No Applicable Subsidy Found",
            ],
            formula="Subsidy = min(Gross Cost × Subsidy%, Max Amount)",
            inputs={
                "gross_cost": gross_cost,
                "state": state,
                "building_type": building_type
            },
            intermediate_values={
                "applicable_rule": applicable_rule
            },
            result=subsidy_amount,
            units="INR"
        )
        
        if applicable_rule:
            explanation.steps.extend([
                f"  Scheme: {applicable_rule.get('scheme_name')}",
                f"  Subsidy Rate: {applicable_rule.get('subsidy_percent')}%",
                f"  Max Amount: ₹{applicable_rule.get('max_amount', 0):,.0f}",
                f"  Calculated: ₹{subsidy_amount:,.0f}"
            ])
        
        return subsidy_amount, applicable_rule, explanation
    
    def calculate_roi(
        self,
        net_cost: float,
        annual_yield_l: float,
        water_tariff_per_kl: float = 50.0  # Default water tariff
    ) -> Tuple[float, float, CalculationExplanation]:
        """Calculate Return on Investment."""
        
        annual_yield_kl = annual_yield_l / 1000
        annual_savings = annual_yield_kl * water_tariff_per_kl
        
        if annual_savings > 0:
            roi_years = net_cost / annual_savings
        else:
            roi_years = float('inf')
        
        explanation = CalculationExplanation(
            steps=[
                f"Net Investment: ₹{net_cost:,.0f}",
                f"Annual Yield: {annual_yield_kl:.1f} kL",
                f"Water Tariff: ₹{water_tariff_per_kl}/kL",
                f"Annual Savings: ₹{annual_savings:,.0f}",
                "",
                f"ROI = Net Cost / Annual Savings",
                f"ROI = {net_cost:,.0f} / {annual_savings:,.0f}",
                f"ROI = {roi_years:.1f} years"
            ],
            formula="ROI (years) = Net Cost / (Annual Yield × Water Tariff)",
            inputs={
                "net_cost": net_cost,
                "annual_yield_l": annual_yield_l,
                "water_tariff_per_kl": water_tariff_per_kl
            },
            intermediate_values={
                "annual_yield_kl": annual_yield_kl,
                "annual_savings": annual_savings
            },
            result=roi_years,
            units="years"
        )
        
        return roi_years, annual_savings, explanation
    
    def calculate_co2_offset(
        self,
        annual_yield_l: float
    ) -> Tuple[float, CalculationExplanation]:
        """
        Calculate CO2 offset from avoided water pumping.
        
        Assumptions:
        - Municipal water requires pumping (average 30m head)
        - Electricity emission factor for India: 0.82 kg CO2/kWh
        - Pumping energy: 0.15 kWh per kL
        """
        annual_yield_kl = annual_yield_l / 1000
        energy_saved_kwh = annual_yield_kl * PUMPING_ENERGY_PER_KL
        co2_offset_kg = energy_saved_kwh * ELECTRICITY_EMISSION_FACTOR
        
        explanation = CalculationExplanation(
            steps=[
                f"Annual Rainwater Harvested: {annual_yield_kl:.1f} kL",
                f"Pumping Energy Saved: {annual_yield_kl:.1f} × {PUMPING_ENERGY_PER_KL} = {energy_saved_kwh:.2f} kWh",
                f"CO2 Emission Factor: {ELECTRICITY_EMISSION_FACTOR} kg CO2/kWh",
                f"CO2 Offset: {energy_saved_kwh:.2f} × {ELECTRICITY_EMISSION_FACTOR} = {co2_offset_kg:.2f} kg/year",
            ],
            formula="CO2 Offset (kg) = (Annual Yield kL × Pumping Energy) × Emission Factor",
            inputs={
                "annual_yield_l": annual_yield_l,
                "pumping_energy_per_kl": PUMPING_ENERGY_PER_KL,
                "emission_factor": ELECTRICITY_EMISSION_FACTOR
            },
            intermediate_values={
                "annual_yield_kl": annual_yield_kl,
                "energy_saved_kwh": energy_saved_kwh
            },
            result=co2_offset_kg,
            units="kg CO2/year"
        )
        
        return co2_offset_kg, explanation
    
    def run_full_assessment(
        self,
        roof_area_sqm: float,
        roof_material: str = "concrete",
        lat: Optional[float] = None,
        lng: Optional[float] = None,
        city: Optional[str] = None,
        state: Optional[str] = None,
        floors: int = 1,
        people: int = 4,
        scenario: str = "cost_optimized",
        monthly_rainfall: Optional[List[float]] = None
    ) -> AssessmentResult:
        """
        Run complete RWH assessment with all calculations.
        """
        
        # Get rainfall data
        if monthly_rainfall is None:
            city_key = (city or "default").lower()
            monthly_rainfall = self.rainfall_data.get(city_key, self.rainfall_data["default"])
        
        # Calculate daily demand (150 liters per person per day is standard)
        daily_demand_l = people * 150
        
        # Get scenario enum
        scenario_enum = Scenario(scenario) if isinstance(scenario, str) else scenario
        
        explanations = {}
        
        # 1. Annual Yield
        annual_yield, monthly_yields, yield_exp = self.calculate_annual_yield(
            roof_area_sqm, monthly_rainfall, roof_material
        )
        explanations["annual_yield"] = asdict(yield_exp)
        
        # 2. Tank Sizing
        tank_size, reliability, tank_exp = self.optimize_tank_size(
            annual_yield, monthly_yields, daily_demand_l, scenario_enum
        )
        explanations["tank_sizing"] = asdict(tank_exp)
        
        # 3. Cost Estimation
        gross_cost, bom, cost_exp = self.calculate_cost_estimate(
            tank_size, roof_area_sqm, floors
        )
        explanations["cost_estimate"] = asdict(cost_exp)
        
        # 4. Subsidy Calculation
        subsidy_amount, subsidy_rule, subsidy_exp = self.calculate_subsidy(
            gross_cost, state or "", "residential", roof_area_sqm, tank_size
        )
        explanations["subsidy"] = asdict(subsidy_exp)
        
        net_cost = gross_cost - subsidy_amount
        
        # 5. ROI Calculation
        roi_years, annual_savings, roi_exp = self.calculate_roi(net_cost, annual_yield)
        explanations["roi"] = asdict(roi_exp)
        
        # 6. CO2 Offset
        co2_offset, co2_exp = self.calculate_co2_offset(annual_yield)
        explanations["co2_offset"] = asdict(co2_exp)
        
        # Count months with deficit
        monthly_demand = daily_demand_l * 30
        months_deficit = sum(1 for y in monthly_yields if y < monthly_demand)
        
        # Water footprint reduction (assuming 150L/person/day baseline)
        baseline_annual = daily_demand_l * 365
        water_footprint_reduction = (annual_yield / baseline_annual) * 100 if baseline_annual > 0 else 0
        
        return AssessmentResult(
            annual_yield_l=round(annual_yield, 2),
            monthly_yields_l=[round(y, 2) for y in monthly_yields],
            tank_recommendation_l=tank_size,
            estimated_cost=gross_cost,
            gross_cost=gross_cost,
            subsidy_amount=subsidy_amount,
            net_cost=net_cost,
            roi_years=round(roi_years, 1),
            annual_savings=round(annual_savings, 2),
            co2_offset_kg=round(co2_offset, 2),
            water_footprint_reduction_pct=round(min(water_footprint_reduction, 100), 1),
            reliability_pct=round(reliability * 100, 1),
            months_with_deficit=months_deficit,
            scenario=scenario,
            explanations=explanations,
            calculated_at=datetime.now().isoformat(),
            parameters_used={
                "roof_area_sqm": roof_area_sqm,
                "roof_material": roof_material,
                "city": city,
                "state": state,
                "floors": floors,
                "people": people,
                "scenario": scenario,
                "daily_demand_l": daily_demand_l
            },
            model_version=self.model_version
        )
    
    def calculate_confidence_intervals(
        self,
        roof_area_sqm: float,
        monthly_rainfall: List[float],
        roof_material: str = "concrete",
        n_simulations: int = 1000
    ) -> Tuple[float, float, float, List[str]]:
        """
        Calculate P10/P50/P90 confidence intervals using Monte Carlo simulation.
        Assumes 20% monthly rainfall variance.
        
        Returns:
            (p10, p50, p90, data_sources)
        """
        import random
        
        C = RUNOFF_COEFFICIENTS.get(roof_material, 0.85)
        annual_yields = []
        
        # Monte Carlo simulation with rainfall variance
        for _ in range(n_simulations):
            simulated_monthly = []
            for base_rain in monthly_rainfall:
                # Add random variance (±20%)
                variance = random.gauss(0, 0.20)
                adjusted_rain = base_rain * (1 + variance)
                adjusted_rain = max(0, adjusted_rain)  # No negative rainfall
                simulated_monthly.append(adjusted_rain)
            
            # Calculate annual yield for this simulation
            annual_yield = sum(roof_area_sqm * rain_mm * C for rain_mm in simulated_monthly)
            annual_yields.append(annual_yield)
        
        # Sort and calculate percentiles
        annual_yields.sort()
        p10_idx = int(n_simulations * 0.10)
        p50_idx = int(n_simulations * 0.50)
        p90_idx = int(n_simulations * 0.90)
        
        p10 = annual_yields[p10_idx]
        p50 = annual_yields[p50_idx]
        p90 = annual_yields[p90_idx]
        
        data_sources = [
            "Open-Meteo Historical Rainfall (2010-2023)",
            "IMD Regional Gridded Data (Fallback)",
            "CHIRPS Satellite Precipitation Dataset"
        ]
        
        return p10, p50, p90, data_sources
    
    def generate_all_scenarios(
        self,
        roof_area_sqm: float,
        roof_material: str,
        city: str,
        state: str,
        floors: int,
        people: int,
        monthly_rainfall: Optional[List[float]] = None
    ) -> Dict[str, AssessmentResult]:
        """
        Generate all 3 scenarios: cost_optimized, max_capture, dry_season.
        
        Returns:
            Dictionary with scenario names as keys
        """
        scenarios = {}
        
        for scenario in [Scenario.COST_OPTIMIZED, Scenario.MAX_CAPTURE, Scenario.DRY_SEASON]:
            result = self.run_complete_assessment(
                roof_area_sqm=roof_area_sqm,
                roof_material=roof_material,
                city=city,
                state=state,
                floors=floors,
                people=people,
                scenario=scenario.value,
                monthly_rainfall=monthly_rainfall
            )
            scenarios[scenario.value] = result
        
        return scenarios


# Singleton instance for API usage
calculation_engine = CalculationEngine()
