"""
RainForge Advanced Analytics
Monte-Carlo simulation, subsidy optimizer, predictive models
"""

import random
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import math


@dataclass
class SimulationResult:
    """Result of Monte-Carlo simulation."""
    p50_yield: float
    p90_yield: float
    p10_yield: float
    mean_yield: float
    std_dev: float
    reliability_pct: float
    simulations_run: int


class MonteCarloSimulator:
    """
    Monte-Carlo uncertainty quantification for yield predictions.
    Provides p50/p90 confidence intervals that government can trust.
    """
    
    def __init__(self, seed: Optional[int] = None):
        if seed:
            random.seed(seed)
    
    def simulate_annual_yield(
        self,
        roof_area_sqm: float,
        annual_rainfall_mm: float,
        runoff_coefficient: float,
        monthly_distribution: List[float],
        n_simulations: int = 1000,
        rainfall_cv: float = 0.25,  # Coefficient of variation for rainfall
        roof_cv: float = 0.10,      # Uncertainty in roof measurement
        runoff_cv: float = 0.05     # Uncertainty in runoff coefficient
    ) -> SimulationResult:
        """
        Run Monte-Carlo simulation for annual yield prediction.
        
        Returns:
            P50, P90, P10 yields with reliability estimate
        """
        
        yields = []
        
        for _ in range(n_simulations):
            # Sample from distributions
            sampled_rainfall = max(0, random.gauss(annual_rainfall_mm, annual_rainfall_mm * rainfall_cv))
            sampled_area = max(1, random.gauss(roof_area_sqm, roof_area_sqm * roof_cv))
            sampled_runoff = min(1.0, max(0.3, random.gauss(runoff_coefficient, runoff_coefficient * runoff_cv)))
            
            # Calculate yield
            annual_yield = sampled_area * sampled_rainfall * sampled_runoff
            yields.append(annual_yield)
        
        # Sort for percentiles
        yields.sort()
        
        p10 = yields[int(n_simulations * 0.10)]
        p50 = yields[int(n_simulations * 0.50)]
        p90 = yields[int(n_simulations * 0.90)]
        mean = sum(yields) / n_simulations
        
        # Calculate standard deviation
        variance = sum((y - mean) ** 2 for y in yields) / n_simulations
        std_dev = math.sqrt(variance)
        
        # Reliability = P(yield >= demand)
        # Assuming demand is 60% of mean yield
        demand_threshold = mean * 0.6
        reliable_count = sum(1 for y in yields if y >= demand_threshold)
        reliability = (reliable_count / n_simulations) * 100
        
        return SimulationResult(
            p50_yield=round(p50, 0),
            p90_yield=round(p90, 0),
            p10_yield=round(p10, 0),
            mean_yield=round(mean, 0),
            std_dev=round(std_dev, 0),
            reliability_pct=round(reliability, 1),
            simulations_run=n_simulations
        )
    
    def simulate_monthly_performance(
        self,
        tank_size_liters: float,
        daily_demand_liters: float,
        monthly_yields: List[float],
        n_simulations: int = 500
    ) -> Dict:
        """
        Simulate monthly water balance to estimate reliability.
        """
        
        results = []
        
        for _ in range(n_simulations):
            tank_level = tank_size_liters * 0.5  # Start half full
            shortfall_days = 0
            overflow_liters = 0
            
            for month_yield in monthly_yields:
                # Add some stochasticity
                actual_yield = max(0, random.gauss(month_yield, month_yield * 0.3))
                actual_demand = daily_demand_liters * 30 * random.gauss(1.0, 0.1)
                
                tank_level += actual_yield
                tank_level -= actual_demand
                
                # Handle overflow
                if tank_level > tank_size_liters:
                    overflow_liters += tank_level - tank_size_liters
                    tank_level = tank_size_liters
                
                # Handle shortfall
                if tank_level < 0:
                    shortfall_days += abs(tank_level) / daily_demand_liters
                    tank_level = 0
            
            results.append({
                "final_level": tank_level,
                "shortfall_days": shortfall_days,
                "overflow_liters": overflow_liters
            })
        
        avg_shortfall = sum(r["shortfall_days"] for r in results) / n_simulations
        avg_overflow = sum(r["overflow_liters"] for r in results) / n_simulations
        
        return {
            "avg_shortfall_days": round(avg_shortfall, 1),
            "max_shortfall_days": max(r["shortfall_days"] for r in results),
            "avg_overflow_liters": round(avg_overflow, 0),
            "reliability_pct": round(100 * (365 - avg_shortfall) / 365, 1),
            "simulations_run": n_simulations
        }


