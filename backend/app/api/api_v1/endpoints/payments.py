"""
RainForge Payment & Escrow API Endpoints
"""

from fastapi import APIRouter, HTTPException
from typing import Optional, List
from pydantic import BaseModel
from app.services.payment_adapter import PaymentAdapter, MilestoneStatus


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
