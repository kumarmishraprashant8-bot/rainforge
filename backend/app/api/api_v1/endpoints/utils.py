"""
Utility API Endpoints
PDF, QR, Export, Import, Health, and Gamification endpoints
"""
from fastapi import APIRouter, HTTPException, Query, File, UploadFile, Response
from fastapi.responses import StreamingResponse
from typing import Optional, List
from datetime import datetime
import io

router = APIRouter(prefix="/utils", tags=["Utilities"])


# ==================== PDF GENERATION ====================

@router.get("/pdf/assessment/{project_id}")
async def generate_assessment_pdf(project_id: int):
    """Generate PDF assessment report."""
    from app.services.pdf_generator import get_pdf_generator
    
    generator = get_pdf_generator()
    
    # Mock data - would fetch from database
    pdf_bytes = generator.generate_assessment_report(
        project_name=f"Project #{project_id}",
        address="123 Sample Street, Mumbai, Maharashtra 400001",
        roof_area_sqm=150,
        annual_rainfall_mm=2200,
        runoff_coefficient=0.85,
        yearly_yield_liters=280500,
        recommended_tank_liters=5000,
        estimated_cost_min=45000,
        estimated_cost_max=75000,
        roi_years=3.5,
        carbon_offset_kg=84,
        recommendations=[
            {"name": "Basic System", "cost_min": 45000, "cost_max": 55000, "roi_years": 3},
            {"name": "Premium System", "cost_min": 65000, "cost_max": 75000, "roi_years": 4}
        ]
    )
    
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=assessment_{project_id}.pdf"}
    )


@router.get("/pdf/certificate/{project_id}")
async def generate_certificate_pdf(project_id: int):
    """Generate installation certificate PDF."""
    from app.services.pdf_generator import get_pdf_generator
    
    generator = get_pdf_generator()
    
    certificate_number = f"RF-{datetime.now().year}-{project_id:06d}"
    
    pdf_bytes = generator.generate_certificate(
        project_id=project_id,
        project_name=f"Project #{project_id}",
        owner_name="Sample Owner",
        address="123 Sample Street, Mumbai, Maharashtra",
        tank_capacity=5000,
        installation_date="15 January 2024",
        installer_name="RWH Solutions Pvt Ltd",
        verification_date="20 January 2024",
        certificate_number=certificate_number
    )
    
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=certificate_{project_id}.pdf"}
    )


# ==================== QR CODES ====================

@router.get("/qr/project/{project_id}")
async def generate_project_qr(project_id: int, style: str = "default"):
    """Generate QR code for project."""
    from app.services.qr_generator import get_qr_generator
    
    generator = get_qr_generator()
    qr = generator.generate_project_qr(project_id, style=style)
    
    return Response(
        content=qr.raw_bytes,
        media_type="image/png",
        headers={"Content-Disposition": f"inline; filename=project_{project_id}_qr.png"}
    )


@router.get("/qr/certificate/{certificate_number}")
async def generate_certificate_qr(certificate_number: str):
    """Generate QR code for certificate verification."""
    from app.services.qr_generator import get_qr_generator
    
    generator = get_qr_generator()
    qr = generator.generate_certificate_qr(certificate_number)
    
    return Response(
        content=qr.raw_bytes,
        media_type="image/png"
    )


@router.get("/qr/payment")
async def generate_payment_qr(
    upi_id: str = Query(...),
    amount: float = Query(...),
    project_id: int = Query(...)
):
    """Generate UPI payment QR code."""
    from app.services.qr_generator import get_qr_generator
    
    generator = get_qr_generator()
    qr = generator.generate_payment_qr(upi_id, amount, project_id)
    
    return Response(
        content=qr.raw_bytes,
        media_type="image/png"
    )


# ==================== DATA EXPORT ====================

@router.get("/export/projects")
async def export_projects(format: str = Query("csv", enum=["csv", "json", "xlsx"])):
    """Export projects data."""
    from app.services.data_export import get_export_service
    
    service = get_export_service()
    
    # Mock data
    projects = [
        {"id": 1, "name": "Project 1", "city": "Mumbai", "status": "completed"},
        {"id": 2, "name": "Project 2", "city": "Delhi", "status": "in_progress"},
        {"id": 3, "name": "Project 3", "city": "Bangalore", "status": "pending"}
    ]
    
    result = service.export_projects(projects, format)
    
    return Response(
        content=result.data,
        media_type=result.content_type,
        headers={"Content-Disposition": f"attachment; filename={result.filename}"}
    )


@router.get("/export/analytics")
async def export_analytics(time_range: str = "month"):
    """Export analytics data as JSON."""
    from app.services.data_export import get_export_service
    from app.services.analytics_dashboard import get_analytics_service, TimeRange
    
    analytics = get_analytics_service()
    export = get_export_service()
    
    data = await analytics.get_dashboard_summary(time_range=TimeRange(time_range))
    result = export.export_analytics(data)
    
    return Response(
        content=result.data,
        media_type=result.content_type,
        headers={"Content-Disposition": f"attachment; filename={result.filename}"}
    )


# ==================== BULK IMPORT ====================

