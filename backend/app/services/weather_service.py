"""
Weather Service - Real Weather Data Integration
Supports: OpenWeatherMap, IMD (India Meteorological Dept), Visual Crossing
"""
import httpx
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import asyncio
from functools import lru_cache

from app.core.config import settings

logger = logging.getLogger(__name__)


class WeatherProvider(str, Enum):
    OPENWEATHERMAP = "openweathermap"
    IMD = "imd"
    VISUAL_CROSSING = "visual_crossing"


@dataclass
class WeatherData:
    """Standardized weather data structure."""
    timestamp: datetime
    temperature_c: float
    humidity_percent: float
    rainfall_mm: float
    rainfall_probability: float
    wind_speed_kmh: float
    description: str
    icon: str
    provider: str


@dataclass
class RainfallForecast:
    """Multi-day rainfall forecast."""
    location: str
    latitude: float
    longitude: float
    forecasts: List[Dict[str, Any]]
    total_expected_mm: float
    generated_at: datetime


class WeatherService:
    """
    Unified weather service with multiple provider support.
    Falls back gracefully if a provider is unavailable.
    """
    
    # API endpoints
    OWM_BASE = "https://api.openweathermap.org/data/2.5"
    IMD_BASE = "https://mausam.imd.gov.in/api"  # Mock - real API requires registration
    VC_BASE = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services"
    
    # Cache duration
    CACHE_DURATION = timedelta(minutes=30)
    
    def __init__(self):
        self.api_key = getattr(settings, 'WEATHER_API_KEY', None)
        self.vc_key = getattr(settings, 'VISUAL_CROSSING_KEY', None)
        self._cache: Dict[str, tuple] = {}
    
    async def get_current_weather(
        self, 
        lat: float, 
        lng: float,
        provider: WeatherProvider = WeatherProvider.OPENWEATHERMAP
    ) -> Optional[WeatherData]:
        """Get current weather for a location."""
        cache_key = f"current_{lat}_{lng}_{provider}"
        
        # Check cache
        if cache_key in self._cache:
            data, cached_at = self._cache[cache_key]
            if datetime.utcnow() - cached_at < self.CACHE_DURATION:
                return data
        
        try:
            if provider == WeatherProvider.OPENWEATHERMAP:
                data = await self._fetch_owm_current(lat, lng)
            elif provider == WeatherProvider.IMD:
                data = await self._fetch_imd_current(lat, lng)
            else:
                data = await self._fetch_vc_current(lat, lng)
            
            if data:
                self._cache[cache_key] = (data, datetime.utcnow())
            return data
            
        except Exception as e:
            logger.error(f"Weather fetch failed: {e}")
            return None
    
    async def get_rainfall_forecast(
        self,
        lat: float,
        lng: float,
        days: int = 7
    ) -> Optional[RainfallForecast]:
        """Get multi-day rainfall forecast."""
        cache_key = f"forecast_{lat}_{lng}_{days}"
        
        if cache_key in self._cache:
            data, cached_at = self._cache[cache_key]
            if datetime.utcnow() - cached_at < self.CACHE_DURATION:
                return data
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                if not self.api_key:
                    logger.warning("No weather API key, using mock data")
                    return self._generate_mock_forecast(lat, lng, days)
                
                response = await client.get(
                    f"{self.OWM_BASE}/forecast",
                    params={
                        "lat": lat,
                        "lon": lng,
                        "appid": self.api_key,
                        "units": "metric",
                        "cnt": days * 8  # 3-hour intervals
                    }
                )
                response.raise_for_status()
                data = response.json()
                
                forecast = self._parse_owm_forecast(lat, lng, data)
                self._cache[cache_key] = (forecast, datetime.utcnow())
                return forecast
                
        except Exception as e:
            logger.error(f"Forecast fetch failed: {e}")
            return self._generate_mock_forecast(lat, lng, days)
    
    async def _fetch_owm_current(self, lat: float, lng: float) -> Optional[WeatherData]:
        """Fetch from OpenWeatherMap."""
        if not self.api_key:
            return self._generate_mock_current(lat, lng)
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{self.OWM_BASE}/weather",
                params={
                    "lat": lat,
                    "lon": lng,
                    "appid": self.api_key,
                    "units": "metric"
                }
            )
            response.raise_for_status()
            data = response.json()
            
            return WeatherData(
                timestamp=datetime.utcnow(),
                temperature_c=data["main"]["temp"],
                humidity_percent=data["main"]["humidity"],
                rainfall_mm=data.get("rain", {}).get("1h", 0),
                rainfall_probability=data.get("pop", 0) * 100,
                wind_speed_kmh=data["wind"]["speed"] * 3.6,
                description=data["weather"][0]["description"],
                icon=data["weather"][0]["icon"],
                provider="openweathermap"
            )
    
    async def _fetch_imd_current(self, lat: float, lng: float) -> Optional[WeatherData]:
        """Fetch from IMD (mock - requires official API access)."""
        # IMD doesn't have a public API, this would need official access
        logger.info("IMD API requires official registration")
        return self._generate_mock_current(lat, lng, provider="imd")
    
    async def _fetch_vc_current(self, lat: float, lng: float) -> Optional[WeatherData]:
        """Fetch from Visual Crossing."""
        if not self.vc_key:
            return self._generate_mock_current(lat, lng)
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{self.VC_BASE}/timeline/{lat},{lng}/today",
                params={
                    "key": self.vc_key,
                    "unitGroup": "metric",
                    "include": "current"
                }
            )
            response.raise_for_status()
            data = response.json()
            current = data.get("currentConditions", {})
            
            return WeatherData(
                timestamp=datetime.utcnow(),
                temperature_c=current.get("temp", 25),
                humidity_percent=current.get("humidity", 60),
                rainfall_mm=current.get("precip", 0),
                rainfall_probability=current.get("precipprob", 0),
                wind_speed_kmh=current.get("windspeed", 10),
                description=current.get("conditions", "Clear"),
                icon=current.get("icon", "clear-day"),
                provider="visual_crossing"
            )
    
    def _parse_owm_forecast(
        self, 
        lat: float, 
        lng: float, 
        data: dict
    ) -> RainfallForecast:
        """Parse OpenWeatherMap forecast response."""
        forecasts = []
        total_rain = 0.0
        
        daily_rain = {}
        
        for item in data.get("list", []):
            dt = datetime.fromtimestamp(item["dt"])
            date_key = dt.strftime("%Y-%m-%d")
            
            rain = item.get("rain", {}).get("3h", 0)
            total_rain += rain
            
            if date_key not in daily_rain:
                daily_rain[date_key] = {
                    "date": date_key,
                    "rainfall_mm": 0,
                    "temp_min": item["main"]["temp_min"],
                    "temp_max": item["main"]["temp_max"],
                    "humidity": item["main"]["humidity"],
                    "description": item["weather"][0]["description"],
                    "probability": item.get("pop", 0) * 100
                }
            
            daily_rain[date_key]["rainfall_mm"] += rain
            daily_rain[date_key]["temp_min"] = min(
                daily_rain[date_key]["temp_min"], 
                item["main"]["temp_min"]
            )
            daily_rain[date_key]["temp_max"] = max(
                daily_rain[date_key]["temp_max"], 
                item["main"]["temp_max"]
            )
        
        forecasts = list(daily_rain.values())
        
        return RainfallForecast(
            location=data.get("city", {}).get("name", "Unknown"),
            latitude=lat,
            longitude=lng,
            forecasts=forecasts,
            total_expected_mm=round(total_rain, 2),
            generated_at=datetime.utcnow()
        )
    
    def _generate_mock_current(
        self, 
        lat: float, 
        lng: float, 
        provider: str = "mock"
    ) -> WeatherData:
        """Generate realistic mock data for demo."""
        import random
        month = datetime.now().month
        
        # Seasonal variation for India
        if month in [6, 7, 8, 9]:  # Monsoon
            rainfall = random.uniform(5, 50)
            rain_prob = random.uniform(60, 95)
            temp = random.uniform(24, 32)
        elif month in [12, 1, 2]:  # Winter
            rainfall = random.uniform(0, 5)
            rain_prob = random.uniform(5, 20)
            temp = random.uniform(10, 25)
        else:  # Summer/Post-monsoon
            rainfall = random.uniform(0, 10)
            rain_prob = random.uniform(10, 40)
            temp = random.uniform(28, 42)
        
        return WeatherData(
            timestamp=datetime.utcnow(),
            temperature_c=round(temp, 1),
            humidity_percent=random.randint(40, 85),
            rainfall_mm=round(rainfall, 1),
            rainfall_probability=round(rain_prob, 0),
            wind_speed_kmh=round(random.uniform(5, 25), 1),
            description="Partly cloudy" if rain_prob < 50 else "Rain expected",
            icon="03d" if rain_prob < 50 else "10d",
            provider=provider
        )
    
    def _generate_mock_forecast(
        self, 
        lat: float, 
        lng: float, 
        days: int
    ) -> RainfallForecast:
        """Generate mock forecast for demo."""
        import random
        forecasts = []
        total_rain = 0.0
        
        for i in range(days):
            date = datetime.now() + timedelta(days=i)
            month = date.month
            
            # Seasonal patterns
            if month in [6, 7, 8, 9]:
                rain = random.uniform(10, 80)
            else:
                rain = random.uniform(0, 15)
            
            total_rain += rain
            forecasts.append({
                "date": date.strftime("%Y-%m-%d"),
                "rainfall_mm": round(rain, 1),
                "temp_min": round(random.uniform(20, 28), 1),
                "temp_max": round(random.uniform(28, 38), 1),
                "humidity": random.randint(50, 90),
                "description": "Rain" if rain > 10 else "Partly cloudy",
                "probability": min(95, rain * 2)
            })
        
        return RainfallForecast(
            location="Demo Location",
            latitude=lat,
            longitude=lng,
            forecasts=forecasts,
            total_expected_mm=round(total_rain, 2),
            generated_at=datetime.utcnow()
        )
    
    async def get_historical_rainfall(
        self,
        lat: float,
        lng: float,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict]:
        """Get historical rainfall data (requires paid API or IMD access)."""
        # This would typically use Visual Crossing or IMD historical data
        logger.info("Historical data requires paid API access")
        return []


# Singleton
_weather_service: Optional[WeatherService] = None

def get_weather_service() -> WeatherService:
    global _weather_service
    if _weather_service is None:
        _weather_service = WeatherService()
    return _weather_service
