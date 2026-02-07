"""
RainForge P0 Payment & Escrow API Endpoints
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime
from app.services.payment_adapter import PaymentAdapter, MilestoneStatus
from app.models.database import get_db, Escrow


router = APIRouter()


# ============== REQUEST MODELS ==============

class PaymentCreate(BaseModel):
    job_id: int
    total_amount: float
    milestones: Optional[List[dict]] = None  # Custom milestone config


class MilestoneAction(BaseModel):
    notes: Optional[str] = None


# ============== ENDPOINTS ==============

@router.post("")
def create_payment(request: PaymentCreate):
    """
    Create a payment with milestone structure for a job.
    """
    try:
        payment = PaymentAdapter.create_payment(
            job_id=request.job_id,
            total_amount=request.total_amount,
            milestone_config=request.milestones
        )
        return {
            "payment_id": payment.id,
            "job_id": payment.job_id,
            "total_amount": payment.total_amount,
            "status": payment.status.value,
            "milestones": [
                {
                    "id": m.id,
                    "name": m.name,
                    "amount": m.amount,
                    "sequence": m.sequence,
                    "status": m.status.value
                }
                for m in payment.milestones
            ],
            "message": "Payment created with milestones"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{payment_id}")
def get_payment(payment_id: str):
    """Get payment details with milestones."""
    try:
        summary = PaymentAdapter.get_payment_summary(payment_id)
        return summary
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/job/{job_id}")
def get_payment_for_job(job_id: int):
    """Get payment for a specific job."""
    payment = PaymentAdapter.get_payment_for_job(job_id)
    if not payment:
        raise HTTPException(status_code=404, detail=f"No payment found for job {job_id}")
    return PaymentAdapter.get_payment_summary(payment.id)


@router.post("/{payment_id}/escrow")
def capture_to_escrow(payment_id: str):
    """
    Capture payment amount to escrow.
    Mock: Always succeeds.
    """
    try:
        result = PaymentAdapter.capture_to_escrow(payment_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{payment_id}/milestones/{milestone_id}/complete")
def complete_milestone(payment_id: str, milestone_id: str, action: MilestoneAction = None):
    """
    Mark a milestone as completed by installer.
    """
    try:
        result = PaymentAdapter.complete_milestone(payment_id, milestone_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{payment_id}/milestones/{milestone_id}/verify")
def verify_milestone(payment_id: str, milestone_id: str, action: MilestoneAction = None):
    """
    Verify a completed milestone (admin action).
    """
    try:
        result = PaymentAdapter.verify_milestone(payment_id, milestone_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{payment_id}/milestones/{milestone_id}/release")
def release_milestone(payment_id: str, milestone_id: str):
    """
    Release funds for a verified milestone.
    """
    try:
        result = PaymentAdapter.release_milestone(payment_id, milestone_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{payment_id}/refund")
def refund_payment(payment_id: str, reason: str = ""):
    """
    Refund remaining escrow to payer.
    """
    try:
        result = PaymentAdapter.refund_to_payer(payment_id, reason)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/demo/workflow")
def demo_payment_workflow():
    """
    Run demo payment workflow for testing.
    """
    PaymentAdapter.clear_demo_data()
    
    # Create payment
    payment = PaymentAdapter.create_payment(job_id=999, total_amount=96000)
    
    # Capture to escrow
    PaymentAdapter.capture_to_escrow(payment.id)
    
    # Complete and release first two milestones
    for m in payment.milestones[:2]:
        PaymentAdapter.complete_milestone(payment.id, m.id)
        PaymentAdapter.verify_milestone(payment.id, m.id)
        PaymentAdapter.release_milestone(payment.id, m.id)
    
    summary = PaymentAdapter.get_payment_summary(payment.id)
    
    return {
        "message": "Demo workflow completed",
        "payment": summary
    }


# ============== P0 SIMPLIFIED ESCROW ENDPOINTS ==============

@router.post("/escrow/{job_id}/create")
def create_escrow_p0(
    job_id: int,
    total_amount: float,
    custom_milestones: Optional[List[Dict]] = None,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    P0: Create escrow with default or custom milestones.
    Default: 10% Design, 70% Installation, 20% Verification
    """
    # Default milestones
    if not custom_milestones:
        milestones = [
            {"id": "MS-001", "name": "Design Approval", "pct": 10, "status": "pending"},
            {"id": "MS-002", "name": "Installation Complete", "pct": 70, "status": "pending"},
            {"id": "MS-003", "name": "Verification Passed", "pct": 20, "status": "pending"}
        ]
    else:
        milestones = custom_milestones
    
    # Calculate milestone amounts
    for m in milestones:
        m["amount"] = total_amount * (m["pct"] / 100)
    
    escrow = Escrow(
        job_id=job_id,
        total_amount_inr=total_amount,
        status="locked",
        milestones=milestones
    )
    
    db.add(escrow)
    db.commit()
    db.refresh(escrow)
    
    return {
        "escrow_id": escrow.id,
        "job_id": job_id,
        "total_amount": total_amount,
        "status": "locked",
        "milestones": milestones,
        "message": "Escrow created successfully"
    }