class SubsidyOptimizer:
    """
    Optimize subsidy allocation across multiple sites.
    Knapsack-style solver to maximize impact given budget.
    """
    
    def optimize_allocation(
        self,
        sites: List[Dict],
        total_budget_inr: float,
        max_subsidy_pct: float = 50
    ) -> Dict:
        """
        Given a list of sites and budget, find optimal subsidy allocation.
        
        Each site dict should have:
        - site_id, cost_inr, annual_yield_liters, priority_score
        """
        
        # Sort by cost-effectiveness (yield per rupee * priority)
        def score(site):
            return (site.get("annual_yield_liters", 0) / max(1, site.get("cost_inr", 1))) * site.get("priority_score", 1)
        
        sorted_sites = sorted(sites, key=score, reverse=True)
        
        allocated = []
        remaining_budget = total_budget_inr
        total_subsidy = 0
        total_yield = 0
        
        for site in sorted_sites:
            cost = site.get("cost_inr", 0)
            subsidy_amount = min(cost * (max_subsidy_pct / 100), remaining_budget)
            
            if subsidy_amount >= cost * 0.10:  # At least 10% subsidy
                allocated.append({
                    "site_id": site["site_id"],
                    "cost_inr": cost,
                    "subsidy_inr": round(subsidy_amount, 0),
                    "subsidy_pct": round((subsidy_amount / cost) * 100, 1),
                    "yield_liters": site.get("annual_yield_liters", 0)
                })
                remaining_budget -= subsidy_amount
                total_subsidy += subsidy_amount
                total_yield += site.get("annual_yield_liters", 0)
        
        return {
            "total_budget_inr": total_budget_inr,
            "total_allocated_inr": round(total_subsidy, 0),
            "remaining_inr": round(remaining_budget, 0),
            "sites_funded": len(allocated),
            "total_yield_liters": round(total_yield, 0),
            "cost_per_liter": round(total_subsidy / max(1, total_yield), 2),
            "allocations": allocated
        }


class EnvironmentalImpactCalculator:
    """
    Calculate environmental co-benefits.
    Flood reduction, carbon credits, groundwater recharge.
    """
    
    # Emission factors
    WATER_TREATMENT_CO2_KG_PER_KL = 0.7  # kg CO2 per 1000L treated water
    PUMP_ENERGY_CO2_KG_PER_KL = 0.3      # kg CO2 per 1000L pumped
    
    # Carbon credit price (India)
    CARBON_CREDIT_INR_PER_TON = 2500
    
    # Flood reduction factors
    FLOOD_REDUCTION_PER_KL = 0.8  # 80% of stored water = reduced runoff
    
    def calculate_impact(
        self,
        annual_capture_liters: float,
        recharge_fraction: float = 0.3,  # Fraction going to groundwater
        years: int = 25  # System lifetime
    ) -> Dict:
        """
        Calculate environmental co-benefits of RWH installation.
        """
        
        annual_kl = annual_capture_liters / 1000
        lifetime_kl = annual_kl * years
        
        # CO2 avoided
        annual_co2_kg = annual_kl * (self.WATER_TREATMENT_CO2_KG_PER_KL + self.PUMP_ENERGY_CO2_KG_PER_KL)
        lifetime_co2_kg = annual_co2_kg * years
        
        # Carbon credits value
        carbon_credit_value = (lifetime_co2_kg / 1000) * self.CARBON_CREDIT_INR_PER_TON
        
        # Groundwater recharge
        annual_recharge_kl = annual_kl * recharge_fraction
        lifetime_recharge_kl = annual_recharge_kl * years
        
        # Flood reduction (peak runoff avoided)
        annual_flood_reduction_kl = annual_kl * self.FLOOD_REDUCTION_PER_KL
        
        return {
            "carbon_impact": {
                "annual_co2_avoided_kg": round(annual_co2_kg, 1),
                "lifetime_co2_avoided_kg": round(lifetime_co2_kg, 1),
                "lifetime_co2_avoided_tons": round(lifetime_co2_kg / 1000, 2),
                "carbon_credit_value_inr": round(carbon_credit_value, 0)
            },
            "water_impact": {
                "annual_capture_kl": round(annual_kl, 1),
                "lifetime_capture_kl": round(lifetime_kl, 1),
                "municipal_water_saved_pct": round(min(100, annual_kl / 150 * 100), 1)  # Assuming 150kl/year avg household
            },
            "groundwater_impact": {
                "annual_recharge_kl": round(annual_recharge_kl, 1),
                "lifetime_recharge_kl": round(lifetime_recharge_kl, 1),
                "aquifer_benefit": "positive" if annual_recharge_kl > 50 else "moderate"
            },
            "flood_reduction": {
                "annual_runoff_reduced_kl": round(annual_flood_reduction_kl, 1),
                "peak_flow_reduction_pct": min(15, annual_kl / 100)  # Simplified
            },
            "system_lifetime_years": years,
            "total_environmental_value_inr": round(carbon_credit_value + (lifetime_kl * 5), 0)  # Rough estimate
        }


