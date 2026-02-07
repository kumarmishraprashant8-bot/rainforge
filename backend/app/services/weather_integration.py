import httpx
from datetime import datetime
from typing import List, Dict, Optional
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

class WeatherForecast(BaseModel):
    date: str
    rainfall_mm: float
    probability_percent: int
    temperature_max: float
    temperature_min: float
    weather_code: int

class CurrentWeather(BaseModel):
    temperature_c: float
    humidity_percent: float
    rainfall_mm: float
    rainfall_probability: int  # Open-Meteo current doesn't give prob, defaulting
    description: str
    provider: str = "Open-Meteo"
    timestamp: datetime

class WeatherService:
    BASE_URL = "https://api.open-meteo.com/v1/forecast"
    
    # Singleton instance
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = WeatherService()
        return cls._instance

    async def get_current_weather(self, lat: float, lon: float) -> Optional[CurrentWeather]:
        """Fetch current weather from Open-Meteo"""
        params = {
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,relative_humidity_2m,rain,weather_code",
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.BASE_URL, params=params, timeout=5.0)
                response.raise_for_status()
                data = response.json()
            
            curr = data.get("current", {})
            return CurrentWeather(
                temperature_c=curr.get("temperature_2m", 0.0),
                humidity_percent=curr.get("relative_humidity_2m", 0.0),
                rainfall_mm=curr.get("rain", 0.0),
                rainfall_probability=0, # Not available in current
                description=self._get_weather_description(curr.get("weather_code", 0)),
                timestamp=datetime.now()
            )
        except Exception as e:
            logger.error(f"Failed to fetch current weather: {e}")
            return CurrentWeather(
                temperature_c=25.0, humidity_percent=60, rainfall_mm=0, 
                rainfall_probability=0, description="Service Unavailable (Mock)", 
                timestamp=datetime.now()
            )

    def _get_weather_description(self, code: int) -> str:
        """Map WMO codes to text"""
        if code == 0: return "Clear sky"
        if code in [1, 2, 3]: return "Partly cloudy"
        if code in [45, 48]: return "Foggy"
        if code in [51, 53, 55]: return "Drizzle"
        if code in [61, 63, 65]: return "Rain"
        if code in [80, 81, 82]: return "Showers"
        return "Unknown"

    async def get_forecast(self, lat: float, lon: float, days: int = 7) -> List[WeatherForecast]:
        """
        Fetch weather forecast for a specific location using Open-Meteo API.
        Does not require an API key.
        """
        params = {
            "latitude": lat,
            "longitude": lon,
            "daily": "precipitation_sum,precipitation_probability_max,temperature_2m_max,temperature_2m_min,weather_code",
            "timezone": "auto",
            "forecast_days": days
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.BASE_URL, params=params, timeout=10.0)
                response.raise_for_status()
                data = response.json()
            
            daily = data.get("daily", {})
            results = []
            
            # Open-Meteo returns parallel arrays
            dates = daily.get("time", [])
            rain_sums = daily.get("precipitation_sum", [])
            probs = daily.get("precipitation_probability_max", [])
            temp_max = daily.get("temperature_2m_max", [])
            temp_min = daily.get("temperature_2m_min", [])
            codes = daily.get("weather_code", [])
            
            for i in range(len(dates)):
                results.append(WeatherForecast(
                    date=dates[i],
                    rainfall_mm=rain_sums[i] if i < len(rain_sums) and rain_sums[i] is not None else 0.0,
                    probability_percent=probs[i] if i < len(probs) and probs[i] is not None else 0,
                    temperature_max=temp_max[i] if i < len(temp_max) else 0.0,
                    temperature_min=temp_min[i] if i < len(temp_min) else 0.0,
                    weather_code=codes[i] if i < len(codes) else 0
                ))
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to fetch weather data: {str(e)}")
            # Fallback to mock data if API fails (graceful degradation)
            return self._get_fallback_data(days)

    def _get_fallback_data(self, days: int) -> List[WeatherForecast]:
        """Return some placeholder data if API is unreachable"""
        results = []
        today = datetime.now()
        import random
        for i in range(days):
            date_str = (today).strftime("%Y-%m-%d") # simplified for mock
            results.append(WeatherForecast(
                date=f"DAY-{i+1}", 
                rainfall_mm=random.uniform(0, 15),
                probability_percent=random.randint(0, 100),
                temperature_max=30.0,
                temperature_min=20.0,
                weather_code=3
            ))
        return results

# Helper to get service
def get_weather_service() -> WeatherService:
    return WeatherService.get_instance()
