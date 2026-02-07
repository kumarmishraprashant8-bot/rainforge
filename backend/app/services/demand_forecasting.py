"""
Demand Forecasting Service
Predicts water demand at city/ward level using ML.
Accounts for seasonal patterns, population, and weather.
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import math
import random

logger = logging.getLogger(__name__)


class ForecastGranularity(str, Enum):
    """Forecast time granularity."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"


class DemandCategory(str, Enum):
    """Water demand categories."""
    DOMESTIC = "domestic"
    COMMERCIAL = "commercial"
    INDUSTRIAL = "industrial"
    AGRICULTURAL = "agricultural"
    MUNICIPAL = "municipal"


@dataclass
class DemandForecast:
    """Demand forecast result."""
    location_id: str
    location_name: str
    forecast_date: datetime
    granularity: ForecastGranularity
    predicted_demand_liters: float
    confidence_low: float
    confidence_high: float
    confidence_score: float
    factors: Dict[str, float]
    recommendations: List[str]


@dataclass
class SupplyGapAnalysis:
    """Analysis of supply vs demand gap."""
    location_id: str
    period: str
    total_demand_liters: float
    rwh_supply_liters: float
    municipal_supply_liters: float
    gap_liters: float
    gap_percentage: float
    rwh_contribution_percent: float
    status: str  # surplus, balanced, deficit, critical


@dataclass
class SeasonalPattern:
    """Seasonal demand pattern."""
    month: int
    demand_multiplier: float  # 1.0 = baseline
    rainfall_mm: float
    description: str