@router.post("/import/projects")
async def import_projects(file: UploadFile = File(...)):
    """Import projects from CSV/Excel file."""
    from app.services.bulk_import import get_import_service
    
    service = get_import_service()
    contents = await file.read()
    
    result = await service.import_projects(
        file_content=contents,
        file_type=file.content_type or "csv"
    )
    
    return {
        "success_count": result.success_count,
        "error_count": result.error_count,
        "errors": result.errors[:20],  # Limit errors shown
        "imported_ids": result.imported_ids[:20]
    }


@router.get("/import/template/{import_type}")
async def get_import_template(import_type: str):
    """Get CSV template for import."""
    from app.services.bulk_import import get_import_service
    
    service = get_import_service()
    filename, content = service.get_template(import_type)
    
    return Response(
        content=content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


# ==================== HEALTH & METRICS ====================

@router.get("/health")
async def get_health_status():
    """Get system health status."""
    from app.services.health_dashboard import get_health_service
    
    service = get_health_service()
    return await service.get_health_summary()


@router.get("/health/metrics")
async def get_request_metrics(period: str = Query("hour", enum=["hour", "day", "month"])):
    """Get request metrics."""
    from app.services.health_dashboard import get_health_service
    
    service = get_health_service()
    return await service.get_request_metrics(period)


@router.get("/health/endpoints")
async def get_endpoint_stats():
    """Get per-endpoint statistics."""
    from app.services.health_dashboard import get_health_service
    
    service = get_health_service()
    return await service.get_endpoint_stats()


# ==================== GAMIFICATION ====================

@router.get("/gamification/badges")
async def get_all_badges():
    """Get all available badges."""
    from app.services.gamification import get_gamification_service
    
    service = get_gamification_service()
    return {"badges": service.get_all_badges()}


@router.get("/gamification/user/{user_id}")
async def get_user_gamification(user_id: str):
    """Get user's gamification data."""
    from app.services.gamification import get_gamification_service
    
    service = get_gamification_service()
    
    return {
        "points": service.get_user_points(user_id),
        "level": service.get_user_level(user_id),
        "badges": [
            {
                "type": b.type.value,
                "name": b.name,
                "icon": b.icon,
                "color": b.color
            }
            for b in service.get_user_badges(user_id)
        ]
    }


@router.get("/gamification/leaderboard/installers")
async def get_installer_leaderboard(
    limit: int = Query(10, le=50),
    period: str = Query("month", enum=["week", "month", "year", "all"])
):
    """Get installer leaderboard."""
    from app.services.gamification import get_gamification_service
    
    service = get_gamification_service()
    entries = await service.get_installer_leaderboard(limit, period)
    
    return {
        "period": period,
        "entries": [
            {
                "rank": e.rank,
                "id": e.id,
                "name": e.name,
                "score": e.score,
                "projects": e.projects,
                "rating": e.rating,
                "badges": e.badges,
                "change": e.change
            }
            for e in entries
        ]
    }


@router.get("/gamification/leaderboard/districts")
async def get_district_leaderboard(
    state: Optional[str] = None,
    limit: int = Query(10, le=50)
):
    """Get district leaderboard."""
    from app.services.gamification import get_gamification_service
    
    service = get_gamification_service()
    return {"entries": await service.get_district_leaderboard(state, limit)}


@router.get("/gamification/challenges/{user_id}")
async def get_user_challenges(user_id: str):
    """Get active challenges for user."""
    from app.services.gamification import get_gamification_service
    
    service = get_gamification_service()
    return {"challenges": await service.get_challenges(user_id)}


# ==================== MAINTENANCE CALENDAR ====================

@router.get("/maintenance/schedule/{project_id}")
async def get_maintenance_schedule(
    project_id: int,
    installation_date: str = Query(...),
    years_ahead: int = Query(2, le=5)
):
    """Get maintenance schedule for project."""
    from app.services.maintenance_calendar import get_calendar_service
    
    service = get_calendar_service()
    
    install_date = datetime.fromisoformat(installation_date)
    events = service.generate_maintenance_schedule(
        project_id=project_id,
        project_name=f"Project #{project_id}",
        installation_date=install_date,
        years_ahead=years_ahead
    )
    
    return {
        "project_id": project_id,
        "events": [
            {
                "id": e.id,
                "type": e.maintenance_type.value,
                "title": e.title,
                "description": e.description,
                "scheduled_date": e.scheduled_date.isoformat(),
                "is_completed": e.is_completed
            }
            for e in events
        ]
    }


@router.get("/maintenance/ical/{project_id}")
async def export_maintenance_ical(
    project_id: int,
    installation_date: str = Query(...)
):
    """Export maintenance schedule as iCal."""
    from app.services.maintenance_calendar import get_calendar_service
    
    service = get_calendar_service()
    
    install_date = datetime.fromisoformat(installation_date)
    events = service.generate_maintenance_schedule(
        project_id=project_id,
        project_name=f"Project #{project_id}",
        installation_date=install_date
    )
    
    ical_content = service.export_to_ical(events)
    
    return Response(
        content=ical_content,
        media_type="text/calendar",
        headers={"Content-Disposition": f"attachment; filename=maintenance_{project_id}.ics"}
    )
