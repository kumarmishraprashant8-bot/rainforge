"""
API Endpoints for New Features
Weather, Notifications, Carbon, Government Data, etc.
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

from app.services.weather_integration import get_weather_service
from app.services.carbon_calculator import get_carbon_calculator
from app.services.government_data import get_gov_data_service, get_satellite_service
from app.services.notification_hub import get_notification_hub

router = APIRouter()


# ==================== WEATHER ENDPOINTS ====================

class WeatherRequest(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)


@router.get("/weather/current")
async def get_current_weather(
    lat: float = Query(..., ge=-90, le=90),
    lng: float = Query(..., ge=-180, le=180)
):
    """Get current weather for a location."""
    service = get_weather_service()
    weather = await service.get_current_weather(lat, lng)
    
    if not weather:
        raise HTTPException(status_code=503, detail="Weather service unavailable")
    
    return weather.dict()


@router.get("/weather/forecast")
async def get_rainfall_forecast(
    lat: float = Query(..., ge=-90, le=90),
    lng: float = Query(..., ge=-180, le=180),
    days: int = Query(7, ge=1, le=14)
):
    """Get multi-day rainfall forecast."""
    service = get_weather_service()
    forecasts = await service.get_forecast(lat, lng, days)
    
    if not forecasts:
        raise HTTPException(status_code=503, detail="Forecast unavailable")
    
    total_rain = sum(f.rainfall_mm for f in forecasts)
    
    return {
        "location": "Unknown Location (Open-Meteo)",
        "total_expected_mm": round(total_rain, 2),
        "forecasts": [f.dict() for f in forecasts],
        "generated_at": datetime.now().isoformat()
    }


# ==================== CARBON CREDIT ENDPOINTS ====================

class CarbonRequest(BaseModel):
    water_liters: float = Field(..., gt=0)
    include_wastewater: bool = True


class AnnualCarbonRequest(BaseModel):
    roof_area_sqm: float = Field(..., gt=0)
    annual_rainfall_mm: float = Field(..., gt=0)
    runoff_coefficient: float = Field(0.85, ge=0, le=1)


@router.post("/carbon/calculate")
async def calculate_carbon_credits(request: CarbonRequest):
    """Calculate carbon credits from water saved."""
    calculator = get_carbon_calculator()
    result = calculator.calculate(
        request.water_liters,
        request.include_wastewater
    )
    
    return {
        "water_saved_liters": result.water_saved_liters,
        "energy_saved_kwh": result.energy_saved_kwh,
        "co2_offset_kg": result.co2_offset_kg,
        "co2_offset_tonnes": result.co2_offset_tonnes,
        "equivalent_trees": result.equivalent_trees,
        "equivalent_car_km": result.equivalent_car_km,
        "carbon_value_inr": result.carbon_credit_value_inr,
        "carbon_value_usd": result.carbon_credit_value_usd
    }


@router.post("/carbon/annual-impact")
async def calculate_annual_impact(request: AnnualCarbonRequest):
    """Calculate annual carbon impact for a RWH system."""
    calculator = get_carbon_calculator()
    result = calculator.calculate_annual_impact(
        request.roof_area_sqm,
        request.annual_rainfall_mm,
        request.runoff_coefficient
    )
    
    return result


@router.get("/carbon/city-impact")
async def get_city_impact(
    total_capacity_liters: float = Query(..., gt=0),
    utilization: float = Query(0.7, ge=0, le=1)
):
    """Get city-wide carbon impact statistics."""
    calculator = get_carbon_calculator()
    return calculator.calculate_city_impact(total_capacity_liters, utilization)


# ==================== GOVERNMENT DATA ENDPOINTS ====================

@router.get("/gov/rainfall")
async def get_district_rainfall(
    district: str,
    state: str,
    days: int = Query(30, ge=1, le=365)
):
    """Get historical rainfall data for a district."""
    service = get_gov_data_service()
    from datetime import timedelta
    
    start = datetime.now() - timedelta(days=days)
    end = datetime.now()
    
    data = await service.get_district_rainfall(district, state, start, end)
    
    return {
        "district": district,
        "state": state,
        "period_days": days,
        "data": [
            {
                "date": d.date.isoformat(),
                "rainfall_mm": d.rainfall_mm,
                "normal_mm": d.normal_mm,
                "departure_percent": d.departure_percent
            }
            for d in data
        ]
    }


@router.get("/gov/groundwater")
async def get_groundwater_data(
    district: str,
    state: str
):
    """Get groundwater level data for a district."""
    service = get_gov_data_service()
    data = await service.get_groundwater_level(district, state)
    
    return {
        "district": district,
        "state": state,
        "wells": [
            {
                "well_id": d.well_id,
                "location": d.location,
                "water_level_m": d.water_level_m,
                "trend": d.trend,
                "last_measured": d.last_measured.isoformat()
            }
            for d in data
        ]
    }


@router.get("/gov/monsoon-forecast")
async def get_monsoon_forecast(region: str = "all-india"):
    """Get monsoon season forecast."""
    service = get_gov_data_service()
    return await service.get_monsoon_forecast(region)


@router.get("/gov/jjm-stats")
async def get_jjm_statistics(
    state: Optional[str] = None,
    district: Optional[str] = None
):
    """Get Jal Jeevan Mission statistics."""
    service = get_gov_data_service()
    return await service.get_jjm_stats(state, district)


@router.get("/gov/sdg-indicators")
async def get_sdg_water_indicators(state: str):
    """Get SDG water indicators for a state."""
    service = get_gov_data_service()
    return await service.get_sdg_water_indicators(state)


# ==================== SATELLITE DATA ENDPOINTS ====================

@router.get("/satellite/rainfall")
async def get_satellite_rainfall(
    lat: float = Query(..., ge=-90, le=90),
    lng: float = Query(..., ge=-180, le=180)
):
    """Get satellite-derived rainfall estimate."""
    service = get_satellite_service()
    return await service.get_satellite_rainfall(lat, lng)


@router.get("/satellite/building")
async def get_building_footprint(
    lat: float = Query(..., ge=-90, le=90),
    lng: float = Query(..., ge=-180, le=180)
):
    """Get building footprint from satellite."""
    service = get_satellite_service()
    return await service.get_building_footprint(lat, lng)


@router.get("/satellite/landuse")
async def get_land_use(
    lat: float = Query(..., ge=-90, le=90),
    lng: float = Query(..., ge=-180, le=180)
):
    """Get land use classification."""
    service = get_satellite_service()
    return await service.get_land_use(lat, lng)


# ==================== NOTIFICATION ENDPOINTS ====================

class TankAlertRequest(BaseModel):
    user_id: str
    phone: str
    tank_level: float
    project_name: str


class PaymentNotificationRequest(BaseModel):
    user_id: str
    phone: str
    amount: float
    reference: str


@router.post("/notifications/tank-alert")
async def send_tank_alert(
    request: TankAlertRequest,
    background_tasks: BackgroundTasks
):
    """Send tank level alert."""
    hub = get_notification_hub()
    
    # Run in background
    background_tasks.add_task(
        hub.send_tank_alert,
        request.user_id,
        request.phone,
        request.tank_level,
        request.project_name
    )
    
    return {"status": "queued", "message": "Tank alert will be sent"}


@router.post("/notifications/payment")
async def send_payment_notification(
    request: PaymentNotificationRequest,
    background_tasks: BackgroundTasks
):
    """Send payment notification."""
    hub = get_notification_hub()
    
    background_tasks.add_task(
        hub.send_payment_notification,
        request.user_id,
        request.phone,
        request.amount,
        request.reference
    )
    
    return {"status": "queued", "message": "Payment notification will be sent"}
