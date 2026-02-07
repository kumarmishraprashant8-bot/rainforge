"""
Community Features API - Water Sharing, Predictive Maintenance, Satellite Detection
Combines multiple new services into unified API endpoints
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/community", tags=["community", "water-sharing", "maintenance", "satellite"])


# ==================== SCHEMAS ====================
class SystemRegistration(BaseModel):
    owner_id: str
    owner_name: str
    address: str
    latitude: float
    longitude: float
    tank_capacity_liters: float


class SharingRequest(BaseModel):
    from_system_id: str
    to_system_id: str
    liters_requested: float
    requestor_name: str


class TelemetryInput(BaseModel):
    site_id: str
    component_type: str  # filter, pump, tank
    hours_since_maintenance: float
    reading_value: float
    timestamp: Optional[datetime] = None


class RoofDetectionRequest(BaseModel):
    latitude: float
    longitude: float
    radius_m: float = 500
    min_confidence: float = 0.7


class NotificationSubscription(BaseModel):
    user_id: str
    endpoint: str
    p256dh_key: str
    auth_key: str
    user_agent: str = ""


# ==================== WATER SHARING ENDPOINTS ====================
@router.post("/systems/register")
def register_system(data: SystemRegistration):
    """Register a new RWH system for community sharing"""
    from app.services.water_sharing import get_water_sharing_service
    service = get_water_sharing_service()
    
    system = service.register_system(
        owner_id=data.owner_id,
        owner_name=data.owner_name,
        address=data.address,
        latitude=data.latitude,
        longitude=data.longitude,
        tank_capacity_liters=data.tank_capacity_liters
    )
    
    return {"success": True, "system_id": system.system_id, "system": system.__dict__}


@router.get("/systems/nearby")
def find_nearby_systems(
    latitude: float = Query(...),
    longitude: float = Query(...),
    max_distance_km: float = Query(5.0),
    surplus_only: bool = Query(False)
):
    """Find RWH systems near a location"""
    from app.services.water_sharing import get_water_sharing_service
    service = get_water_sharing_service()
    
    systems = service.find_nearby_systems(
        latitude=latitude,
        longitude=longitude,
        max_distance_km=max_distance_km,
        surplus_only=surplus_only
    )
    
    return {"count": len(systems), "systems": systems}


@router.post("/sharing/request")
def request_water_sharing(data: SharingRequest):
    """Request water from a nearby system"""
    from app.services.water_sharing import get_water_sharing_service
    service = get_water_sharing_service()
    
    try:
        request = service.request_water(
            from_system_id=data.from_system_id,
            to_system_id=data.to_system_id,
            liters_requested=data.liters_requested,
            requestor_name=data.requestor_name
        )
        return {"success": True, "request_id": request.request_id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/sharing/{request_id}/respond")
def respond_to_request(request_id: str, accept: bool):
    """Accept or reject a sharing request"""
    from app.services.water_sharing import get_water_sharing_service
    service = get_water_sharing_service()
    
    try:
        request = service.respond_to_request(request_id, accept)
        return {"success": True, "status": request.status.value}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/leaderboard")
def get_community_leaderboard():
    """Get community sharing leaderboard"""
    from app.services.water_sharing import get_water_sharing_service
    service = get_water_sharing_service()
    return service.get_community_leaderboard()


# ==================== PREDICTIVE MAINTENANCE ENDPOINTS ====================
@router.post("/maintenance/telemetry")
def ingest_telemetry(data: TelemetryInput):
    """Ingest sensor telemetry for maintenance prediction"""
    from app.services.predictive_maintenance import get_predictive_maintenance_service
    service = get_predictive_maintenance_service()
    
    service.ingest_telemetry(
        site_id=data.site_id,
        component_type=data.component_type,
        reading_value=data.reading_value,
        hours_since_maintenance=data.hours_since_maintenance,
        timestamp=data.timestamp or datetime.now()
    )
    
    return {"success": True, "message": "Telemetry ingested"}


@router.get("/maintenance/{site_id}/health")
def get_site_health(site_id: str):
    """Get maintenance health summary for a site"""
    from app.services.predictive_maintenance import get_predictive_maintenance_service
    service = get_predictive_maintenance_service()
    return service.get_site_health_summary(site_id)


@router.get("/maintenance/{site_id}/schedule")
def get_maintenance_schedule(site_id: str, days_ahead: int = Query(90)):
    """Get predicted maintenance schedule"""
    from app.services.predictive_maintenance import get_predictive_maintenance_service
    service = get_predictive_maintenance_service()
    return service.predict_maintenance_schedule(site_id, days_ahead)


# ==================== SATELLITE DETECTION ENDPOINTS ====================
@router.post("/satellite/detect")
def detect_roofs(data: RoofDetectionRequest):
    """Detect roofs in a circular area from satellite imagery"""
    from app.services.satellite_detector import get_satellite_detector
    service = get_satellite_detector()
    
    result = service.detect_roofs(
        center_lat=data.latitude,
        center_lon=data.longitude,
        radius_m=data.radius_m,
        min_confidence=data.min_confidence
    )
    
    return {
        "detection_id": result.detection_id,
        "roofs_detected": result.roofs_detected,
        "suitable_roofs": result.suitable_roofs,
        "total_area_sqm": result.total_roof_area_sqm,
        "suitable_area_sqm": result.suitable_area_sqm,
        "polygons": [p.__dict__ for p in result.polygons[:20]]  # Limit response size
    }


@router.get("/satellite/{detection_id}/potential")
def get_rwh_potential(detection_id: str, annual_rainfall_mm: float = Query(1200)):
    """Estimate RWH potential for a detection area"""
    from app.services.satellite_detector import get_satellite_detector
    service = get_satellite_detector()
    
    try:
        return service.estimate_rwh_potential(detection_id, annual_rainfall_mm)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/satellite/address")
def detect_single_address(lat: float, lon: float, address: str = ""):
    """Detect roof for a single address"""
    from app.services.satellite_detector import get_satellite_detector
    service = get_satellite_detector()
    
    polygon = service.detect_single_address(lat, lon, address)
    if polygon:
        return {"found": True, "polygon": polygon.__dict__}
    return {"found": False, "polygon": None}


# ==================== PUSH NOTIFICATIONS ENDPOINTS ====================
@router.post("/notifications/subscribe")
def subscribe_push(data: NotificationSubscription):
    """Subscribe to push notifications"""
    from app.services.push_notification import get_push_notification_service
    service = get_push_notification_service()
    
    subscription = service.subscribe(
        user_id=data.user_id,
        endpoint=data.endpoint,
        p256dh_key=data.p256dh_key,
        auth_key=data.auth_key,
        user_agent=data.user_agent
    )
    
    return {"success": True, "subscription_id": subscription.subscription_id}


@router.delete("/notifications/{user_id}/unsubscribe")
def unsubscribe_push(user_id: str, endpoint: str = Query(...)):
    """Unsubscribe from push notifications"""
    from app.services.push_notification import get_push_notification_service
    service = get_push_notification_service()
    
    result = service.unsubscribe(user_id, endpoint)
    return {"success": result}


@router.get("/notifications/{user_id}")
def get_user_notifications(user_id: str, unread_only: bool = Query(False)):
    """Get notifications for a user"""
    from app.services.push_notification import get_push_notification_service
    service = get_push_notification_service()
    
    notifications = service.get_user_notifications(user_id, unread_only)
    return {"count": len(notifications), "notifications": [n.__dict__ for n in notifications]}


# ==================== DEMAND FORECASTING ENDPOINTS ====================
@router.get("/forecasting/{location_id}/demand")
def forecast_demand(
    location_id: str,
    days_ahead: int = Query(30),
    granularity: str = Query("daily")
):
    """Forecast water demand for a location"""
    from app.services.demand_forecasting import get_demand_forecasting_service
    service = get_demand_forecasting_service()
    
    forecast = service.forecast_demand(
        location_id=location_id,
        days_ahead=days_ahead,
        granularity=granularity
    )
    
    return {"location_id": location_id, "forecast": [f.__dict__ for f in forecast]}


@router.get("/forecasting/{location_id}/gap-analysis")
def analyze_supply_gap(location_id: str, forecasted_supply_liters: float = Query(...)):
    """Analyze supply gap for a location"""
    from app.services.demand_forecasting import get_demand_forecasting_service
    service = get_demand_forecasting_service()
    
    return service.analyze_supply_gap(location_id, forecasted_supply_liters).__dict__


@router.get("/forecasting/monsoon-report")
def get_monsoon_report(year: int = Query(2026)):
    """Get monsoon planning report"""
    from app.services.demand_forecasting import get_demand_forecasting_service
    service = get_demand_forecasting_service()
    
    # Register a sample location if needed
    service.register_location("city_sample", "Sample City", 5000000, 850)
    return service.generate_monsoon_planning_report("city_sample", year)
