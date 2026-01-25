"""
RainForge Verification API Endpoints
Installation verification workflow.
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime
from typing import Optional
from app.schemas.schemas import VerificationRequest, VerificationStatus

router = APIRouter()

# In-memory store for demo (use DB in production)
VERIFICATION_RECORDS = {}


@router.post("/{project_id}/submit")
async def submit_verification(project_id: int, request: VerificationRequest):
    """
    Submit verification record (photo, geo-tag).
    """
    record = {
        "id": len(VERIFICATION_RECORDS) + 1,
        "project_id": project_id,
        "photo_url": request.photo_url,
        "geo_lat": request.geo_lat,
        "geo_lng": request.geo_lng,
        "notes": request.notes,
        "installer_id": request.installer_id,
        "timestamp": datetime.utcnow().isoformat(),
        "status": VerificationStatus.PENDING.value
    }
    
    VERIFICATION_RECORDS[project_id] = record
    
    return {
        "message": "Verification submitted successfully",
        "record": record
    }


@router.get("/{project_id}")
async def get_verification_status(project_id: int):
    """
    Get verification status for a project.
    """
    if project_id in VERIFICATION_RECORDS:
        return VERIFICATION_RECORDS[project_id]
    
    # Return pending status if no record
    return {
        "project_id": project_id,
        "status": "not_submitted",
        "message": "No verification record found"
    }


@router.post("/{project_id}/approve")
async def approve_verification(project_id: int, admin_id: int = 1):
    """
    Approve verification (admin only).
    """
    if project_id not in VERIFICATION_RECORDS:
        raise HTTPException(status_code=404, detail="Verification record not found")
    
    VERIFICATION_RECORDS[project_id]["status"] = VerificationStatus.VERIFIED.value
    VERIFICATION_RECORDS[project_id]["verified_by"] = admin_id
    VERIFICATION_RECORDS[project_id]["verified_at"] = datetime.utcnow().isoformat()
    
    return {
        "message": "Verification approved",
        "record": VERIFICATION_RECORDS[project_id]
    }


@router.post("/{project_id}/reject")
async def reject_verification(project_id: int, reason: str = "Insufficient evidence"):
    """
    Reject verification (admin only).
    """
    if project_id not in VERIFICATION_RECORDS:
        raise HTTPException(status_code=404, detail="Verification record not found")
    
    VERIFICATION_RECORDS[project_id]["status"] = VerificationStatus.REJECTED.value
    VERIFICATION_RECORDS[project_id]["rejection_reason"] = reason
    
    return {
        "message": "Verification rejected",
        "record": VERIFICATION_RECORDS[project_id]
    }


@router.post("/{project_id}/mark-installed")
async def mark_installed(project_id: int):
    """
    Mark project as installed after verification.
    """
    if project_id not in VERIFICATION_RECORDS:
        VERIFICATION_RECORDS[project_id] = {"project_id": project_id}
    
    VERIFICATION_RECORDS[project_id]["status"] = VerificationStatus.INSTALLED.value
    VERIFICATION_RECORDS[project_id]["installed_at"] = datetime.utcnow().isoformat()
    
    return {
        "message": "Project marked as installed",
        "record": VERIFICATION_RECORDS[project_id]
    }


@router.get("/")
async def list_pending_verifications():
    """
    List all pending verifications (for admin dashboard).
    """
    pending = [
        r for r in VERIFICATION_RECORDS.values() 
        if r.get("status") == VerificationStatus.PENDING.value
    ]
    return {"pending_count": len(pending), "records": pending}
