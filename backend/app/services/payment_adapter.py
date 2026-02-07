"""
RainForge Payment Adapter
Mock escrow and milestone payment system.
"""

from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid


class PaymentStatus(str, Enum):
    PENDING = "pending"
    ESCROW = "escrow"
    PARTIAL_RELEASED = "partial_released"
    RELEASED = "released"
    REFUNDED = "refunded"
    FAILED = "failed"


class MilestoneStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    VERIFIED = "verified"
    RELEASED = "released"
    DISPUTED = "disputed"


@dataclass
class Milestone:
    id: str
    payment_id: str
    name: str
    amount: float
    sequence: int
    status: MilestoneStatus = MilestoneStatus.PENDING
    completed_at: Optional[datetime] = None
    released_at: Optional[datetime] = None


@dataclass
class Payment:
    id: str
    job_id: int
    total_amount: float
    escrow_amount: float = 0.0
    released_amount: float = 0.0
    provider: str = "mock"
    provider_ref: Optional[str] = None
    status: PaymentStatus = PaymentStatus.PENDING
    milestones: List[Milestone] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)


class PaymentAdapter:
    """
    Mock payment provider adapter.
    In production, replace with Stripe/PayU/Razorpay integration.
    """
    
    # In-memory storage
    _payments: Dict[str, Payment] = {}
    _job_payments: Dict[int, str] = {}  # job_id -> payment_id
    
    # Default milestone structure
    DEFAULT_MILESTONES = [
        {"name": "Design Approval", "percentage": 20, "sequence": 1},
        {"name": "Installation Complete", "percentage": 40, "sequence": 2},
        {"name": "Verification Passed", "percentage": 30, "sequence": 3},
        {"name": "Post-Performance Check", "percentage": 10, "sequence": 4},
    ]
    
    @classmethod
    def create_payment(
        cls,
        job_id: int,
        total_amount: float,
        milestone_config: Optional[List[Dict]] = None
    ) -> Payment:
        """
        Create a payment with milestone structure.
        """
        payment_id = f"PAY-{uuid.uuid4().hex[:8].upper()}"
        
        # Use default or custom milestones
        config = milestone_config or cls.DEFAULT_MILESTONES
        
        milestones = []
        for m in config:
            amount = total_amount * (m.get("percentage", 25) / 100)
            milestone = Milestone(
                id=f"MS-{uuid.uuid4().hex[:6].upper()}",
                payment_id=payment_id,
                name=m["name"],
                amount=amount,
                sequence=m.get("sequence", len(milestones) + 1)
            )
            milestones.append(milestone)
        
        payment = Payment(
            id=payment_id,
            job_id=job_id,
            total_amount=total_amount,
            milestones=milestones
        )
        
        cls._payments[payment_id] = payment
        cls._job_payments[job_id] = payment_id
        
        return payment
    
    @classmethod
    def capture_to_escrow(cls, payment_id: str) -> Dict:
        """
        Capture payment to escrow.
        Persists transaction to DB for audit.
        """
        if payment_id not in cls._payments:
            raise ValueError(f"Payment {payment_id} not found")
        
        payment = cls._payments[payment_id]
        
        # Mock provider reference
        provider_ref = f"ESCROW-{uuid.uuid4().hex[:10].upper()}"
        
        payment.status = PaymentStatus.ESCROW
        payment.escrow_amount = payment.total_amount
        payment.provider_ref = provider_ref
        
        # PERSIST TO DB (Audit Log)
        from app.core.database import SessionLocal
        from app.models.escrow import EscrowTransaction, EscrowStatus
        
        db = SessionLocal()
        try:
            tx = EscrowTransaction(
                project_id=str(payment.job_id),
                payer_id="PAYER_MOCK", # In real app, get from context
                payee_id="INSTALLER_MOCK",
                amount=payment.escrow_amount,
                status=EscrowStatus.LOCKED,
                verification_proof_id=provider_ref
            )
            db.add(tx)
            db.commit()
        except Exception as e:
            print(f"DB Error: {e}")
        finally:
            db.close()
            
        return {
            "payment_id": payment_id,
            "status": "escrow",
            "escrow_amount": payment.escrow_amount,
            "provider_ref": provider_ref,
            "message": "Funds captured to escrow (Audit Logged)"
        }
    
    @classmethod
    def complete_milestone(cls, payment_id: str, milestone_id: str) -> Dict:
        """
        Mark a milestone as completed (awaiting verification).
        """
        if payment_id not in cls._payments:
            raise ValueError(f"Payment {payment_id} not found")
        
        payment = cls._payments[payment_id]
        milestone = next((m for m in payment.milestones if m.id == milestone_id), None)
        
        if not milestone:
            raise ValueError(f"Milestone {milestone_id} not found")
        
        if milestone.status not in [MilestoneStatus.PENDING, MilestoneStatus.IN_PROGRESS]:
            raise ValueError(f"Milestone cannot be completed (status: {milestone.status})")
        
        milestone.status = MilestoneStatus.COMPLETED
        milestone.completed_at = datetime.utcnow()
        
        return {
            "milestone_id": milestone_id,
            "name": milestone.name,
            "status": "completed",
            "amount": milestone.amount,
            "message": "Milestone completed, awaiting verification"
        }
    
    @classmethod
    def verify_milestone(cls, payment_id: str, milestone_id: str) -> Dict:
        """
        Verify a completed milestone (admin action).
        """
        if payment_id not in cls._payments:
            raise ValueError(f"Payment {payment_id} not found")
        
        payment = cls._payments[payment_id]
        milestone = next((m for m in payment.milestones if m.id == milestone_id), None)
        
        if not milestone:
            raise ValueError(f"Milestone {milestone_id} not found")
        
        if milestone.status != MilestoneStatus.COMPLETED:
            raise ValueError(f"Milestone must be completed first (status: {milestone.status})")
        
        milestone.status = MilestoneStatus.VERIFIED
        
        return {
            "milestone_id": milestone_id,
            "name": milestone.name,
            "status": "verified",
            "amount": milestone.amount,
            "message": "Milestone verified, ready for release"
        }
    
    @classmethod
    def release_milestone(cls, payment_id: str, milestone_id: str) -> Dict:
        """
        Release funds for a verified milestone.
        """
        if payment_id not in cls._payments:
            raise ValueError(f"Payment {payment_id} not found")
        
        payment = cls._payments[payment_id]
        
        if payment.status not in [PaymentStatus.ESCROW, PaymentStatus.PARTIAL_RELEASED]:
            raise ValueError(f"Payment not in escrow (status: {payment.status})")
        
        milestone = next((m for m in payment.milestones if m.id == milestone_id), None)
        
        if not milestone:
            raise ValueError(f"Milestone {milestone_id} not found")
        
        if milestone.status != MilestoneStatus.VERIFIED:
            raise ValueError(f"Milestone must be verified first (status: {milestone.status})")
        
        # Release funds
        milestone.status = MilestoneStatus.RELEASED
        milestone.released_at = datetime.utcnow()
        
        payment.released_amount += milestone.amount
        payment.escrow_amount -= milestone.amount
        
        # Update payment status
        if payment.released_amount >= payment.total_amount:
            payment.status = PaymentStatus.RELEASED
        else:
            payment.status = PaymentStatus.PARTIAL_RELEASED
        
        return {
            "milestone_id": milestone_id,
            "name": milestone.name,
            "released_amount": milestone.amount,
            "total_released": payment.released_amount,
            "remaining_escrow": payment.escrow_amount,
            "payment_status": payment.status.value,
            "message": f"₹{milestone.amount:.0f} released to installer"
        }
    
    @classmethod
    def get_payment(cls, payment_id: str) -> Optional[Payment]:
        """Get payment by ID."""
        return cls._payments.get(payment_id)
    
    @classmethod
    def get_payment_for_job(cls, job_id: int) -> Optional[Payment]:
        """Get payment for a job."""
        payment_id = cls._job_payments.get(job_id)
        return cls._payments.get(payment_id) if payment_id else None
    
    @classmethod
    def get_payment_summary(cls, payment_id: str) -> Dict:
        """Get detailed payment summary."""
        payment = cls._payments.get(payment_id)
        if not payment:
            raise ValueError(f"Payment {payment_id} not found")
        
        return {
            "payment_id": payment.id,
            "job_id": payment.job_id,
            "total_amount": payment.total_amount,
            "escrow_amount": payment.escrow_amount,
            "released_amount": payment.released_amount,
            "status": payment.status.value,
            "provider": payment.provider,
            "provider_ref": payment.provider_ref,
            "milestones": [
                {
                    "id": m.id,
                    "name": m.name,
                    "amount": m.amount,
                    "sequence": m.sequence,
                    "status": m.status.value,
                    "completed_at": m.completed_at.isoformat() if m.completed_at else None,
                    "released_at": m.released_at.isoformat() if m.released_at else None
                }
                for m in sorted(payment.milestones, key=lambda x: x.sequence)
            ],
            "created_at": payment.created_at.isoformat()
        }
    
    @classmethod
    def refund_to_payer(cls, payment_id: str, reason: str = "") -> Dict:
        """Refund remaining escrow to payer."""
        payment = cls._payments.get(payment_id)
        if not payment:
            raise ValueError(f"Payment {payment_id} not found")
        
        refund_amount = payment.escrow_amount
        payment.escrow_amount = 0
        payment.status = PaymentStatus.REFUNDED
        
        return {
            "payment_id": payment_id,
            "refunded_amount": refund_amount,
            "reason": reason,
            "message": "Refund processed"
        }
    
    @classmethod
    def clear_demo_data(cls):
        """Clear all demo data."""
        cls._payments = {}
        cls._job_payments = {}


# ============== DEMO ==============

def demo_payment_flow():
    """Demo the payment/escrow workflow."""
    PaymentAdapter.clear_demo_data()
    
    # Create payment
    payment = PaymentAdapter.create_payment(job_id=101, total_amount=96000)
    print(f"Created payment: {payment.id}")
    print(f"Milestones: {[m.name for m in payment.milestones]}")
    
    # Capture to escrow
    result = PaymentAdapter.capture_to_escrow(payment.id)
    print(f"Escrow: ₹{result['escrow_amount']}")
    
    # Complete and release first milestone
    m1 = payment.milestones[0]
    PaymentAdapter.complete_milestone(payment.id, m1.id)
    PaymentAdapter.verify_milestone(payment.id, m1.id)
    result = PaymentAdapter.release_milestone(payment.id, m1.id)
    print(f"Released M1: ₹{result['released_amount']}, Remaining: ₹{result['remaining_escrow']}")
    
    # Get summary
    summary = PaymentAdapter.get_payment_summary(payment.id)
    print(f"Payment Status: {summary['status']}")
    
    return summary


if __name__ == "__main__":
    demo_payment_flow()