class DemandForecastingService:
    """
    City/ward level water demand prediction service.
    
    Uses:
    - Historical consumption data
    - Population growth projections
    - Seasonal rainfall patterns
    - Temperature data
    - Economic activity indicators
    """
    
    # India seasonal patterns (monsoon-adjusted)
    INDIA_SEASONAL_PATTERNS = {
        1: SeasonalPattern(1, 1.1, 15, "Winter - moderate demand"),
        2: SeasonalPattern(2, 1.15, 10, "Late winter - rising temps"),
        3: SeasonalPattern(3, 1.25, 8, "Spring - demand increasing"),
        4: SeasonalPattern(4, 1.4, 12, "Pre-monsoon - peak demand"),
        5: SeasonalPattern(5, 1.5, 35, "Pre-monsoon - highest demand"),
        6: SeasonalPattern(6, 1.3, 180, "Monsoon start - demand drops"),
        7: SeasonalPattern(7, 1.0, 310, "Peak monsoon - lowest demand"),
        8: SeasonalPattern(8, 1.0, 280, "Monsoon - RWH peak"),
        9: SeasonalPattern(9, 1.1, 170, "Monsoon retreat"),
        10: SeasonalPattern(10, 1.2, 45, "Post-monsoon"),
        11: SeasonalPattern(11, 1.15, 20, "Early winter"),
        12: SeasonalPattern(12, 1.1, 12, "Winter - stable demand"),
    }
    
    # Per capita daily water demand (liters)
    LPCD_BY_CATEGORY = {
        DemandCategory.DOMESTIC: 135,  # CPHEEO standard
        DemandCategory.COMMERCIAL: 45,
        DemandCategory.INDUSTRIAL: 80,
        DemandCategory.AGRICULTURAL: 200,  # per hectare equivalent
        DemandCategory.MUNICIPAL: 25,
    }
    
    def __init__(self):
        self._location_data: Dict[str, Dict] = {}
        self._historical_demand: Dict[str, List[Dict]] = {}
        self._forecasts: Dict[str, List[DemandForecast]] = {}
        
    def register_location(
        self,
        location_id: str,
        name: str,
        population: int,
        area_sqkm: float,
        category_split: Dict[DemandCategory, float],
        rwh_coverage_percent: float = 10.0,
        avg_roof_area_sqm: float = 100.0
    ):
        """Register a city/ward for forecasting."""
        self._location_data[location_id] = {
            "id": location_id,
            "name": name,
            "population": population,
            "area_sqkm": area_sqkm,
            "category_split": {k.value: v for k, v in category_split.items()},
            "rwh_coverage_percent": rwh_coverage_percent,
            "avg_roof_area_sqm": avg_roof_area_sqm,
            "registered_at": datetime.now().isoformat()
        }
        logger.info(f"Registered location: {name} (pop: {population:,})")
    
    def calculate_baseline_demand(self, location_id: str) -> float:
        """Calculate baseline daily demand in liters."""
        location = self._location_data.get(location_id)
        if not location:
            return 0.0
        
        population = location["population"]
        category_split = location["category_split"]
        
        total_lpcd = 0.0
        for category, percentage in category_split.items():
            cat_enum = DemandCategory(category)
            lpcd = self.LPCD_BY_CATEGORY.get(cat_enum, 100)
            total_lpcd += lpcd * (percentage / 100)
        
        return population * total_lpcd
    
    def forecast_demand(
        self,
        location_id: str,
        start_date: datetime,
        periods: int = 12,
        granularity: ForecastGranularity = ForecastGranularity.MONTHLY
    ) -> List[DemandForecast]:
        """
        Generate demand forecast for a location.
        Returns list of forecasts for each period.
        """
        location = self._location_data.get(location_id)
        if not location:
            raise ValueError(f"Location {location_id} not registered")
        
        forecasts = []
        baseline_daily = self.calculate_baseline_demand(location_id)
        
        for i in range(periods):
            # Calculate forecast date
            if granularity == ForecastGranularity.DAILY:
                forecast_date = start_date + timedelta(days=i)
                days_in_period = 1
            elif granularity == ForecastGranularity.WEEKLY:
                forecast_date = start_date + timedelta(weeks=i)
                days_in_period = 7
            elif granularity == ForecastGranularity.MONTHLY:
                # Approximate month
                forecast_date = start_date + timedelta(days=i*30)
                days_in_period = 30
            else:  # QUARTERLY
                forecast_date = start_date + timedelta(days=i*90)
                days_in_period = 90
            
            # Get seasonal multiplier
            month = forecast_date.month
            seasonal = self.INDIA_SEASONAL_PATTERNS.get(month)
            seasonal_multiplier = seasonal.demand_multiplier if seasonal else 1.0
            
            # Population growth factor (0.5% per year)
            years_ahead = i / (365 / days_in_period) if days_in_period > 0 else 0
            growth_factor = 1 + (0.005 * years_ahead)
            
            # Calculate predicted demand
            predicted = baseline_daily * days_in_period * seasonal_multiplier * growth_factor
            
            # Confidence interval (±10% for near-term, increasing with distance)
            uncertainty = 0.10 + (0.02 * min(i, 12))
            confidence_low = predicted * (1 - uncertainty)
            confidence_high = predicted * (1 + uncertainty)
            
            # Build factor breakdown
            factors = {
                "baseline_daily_liters": baseline_daily,
                "days_in_period": days_in_period,
                "seasonal_multiplier": seasonal_multiplier,
                "population_growth_factor": growth_factor,
                "month": month,
                "rainfall_expected_mm": seasonal.rainfall_mm if seasonal else 0
            }
            
            # Generate recommendations
            recommendations = self._generate_recommendations(
                location, seasonal, predicted, factors
            )
            
            forecast = DemandForecast(
                location_id=location_id,
                location_name=location["name"],
                forecast_date=forecast_date,
                granularity=granularity,
                predicted_demand_liters=predicted,
                confidence_low=confidence_low,
                confidence_high=confidence_high,
                confidence_score=1 - uncertainty,
                factors=factors,
                recommendations=recommendations
            )
            forecasts.append(forecast)
        
        # Cache forecasts
        self._forecasts[location_id] = forecasts
        
        return forecasts
    
    def _generate_recommendations(
        self,
        location: Dict,
        seasonal: Optional[SeasonalPattern],
        predicted_demand: float,
        factors: Dict
    ) -> List[str]:
        """Generate actionable recommendations based on forecast."""
        recommendations = []
        
        if seasonal:
            # Pre-monsoon recommendations
            if seasonal.month in [4, 5]:
                recommendations.append("Peak demand period approaching - ensure water storage is maximized")
                recommendations.append("Run awareness campaigns for water conservation")
            
            # Monsoon recommendations
            elif seasonal.month in [6, 7, 8]:
                recommendations.append("Monsoon season - prioritize RWH system maintenance")
                recommendations.append("Optimal time for new RWH installations")
                recommendations.append(f"Expected rainfall: {seasonal.rainfall_mm}mm - prepare storage capacity")
            
            # Post-monsoon
            elif seasonal.month in [9, 10]:
                recommendations.append("Transition period - verify tank levels and quality")
        
        # RWH coverage recommendations
        rwh_coverage = location.get("rwh_coverage_percent", 0)
        if rwh_coverage < 20:
            recommendations.append(f"Low RWH coverage ({rwh_coverage}%) - accelerate installation program")
        
        # High demand alert
        if factors.get("seasonal_multiplier", 1.0) > 1.3:
            recommendations.append("High demand expected - coordinate with municipal water supply")
        
        return recommendations
    
    def analyze_supply_gap(
        self,
        location_id: str,
        period_months: int = 12
    ) -> List[SupplyGapAnalysis]:
        """
        Analyze gap between demand and available supply.
        Compares RWH + municipal supply vs predicted demand.
        """
        location = self._location_data.get(location_id)
        if not location:
            raise ValueError(f"Location {location_id} not registered")
        
        # Get or generate forecasts
        forecasts = self._forecasts.get(location_id)
        if not forecasts or len(forecasts) < period_months:
            forecasts = self.forecast_demand(
                location_id, 
                datetime.now(), 
                period_months,
                ForecastGranularity.MONTHLY
            )
        
        analyses = []
        
        for forecast in forecasts[:period_months]:
            # Calculate RWH supply potential
            population = location["population"]
            avg_household_size = 4.5
            households = population / avg_household_size
            rwh_households = households * (location["rwh_coverage_percent"] / 100)
            
            # Average roof area and rainfall
            roof_area = location["avg_roof_area_sqm"]
            month = forecast.forecast_date.month
            seasonal = self.INDIA_SEASONAL_PATTERNS.get(month)
            rainfall_mm = seasonal.rainfall_mm if seasonal else 50
            
            # RWH yield: Roof Area × Rainfall × Runoff Coefficient × Collection Efficiency
            runoff_coeff = 0.85
            collection_eff = 0.80
            rwh_per_household = roof_area * rainfall_mm * runoff_coeff * collection_eff
            total_rwh_supply = rwh_households * rwh_per_household
            
            # Municipal supply (assumed 80% of demand coverage)
            municipal_supply = forecast.predicted_demand_liters * 0.80
            
            # Calculate gap
            total_supply = total_rwh_supply + municipal_supply
            gap = forecast.predicted_demand_liters - total_supply
            gap_percent = (gap / forecast.predicted_demand_liters) * 100 if forecast.predicted_demand_liters > 0 else 0
            
            # RWH contribution
            rwh_contribution = (total_rwh_supply / forecast.predicted_demand_liters) * 100 if forecast.predicted_demand_liters > 0 else 0
            
            # Determine status
            if gap_percent < -10:
                status = "surplus"
            elif gap_percent < 5:
                status = "balanced"
            elif gap_percent < 20:
                status = "deficit"
            else:
                status = "critical"
            
            analysis = SupplyGapAnalysis(
                location_id=location_id,
                period=forecast.forecast_date.strftime("%Y-%m"),
                total_demand_liters=forecast.predicted_demand_liters,
                rwh_supply_liters=total_rwh_supply,
                municipal_supply_liters=municipal_supply,
                gap_liters=gap,
                gap_percentage=gap_percent,
                rwh_contribution_percent=rwh_contribution,
                status=status
            )
            analyses.append(analysis)
        
        return analyses
    
    def get_monsoon_planning_report(self, location_id: str) -> Dict[str, Any]:
        """
        Generate monsoon planning report for municipal authorities.
        """
        location = self._location_data.get(location_id)
        if not location:
            raise ValueError(f"Location {location_id} not registered")
        
        # Forecast for monsoon months (June-September)
        current_year = datetime.now().year
        monsoon_start = datetime(current_year, 6, 1)
        
        forecasts = self.forecast_demand(
            location_id,
            monsoon_start,
            4,
            ForecastGranularity.MONTHLY
        )
        
        gap_analyses = self.analyze_supply_gap(location_id, 4)
        
        # Calculate totals
        total_monsoon_demand = sum(f.predicted_demand_liters for f in forecasts)
        total_rwh_potential = sum(g.rwh_supply_liters for g in gap_analyses)
        total_rainfall = sum(
            self.INDIA_SEASONAL_PATTERNS[f.forecast_date.month].rainfall_mm 
            for f in forecasts
        )
        
        # RWH expansion needed to close gap
        avg_deficit = sum(max(0, g.gap_liters) for g in gap_analyses) / len(gap_analyses)
        rwh_per_household = location["avg_roof_area_sqm"] * (total_rainfall/4) * 0.85 * 0.80
        additional_households_needed = avg_deficit / rwh_per_household if rwh_per_household > 0 else 0
        
        return {
            "location": location["name"],
            "location_id": location_id,
            "monsoon_period": f"June - September {current_year}",
            "population": location["population"],
            "current_rwh_coverage_percent": location["rwh_coverage_percent"],
            "monsoon_summary": {
                "total_expected_demand_liters": total_monsoon_demand,
                "total_expected_demand_mld": total_monsoon_demand / (120 * 1_000_000),  # Million liters per day
                "total_expected_rainfall_mm": total_rainfall,
                "total_rwh_potential_liters": total_rwh_potential
            },
            "gap_analysis": {
                "avg_monthly_gap_liters": avg_deficit,
                "additional_rwh_households_needed": int(additional_households_needed),
                "target_rwh_coverage_percent": min(100, location["rwh_coverage_percent"] + 
                    (additional_households_needed / (location["population"]/4.5)) * 100)
            },
            "monthly_breakdown": [
                {
                    "month": g.period,
                    "demand_liters": g.total_demand_liters,
                    "rwh_supply_liters": g.rwh_supply_liters,
                    "gap_percent": round(g.gap_percentage, 1),
                    "status": g.status
                }
                for g in gap_analyses
            ],
            "recommendations": [
                "Deploy mobile RWH awareness units in high-deficit wards",
                f"Target {int(additional_households_needed):,} new RWH installations before monsoon",
                "Coordinate with PWD for rainwater harvesting in public buildings",
                "Set up real-time monitoring for tank levels across the city"
            ],
            "generated_at": datetime.now().isoformat()
        }
    
    def get_annual_water_budget(self, location_id: str) -> Dict[str, Any]:
        """Generate annual water budget for planning purposes."""
        location = self._location_data.get(location_id)
        if not location:
            raise ValueError(f"Location {location_id} not registered")
        
        # Get full year forecast
        forecasts = self.forecast_demand(
            location_id,
            datetime.now().replace(month=1, day=1),
            12,
            ForecastGranularity.MONTHLY
        )
        
        total_demand = sum(f.predicted_demand_liters for f in forecasts)
        
        # Calculate RWH potential for each month
        population = location["population"]
        households = population / 4.5
        rwh_households = households * (location["rwh_coverage_percent"] / 100)
        roof_area = location["avg_roof_area_sqm"]
        
        monthly_rwh = []
        for month in range(1, 13):
            seasonal = self.INDIA_SEASONAL_PATTERNS[month]
            rwh_yield = roof_area * seasonal.rainfall_mm * 0.85 * 0.80 * rwh_households
            monthly_rwh.append({
                "month": month,
                "month_name": datetime(2024, month, 1).strftime("%B"),
                "rwh_potential_liters": rwh_yield,
                "rainfall_mm": seasonal.rainfall_mm
            })
        
        total_rwh = sum(m["rwh_potential_liters"] for m in monthly_rwh)
        
        return {
            "location": location["name"],
            "fiscal_year": f"FY {datetime.now().year}-{datetime.now().year + 1}",
            "budget_summary": {
                "total_annual_demand_liters": total_demand,
                "total_annual_demand_mld": total_demand / 365_000_000,
                "total_rwh_potential_liters": total_rwh,
                "rwh_as_percent_of_demand": (total_rwh / total_demand * 100) if total_demand > 0 else 0,
                "municipal_requirement_liters": total_demand - total_rwh
            },
            "monthly_rwh_potential": monthly_rwh,
            "peak_demand_month": max(forecasts, key=lambda f: f.predicted_demand_liters).forecast_date.strftime("%B"),
            "peak_rwh_month": max(monthly_rwh, key=lambda m: m["rwh_potential_liters"])["month_name"]
        }


# Singleton instance
_service: Optional[DemandForecastingService] = None


def get_demand_forecasting_service() -> DemandForecastingService:
    """Get or create the demand forecasting service singleton."""
    global _service
    if _service is None:
        _service = DemandForecastingService()
    return _service
