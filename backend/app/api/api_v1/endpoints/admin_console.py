"""
RainForge Admin Console API
Search, filter, bulk actions for administrators
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from app.models.database import (
    get_db, Assessment, Job, Verification, Installer, Escrow, AuditLog,
    AssessmentStatus, JobStatus, VerificationStatus, EscrowStatus
)

router = APIRouter(prefix="/admin", tags=["Admin"])


# ==================== SCHEMAS ====================

class BulkActionRequest(BaseModel):
    action: str = Field(..., pattern="^(approve|reject|flag|reassign|cancel)$")
    entity_type: str = Field(..., pattern="^(verification|job|assessment|escrow)$")
    entity_ids: List[str]
    reason: Optional[str] = None
    reassign_to: Optional[int] = None  # For reassign action


class AdminSearchFilters(BaseModel):
    status: Optional[str] = None
    ward_id: Optional[str] = None
    installer_id: Optional[int] = None
    min_fraud_score: Optional[float] = None
    max_fraud_score: Optional[float] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    min_cost: Optional[float] = None
    max_cost: Optional[float] = None


# ==================== DASHBOARD ====================

@router.get("/dashboard")
async def admin_dashboard(db: Session = Depends(get_db)):
    """
    Admin overview dashboard with key metrics.
    """
    
    now = datetime.utcnow()
    last_24h = now - timedelta(hours=24)
    last_7d = now - timedelta(days=7)
    
    # Counts
    total_assessments = db.query(Assessment).count()
    pending_verifications = db.query(Verification).filter(
        Verification.status == VerificationStatus.PENDING
    ).count()
    flagged_verifications = db.query(Verification).filter(
        Verification.status == VerificationStatus.FRAUD_FLAGGED
    ).count()
    active_jobs = db.query(Job).filter(
        Job.status.in_([JobStatus.PENDING, JobStatus.ALLOCATED, JobStatus.IN_PROGRESS])
    ).count()
    
    # Recent activity
    new_assessments_24h = db.query(Assessment).filter(
        Assessment.created_at >= last_24h
    ).count()
    completed_jobs_7d = db.query(Job).filter(
        Job.status == JobStatus.COMPLETED,
        Job.completed_at >= last_7d
    ).count()
    
    # Fraud stats
    high_risk_count = db.query(Verification).filter(
        Verification.fraud_score >= 0.7
    ).count()
    
    # Financial
    total_escrow = db.query(func.sum(Escrow.total_amount_inr)).scalar() or 0
    released_escrow = db.query(Escrow).filter(
        Escrow.status == EscrowStatus.FULLY_RELEASED
    ).count()
    
    return {
        "overview": {
            "total_assessments": total_assessments,
            "active_jobs": active_jobs,
            "pending_verifications": pending_verifications,
            "flagged_verifications": flagged_verifications
        },
        "activity_24h": {
            "new_assessments": new_assessments_24h,
            "verifications_submitted": db.query(Verification).filter(
                Verification.created_at >= last_24h
            ).count()
        },
        "activity_7d": {
            "completed_jobs": completed_jobs_7d,
            "total_capture_liters": db.query(
                func.sum(Assessment.annual_yield_liters)
            ).filter(Assessment.created_at >= last_7d).scalar() or 0
        },
        "fraud_metrics": {
            "high_risk_verifications": high_risk_count,
            "pending_review": pending_verifications,
            "flagged_rate_pct": round(
                (flagged_verifications / max(1, total_assessments)) * 100, 1
            )
        },
        "financial": {
            "total_escrow_inr": total_escrow,
            "escrows_released": released_escrow
        },
        "timestamp": now.isoformat()
    }


# ==================== SEARCH ====================

@router.get("/projects")
async def search_projects(
    q: Optional[str] = Query(None, description="Search query"),
    status: Optional[str] = Query(None),
    ward_id: Optional[str] = Query(None),
    installer_id: Optional[int] = Query(None),
    min_fraud_score: Optional[float] = Query(None),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    sort_by: str = Query("created_at", pattern="^(created_at|fraud_score|cost|status)$"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    Search and filter projects with advanced options.
    """
    
    query = db.query(Assessment)
    
    # Text search
    if q:
        query = query.filter(or_(
            Assessment.site_id.ilike(f"%{q}%"),
            Assessment.address.ilike(f"%{q}%"),
            Assessment.city.ilike(f"%{q}%")
        ))
    
    # Status filter
    if status:
        try:
            status_enum = AssessmentStatus(status)
            query = query.filter(Assessment.status == status_enum)
        except:
            pass
    
    # Date range
    if date_from:
        query = query.filter(Assessment.created_at >= date_from)
    if date_to:
        query = query.filter(Assessment.created_at <= date_to)
    
    # Sorting
    if sort_order == "desc":
        query = query.order_by(getattr(Assessment, sort_by).desc())
    else:
        query = query.order_by(getattr(Assessment, sort_by).asc())
    
    # Pagination
    total = query.count()
    results = query.offset(offset).limit(limit).all()
    
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "results": [
            {
                "assessment_id": a.assessment_id,
                "site_id": a.site_id,
                "address": a.address,
                "city": a.city,
                "state": a.state,
                "status": a.status.value if a.status else None,
                "annual_yield_liters": a.annual_yield_liters,
                "net_cost_inr": a.net_cost_inr,
                "created_at": a.created_at.isoformat() if a.created_at else None
            }
            for a in results
        ]
    }


