from typing import List, Optional
import random

class WeatherService:
    """
    Adapter for fetching rainfall data.
    """
    
    @staticmethod
    def get_historical_rainfall(lat: float, lng: float) -> dict:
        """
        Fetch monthly average rainfall (mm).
        For MVP/Demo, returning mock data based on general climate zones using lat/lng.
        """
        # Mock logic:
        # If lat is close to equator (0-20), tropical mock.
        # If lat is > 40, temperate mock.
        
        # Consistent mock based on coordinates to be deterministic for demo
        seed = int(abs(lat + lng) * 100)
        random.seed(seed)
        
        # Base annual rainfall 500mm to 1500mm
        base_annual = random.uniform(500, 1500)
        
        # Distribute over 12 months with some seasonality
        # Simple bell curve distribution peaking in July (Month 7)
        monthly = []
        for month in range(1, 13):
            # Peak in summer
            dist = math.exp(-((month - 7) ** 2) / (2 * 1.5 ** 2))
            rain = (base_annual / 12) * (0.5 + 1.5 * dist)
            monthly.append(round(rain, 1))
            
        return {
            "source": "MockProvider", 
            "lat": lat,
            "lng": lng,
            "annual_mm": round(sum(monthly), 1),
            "monthly_mm": monthly
        }

import math
