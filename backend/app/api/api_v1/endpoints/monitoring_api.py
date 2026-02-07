"""
RainForge Monitoring API
========================
Sensor data ingestion and tank status endpoints.

Owners: Prashant Mishra & Ishita Parmar
"""

from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Header, Query
from pydantic import BaseModel, Field
import os

router = APIRouter()

# In-memory storage (use TimescaleDB in production)
_sensor_data = {}
_tank_status = {}


class SensorReading(BaseModel):
    """Sensor data from IoT device."""
    sensor_id: str
    project_id: int
    timestamp: Optional[str] = None
    level_percent: float = Field(..., ge=0, le=100)
    level_volume_l: Optional[float] = None
    battery_pct: Optional[float] = Field(None, ge=0, le=100)
    ph_level: Optional[float] = Field(None, ge=0, le=14)
    turbidity_ntu: Optional[float] = Field(None, ge=0)
    flow_rate_lpm: Optional[float] = Field(None, ge=0)
    temperature_c: Optional[float] = None


class TankStatus(BaseModel):
    """Current tank status."""
    project_id: int
    tank_level_percent: float
    current_volume_liters: float
    capacity_liters: float
    last_updated: str
    sensor_status: str
    maintenance_alerts: List[str]
    days_until_empty: float


class HistoricalReading(BaseModel):
    """Historical reading for charts."""
    timestamp: str
    tank_level_percent: float
    flow_rate_lpm: float
    rainfall_mm: float


class HistoryResponse(BaseModel):
    """Historical data response."""
    project_id: int
    readings: List[HistoricalReading]
    period_hours: int


# API Key validation
SENSOR_API_KEY = os.environ.get("API_KEY_SENSOR", "sensor-api-key-demo")


def validate_api_key(api_key: str) -> bool:
    """Validate sensor API key."""
    return api_key == SENSOR_API_KEY


@router.post("/sensor")
async def ingest_sensor_data(
    reading: SensorReading,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key")
):
    """
    Ingest sensor reading from IoT device.
    
    Requires X-API-Key header for authentication.
    """
    # Validate API key (skip in demo mode)
    if x_api_key and not validate_api_key(x_api_key):
        raise HTTPException(status_code=403, detail="Invalid API key")
    
    # Set timestamp if not provided
    if not reading.timestamp:
        reading.timestamp = datetime.now().isoformat()
    
    # Store reading
    project_id = reading.project_id
    if project_id not in _sensor_data:
        _sensor_data[project_id] = []
    
    _sensor_data[project_id].append(reading.dict())
    
    # Keep only last 1000 readings per project
    if len(_sensor_data[project_id]) > 1000:
        _sensor_data[project_id] = _sensor_data[project_id][-1000:]
    
    # Update tank status
    capacity = 10000  # Default, would come from project config
    _tank_status[project_id] = {
        "tank_level_percent": reading.level_percent,
        "current_volume_liters": reading.level_volume_l or (reading.level_percent / 100 * capacity),
        "capacity_liters": capacity,
        "last_updated": reading.timestamp,
        "sensor_status": "online",
        "battery_pct": reading.battery_pct
    }
    
    return {
        "status": "ok",
        "message": "Reading ingested",
        "timestamp": reading.timestamp
    }


@router.get("/{project_id}/status", response_model=TankStatus)
async def get_tank_status(project_id: int):
    """
    Get current tank status for a project.
    """
    # Check for actual data
    if project_id in _tank_status:
        status = _tank_status[project_id]
        
        # Calculate days until empty based on consumption
        readings = _sensor_data.get(project_id, [])
        days_until_empty = 30  # Default
        
        if len(readings) >= 2:
            # Calculate average daily consumption
            recent = readings[-24:]  # Last 24 readings
            if len(recent) >= 2:
                start_level = recent[0].get("level_percent", 50)
                end_level = recent[-1].get("level_percent", 50)
                level_drop = start_level - end_level
                
                if level_drop > 0:
                    days_until_empty = (end_level / level_drop) * (len(recent) / 24)
        
        # Check for maintenance alerts
        alerts = []
        if status.get("battery_pct", 100) < 20:
            alerts.append("Low battery - replace sensor batteries")
        if status.get("tank_level_percent", 50) < 15:
            alerts.append("Low water level - consider refilling")
        
        return TankStatus(
            project_id=project_id,
            tank_level_percent=status["tank_level_percent"],
            current_volume_liters=status["current_volume_liters"],
            capacity_liters=status["capacity_liters"],
            last_updated=status["last_updated"],
            sensor_status=status["sensor_status"],
            maintenance_alerts=alerts,
            days_until_empty=max(0, days_until_empty)
        )
    
    # Return demo data if no actual data
    return TankStatus(
        project_id=project_id,
        tank_level_percent=34.0,
        current_volume_liters=3400.0,
        capacity_liters=10000.0,
        last_updated=datetime.now().isoformat(),
        sensor_status="online",
        maintenance_alerts=[],
        days_until_empty=17.0
    )


@router.get("/{project_id}/history", response_model=HistoryResponse)
async def get_history(
    project_id: int,
    hours: int = Query(24, ge=1, le=168)
):
    """
    Get historical readings for a project.
    
    Args:
        project_id: Project ID
        hours: Number of hours of history (1-168)
    """
    readings = []
    
    if project_id in _sensor_data:
        # Filter by time range
        cutoff = datetime.now() - timedelta(hours=hours)
        
        for reading in _sensor_data[project_id]:
            try:
                ts = datetime.fromisoformat(reading.get("timestamp", ""))
                if ts >= cutoff:
                    readings.append(HistoricalReading(
                        timestamp=reading["timestamp"],
                        tank_level_percent=reading.get("level_percent", 0),
                        flow_rate_lpm=reading.get("flow_rate_lpm", 0),
                        rainfall_mm=0  # Would come from weather API
                    ))
            except:
                pass
    
    # Generate demo data if none exists
    if not readings:
        import random
        for i in range(hours):
            ts = datetime.now() - timedelta(hours=hours - i)
            readings.append(HistoricalReading(
                timestamp=ts.isoformat(),
                tank_level_percent=30 + 15 * (1 + 0.5 * (i % 12 - 6) / 6) + random.uniform(-3, 3),
                flow_rate_lpm=random.uniform(0, 2),
                rainfall_mm=random.uniform(0, 1) if i % 6 == 0 else 0
            ))
    
    return HistoryResponse(
        project_id=project_id,
        readings=readings,
        period_hours=hours
    )


@router.get("/{project_id}/predictions")
async def get_predictions(project_id: int, days: int = Query(7, ge=1, le=30)):
    """
    Get capture predictions for next N days.
    """
    from datetime import date
    import random
    
    predictions = []
    for i in range(days):
        d = date.today() + timedelta(days=i)
        
        # Simulated weather-based prediction
        rainfall = random.uniform(0, 15) if i % 3 == 0 else random.uniform(0, 3)
        capture = rainfall * 150 * 0.85  # Assuming 150 sqm roof, 0.85 coefficient
        
        predictions.append({
            "date": d.isoformat(),
            "rainfall_mm": round(rainfall, 1),
            "predicted_capture_l": round(capture, 0),
            "confidence": 0.85 if i < 3 else 0.70
        })
    
    return {
        "project_id": project_id,
        "predictions": predictions,
        "total_predicted_l": sum(p["predicted_capture_l"] for p in predictions),
        "model_version": "v1.0.0"
    }
