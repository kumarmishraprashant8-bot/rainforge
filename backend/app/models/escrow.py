from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class EscrowStatus(str, enum.Enum):
    LOCKED = "LOCKED"
    PENDING_VERIFICATION = "PENDING_VERIFICATION"
    RELEASED = "RELEASED"
    DISPUTED = "DISPUTED"
    REFUNDED = "REFUNDED"

class EscrowTransaction(Base):
    __tablename__ = "escrow_transactions"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(String, index=True) # Linking to project ID string (or int if project model uses int)
    payer_id = Column(String, index=True)
    payee_id = Column(String, index=True)
    amount = Column(Float, nullable=False)
    currency = Column(String, default="INR")
    status = Column(Enum(EscrowStatus), default=EscrowStatus.LOCKED)
    
    milestone_description = Column(String, nullable=True)
    verification_proof_id = Column(String, nullable=True) # Link to photo proof ID
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    released_at = Column(DateTime(timezone=True), nullable=True)

    def release(self):
        self.status = EscrowStatus.RELEASED
        self.released_at = func.now()

    def dispute(self):
        self.status = EscrowStatus.DISPUTED
