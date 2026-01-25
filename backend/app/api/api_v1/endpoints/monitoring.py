"""
RainForge Monitoring API Endpoints
IoT data and live water accounting.
"""

from fastapi import APIRouter, HTTPException
from typing import List
from app.services.iot_gateway import IoTGateway

router = APIRouter()


@router.get("/{project_id}/current")
async def get_current_reading(project_id: int):
    """
    Get current sensor reading for a project.
    """
    reading = IoTGateway.get_current_reading(project_id)
    return reading


@router.get("/{project_id}/history")
async def get_historical_readings(project_id: int, hours: int = 24):
    """
    Get historical readings for charting.
    """
    readings = IoTGateway.get_historical_readings(project_id, hours=hours)
    return {"project_id": project_id, "readings": readings, "total": len(readings)}


@router.get("/{project_id}/status")
async def get_tank_status(project_id: int, capacity: float = 10000):
    """
    Get comprehensive tank status with predictions.
    """
    status = IoTGateway.get_tank_status(project_id, tank_capacity=capacity)
    return status


@router.get("/{project_id}/alerts")
async def get_alerts(project_id: int):
    """
    Get active alerts for a project.
    """
    reading = IoTGateway.get_current_reading(project_id)
    alerts = IoTGateway.check_alerts(project_id, reading)
    return {"project_id": project_id, "alerts": alerts}


@router.post("/portfolio")
async def get_portfolio_monitoring(project_ids: List[int]):
    """
    Get monitoring summary for multiple projects.
    """
    result = IoTGateway.get_portfolio_monitoring(project_ids)
    return result


@router.get("/demo/simulate")
async def simulate_day(project_id: int = 1):
    """
    Simulate a full day of IoT readings (for demo).
    """
    readings = IoTGateway.get_historical_readings(project_id, hours=24, interval_minutes=30)
    return {
        "project_id": project_id,
        "simulation": "24-hour",
        "data_points": len(readings),
        "readings": readings
    }
