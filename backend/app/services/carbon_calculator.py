"""
Carbon Credit Calculator
Estimates CO2 offset from rainwater harvesting
Based on water-energy nexus calculations
"""
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class CarbonCredit:
    """Carbon credit calculation result."""
    water_saved_liters: float
    energy_saved_kwh: float
    co2_offset_kg: float
    co2_offset_tonnes: float
    equivalent_trees: int
    equivalent_car_km: float
    carbon_credit_value_inr: float
    carbon_credit_value_usd: float
    calculation_method: str
    calculated_at: datetime


class CarbonCreditCalculator:
    """
    Calculate carbon credits from rainwater harvesting.
    
    Methodology:
    1. Water saved = Rainwater collected (reduces municipal water demand)
    2. Energy saved = Pumping & treatment energy avoided
    3. CO2 offset = Energy saved × Grid emission factor
    """
    
    # Constants (India-specific)
    
    # Energy required to pump and treat 1 kL of municipal water
    # Source: Bureau of Energy Efficiency, India (0.2-0.5 kWh/kL)
    ENERGY_PER_KL = 0.35  # kWh per kiloliter
    
    # Additional energy for wastewater treatment avoided
    WASTEWATER_ENERGY_PER_KL = 0.25  # kWh per kiloliter
    
    # India grid emission factor (kg CO2 per kWh)
    # Source: Central Electricity Authority, 2023
    GRID_EMISSION_FACTOR = 0.71  # kg CO2/kWh
    
    # Carbon credit pricing
    CARBON_PRICE_USD = 15.0  # USD per tonne CO2 (voluntary market)
    CARBON_PRICE_INR = 1200.0  # INR per tonne CO2
    
    # Conversion factors
    TREES_PER_TONNE_CO2 = 45  # Mature trees to absorb 1 tonne CO2/year
    KM_PER_KG_CO2 = 6.5  # Average car km per kg CO2
    
    def __init__(self):
        pass
    
    def calculate(
        self,
        water_saved_liters: float,
        include_wastewater: bool = True,
        region: str = "india"
    ) -> CarbonCredit:
        """
        Calculate carbon credits from water saved.
        
        Args:
            water_saved_liters: Total water saved in liters
            include_wastewater: Include wastewater treatment savings
            region: Region for emission factors
        """
        # Convert to kiloliters
        water_kl = water_saved_liters / 1000
        
        # Calculate energy saved
        energy_saved = water_kl * self.ENERGY_PER_KL
        if include_wastewater:
            energy_saved += water_kl * self.WASTEWATER_ENERGY_PER_KL
        
        # Calculate CO2 offset
        co2_kg = energy_saved * self.GRID_EMISSION_FACTOR
        co2_tonnes = co2_kg / 1000
        
        # Calculate equivalents
        trees = int(co2_tonnes * self.TREES_PER_TONNE_CO2)
        car_km = co2_kg * self.KM_PER_KG_CO2
        
        # Calculate carbon credit value
        value_usd = co2_tonnes * self.CARBON_PRICE_USD
        value_inr = co2_tonnes * self.CARBON_PRICE_INR
        
        return CarbonCredit(
            water_saved_liters=water_saved_liters,
            energy_saved_kwh=round(energy_saved, 2),
            co2_offset_kg=round(co2_kg, 2),
            co2_offset_tonnes=round(co2_tonnes, 4),
            equivalent_trees=trees,
            equivalent_car_km=round(car_km, 1),
            carbon_credit_value_inr=round(value_inr, 2),
            carbon_credit_value_usd=round(value_usd, 2),
            calculation_method="water-energy-nexus-v1",
            calculated_at=datetime.utcnow()
        )
    
    def calculate_annual_impact(
        self,
        roof_area_sqm: float,
        annual_rainfall_mm: float,
        runoff_coefficient: float = 0.85,
        collection_efficiency: float = 0.80
    ) -> Dict[str, Any]:
        """
        Estimate annual carbon impact from a RWH system.
        """
        # Calculate annual water collected
        annual_liters = (
            roof_area_sqm * 
            annual_rainfall_mm * 
            runoff_coefficient * 
            collection_efficiency
        )
        
        # Calculate carbon credits
        credits = self.calculate(annual_liters)
        
        # Project 10-year impact
        ten_year = self.calculate(annual_liters * 10)
        
        return {
            "annual": {
                "water_liters": round(annual_liters, 0),
                "water_kiloliters": round(annual_liters / 1000, 2),
                "co2_offset_kg": credits.co2_offset_kg,
                "carbon_value_inr": credits.carbon_credit_value_inr
            },
            "ten_year": {
                "water_kiloliters": round(annual_liters * 10 / 1000, 0),
                "co2_offset_tonnes": ten_year.co2_offset_tonnes,
                "equivalent_trees": ten_year.equivalent_trees,
                "carbon_value_inr": ten_year.carbon_credit_value_inr
            },
            "inputs": {
                "roof_area_sqm": roof_area_sqm,
                "annual_rainfall_mm": annual_rainfall_mm,
                "runoff_coefficient": runoff_coefficient,
                "collection_efficiency": collection_efficiency
            },
            "methodology": "water-energy-nexus-v1"
        }
    
    def calculate_city_impact(
        self,
        total_capacity_liters: float,
        average_utilization: float = 0.70
    ) -> Dict[str, Any]:
        """
        Calculate city-wide carbon impact for public dashboard.
        """
        actual_savings = total_capacity_liters * average_utilization
        credits = self.calculate(actual_savings)
        
        return {
            "total_capacity_liters": total_capacity_liters,
            "estimated_usage_liters": actual_savings,
            "co2_offset_tonnes": credits.co2_offset_tonnes,
            "equivalent_trees": credits.equivalent_trees,
            "equivalent_car_km_avoided": credits.equivalent_car_km,
            "carbon_credit_potential_inr": credits.carbon_credit_value_inr,
            "municipal_water_saved_kl": round(actual_savings / 1000, 0),
            "energy_saved_mwh": round(credits.energy_saved_kwh / 1000, 2)
        }
    
    def get_environmental_badges(
        self,
        co2_tonnes: float
    ) -> list[Dict[str, Any]]:
        """
        Generate achievement badges based on CO2 offset.
        """
        badges = []
        
        if co2_tonnes >= 0.001:
            badges.append({
                "name": "Green Starter",
                "icon": "🌱",
                "description": "Started your carbon offset journey",
                "threshold": 0.001
            })
        
        if co2_tonnes >= 0.1:
            badges.append({
                "name": "Water Warrior",
                "icon": "💧",
                "description": "Offset 100kg of CO2",
                "threshold": 0.1
            })
        
        if co2_tonnes >= 0.5:
            badges.append({
                "name": "Climate Champion",
                "icon": "🏆",
                "description": "Offset half a tonne of CO2",
                "threshold": 0.5
            })
        
        if co2_tonnes >= 1.0:
            badges.append({
                "name": "Planet Protector",
                "icon": "🌍",
                "description": "Offset 1 tonne of CO2",
                "threshold": 1.0
            })
        
        if co2_tonnes >= 5.0:
            badges.append({
                "name": "Eco Hero",
                "icon": "🦸",
                "description": "Offset 5 tonnes of CO2",
                "threshold": 5.0
            })
        
        if co2_tonnes >= 10.0:
            badges.append({
                "name": "Climate Legend",
                "icon": "👑",
                "description": "Offset 10 tonnes of CO2",
                "threshold": 10.0
            })
        
        return badges


# Constants for display
CARBON_FACTS = [
    "1 kL of rainwater saves 0.71 kg of CO2 emissions",
    "A 100 sqm roof in Mumbai can offset 50kg CO2 annually",
    "Rainwater harvesting reduces urban flooding by 30%",
    "Each RWH system saves 500+ kWh of pumping energy per year",
    "Ground recharge from RWH helps maintain water tables",
]


# Singleton
_calculator: Optional[CarbonCreditCalculator] = None

def get_carbon_calculator() -> CarbonCreditCalculator:
    global _calculator
    if _calculator is None:
        _calculator = CarbonCreditCalculator()
    return _calculator