class PredictiveMaintenanceScheduler:
    """
    Predict maintenance needs based on installation and telemetry.
    """
    
    MAINTENANCE_INTERVALS = {
        "filter_cleaning": {"months": 3, "cost_inr": 500},
        "gutter_inspection": {"months": 6, "cost_inr": 1000},
        "tank_cleaning": {"months": 12, "cost_inr": 2500},
        "pump_service": {"months": 18, "cost_inr": 3500},
        "full_inspection": {"months": 24, "cost_inr": 5000},
    }
    
    def generate_schedule(
        self,
        installation_date: datetime,
        tank_type: str = "ferrocement",
        has_pump: bool = False,
        years: int = 5
    ) -> Dict:
        """
        Generate maintenance schedule for an installation.
        """
        
        schedule = []
        total_cost = 0
        
        for task, config in self.MAINTENANCE_INTERVALS.items():
            if task == "pump_service" and not has_pump:
                continue
            
            interval_months = config["months"]
            occurrences = int((years * 12) / interval_months)
            
            for i in range(1, occurrences + 1):
                from datetime import timedelta
                task_date = installation_date + timedelta(days=interval_months * 30 * i)
                schedule.append({
                    "task": task,
                    "due_date": task_date.strftime("%Y-%m-%d"),
                    "estimated_cost_inr": config["cost_inr"],
                    "priority": "high" if task in ["tank_cleaning", "full_inspection"] else "normal"
                })
                total_cost += config["cost_inr"]
        
        # Sort by date
        schedule.sort(key=lambda x: x["due_date"])
        
        return {
            "installation_date": installation_date.strftime("%Y-%m-%d"),
            "schedule_years": years,
            "total_tasks": len(schedule),
            "total_maintenance_cost_inr": total_cost,
            "annual_maintenance_cost_inr": round(total_cost / years, 0),
            "schedule": schedule[:20],  # First 20 tasks
            "next_task": schedule[0] if schedule else None
        }
    
    def predict_from_telemetry(
        self,
        tank_levels: List[float],
        timestamps: List[datetime]
    ) -> Dict:
        """
        Predict maintenance needs from tank telemetry patterns.
        """
        
        alerts = []
        
        if len(tank_levels) < 10:
            return {"alerts": [], "prediction": "insufficient_data"}
        
        # Check for leaks (consistent decline without rain)
        recent_levels = tank_levels[-10:]
        if all(recent_levels[i] >= recent_levels[i+1] for i in range(len(recent_levels)-1)):
            decline_rate = (recent_levels[0] - recent_levels[-1]) / len(recent_levels)
            if decline_rate > 50:  # More than 50L per reading
                alerts.append({
                    "type": "potential_leak",
                    "severity": "high",
                    "message": f"Consistent water level decline detected ({decline_rate:.0f}L/reading)",
                    "action": "Inspect tank and connections for leaks"
                })
        
        # Check for sensor issues (stuck readings)
        if len(set(recent_levels)) == 1:
            alerts.append({
                "type": "sensor_issue",
                "severity": "medium",
                "message": "Sensor readings unchanged - possible malfunction",
                "action": "Check sensor connection and calibration"
            })
        
        return {
            "alerts": alerts,
            "readings_analyzed": len(tank_levels),
            "prediction": "leak_suspected" if alerts else "normal",
            "analysis_time": datetime.utcnow().isoformat()
        }