@router.get("/escrow/{job_id}")
def get_escrow_status(
    job_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    P0: Get escrow status and milestone details.
    """
    escrow = db.query(Escrow).filter(Escrow.job_id == job_id).first()
    
    if not escrow:
        raise HTTPException(status_code=404, detail="Escrow not found for this job")
    
    # Calculate released and remaining amounts
    released_amount = sum(
        m["amount"] for m in escrow.milestones
        if m.get("status") == "released"
    )
    remaining_amount = escrow.total_amount_inr - released_amount
    
    return {
        "escrow_id": escrow.id,
        "job_id": job_id,
        "total_amount": escrow.total_amount_inr,
        "released_amount": released_amount,
        "remaining_amount": remaining_amount,
        "status": escrow.status,
        "milestones": escrow.milestones,
        "funded_at": escrow.funded_at.isoformat() if escrow.funded_at else None
    }


@router.post("/escrow/{job_id}/release")
def release_escrow_milestone(
    job_id: int,
    milestone_id: str,
    verification_id: Optional[int] = None,
    admin_notes: Optional[str] = None,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    P0: Release milestone payment after verification.
    """
    escrow = db.query(Escrow).filter(Escrow.job_id == job_id).first()
    
    if not escrow:
        raise HTTPException(status_code=404, detail="Escrow not found")
    
    # 🔥 WOW MOMENT #2: Check if escrow is frozen due to fraud
    if escrow.status == "FROZEN":
        raise HTTPException(
            status_code=403,
            detail="⚠️ Payment frozen due to verification risk. Manual review required."
        )
    
    # Find milestone
    milestone = next((m for m in escrow.milestones if m["id"] == milestone_id), None)
    
    if not milestone:
        raise HTTPException(status_code=404, detail="Milestone not found")
    
    if milestone["status"] == "released":
        raise HTTPException(status_code=400, detail="Milestone already released")
    
    # Update milestone status
    milestone["status"] = "released"
    milestone["released_at"] = datetime.now().isoformat()
    if verification_id:
        milestone["verification_id"] = verification_id
    if admin_notes:
        milestone["admin_notes"] = admin_notes
    
    # Update escrow
    db.commit()
    db.refresh(escrow)
    
    return {
        "escrow_id": escrow.id,
        "milestone_id": milestone_id,
        "amount_released": milestone["amount"],
        "status": "released",
        "message": f"Milestone '{milestone['name']}' released successfully"
    }


# ============== WOW MOMENT #2: ESCROW FREEZE ON FRAUD ==============

@router.post("/escrow/{job_id}/freeze")
def freeze_escrow_on_fraud(
    job_id: int,
    fraud_score: float,
    verification_id: Optional[int] = None,
    fraud_flags: Optional[List[str]] = None,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    🔥 WOW MOMENT #2: Freeze escrow when fraud detected.
    
    Automatically triggered when fraud_score >= 0.5
    - Escrow status changes to FROZEN
    - All pending releases blocked
    - Audit trail created
    """
    escrow = db.query(Escrow).filter(Escrow.job_id == job_id).first()
    
    if not escrow:
        raise HTTPException(status_code=404, detail="Escrow not found")
    
    if fraud_score >= 0.5:
        escrow.status = "FROZEN"
        
        # Store fraud details in milestones metadata
        escrow.milestones.append({
            "id": "FRAUD-FREEZE",
            "name": "⚠️ FRAUD DETECTED - PAYMENT FROZEN",
            "pct": 0,
            "amount": 0,
            "status": "frozen",
            "fraud_score": fraud_score,
            "fraud_flags": fraud_flags or [],
            "verification_id": verification_id,
            "frozen_at": datetime.now().isoformat()
        })
        
        db.commit()
        db.refresh(escrow)
        
        return {
            "escrow_id": escrow.id,
            "job_id": job_id,
            "status": "FROZEN",
            "fraud_score": fraud_score,
            "fraud_flags": fraud_flags or [],
            "message": "⚠️ Payment frozen due to verification risk. Manual review required.",
            "action_required": "ADMIN_REVIEW",
            "payment_blocked": True
        }
    
    return {
        "escrow_id": escrow.id,
        "job_id": job_id,
        "status": escrow.status,
        "fraud_score": fraud_score,
        "message": "Fraud score below threshold. Escrow remains active.",
        "payment_blocked": False
    }


@router.post("/escrow/{job_id}/unfreeze")
def unfreeze_escrow(
    job_id: int,
    admin_notes: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Admin action to unfreeze escrow after manual review.
    """
    escrow = db.query(Escrow).filter(Escrow.job_id == job_id).first()
    
    if not escrow:
        raise HTTPException(status_code=404, detail="Escrow not found")
    
    if escrow.status != "FROZEN":
        raise HTTPException(status_code=400, detail="Escrow is not frozen")
    
    escrow.status = "locked"  # Back to normal locked state
    
    # Add unfreeze audit entry
    escrow.milestones.append({
        "id": "FRAUD-UNFREEZE",
        "name": "✅ MANUALLY REVIEWED - UNFROZEN",
        "pct": 0,
        "amount": 0,
        "status": "reviewed",
        "admin_notes": admin_notes,
        "unfrozen_at": datetime.now().isoformat()
    })
    
    db.commit()
    db.refresh(escrow)
    
    return {
        "escrow_id": escrow.id,
        "job_id": job_id,
        "status": "locked",
        "message": "Escrow unfrozen after manual review",
        "admin_notes": admin_notes
    }

