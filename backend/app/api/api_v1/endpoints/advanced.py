"""
Advanced Features API Endpoints
God Mode features exposed via REST API
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, Body
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel

router = APIRouter(prefix="/advanced", tags=["Advanced Features"])


# ==================== REQUEST/RESPONSE MODELS ====================

class ForecastRequest(BaseModel):
    project_id: int
    roof_area_sqm: float
    runoff_coefficient: float = 0.85
    days_ahead: int = 7


class RecommendationRequest(BaseModel):
    roof_area_sqm: float
    building_type: str
    annual_rainfall_mm: float
    budget_range: Optional[str] = None
    water_needs_daily_liters: Optional[float] = None


class ChatMessage(BaseModel):
    user_id: str
    message: str
    context: Optional[Dict] = None


class TenantCreate(BaseModel):
    name: str
    slug: str
    tenant_type: str
    config: Optional[Dict] = None
    admin_email: Optional[str] = None


class RoleAssignment(BaseModel):
    user_id: str
    role_id: str
    scope: Optional[str] = None


class LoRaDeviceRegister(BaseModel):
    dev_eui: str
    app_key: str
    name: str
    project_id: int
    device_type: str = "tank_sensor"


# ==================== FORECASTING ====================

@router.post("/forecast/water-collection")
async def forecast_water_collection(request: ForecastRequest):
    """Forecast water collection based on weather predictions."""
    from app.services.forecasting_service import get_forecasting_service
    
    service = get_forecasting_service()
    forecast = await service.forecast_water_collection(
        project_id=request.project_id,
        roof_area_sqm=request.roof_area_sqm,
        runoff_coefficient=request.runoff_coefficient,
        days_ahead=request.days_ahead
    )
    
    return {
        "target": forecast.target,
        "predictions": forecast.predictions,
        "confidence": forecast.confidence_interval,
        "model": forecast.model_type
    }


@router.post("/forecast/tank-depletion")
async def forecast_tank_depletion(
    project_id: int = Body(...),
    current_level_liters: float = Body(...),
    tank_capacity_liters: float = Body(...),
    usage_history: Optional[List[float]] = Body(None)
):
    """Predict when tank will be empty."""
    from app.services.forecasting_service import get_forecasting_service
    
    service = get_forecasting_service()
    forecast = await service.forecast_tank_depletion(
        project_id=project_id,
        current_level_liters=current_level_liters,
        tank_capacity_liters=tank_capacity_liters,
        usage_history=usage_history
    )
    
    return {
        "predictions": forecast.predictions,
        "confidence": forecast.confidence_interval
    }


@router.get("/forecast/maintenance/{project_id}")
async def forecast_maintenance(
    project_id: int,
    installation_date: str = Query(..., description="ISO date string")
):
    """Predict maintenance needs."""
    from app.services.forecasting_service import get_forecasting_service
    
    service = get_forecasting_service()
    result = await service.forecast_maintenance(
        project_id=project_id,
        installation_date=datetime.fromisoformat(installation_date)
    )
    
    return result


@router.get("/forecast/demand")
async def forecast_demand(
    month: int = Query(..., ge=1, le=12),
    avg_temp: float = Query(...),
    roof_area: float = Query(...),
    occupants: int = Query(...)
):
    """
    ML-Powered Water Demand Forecast.
    Uses RandomForestRegressor to predict monthly demand in liters.
    """
    from app.ml.predict import get_forecaster
    
    forecaster = get_forecaster()
    result = forecaster.predict_demand(month, avg_temp, roof_area, occupants)
    
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
        
    return result


# ==================== RECOMMENDATIONS ====================

@router.post("/recommendations/system")
async def get_system_recommendations(request: RecommendationRequest):
    """Get personalized RWH system recommendations."""
    from app.services.recommendation_engine import get_recommendation_engine, BuildingType, BudgetRange
    
    engine = get_recommendation_engine()
    
    # Map string to enum
    building_type = BuildingType(request.building_type)
    budget = BudgetRange(request.budget_range) if request.budget_range else None
    
    recommendations = await engine.get_recommendations(
        roof_area_sqm=request.roof_area_sqm,
        building_type=building_type,
        annual_rainfall_mm=request.annual_rainfall_mm,
        budget_range=budget,
        water_needs_daily_liters=request.water_needs_daily_liters
    )
    
    return {
        "count": len(recommendations),
        "recommendations": [
            {
                "system_id": r.system_id,
                "name": r.name,
                "description": r.description,
                "components": r.components,
                "cost_range": {
                    "min": r.estimated_cost_min,
                    "max": r.estimated_cost_max
                },
                "roi_years": r.roi_years,
                "water_savings_yearly": r.water_savings_yearly,
                "match_score": r.match_score,
                "pros": r.pros,
                "cons": r.cons
            }
            for r in recommendations
        ]
    }


@router.get("/recommendations/quick-estimate")
async def get_quick_estimate(
    roof_area_sqm: float = Query(...),
    city: str = Query(...)
):
    """Get quick cost estimate without detailed inputs."""
    from app.services.recommendation_engine import get_recommendation_engine
    
    engine = get_recommendation_engine()
    return await engine.get_quick_estimate(roof_area_sqm, city)


# ==================== CHATBOT ====================

@router.post("/chatbot/message")
async def process_chat_message(message: ChatMessage):
    """Process chatbot message and get response."""
    from app.services.chatbot_service import get_chatbot_service
    
    chatbot = get_chatbot_service()
    response = await chatbot.process_message(
        user_id=message.user_id,
        message_text=message.message,
        context=message.context
    )
    
    return {
        "text": response.text,
        "quick_replies": response.quick_replies,
        "buttons": response.buttons
    }


@router.get("/chatbot/quick-actions")
async def get_chatbot_quick_actions():
    """Get available quick actions for chatbot UI."""
    from app.services.chatbot_service import get_chatbot_service
    
    chatbot = get_chatbot_service()
    return {"actions": chatbot.get_quick_actions()}


# ==================== VOICE ALERTS ====================

@router.post("/voice/alert")
async def send_voice_alert(
    to_phone: str = Body(...),
    message: str = Body(...),
    language: str = Body("en-IN")
):
    """Send voice call alert."""
    from app.services.voice_service import get_voice_service
    
    service = get_voice_service()
    return await service.make_call(
        to_phone=to_phone,
        message=message,
        language=language
    )


# ==================== IMAGE SIMILARITY ====================

@router.post("/image/check-duplicate")
async def check_duplicate_image(
    file: UploadFile = File(...),
    project_id: int = Query(...),
    user_id: str = Query(...)
):
    """Check if verification photo might be duplicate/fraudulent."""
    from app.services.image_similarity import get_similarity_service
    
    contents = await file.read()
    service = get_similarity_service()
    
    result = await service.check_for_fraud(
        image_data=contents,
        project_id=project_id,
        user_id=user_id
    )
    
    return result


# ==================== ANALYTICS ====================

@router.get("/analytics/dashboard")
async def get_dashboard(
    time_range: str = Query("month"),
    tenant_id: Optional[str] = None
):
    """Get dashboard summary with key metrics."""
    from app.services.analytics_dashboard import get_analytics_service, TimeRange
    
    service = get_analytics_service()
    return await service.get_dashboard_summary(
        tenant_id=tenant_id,
        time_range=TimeRange(time_range)
    )


@router.get("/analytics/installation-trend")
async def get_installation_trend(
    time_range: str = Query("month"),
    granularity: str = Query("day")
):
    """Get installation trend chart data."""
    from app.services.analytics_dashboard import get_analytics_service, TimeRange
    
    service = get_analytics_service()
    chart = await service.get_installation_trend(TimeRange(time_range), granularity)
    
    return {
        "labels": chart.labels,
        "datasets": chart.datasets
    }


@router.get("/analytics/geographic")
async def get_geographic_distribution(tenant_id: Optional[str] = None):
    """Get geographic distribution of installations."""
    from app.services.analytics_dashboard import get_analytics_service
    
    service = get_analytics_service()
    return await service.get_geographic_distribution(tenant_id)


@router.get("/analytics/verification-stats")
async def get_verification_stats(time_range: str = Query("month")):
    """Get verification statistics."""
    from app.services.analytics_dashboard import get_analytics_service, TimeRange
    
    service = get_analytics_service()
    return await service.get_verification_stats(TimeRange(time_range))


@router.get("/analytics/sensor-health")
async def get_sensor_health():
    """Get IoT sensor health overview."""
    from app.services.analytics_dashboard import get_analytics_service
    
    service = get_analytics_service()
    return await service.get_sensor_health()


# ==================== MULTI-TENANT ====================

@router.post("/tenants")
async def create_tenant(tenant: TenantCreate):
    """Create a new tenant."""
    from app.services.multi_tenant import get_tenant_service, TenantType
    
    service = get_tenant_service()
    result = await service.create_tenant(
        name=tenant.name,
        slug=tenant.slug,
        tenant_type=TenantType(tenant.tenant_type),
        config=tenant.config,
        admin_email=tenant.admin_email
    )
    
    return {
        "id": result.id,
        "slug": result.slug,
        "status": result.status.value
    }


@router.get("/tenants")
async def list_tenants(
    tenant_type: Optional[str] = None,
    status: Optional[str] = None
):
    """List all tenants."""
    from app.services.multi_tenant import get_tenant_service, TenantType, TenantStatus
    
    service = get_tenant_service()
    return await service.list_tenants(
        tenant_type=TenantType(tenant_type) if tenant_type else None,
        status=TenantStatus(status) if status else None
    )


@router.get("/tenants/{tenant_id}/branding")
async def get_tenant_branding(tenant_id: str):
    """Get branding configuration for tenant."""
    from app.services.multi_tenant import get_tenant_service
    
    service = get_tenant_service()
    return await service.get_tenant_branding(tenant_id)


# ==================== RBAC ====================

@router.post("/roles/assign")
async def assign_role(assignment: RoleAssignment):
    """Assign a role to a user."""
    from app.services.rbac_service import get_rbac_service
    
    rbac = get_rbac_service()
    result = await rbac.assign_role(
        user_id=assignment.user_id,
        role_id=assignment.role_id,
        scope=assignment.scope
    )
    
    return {
        "user_id": result.user_id,
        "role_id": result.role_id,
        "granted_at": result.granted_at.isoformat()
    }


@router.get("/roles/hierarchy")
async def get_role_hierarchy():
    """Get role hierarchy for UI."""
    from app.services.rbac_service import get_rbac_service
    
    rbac = get_rbac_service()
    return {"roles": await rbac.get_role_hierarchy()}


@router.get("/roles/user/{user_id}/permissions")
async def get_user_permissions(user_id: str, scope: Optional[str] = None):
    """Get all permissions for a user."""
    from app.services.rbac_service import get_rbac_service
    
    rbac = get_rbac_service()
    permissions = await rbac.get_user_permissions(user_id, scope)
    
    return {"permissions": [p.value for p in permissions]}


# ==================== SSO/OAUTH ====================

@router.get("/auth/oauth/{provider}/authorize")
async def get_oauth_url(provider: str, redirect_uri: Optional[str] = None):
    """Get OAuth authorization URL."""
    from app.services.sso_service import get_sso_service
    
    sso = get_sso_service()
    return sso.get_authorization_url(provider, redirect_uri)


@router.post("/auth/oauth/{provider}/callback")
async def oauth_callback(
    provider: str,
    code: str = Body(...),
    state: str = Body(...)
):
    """Handle OAuth callback."""
    from app.services.sso_service import get_sso_service
    
    sso = get_sso_service()
    user = await sso.handle_callback(provider, code, state)
    
    return {
        "provider": user.provider,
        "email": user.email,
        "name": user.name,
        "provider_id": user.provider_id
    }


@router.get("/auth/oauth/providers")
async def get_oauth_providers():
    """Get list of configured OAuth providers."""
    from app.services.sso_service import get_sso_service
    
    sso = get_sso_service()
    return {"providers": sso.get_available_providers()}


# ==================== LORAWAN ====================

@router.post("/lora/devices")
async def register_lora_device(device: LoRaDeviceRegister):
    """Register a new LoRaWAN device."""
    from app.services.lorawan_service import get_lora_service
    
    service = get_lora_service()
    result = await service.register_device(
        dev_eui=device.dev_eui,
        app_key=device.app_key,
        name=device.name,
        project_id=device.project_id,
        device_type=device.device_type
    )
    
    return {
        "dev_eui": result.dev_eui,
        "name": result.name,
        "project_id": result.project_id
    }


@router.get("/lora/devices")
async def list_lora_devices(project_id: Optional[int] = None):
    """List LoRaWAN devices."""
    from app.services.lorawan_service import get_lora_service
    
    service = get_lora_service()
    return {"devices": service.list_devices(project_id)}


@router.get("/lora/devices/{dev_eui}")
async def get_lora_device(dev_eui: str):
    """Get LoRaWAN device status."""
    from app.services.lorawan_service import get_lora_service
    
    service = get_lora_service()
    status = service.get_device_status(dev_eui)
    
    if not status:
        raise HTTPException(status_code=404, detail="Device not found")
    
    return status


# ==================== AUDIT LOG ====================

@router.get("/audit/logs")
async def search_audit_logs(
    action: Optional[str] = None,
    user_id: Optional[str] = None,
    resource_type: Optional[str] = None,
    limit: int = Query(100, le=1000),
    offset: int = Query(0, ge=0)
):
    """Search audit logs."""
    from app.services.audit_service import get_audit_service, AuditAction
    
    audit = get_audit_service()
    entries = await audit.search(
        action=AuditAction(action) if action else None,
        user_id=user_id,
        resource_type=resource_type,
        limit=limit,
        offset=offset
    )
    
    return {
        "count": len(entries),
        "entries": [
            {
                "id": e.id,
                "timestamp": e.timestamp.isoformat(),
                "action": e.action.value,
                "user": e.user_email or e.user_id,
                "resource": f"{e.resource_type}/{e.resource_id}" if e.resource_type else None,
                "level": e.level.value
            }
            for e in entries
        ]
    }


@router.get("/audit/user/{user_id}/activity")
async def get_user_activity(user_id: str, days: int = Query(30, le=365)):
    """Get user activity summary."""
    from app.services.audit_service import get_audit_service
    
    audit = get_audit_service()
    return await audit.get_user_activity(user_id, days)


@router.get("/audit/resource/{resource_type}/{resource_id}/history")
async def get_resource_history(resource_type: str, resource_id: str):
    """Get complete history for a resource."""
    from app.services.audit_service import get_audit_service
    
    audit = get_audit_service()
    return {"history": await audit.get_resource_history(resource_type, resource_id)}
