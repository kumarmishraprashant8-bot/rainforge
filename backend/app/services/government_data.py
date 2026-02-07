"""
Government Data Sources Integration
APIs for: IMD, CGWB, India Water Portal, Census, NITI Aayog
"""
import httpx
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
from dataclasses import dataclass
from functools import lru_cache

from app.core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class RainfallData:
    """Rainfall data from IMD."""
    station: str
    date: datetime
    rainfall_mm: float
    normal_mm: float
    departure_percent: float
    district: str
    state: str


@dataclass
class GroundwaterData:
    """Groundwater data from CGWB."""
    well_id: str
    location: str
    water_level_m: float
    last_measured: datetime
    trend: str  # raising, stable, falling
    district: str


@dataclass 
class WaterShedData:
    """Watershed data."""
    name: str
    area_km2: float
    annual_rainfall_mm: float
    runoff_potential_mm: float
    groundwater_potential_mcm: float


class GovernmentDataService:
    """
    Integration with Indian government data sources.
    
    Note: Many of these APIs require official registration.
    Mock data is provided for development.
    """
    
    # API Endpoints
    IMD_API = "https://mausam.imd.gov.in/api"
    CGWB_API = "https://cgwb.gov.in/api"
    INDIA_WATER_PORTAL = "https://indiawaterportal.org/api"
    
    def __init__(self):
        self.imd_key = getattr(settings, 'IMD_API_KEY', None)
        self.cgwb_key = getattr(settings, 'CGWB_API_KEY', None)
    
    # ==================== IMD RAINFALL DATA ====================
    
    async def get_district_rainfall(
        self,
        district: str,
        state: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[RainfallData]:
        """
        Get historical rainfall data for a district.
        Source: India Meteorological Department
        """
        if not start_date:
            start_date = datetime.now() - timedelta(days=30)
        if not end_date:
            end_date = datetime.now()
        
        # In production, this would call IMD API
        # For now, return mock data
        return self._mock_rainfall_data(district, state, start_date, end_date)
    
    async def get_monsoon_forecast(
        self,
        region: str = "all-india"
    ) -> Dict[str, Any]:
        """
        Get monsoon season forecast.
        Source: IMD Long Range Forecast
        """
        # Mock monsoon forecast
        return {
            "region": region,
            "season": "southwest_monsoon",
            "year": datetime.now().year,
            "forecast": {
                "june": {"normal_mm": 164, "predicted_mm": 170, "category": "normal"},
                "july": {"normal_mm": 293, "predicted_mm": 310, "category": "above_normal"},
                "august": {"normal_mm": 261, "predicted_mm": 250, "category": "normal"},
                "september": {"normal_mm": 170, "predicted_mm": 180, "category": "normal"}
            },
            "overall": {
                "category": "normal",
                "departure_percent": 3,
                "confidence": 0.75
            },
            "issued_date": datetime.now().isoformat(),
            "source": "IMD Long Range Forecast"
        }
    
    # ==================== CGWB GROUNDWATER DATA ====================
    
    async def get_groundwater_level(
        self,
        district: str,
        state: str
    ) -> List[GroundwaterData]:
        """
        Get groundwater level data.
        Source: Central Ground Water Board
        """
        # Mock groundwater data
        return [
            GroundwaterData(
                well_id=f"GW-{district[:3].upper()}-001",
                location=f"North {district}",
                water_level_m=8.5,
                last_measured=datetime.now() - timedelta(days=7),
                trend="falling",
                district=district
            ),
            GroundwaterData(
                well_id=f"GW-{district[:3].upper()}-002",
                location=f"Central {district}",
                water_level_m=12.3,
                last_measured=datetime.now() - timedelta(days=7),
                trend="stable",
                district=district
            ),
            GroundwaterData(
                well_id=f"GW-{district[:3].upper()}-003",
                location=f"South {district}",
                water_level_m=6.8,
                last_measured=datetime.now() - timedelta(days=7),
                trend="raising",
                district=district
            )
        ]
    
    async def get_aquifer_info(
        self,
        lat: float,
        lng: float
    ) -> Dict[str, Any]:
        """Get aquifer characteristics for a location."""
        return {
            "aquifer_type": "Unconfined",
            "rock_type": "Alluvium",
            "yield_lps": 5.0,
            "quality": "Potable",
            "recharge_potential": "High",
            "depth_to_water_m": 10.5,
            "recommended_for_rwh": True,
            "notes": "Suitable for ground recharge from RWH"
        }
    
    # ==================== WATERSHED DATA ====================
    
    async def get_watershed_info(
        self,
        lat: float,
        lng: float
    ) -> Optional[WaterShedData]:
        """
        Get watershed information for a location.
        Source: India-WRIS / NRSC
        """
        # Mock watershed data
        return WaterShedData(
            name="Sample Watershed",
            area_km2=125.5,
            annual_rainfall_mm=890,
            runoff_potential_mm=320,
            groundwater_potential_mcm=15.8
        )
    
    # ==================== CENSUS WATER DATA ====================
    
    async def get_household_water_sources(
        self,
        district: str,
        state: str
    ) -> Dict[str, Any]:
        """
        Get household water source statistics.
        Source: Census of India
        """
        return {
            "district": district,
            "state": state,
            "census_year": 2011,
            "total_households": 250000,
            "sources": {
                "tap": {"percent": 35.5, "households": 88750},
                "handpump": {"percent": 28.2, "households": 70500},
                "tubewell": {"percent": 18.5, "households": 46250},
                "well": {"percent": 12.3, "households": 30750},
                "tank": {"percent": 3.5, "households": 8750},
                "river": {"percent": 1.2, "households": 3000},
                "other": {"percent": 0.8, "households": 2000}
            },
            "rwh_adoption": {
                "estimated_percent": 5.2,
                "trend": "increasing"
            }
        }
    
    # ==================== NITI AAYOG SDG DATA ====================
    
    async def get_sdg_water_indicators(
        self,
        state: str
    ) -> Dict[str, Any]:
        """
        Get SDG water-related indicators.
        Source: NITI Aayog SDG Dashboard
        """
        return {
            "state": state,
            "year": 2022,
            "indicators": {
                "sdg_6_1": {
                    "name": "Safe drinking water access",
                    "value": 78.5,
                    "unit": "percent",
                    "target": 100,
                    "status": "on_track"
                },
                "sdg_6_3": {
                    "name": "Wastewater treatment",
                    "value": 45.2,
                    "unit": "percent",
                    "target": 100,
                    "status": "needs_improvement"
                },
                "sdg_6_4": {
                    "name": "Water use efficiency",
                    "value": 65.8,
                    "unit": "index",
                    "target": 100,
                    "status": "moderate"
                },
                "sdg_6_b": {
                    "name": "Local water management",
                    "value": 52.3,
                    "unit": "percent",
                    "target": 100,
                    "status": "moderate"
                }
            },
            "overall_score": 60.4,
            "rank": 12,
            "source": "NITI Aayog SDG India Index"
        }
    
    # ==================== JAL JEEVAN MISSION DATA ====================
    
    async def get_jjm_stats(
        self,
        state: Optional[str] = None,
        district: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get Jal Jeevan Mission statistics.
        Source: JJM Dashboard
        """
        return {
            "state": state or "All India",
            "district": district,
            "as_on": datetime.now().strftime("%Y-%m-%d"),
            "statistics": {
                "total_rural_households": 19_20_00_000,
                "tap_connections_aug2019": 3_23_62_000,
                "tap_connections_current": 15_08_00_000,
                "coverage_percent": 78.5,
                "functional_tap_connections": 14_85_00_000
            },
            "progress": {
                "har_ghar_jal_states": 7,
                "har_ghar_jal_districts": 183,
                "har_ghar_jal_blocks": 1215
            },
            "rwh_component": {
                "villages_covered": 125000,
                "structures_created": 850000,
                "capacity_mcm": 425
            }
        }
    
    # ==================== MOCK DATA GENERATORS ====================
    
    def _mock_rainfall_data(
        self,
        district: str,
        state: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[RainfallData]:
        """Generate mock rainfall data."""
        import random
        
        data = []
        current = start_date
        
        while current <= end_date:
            month = current.month
            
            # Seasonal variation
            if month in [6, 7, 8, 9]:  # Monsoon
                normal = random.uniform(150, 350)
                actual = random.uniform(100, 400)
            elif month in [10, 11]:  # Post-monsoon
                normal = random.uniform(50, 150)
                actual = random.uniform(20, 180)
            else:  # Dry
                normal = random.uniform(5, 30)
                actual = random.uniform(0, 50)
            
            departure = ((actual - normal) / normal) * 100 if normal > 0 else 0
            
            data.append(RainfallData(
                station=f"{district} AWS",
                date=current,
                rainfall_mm=round(actual, 1),
                normal_mm=round(normal, 1),
                departure_percent=round(departure, 1),
                district=district,
                state=state
            ))
            
            current += timedelta(days=1)
        
        return data


# ==================== SATELLITE DATA ====================

class SatelliteDataService:
    """
    Satellite-based data integration.
    Sources: ISRO Bhuvan, NASA GPM, Sentinel
    """
    
    async def get_satellite_rainfall(
        self,
        lat: float,
        lng: float,
        date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get satellite-derived rainfall estimate.
        Source: GPM IMERG or ISRO Bhuvan
        """
        import random
        
        if not date:
            date = datetime.now()
        
        return {
            "latitude": lat,
            "longitude": lng,
            "date": date.isoformat(),
            "rainfall_mm": round(random.uniform(0, 50), 1),
            "source": "GPM_IMERG_V06",
            "resolution_km": 10,
            "uncertainty_percent": 15,
            "quality_flag": "good"
        }
    
    async def get_building_footprint(
        self,
        lat: float,
        lng: float,
        radius_m: float = 50
    ) -> Dict[str, Any]:
        """
        Get building footprint from satellite imagery.
        Source: Microsoft Building Footprints / OpenStreetMap
        """
        return {
            "latitude": lat,
            "longitude": lng,
            "buildings_found": 1,
            "primary_building": {
                "area_sqm": 125.5,
                "perimeter_m": 48.2,
                "confidence": 0.85,
                "roof_type": "flat",
                "source": "microsoft_footprints"
            },
            "notes": "Roof area estimated from satellite footprint"
        }
    
    async def get_land_use(
        self,
        lat: float,
        lng: float
    ) -> Dict[str, Any]:
        """
        Get land use classification.
        Source: ISRO Bhuvan Land Use
        """
        return {
            "latitude": lat,
            "longitude": lng,
            "land_use": "residential",
            "sub_type": "urban_residential",
            "density": "medium",
            "green_cover_percent": 15,
            "impervious_percent": 65,
            "source": "bhuvan_lulc_2021"
        }


# Singleton instances
_gov_service: Optional[GovernmentDataService] = None
_sat_service: Optional[SatelliteDataService] = None

def get_gov_data_service() -> GovernmentDataService:
    global _gov_service
    if _gov_service is None:
        _gov_service = GovernmentDataService()
    return _gov_service

def get_satellite_service() -> SatelliteDataService:
    global _sat_service
    if _sat_service is None:
        _sat_service = SatelliteDataService()
    return _sat_service
