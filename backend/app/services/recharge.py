"""
RainForge Recharge Service
Groundwater recharge analysis and percolation pit sizing.
"""

from typing import Dict, List
from enum import Enum


class SoilType(str, Enum):
    SANDY = "sandy"
    LOAMY = "loamy"
    CLAY = "clay"
    ROCKY = "rocky"


class RechargeService:
    """
    Service for groundwater recharge calculations.
    Based on CGWB (Central Ground Water Board) guidelines.
    """
    
    # Permeability coefficients (m/day)
    SOIL_PERMEABILITY = {
        SoilType.SANDY: 5.0,
        SoilType.LOAMY: 1.0,
        SoilType.CLAY: 0.05,
        SoilType.ROCKY: 0.01,
    }
    
    # Recharge structure costs (INR)
    STRUCTURE_COSTS = {
        "recharge_well": 25000,
        "recharge_pit": 15000,
        "percolation_tank": 50000,
        "injection_well": 100000,
    }
    
    @staticmethod
    def calculate_suitability(
        soil_type: SoilType,
        groundwater_depth_m: float,
        catchment_area_sqm: float,
        annual_rainfall_mm: float
    ) -> Dict:
        """
        Calculate recharge suitability and design parameters.
        """
        permeability = RechargeService.SOIL_PERMEABILITY[soil_type]
        
        # Suitability scoring (0-100)
        permeability_score = min(100, permeability * 20)
        depth_score = min(100, max(0, (groundwater_depth_m - 3) * 10))
        rainfall_score = min(100, annual_rainfall_mm / 10)
        
        overall_score = (
            permeability_score * 0.4 +
            depth_score * 0.3 +
            rainfall_score * 0.3
        )
        
        # Potential recharge volume
        runoff_volume_m3 = (catchment_area_sqm * annual_rainfall_mm * 0.85) / 1000
        recharge_rate_m3_day = permeability * catchment_area_sqm * 0.001
        
        # Structure recommendation
        if overall_score >= 70:
            structure = "recharge_well"
            structure_desc = "Borewell-based recharge with filter stack"
        elif overall_score >= 50:
            structure = "recharge_pit"
            structure_desc = "Gravel-filled pit with filter layers"
        elif overall_score >= 30:
            structure = "percolation_tank"
            structure_desc = "Surface tank with slow filtration"
        else:
            structure = None
            structure_desc = "Groundwater recharge not recommended - use storage"
        
        # Pit sizing (for recharge pit)
        if structure == "recharge_pit":
            # Size to handle 1-day peak rainfall event
            peak_day_runoff = catchment_area_sqm * 50 * 0.85 / 1000  # 50mm peak day
            pit_volume_m3 = peak_day_runoff / permeability  # Time to percolate
            pit_depth = 2.0  # Standard depth
            pit_area = pit_volume_m3 / pit_depth
            pit_side = pit_area ** 0.5
        else:
            pit_side = 0
            pit_depth = 0
        
        return {
            "suitability_score": round(overall_score, 1),
            "suitability_grade": (
                "Excellent" if overall_score >= 70 else
                "Good" if overall_score >= 50 else
                "Moderate" if overall_score >= 30 else
                "Poor"
            ),
            "recommended_structure": structure,
            "structure_description": structure_desc,
            "potential_recharge_m3_year": round(runoff_volume_m3 * 0.7, 1),  # 70% recharge efficiency
            "recharge_rate_m3_day": round(recharge_rate_m3_day, 2),
            "pit_dimensions": {
                "length_m": round(pit_side, 1),
                "width_m": round(pit_side, 1),
                "depth_m": pit_depth
            } if pit_side > 0 else None,
            "estimated_cost_inr": RechargeService.STRUCTURE_COSTS.get(structure, 0) if structure else 0,
            "explanation": {
                "permeability_score": round(permeability_score, 1),
                "depth_score": round(depth_score, 1),
                "rainfall_score": round(rainfall_score, 1),
                "reference": "CGWB Manual on Artificial Recharge, 2007"
            }
        }
    
    @staticmethod
    def get_filter_design(structure_type: str, daily_inflow_m3: float) -> List[Dict]:
        """
        Get filter stack design for recharge structure.
        """
        base_layers = [
            {"layer": "Top mesh", "material": "Stainless steel 2mm", "thickness_cm": 1},
            {"layer": "Charcoal", "material": "Coconut shell charcoal", "thickness_cm": 15},
            {"layer": "Coarse sand", "material": "River sand 1-2mm", "thickness_cm": 20},
            {"layer": "Gravel fine", "material": "6-12mm graded gravel", "thickness_cm": 20},
            {"layer": "Gravel coarse", "material": "20-40mm graded gravel", "thickness_cm": 30},
            {"layer": "Boulders", "material": "40-80mm stones", "thickness_cm": 30},
        ]
        
        if structure_type == "recharge_well":
            # Add injection pipe specification
            base_layers.append({
                "layer": "Injection pipe",
                "material": "PVC 150mm slotted",
                "thickness_cm": "Full depth"
            })
        
        return base_layers
