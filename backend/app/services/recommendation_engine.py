"""
Recommendation Engine
Personalized RWH system recommendations
"""
import logging
from datetime import datetime
from typing import Optional, Dict, List, Any
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class BuildingType(str, Enum):
    RESIDENTIAL_SMALL = "residential_small"
    RESIDENTIAL_LARGE = "residential_large"
    APARTMENT = "apartment"
    COMMERCIAL = "commercial"
    INDUSTRIAL = "industrial"
    SCHOOL = "school"
    HOSPITAL = "hospital"
    GOVERNMENT = "government"


class BudgetRange(str, Enum):
    ECONOMY = "economy"
    STANDARD = "standard"
    PREMIUM = "premium"


@dataclass
class SystemRecommendation:
    """RWH system recommendation."""
    system_id: str
    name: str
    description: str
    components: List[Dict[str, Any]]
    estimated_cost_min: float
    estimated_cost_max: float
    roi_years: float
    water_savings_yearly: float
    match_score: float
    pros: List[str]
    cons: List[str]


class RecommendationEngine:
    """
    Personalized RWH system recommendation engine.
    
    Considers:
    - Roof area and type
    - Local rainfall
    - Budget
    - Water needs
    - Building type
    - Groundwater conditions
    """
    
    # System templates
    SYSTEM_TEMPLATES = {
        "basic": {
            "name": "Basic RWH System",
            "description": "Simple, cost-effective system for small roofs",
            "components": [
                {"name": "PVC Gutter", "qty": 1, "unit": "set", "cost": 3000},
                {"name": "First Flush Diverter", "qty": 1, "unit": "unit", "cost": 2000},
                {"name": "Storage Tank (1000L)", "qty": 1, "unit": "unit", "cost": 8000},
                {"name": "Pipes & Fittings", "qty": 1, "unit": "set", "cost": 2000},
                {"name": "Installation", "qty": 1, "unit": "service", "cost": 5000}
            ],
            "min_roof_sqm": 25,
            "max_roof_sqm": 100,
            "building_types": [BuildingType.RESIDENTIAL_SMALL],
            "budget_range": BudgetRange.ECONOMY
        },
        "standard": {
            "name": "Standard RWH System",
            "description": "Complete system with filtration for medium homes",
            "components": [
                {"name": "Metal Gutter", "qty": 1, "unit": "set", "cost": 8000},
                {"name": "First Flush Diverter", "qty": 1, "unit": "unit", "cost": 3000},
                {"name": "Sand Filter", "qty": 1, "unit": "unit", "cost": 5000},
                {"name": "Storage Tank (3000L)", "qty": 1, "unit": "unit", "cost": 18000},
                {"name": "Pump (0.5HP)", "qty": 1, "unit": "unit", "cost": 8000},
                {"name": "Pipes & Fittings", "qty": 1, "unit": "set", "cost": 5000},
                {"name": "Installation", "qty": 1, "unit": "service", "cost": 10000}
            ],
            "min_roof_sqm": 75,
            "max_roof_sqm": 200,
            "building_types": [BuildingType.RESIDENTIAL_SMALL, BuildingType.RESIDENTIAL_LARGE],
            "budget_range": BudgetRange.STANDARD
        },
        "premium": {
            "name": "Premium RWH System",
            "description": "High-capacity system with IoT monitoring",
            "components": [
                {"name": "SS Gutter System", "qty": 1, "unit": "set", "cost": 15000},
                {"name": "First Flush Diverter", "qty": 2, "unit": "unit", "cost": 6000},
                {"name": "Multi-stage Filter", "qty": 1, "unit": "unit", "cost": 12000},
                {"name": "UV Purifier", "qty": 1, "unit": "unit", "cost": 8000},
                {"name": "Storage Tank (5000L)", "qty": 2, "unit": "unit", "cost": 50000},
                {"name": "Pump (1HP)", "qty": 1, "unit": "unit", "cost": 12000},
                {"name": "IoT Level Sensor", "qty": 2, "unit": "unit", "cost": 10000},
                {"name": "Control Panel", "qty": 1, "unit": "unit", "cost": 15000},
                {"name": "Pipes & Fittings", "qty": 1, "unit": "set", "cost": 10000},
                {"name": "Installation", "qty": 1, "unit": "service", "cost": 20000}
            ],
            "min_roof_sqm": 150,
            "max_roof_sqm": 500,
            "building_types": [BuildingType.RESIDENTIAL_LARGE, BuildingType.APARTMENT, BuildingType.COMMERCIAL],
            "budget_range": BudgetRange.PREMIUM
        },
        "groundwater_recharge": {
            "name": "Groundwater Recharge System",
            "description": "System designed for aquifer recharge",
            "components": [
                {"name": "Gutter System", "qty": 1, "unit": "set", "cost": 8000},
                {"name": "Settlement Tank", "qty": 1, "unit": "unit", "cost": 15000},
                {"name": "Recharge Well", "qty": 1, "unit": "unit", "cost": 25000},
                {"name": "Percolation Pit", "qty": 2, "unit": "unit", "cost": 10000},
                {"name": "Filter Media", "qty": 1, "unit": "set", "cost": 5000},
                {"name": "Installation", "qty": 1, "unit": "service", "cost": 15000}
            ],
            "min_roof_sqm": 100,
            "max_roof_sqm": 1000,
            "building_types": [BuildingType.RESIDENTIAL_LARGE, BuildingType.COMMERCIAL, BuildingType.INDUSTRIAL, BuildingType.GOVERNMENT],
            "budget_range": BudgetRange.STANDARD
        },
        "institutional": {
            "name": "Institutional RWH System",
            "description": "Large-scale system for schools, hospitals, offices",
            "components": [
                {"name": "Industrial Gutter System", "qty": 1, "unit": "set", "cost": 50000},
                {"name": "Multi-stage Filtration", "qty": 1, "unit": "system", "cost": 35000},
                {"name": "Underground Tank (20000L)", "qty": 1, "unit": "unit", "cost": 150000},
                {"name": "Pump System", "qty": 1, "unit": "system", "cost": 40000},
                {"name": "SCADA Monitoring", "qty": 1, "unit": "system", "cost": 50000},
                {"name": "Pipes & Fittings", "qty": 1, "unit": "set", "cost": 30000},
                {"name": "Installation", "qty": 1, "unit": "service", "cost": 80000}
            ],
            "min_roof_sqm": 300,
            "max_roof_sqm": 5000,
            "building_types": [BuildingType.SCHOOL, BuildingType.HOSPITAL, BuildingType.GOVERNMENT, BuildingType.COMMERCIAL, BuildingType.INDUSTRIAL],
            "budget_range": BudgetRange.PREMIUM
        }
    }
    
    def __init__(self):
        pass
    
    async def get_recommendations(
        self,
        roof_area_sqm: float,
        building_type: BuildingType,
        annual_rainfall_mm: float,
        budget_range: Optional[BudgetRange] = None,
        water_needs_daily_liters: Optional[float] = None,
        has_existing_system: bool = False,
        groundwater_recharge: bool = False
    ) -> List[SystemRecommendation]:
        """
        Get personalized system recommendations.
        """
        recommendations = []
        
        # Calculate potential
        runoff_coefficient = 0.85  # For concrete roofs
        yearly_collection = roof_area_sqm * annual_rainfall_mm * runoff_coefficient
        
        # Estimate water savings value
        water_rate_per_liter = 0.05  # ₹0.05/L
        yearly_savings_inr = yearly_collection * water_rate_per_liter
        
        for system_id, template in self.SYSTEM_TEMPLATES.items():
            # Check roof size compatibility
            if roof_area_sqm < template["min_roof_sqm"] or roof_area_sqm > template["max_roof_sqm"]:
                continue
            
            # Check building type compatibility
            if building_type not in template["building_types"]:
                continue
            
            # Check budget if specified
            if budget_range and template["budget_range"] != budget_range:
                continue
            
            # Calculate costs
            total_cost = sum(c["cost"] * c.get("qty", 1) for c in template["components"])
            cost_min = total_cost * 0.9  # 10% variance
            cost_max = total_cost * 1.1
            
            # Calculate ROI
            roi_years = total_cost / yearly_savings_inr if yearly_savings_inr > 0 else 99
            
            # Calculate match score
            match_score = self._calculate_match_score(
                roof_area_sqm,
                template["min_roof_sqm"],
                template["max_roof_sqm"],
                building_type,
                template["building_types"],
                budget_range,
                template["budget_range"]
            )
            
            # Generate pros/cons
            pros, cons = self._generate_pros_cons(
                system_id,
                total_cost,
                roi_years,
                yearly_collection
            )
            
            recommendations.append(SystemRecommendation(
                system_id=system_id,
                name=template["name"],
                description=template["description"],
                components=template["components"],
                estimated_cost_min=cost_min,
                estimated_cost_max=cost_max,
                roi_years=round(roi_years, 1),
                water_savings_yearly=round(yearly_collection, 0),
                match_score=match_score,
                pros=pros,
                cons=cons
            ))
        
        # Sort by match score
        recommendations.sort(key=lambda r: r.match_score, reverse=True)
        
        return recommendations
    
    def _calculate_match_score(
        self,
        roof_area: float,
        min_area: float,
        max_area: float,
        building_type: BuildingType,
        supported_types: List[BuildingType],
        budget: Optional[BudgetRange],
        template_budget: BudgetRange
    ) -> float:
        """Calculate match score between 0-1."""
        score = 0.0
        
        # Area fit (40% weight)
        area_mid = (min_area + max_area) / 2
        area_range = max_area - min_area
        area_diff = abs(roof_area - area_mid) / (area_range / 2) if area_range > 0 else 0
        area_score = max(0, 1 - area_diff) * 0.4
        score += area_score
        
        # Building type match (30% weight)
        if building_type in supported_types:
            type_score = 0.3
            # Bonus if first in list
            if building_type == supported_types[0]:
                type_score += 0.1
            score += type_score
        
        # Budget match (30% weight)
        if budget is None:
            score += 0.2  # Partial credit if not specified
        elif budget == template_budget:
            score += 0.3
        
        return round(score, 2)
    
    def _generate_pros_cons(
        self,
        system_id: str,
        cost: float,
        roi: float,
        yearly_collection: float
    ) -> tuple:
        """Generate pros and cons for a system."""
        pros_map = {
            "basic": [
                "Low initial investment",
                "Easy installation",
                "Minimal maintenance"
            ],
            "standard": [
                "Good balance of cost and features",
                "Includes filtration",
                "Suitable for most homes"
            ],
            "premium": [
                "IoT monitoring included",
                "High water quality",
                "Large capacity",
                "Smart alerts"
            ],
            "groundwater_recharge": [
                "Recharges aquifer",
                "Long-term sustainability",
                "Government incentives available"
            ],
            "institutional": [
                "Industrial-grade components",
                "SCADA monitoring",
                "High capacity",
                "Low per-liter cost"
            ]
        }
        
        cons_map = {
            "basic": [
                "Limited capacity",
                "No monitoring",
                "Basic filtration only"
            ],
            "standard": [
                "Moderate cost",
                "Requires pump maintenance"
            ],
            "premium": [
                "High initial cost",
                "Requires technical maintenance",
                "Complex installation"
            ],
            "groundwater_recharge": [
                "Not for direct use",
                "Requires suitable soil",
                "Higher installation complexity"
            ],
            "institutional": [
                "Very high cost",
                "Requires dedicated staff",
                "Long installation time"
            ]
        }
        
        pros = pros_map.get(system_id, ["Cost-effective", "Reliable"])
        cons = cons_map.get(system_id, ["Standard features"])
        
        # Add dynamic pros
        if roi < 3:
            pros.append(f"Quick ROI: {roi:.1f} years")
        if yearly_collection > 50000:
            pros.append(f"High collection: {yearly_collection/1000:.0f} kL/year")
        
        return pros, cons
    
    async def get_quick_estimate(
        self,
        roof_area_sqm: float,
        city: str
    ) -> Dict[str, Any]:
        """Get quick cost estimate without detailed inputs."""
        # Get city rainfall
        city_rainfall = {
            "mumbai": 2200,
            "chennai": 1400,
            "bengaluru": 970,
            "delhi": 617,
            "hyderabad": 812,
            "kolkata": 1582,
            "pune": 722,
            "default": 900
        }
        
        rainfall = city_rainfall.get(city.lower(), city_rainfall["default"])
        yearly_collection = roof_area_sqm * rainfall * 0.85
        
        # Quick cost estimate
        if roof_area_sqm < 50:
            cost_range = (15000, 25000)
        elif roof_area_sqm < 100:
            cost_range = (25000, 50000)
        elif roof_area_sqm < 200:
            cost_range = (50000, 100000)
        else:
            cost_range = (100000, 300000)
        
        return {
            "roof_area_sqm": roof_area_sqm,
            "city": city,
            "annual_rainfall_mm": rainfall,
            "yearly_collection_liters": round(yearly_collection, 0),
            "yearly_collection_kl": round(yearly_collection / 1000, 1),
            "cost_estimate_min": cost_range[0],
            "cost_estimate_max": cost_range[1],
            "monthly_savings_inr": round(yearly_collection * 0.05 / 12, 0),
            "roi_years": round((cost_range[0] + cost_range[1]) / 2 / (yearly_collection * 0.05), 1)
        }


# Singleton
_recommendation_engine: Optional[RecommendationEngine] = None

def get_recommendation_engine() -> RecommendationEngine:
    global _recommendation_engine
    if _recommendation_engine is None:
        _recommendation_engine = RecommendationEngine()
    return _recommendation_engine
