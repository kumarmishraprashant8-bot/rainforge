"""
RainForge P0 Verification API - Enhanced with pHash fraud detection
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime
import uuid
import os
import shutil

from app.services.fraud_detector import get_fraud_detector
from app.models.database import get_db, Verification, Assessment


router = APIRouter()

# Upload directory
UPLOAD_DIR = "backend/uploads/verifications"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/verify")
async def submit_verification(
    project_id: int = Form(...),
    installer_id: int = Form(...),
    milestone: str = Form("installation_complete"),
    notes: Optional[str] = Form(None),
    photo: UploadFile = File(...),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    P0 Verification Endpoint - Accept photo upload with fraud detection.
    
    Steps:
    1. Save uploaded photo
    2. Extract EXIF GPS data
    3. Calculate pHash
    4. Run comprehensive fraud detection
    5. Store verification record
    6. Return verification ID + fraud flags
    """
    try:
        # Get project details for geo-validation
        assessment = db.query(Assessment).filter(Assessment.id == project_id).first()
        if not assessment:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Save uploaded photo
        verification_id = str(uuid.uuid4())
        file_extension = os.path.splitext(photo.filename)[1]
        filename = f"{verification_id}{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(photo.file, buffer)
        
        # Run fraud detection
        fraud_detector = get_fraud_detector()
        fraud_result = fraud_detector.analyze_verification(
            image_path=file_path,
            photo_id=verification_id,
            project_lat=assessment.lat or 28.6,
            project_lng=assessment.lng or 77.2,
            installer_id=installer_id
        )
        
        # Determine status
        if fraud_result["recommendation"] == "auto_approve":
            status = "approved"
        elif fraud_result["recommendation"] == "reject":
            status = "rejected"
        else:
            status = "pending"
        
        # Store verification in database
        verification = Verification(
            project_id=project_id,
            submission_type=milestone,
            status=status,
            submitted_by=None,  # Would use current_user in production
            fraud_score=fraud_result["fraud_score"],
            metadata={
                "phash": fraud_result["details"]["phash"],
                "fraud_flags": fraud_result["flags"],
                "recommendation": fraud_result["recommendation"],
                "geo_distance_m": fraud_result["details"].get("geo_distance_m"),
                "has_exif": fraud_result["details"]["has_exif"],
                "has_gps": fraud_result["details"]["has_gps"],
                "is_duplicate": fraud_result["details"]["is_duplicate"]
            },
            notes=notes
        )
        
        db.add(verification)
        db.commit()
        db.refresh(verification)
        
        return {
            "verification_id": verification.id,
            "status": status,
            "fraud_score": fraud_result["fraud_score"],
            "flags": fraud_result["flags"],
            "recommendation": fraud_result["recommendation"],
            "geo_distance_m": fraud_result["details"].get("geo_distance_m"),
            "requires_manual_review": status == "pending",
            "audit_trail": [
                {
                    "timestamp": datetime.now().isoformat(),
                    "action": "verification_submitted",
                    "actor": f"installer_{installer_id}",
                    "fraud_score": fraud_result["fraud_score"]
                }
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Verification failed: {str(e)}")


@router.get("/admin/verifications/pending")
def get_pending_verifications(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    """
    Get all verifications pending manual review.
    """
    verifications = db.query(Verification).filter(
        Verification.status == "pending"
    ).order_by(Verification.submitted_at.desc()).all()
    
    return [
        {
            "id": v.id,
            "project_id": v.project_id,
            "submitted_at": v.submitted_at.isoformat() if v.submitted_at else None,
            "fraud_score": v.fraud_score,
            "flags": v.metadata.get("fraud_flags", []) if v.metadata else [],
            "geo_distance_m": v.metadata.get("geo_distance_m") if v.metadata else None
        }
        for v in verifications
    ]


@router.post("/admin/verifications/{verification_id}/approve")
def approve_verification(
    verification_id: int,
    admin_notes: Optional[str] = None,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Admin endpoint to manually approve a verification.
    """
    verification = db.query(Verification).filter(
        Verification.id == verification_id
    ).first()
    
    if not verification:
        raise HTTPException(status_code=404, detail="Verification not found")
    
    verification.status = "approved"
    verification.reviewed_at = datetime.now()
    verification.reviewed_by = None  # Would use current_admin in production
    
    if admin_notes:
        if not verification.metadata:
            verification.metadata = {}
        verification.metadata["admin_notes"] = admin_notes
    
    db.commit()
    
    return {
        "verification_id": verification_id,
        "status": "approved",
        "reviewed_at": verification.reviewed_at.isoformat()
    }


@router.post("/admin/verifications/{verification_id}/reject")
def reject_verification(
    verification_id: int,
    rejection_reason: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Admin endpoint to reject a verification.
    """
    verification = db.query(Verification).filter(
        Verification.id == verification_id
    ).first()
    
    if not verification:
        raise HTTPException(status_code=404, detail="Verification not found")
    
    verification.status = "rejected"
    verification.reviewed_at = datetime.now()
    verification.reviewed_by = None  # Would use current_admin in production
    verification.rejection_reason = rejection_reason
    
    db.commit()
    
    return {
        "verification_id": verification_id,
        "status": "rejected",
        "rejection_reason": rejection_reason,
        "reviewed_at": verification.reviewed_at.isoformat()
    }


# ============== WOW MOMENT #1: FRAUD INSPECTOR ENDPOINT ==============

@router.get("/verify/{verification_id}/inspect")
def inspect_verification(
    verification_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    🔥 WOW MOMENT #1: Instant Fraud Exposure
    
    Returns comprehensive fraud analysis for a verification:
    - EXIF metadata
    - pHash matches (duplicates)
    - GPS distance from expected location
    - Risk score and recommendation
    """
    verification = db.query(Verification).filter(
        Verification.id == verification_id
    ).first()
    
    if not verification:
        raise HTTPException(status_code=404, detail="Verification not found")
    
    # Get associated assessment for location context
    assessment = db.query(Assessment).filter(
        Assessment.id == verification.project_id
    ).first()
    
    metadata = verification.metadata or {}
    
    # Build EXIF block
    exif_data = metadata.get("exif_data", {})
    exif = {
        "lat": exif_data.get("latitude"),
        "lng": exif_data.get("longitude"),
        "timestamp": exif_data.get("timestamp"),
        "software": exif_data.get("software"),
        "camera": exif_data.get("camera_make", "") + " " + exif_data.get("camera_model", ""),
        "has_gps": metadata.get("has_gps", False),
        "has_exif": metadata.get("has_exif", False)
    }
    
    # pHash matches (duplicates)
    phash_matches = []
    if metadata.get("is_duplicate"):
        # Find the matching verification
        match_id = metadata.get("duplicate_match_id")
        if match_id:
            phash_matches.append({
                "verification_id": match_id,
                "distance": metadata.get("hamming_distance", 0)
            })
    
    # GPS distance
    gps_distance_m = metadata.get("geo_distance_m")
    
    # Determine recommendation based on score
    fraud_score = verification.fraud_score or 0
    if fraud_score >= 0.8:
        recommendation = "REJECT"
    elif fraud_score >= 0.5:
        recommendation = "MANUAL_REVIEW"
    elif fraud_score >= 0.3:
        recommendation = "FLAG"
    else:
        recommendation = "AUTO_APPROVE"
    
    # Extract flags
    flags = metadata.get("fraud_flags", [])
    
    # Clean flag descriptions for UI
    flag_types = []
    for flag in flags:
        if "DUPLICATE" in flag.upper() or "REUSE" in flag.upper():
            flag_types.append("DUPLICATE_PHOTO")
        elif "GEO" in flag.upper() or "MISMATCH" in flag.upper():
            flag_types.append("GPS_MISMATCH")
        elif "EXIF" in flag.upper() or "MISSING" in flag.upper():
            flag_types.append("EXIF_MISSING")
        elif "SOFTWARE" in flag.upper() or "MANIPULATION" in flag.upper():
            flag_types.append("SOFTWARE_MANIPULATION")
        elif "TIMESTAMP" in flag.upper():
            flag_types.append("TIMESTAMP_ANOMALY")
    
    # Unique flags
    flag_types = list(set(flag_types))
    
    return {
        "verification_id": verification_id,
        "project_id": verification.project_id,
        "risk_score": round(fraud_score, 2),
        "flags": flag_types,
        "flags_detailed": flags,
        "exif": exif,
        "phash": metadata.get("phash", ""),
        "phash_matches": phash_matches,
        "gps_distance_m": round(gps_distance_m, 1) if gps_distance_m else None,
        "expected_location": {
            "lat": assessment.lat if assessment else None,
            "lng": assessment.lng if assessment else None
        },
        "recommendation": recommendation,
        "status": verification.status,
        "submitted_at": verification.submitted_at.isoformat() if verification.submitted_at else None,
        "fraud_detected": fraud_score >= 0.5,
        "payment_blocked": fraud_score >= 0.5  # For WOW Moment #2
    }


@router.get("/stats/summary")
def get_verification_stats(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Get verification statistics."""
    from sqlalchemy import func
    
    total = db.query(Verification).count()
    approved = db.query(Verification).filter(Verification.status == "approved").count()
    rejected = db.query(Verification).filter(Verification.status == "rejected").count()
    pending = db.query(Verification).filter(Verification.status == "pending").count()
    
    # Count fraud prevented (rejected + high score pending)
    fraud_prevented = db.query(Verification).filter(
        Verification.fraud_score >= 0.5
    ).count()
    
    return {
        "total": total,
        "approved": approved,
        "rejected": rejected,
        "pending": pending,
        "fraud_prevented": fraud_prevented,
        "approval_rate": round(approved / max(1, total) * 100, 1)
    }


# Demo data stores for in-memory verification (for demo mode)
_verifications: Dict[str, Dict] = {}
_job_verifications: Dict[int, str] = {}


@router.post("/demo/seed")
def seed_demo_verifications(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Seed demo verification data with fraud scenarios."""
    from app.services.fraud_detector import FraudDetector
    
    # Clear existing demo data
    FraudDetector._demo_history = []
    FraudDetector._phash_database = {}
    
    # Create 6 demo verifications with different fraud scenarios
    demo_scenarios = [
        {"type": "genuine", "fraud_score": 0.05, "flags": []},
        {"type": "gps_mismatch", "fraud_score": 0.65, "flags": ["GEO_MISMATCH: Photo taken 487m from site"]},
        {"type": "duplicate", "fraud_score": 0.75, "flags": ["DUPLICATE_PHOTO: Matches photo V-001"]},
        {"type": "no_exif", "fraud_score": 0.35, "flags": ["EXIF_MISSING: No EXIF metadata found"]},
        {"type": "photoshop", "fraud_score": 0.55, "flags": ["SOFTWARE_MANIPULATION: Edited with Adobe Photoshop"]},
        {"type": "multi_fraud", "fraud_score": 0.92, "flags": ["DUPLICATE_PHOTO", "GPS_MISMATCH", "TIMESTAMP_ANOMALY"]}
    ]
    
    created = []
    for i, scenario in enumerate(demo_scenarios):
        verification = Verification(
            project_id=1,  # Link to first assessment
            submission_type="installation_complete",
            status="rejected" if scenario["fraud_score"] >= 0.8 else ("pending" if scenario["fraud_score"] >= 0.3 else "approved"),
            fraud_score=scenario["fraud_score"],
            metadata={
                "fraud_flags": scenario["flags"],
                "scenario_type": scenario["type"],
                "phash": f"phash_{scenario['type']}",
                "has_exif": scenario["type"] != "no_exif",
                "has_gps": scenario["type"] not in ["no_exif", "gps_mismatch"],
                "is_duplicate": "duplicate" in scenario["type"],
                "geo_distance_m": 487.3 if scenario["type"] == "gps_mismatch" else 12.5
            }
        )
        db.add(verification)
        created.append(scenario["type"])
    
    db.commit()
    
    return {
        "seeded": len(created),
        "scenarios": created,
        "message": "Demo verifications seeded with fraud scenarios"
    }

