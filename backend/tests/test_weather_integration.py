import pytest
from app.services.weather_integration import WeatherService

@pytest.mark.asyncio
async def test_get_forecast():
    service = WeatherService.get_instance()
    # Mocking httpx would be ideal, but testing real integration logic structure
    # For acceptance, we will allow a real call or fallback
    forecast = await service.get_forecast(12.97, 77.59, days=3) # Bangalore
    
    assert len(forecast) == 3
    assert forecast[0].rainfall_mm >= 0.0
    assert forecast[0].temperature_max > -50

@pytest.mark.asyncio
async def test_get_current_weather():
    service = WeatherService.get_instance()
    weather = await service.get_current_weather(12.97, 77.59)
    
    assert weather is not None
    assert weather.provider == "Open-Meteo"
    assert weather.temperature_c > -50
