"""
RainForge Verification & Audit API Endpoints
Enhanced with fraud detection
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime
import hashlib
import uuid
from app.services.fraud_detector import FraudDetector, VerificationData


router = APIRouter()


# ============== IN-MEMORY STORAGE ==============

_verifications = {}  # id -> verification record
_job_verifications = {}  # job_id -> verification_id


# ============== REQUEST MODELS ==============

class VerificationSubmit(BaseModel):
    job_id: int
    installer_id: int
    photo_url: str
    photo_hash: Optional[str] = None
    geo_lat: float
    geo_lng: float
    expected_lat: float = 28.6139
    expected_lng: float = 77.2090
    notes: Optional[str] = None


class VerificationReview(BaseModel):
    status: str  # approved, rejected
    verifier_notes: Optional[str] = None
    require_rework: bool = False


# ============== ENDPOINTS ==============

@router.post("/submit")
def submit_verification(request: VerificationSubmit):
    """
    Submit verification for a completed installation.
    Runs fraud detection automatically.
    """
    verification_id = f"VER-{uuid.uuid4().hex[:8].upper()}"
    
    # Generate photo hash if not provided (would use actual file hash in production)
    photo_hash = request.photo_hash or hashlib.sha256(request.photo_url.encode()).hexdigest()[:16]
    
    # Create verification data for fraud analysis
    verification_data = VerificationData(
        job_id=request.job_id,
        installer_id=request.installer_id,
        photo_url=request.photo_url,
        photo_hash=photo_hash,
        geo_lat=request.geo_lat,
        geo_lng=request.geo_lng,
        expected_lat=request.expected_lat,
        expected_lng=request.expected_lng,
        timestamp=datetime.utcnow()
    )
    
    # Run fraud detection
    fraud_analysis = FraudDetector.analyze(verification_data)
    
    # Determine initial status based on fraud analysis
    if fraud_analysis["recommendation"] == "auto_approve":
        status = "auto_approved"
    elif fraud_analysis["recommendation"] == "reject":
        status = "flagged"
    else:
        status = "pending_review"
    
    # Store verification
    record = {
        "id": verification_id,
        "job_id": request.job_id,
        "installer_id": request.installer_id,
        "photo_url": request.photo_url,
        "photo_hash": photo_hash,
        "geo_lat": request.geo_lat,
        "geo_lng": request.geo_lng,
        "expected_lat": request.expected_lat,
        "expected_lng": request.expected_lng,
        "geo_distance_m": fraud_analysis["geo_distance_m"],
        "status": status,
        "fraud_analysis": fraud_analysis,
        "notes": request.notes,
        "verifier_notes": None,
        "submitted_at": datetime.utcnow().isoformat(),
        "reviewed_at": None
    }
    
    _verifications[verification_id] = record
    _job_verifications[request.job_id] = verification_id
    
    return {
        "verification_id": verification_id,
        "job_id": request.job_id,
        "status": status,
        "geo_distance_m": round(fraud_analysis["geo_distance_m"], 1),
        "fraud_risk_score": fraud_analysis["risk_score"],
        "fraud_flags": fraud_analysis["flags"],
        "recommendation": fraud_analysis["recommendation"],
        "message": f"Verification submitted - Status: {status}"
    }


@router.get("/pending")
def get_pending_verifications():
    """Get list of verifications pending review."""
    pending = [
        v for v in _verifications.values()
        if v["status"] in ["pending_review", "flagged"]
    ]
    
    # Sort by risk score (highest first)
    pending.sort(key=lambda x: x["fraud_analysis"]["risk_score"], reverse=True)
    
    return {
        "total": len(pending),
        "verifications": [
            {
                "id": v["id"],
                "job_id": v["job_id"],
                "installer_id": v["installer_id"],
                "status": v["status"],
                "risk_score": v["fraud_analysis"]["risk_score"],
                "flags": v["fraud_analysis"]["flags"],
                "geo_distance_m": v["geo_distance_m"],
                "submitted_at": v["submitted_at"]
            }
            for v in pending
        ]
    }


@router.get("/{verification_id}")
def get_verification(verification_id: str):
    """Get verification details."""
    if verification_id not in _verifications:
        raise HTTPException(status_code=404, detail="Verification not found")
    return _verifications[verification_id]


@router.get("/job/{job_id}")
def get_verification_for_job(job_id: int):
    """Get verification for a specific job."""
    verification_id = _job_verifications.get(job_id)
    if not verification_id:
        raise HTTPException(status_code=404, detail=f"No verification for job {job_id}")
    return _verifications[verification_id]


@router.post("/{verification_id}/approve")
def approve_verification(verification_id: str, review: VerificationReview = None):
    """Approve a verification (admin action)."""
    if verification_id not in _verifications:
        raise HTTPException(status_code=404, detail="Verification not found")
    
    record = _verifications[verification_id]
    
    if record["status"] not in ["pending_review", "flagged", "auto_approved"]:
        raise HTTPException(status_code=400, detail=f"Cannot approve - status: {record['status']}")
    
    record["status"] = "approved"
    record["reviewed_at"] = datetime.utcnow().isoformat()
    if review:
        record["verifier_notes"] = review.verifier_notes
    
    return {
        "verification_id": verification_id,
        "status": "approved",
        "message": "Verification approved"
    }


@router.post("/{verification_id}/reject")
def reject_verification(verification_id: str, review: VerificationReview):
    """Reject a verification (admin action)."""
    if verification_id not in _verifications:
        raise HTTPException(status_code=404, detail="Verification not found")
    
    record = _verifications[verification_id]
    
    record["status"] = "rejected" if not review.require_rework else "rework_required"
    record["reviewed_at"] = datetime.utcnow().isoformat()
    record["verifier_notes"] = review.verifier_notes
    
    return {
        "verification_id": verification_id,
        "status": record["status"],
        "require_rework": review.require_rework,
        "message": "Verification rejected" + (" - rework required" if review.require_rework else "")
    }


@router.get("/stats/summary")
def get_verification_stats():
    """Get verification statistics."""
    total = len(_verifications)
    approved = sum(1 for v in _verifications.values() if v["status"] == "approved")
    rejected = sum(1 for v in _verifications.values() if v["status"] == "rejected")
    flagged = sum(1 for v in _verifications.values() if v["status"] == "flagged")
    pending = sum(1 for v in _verifications.values() if v["status"] == "pending_review")
    
    avg_geo_distance = sum(v["geo_distance_m"] for v in _verifications.values()) / max(1, total)
    
    return {
        "total": total,
        "approved": approved,
        "rejected": rejected,
        "flagged": flagged,
        "pending_review": pending,
        "approval_rate": round(approved / max(1, total) * 100, 1),
        "average_geo_distance_m": round(avg_geo_distance, 1)
    }


@router.post("/demo/seed")
def seed_demo_verifications():
    """Seed demo verification data."""
    global _verifications, _job_verifications
    _verifications = {}
    _job_verifications = {}
    FraudDetector.clear_demo_data()
    
    # Create demo verifications
    demo_data = [
        {"job_id": 101, "installer_id": 1, "geo_offset": 0.0001, "status": "normal"},
        {"job_id": 102, "installer_id": 2, "geo_offset": 0.0002, "status": "normal"},
        {"job_id": 103, "installer_id": 3, "geo_offset": 0.005, "status": "geo_mismatch"},
        {"job_id": 104, "installer_id": 1, "geo_offset": 0.0001, "status": "photo_reuse"},
    ]
    
    results = []
    for d in demo_data:
        request = VerificationSubmit(
            job_id=d["job_id"],
            installer_id=d["installer_id"],
            photo_url=f"https://demo.com/photo_{d['job_id']}.jpg" if d["status"] != "photo_reuse" else "https://demo.com/photo_101.jpg",
            geo_lat=28.6139 + d["geo_offset"],
            geo_lng=77.2090 + d["geo_offset"],
            expected_lat=28.6139,
            expected_lng=77.2090
        )
        result = submit_verification(request)
        results.append(result)
    
    return {"seeded": len(results), "verifications": results}