@router.get("/verifications")
async def search_verifications(
    status: Optional[str] = Query(None),
    min_fraud_score: Optional[float] = Query(None),
    max_fraud_score: Optional[float] = Query(None),
    installer_id: Optional[int] = Query(None),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    Search verifications with fraud score filtering.
    """
    
    query = db.query(Verification)
    
    if status:
        try:
            status_enum = VerificationStatus(status)
            query = query.filter(Verification.status == status_enum)
        except:
            pass
    
    if min_fraud_score is not None:
        query = query.filter(Verification.fraud_score >= min_fraud_score)
    
    if max_fraud_score is not None:
        query = query.filter(Verification.fraud_score <= max_fraud_score)
    
    query = query.order_by(Verification.fraud_score.desc())
    
    total = query.count()
    results = query.offset(offset).limit(limit).all()
    
    return {
        "total": total,
        "results": [
            {
                "verification_id": v.verification_id,
                "job_id": v.job_id,
                "status": v.status.value if v.status else None,
                "fraud_score": v.fraud_score,
                "fraud_flags": v.fraud_flags,
                "geo_distance_m": v.geo_distance_m,
                "created_at": v.created_at.isoformat() if v.created_at else None
            }
            for v in results
        ]
    }


# ==================== BULK ACTIONS ====================

@router.post("/bulk-action")
async def bulk_action(request: BulkActionRequest, db: Session = Depends(get_db)):
    """
    Perform bulk actions on multiple entities.
    Supported actions: approve, reject, flag, reassign, cancel
    """
    
    results = []
    
    for entity_id in request.entity_ids:
        try:
            if request.entity_type == "verification":
                result = _process_verification_action(
                    db, entity_id, request.action, request.reason
                )
            elif request.entity_type == "job":
                result = _process_job_action(
                    db, entity_id, request.action, request.reason, request.reassign_to
                )
            elif request.entity_type == "escrow":
                result = _process_escrow_action(
                    db, entity_id, request.action, request.reason
                )
            else:
                result = {"entity_id": entity_id, "success": False, "error": "Unknown entity type"}
            
            results.append(result)
            
        except Exception as e:
            results.append({"entity_id": entity_id, "success": False, "error": str(e)})
    
    db.commit()
    
    return {
        "action": request.action,
        "entity_type": request.entity_type,
        "total_processed": len(results),
        "successful": sum(1 for r in results if r.get("success")),
        "failed": sum(1 for r in results if not r.get("success")),
        "results": results
    }


def _process_verification_action(db: Session, ver_id: str, action: str, reason: Optional[str]) -> Dict:
    """Process verification bulk action."""
    
    verification = db.query(Verification).filter(
        Verification.verification_id == ver_id
    ).first()
    
    if not verification:
        return {"entity_id": ver_id, "success": False, "error": "Not found"}
    
    if action == "approve":
        verification.status = VerificationStatus.VERIFIED
    elif action == "reject":
        verification.status = VerificationStatus.REJECTED
    elif action == "flag":
        verification.status = VerificationStatus.FRAUD_FLAGGED
    else:
        return {"entity_id": ver_id, "success": False, "error": f"Invalid action: {action}"}
    
    # Create audit log
    audit = AuditLog(
        entity_type="verification",
        entity_id=ver_id,
        action=f"bulk_{action}",
        actor_type="admin",
        details={"reason": reason}
    )
    db.add(audit)
    
    return {"entity_id": ver_id, "success": True, "new_status": verification.status.value}


def _process_job_action(db: Session, job_id: str, action: str, reason: Optional[str], reassign_to: Optional[int]) -> Dict:
    """Process job bulk action."""
    
    job = db.query(Job).filter(Job.job_id == job_id).first()
    
    if not job:
        return {"entity_id": job_id, "success": False, "error": "Not found"}
    
    if action == "cancel":
        job.status = JobStatus.CANCELLED
    elif action == "reassign" and reassign_to:
        job.installer_id = reassign_to
        job.status = JobStatus.ALLOCATED
    else:
        return {"entity_id": job_id, "success": False, "error": f"Invalid action: {action}"}
    
    return {"entity_id": job_id, "success": True, "new_status": job.status.value}


def _process_escrow_action(db: Session, escrow_id: str, action: str, reason: Optional[str]) -> Dict:
    """Process escrow bulk action."""
    
    escrow = db.query(Escrow).filter(Escrow.escrow_id == escrow_id).first()
    
    if not escrow:
        return {"entity_id": escrow_id, "success": False, "error": "Not found"}
    
    if action == "approve":
        escrow.status = EscrowStatus.FULLY_RELEASED
    elif action == "flag":
        escrow.status = EscrowStatus.DISPUTED
    else:
        return {"entity_id": escrow_id, "success": False, "error": f"Invalid action: {action}"}
    
    return {"entity_id": escrow_id, "success": True, "new_status": escrow.status.value}


# ==================== AUDIT LOG ====================

@router.get("/audit-log")
async def get_audit_log(
    entity_type: Optional[str] = Query(None),
    entity_id: Optional[str] = Query(None),
    action: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Get audit log entries for compliance and tracking.
    """
    
    query = db.query(AuditLog)
    
    if entity_type:
        query = query.filter(AuditLog.entity_type == entity_type)
    if entity_id:
        query = query.filter(AuditLog.entity_id == entity_id)
    if action:
        query = query.filter(AuditLog.action.ilike(f"%{action}%"))
    
    query = query.order_by(AuditLog.created_at.desc()).limit(limit)
    logs = query.all()
    
    return {
        "total": len(logs),
        "logs": [
            {
                "id": log.id,
                "entity_type": log.entity_type,
                "entity_id": log.entity_id,
                "action": log.action,
                "actor_type": log.actor_type,
                "actor_id": log.actor_id,
                "details": log.details,
                "created_at": log.created_at.isoformat() if log.created_at else None
            }
            for log in logs
        ]
    }


# ==================== INSTALLER MANAGEMENT ====================

@router.get("/installers")
async def admin_list_installers(
    include_blacklisted: bool = Query(False),
    min_rpi: Optional[float] = Query(None),
    db: Session = Depends(get_db)
):
    """
    List all installers with admin details.
    """
    
    query = db.query(Installer)
    
    if not include_blacklisted:
        query = query.filter(Installer.is_blacklisted == False)
    
    if min_rpi:
        query = query.filter(Installer.rpi_score >= min_rpi)
    
    installers = query.order_by(Installer.rpi_score.desc()).all()
    
    return {
        "total": len(installers),
        "installers": [
            {
                "id": i.id,
                "name": i.name,
                "company": i.company,
                "email": i.email,
                "phone": i.phone,
                "rpi_score": i.rpi_score,
                "is_active": i.is_active,
                "is_blacklisted": i.is_blacklisted,
                "jobs_completed": i.jobs_completed,
                "capacity_available": i.capacity_available,
                "capacity_max": i.capacity_max,
                "sla_compliance_pct": i.sla_compliance_pct,
                "created_at": i.created_at.isoformat() if i.created_at else None
            }
            for i in installers
        ]
    }


@router.post("/installers/{installer_id}/blacklist")
async def blacklist_installer(
    installer_id: int,
    reason: str = Query(...),
    db: Session = Depends(get_db)
):
    """
    Blacklist an installer for fraud or poor performance.
    """
    
    installer = db.query(Installer).filter(Installer.id == installer_id).first()
    if not installer:
        raise HTTPException(status_code=404, detail="Installer not found")
    
    installer.is_blacklisted = True
    installer.is_active = False
    
    audit = AuditLog(
        entity_type="installer",
        entity_id=str(installer_id),
        action="blacklisted",
        actor_type="admin",
        details={"reason": reason}
    )
    db.add(audit)
    db.commit()
    
    return {
        "installer_id": installer_id,
        "status": "blacklisted",
        "reason": reason
    }


# ==================== REPORTS ====================

@router.get("/reports/fraud-summary")
async def fraud_summary_report(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """
    Generate fraud detection summary report.
    """
    
    cutoff = datetime.utcnow() - timedelta(days=days)
    
    verifications = db.query(Verification).filter(
        Verification.created_at >= cutoff
    ).all()
    
    # Calculate stats
    total = len(verifications)
    auto_approved = sum(1 for v in verifications if v.status == VerificationStatus.AUTO_APPROVED)
    manual_review = sum(1 for v in verifications if v.status == VerificationStatus.MANUAL_REVIEW)
    flagged = sum(1 for v in verifications if v.status == VerificationStatus.FRAUD_FLAGGED)
    
    # Fraud flag frequency
    all_flags = []
    for v in verifications:
        if v.fraud_flags:
            all_flags.extend(v.fraud_flags)
    
    flag_counts = {}
    for flag in all_flags:
        flag_counts[flag] = flag_counts.get(flag, 0) + 1
    
    return {
        "period_days": days,
        "total_verifications": total,
        "auto_approved": auto_approved,
        "auto_approve_rate_pct": round((auto_approved / max(1, total)) * 100, 1),
        "manual_review": manual_review,
        "flagged": flagged,
        "flagged_rate_pct": round((flagged / max(1, total)) * 100, 1),
        "avg_fraud_score": round(
            sum(v.fraud_score or 0 for v in verifications) / max(1, total), 2
        ),
        "flag_frequency": dict(sorted(
            flag_counts.items(), key=lambda x: x[1], reverse=True
        )[:10]),
        "report_generated": datetime.utcnow().isoformat()
    }
