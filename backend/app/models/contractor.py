"""
Contractor Marketplace Models
Database models for contractors, quotes, work orders, and reviews.
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, JSON, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

try:
    from app.core.database import Base
except ImportError:
    from sqlalchemy.ext.declarative import declarative_base
    Base = declarative_base()


class Contractor(Base):
    """Contractor profile for marketplace."""
    __tablename__ = "contractors"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Company Info
    company_name = Column(String(150), nullable=False)
    owner_name = Column(String(100), nullable=False)
    company_type = Column(String(30))  # sole_proprietor, partnership, pvt_ltd
    
    # Contact
    phone = Column(String(15), nullable=False)
    alternate_phone = Column(String(15))
    email = Column(String(100))
    website = Column(String(200))
    
    # Address
    address = Column(Text)
    city = Column(String(100))
    state = Column(String(100))
    pincode = Column(String(6))
    
    # Service Areas
    service_cities = Column(JSON)  # List of cities served
    service_radius_km = Column(Integer, default=50)
    
    # Registration
    gst_number = Column(String(15))
    pan_number = Column(String(10))
    license_number = Column(String(50))
    registration_date = Column(DateTime)
    
    # Experience
    years_experience = Column(Integer, default=0)
    projects_completed = Column(Integer, default=0)
    total_capacity_installed_liters = Column(Float, default=0)
    
    # Team
    team_size = Column(Integer, default=1)
    engineers_count = Column(Integer, default=0)
    technicians_count = Column(Integer, default=0)
    
    # Ratings
    average_rating = Column(Float, default=0.0)
    total_reviews = Column(Integer, default=0)
    quality_rating = Column(Float, default=0.0)
    timeliness_rating = Column(Float, default=0.0)
    communication_rating = Column(Float, default=0.0)
    value_rating = Column(Float, default=0.0)
    
    # Certifications
    certifications = Column(JSON)  # List of certifications
    training_completed = Column(JSON)  # List of trainings
    
    # Insurance
    insurance_valid = Column(Boolean, default=False)
    insurance_expiry = Column(Date)
    insurance_amount = Column(Float)
    
    # Bank Details
    bank_account_name = Column(String(100))
    bank_account_number_encrypted = Column(String(256))
    bank_ifsc = Column(String(11))
    
    # Status
    status = Column(String(30), default="pending_verification")
    verified = Column(Boolean, default=False)
    verified_at = Column(DateTime)
    verified_by = Column(Integer)
    
    # Profile
    profile_photo_url = Column(String(500))
    portfolio_urls = Column(JSON)  # List of project photos
    description = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    last_active_at = Column(DateTime)
    
    # Relationships
    quotes = relationship("Quote", back_populates="contractor")
    work_orders = relationship("WorkOrder", back_populates="contractor")
    reviews = relationship("ContractorReview", back_populates="contractor")


class QuoteRequest(Base):
    """Quote request from user."""
    __tablename__ = "quote_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(String(50), unique=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Property Details
    property_address = Column(Text, nullable=False)
    city = Column(String(100))
    state = Column(String(100))
    pincode = Column(String(6))
    
    # Scope
    roof_area_sqm = Column(Float, nullable=False)
    tank_capacity_liters = Column(Integer, nullable=False)
    includes_recharge = Column(Boolean, default=False)
    includes_filter = Column(Boolean, default=True)
    includes_plumbing = Column(Boolean, default=True)
    
    # Requirements
    requirements_description = Column(Text)
    preferred_start_date = Column(Date)
    urgency = Column(String(20), default="normal")  # urgent, normal, flexible
    
    # Budget
    budget_min_inr = Column(Float)
    budget_max_inr = Column(Float)
    
    # Contact
    contact_name = Column(String(100))
    contact_phone = Column(String(15))
    preferred_contact_time = Column(String(50))
    
    # Status
    status = Column(String(30), default="open")  # open, closed, cancelled, expired
    quotes_received = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    expires_at = Column(DateTime)
    closed_at = Column(DateTime)
    
    # Relationships
    quotes = relationship("Quote", back_populates="quote_request")


class Quote(Base):
    """Quote from contractor."""
    __tablename__ = "quotes"
    
    id = Column(Integer, primary_key=True, index=True)
    quote_id = Column(String(50), unique=True, index=True)
    quote_request_id = Column(Integer, ForeignKey("quote_requests.id"))
    contractor_id = Column(Integer, ForeignKey("contractors.id"))
    project_id = Column(Integer)
    
    # Pricing
    material_cost = Column(Float, nullable=False)
    labor_cost = Column(Float, nullable=False)
    transportation_cost = Column(Float, default=0)
    permit_fee = Column(Float, default=0)
    other_charges = Column(Float, default=0)
    total_cost = Column(Float, nullable=False)
    
    # Discounts
    discount_percent = Column(Float, default=0)
    discount_amount = Column(Float, default=0)
    final_amount = Column(Float, nullable=False)
    
    # Timeline
    estimated_days = Column(Integer, nullable=False)
    proposed_start_date = Column(Date)
    proposed_end_date = Column(Date)
    
    # Scope
    scope_of_work = Column(Text)
    materials_included = Column(JSON)  # List of materials
    exclusions = Column(JSON)  # What's not included
    
    # Terms
    warranty_months = Column(Integer, default=12)
    payment_terms = Column(Text)
    advance_percent = Column(Integer, default=20)
    
    # Validity
    validity_days = Column(Integer, default=15)
    valid_until = Column(Date)
    
    # Status
    status = Column(String(30), default="submitted")  # submitted, viewed, accepted, rejected, expired
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    viewed_at = Column(DateTime)
    responded_at = Column(DateTime)
    
    # Relationships
    quote_request = relationship("QuoteRequest", back_populates="quotes")
    contractor = relationship("Contractor", back_populates="quotes")


class WorkOrder(Base):
    """Work order for accepted quote."""
    __tablename__ = "work_orders"
    
    id = Column(Integer, primary_key=True, index=True)
    work_order_id = Column(String(50), unique=True, index=True)
    quote_id = Column(Integer, ForeignKey("quotes.id"))
    contractor_id = Column(Integer, ForeignKey("contractors.id"))
    project_id = Column(Integer, ForeignKey("projects.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Contract
    agreed_amount = Column(Float, nullable=False)
    advance_amount = Column(Float)
    advance_paid = Column(Boolean, default=False)
    advance_paid_at = Column(DateTime)
    
    # Payment Terms
    advance_percent = Column(Integer, default=20)
    retention_percent = Column(Integer, default=10)
    retention_amount = Column(Float)
    
    # Timeline
    start_date = Column(Date)
    expected_end_date = Column(Date)
    actual_end_date = Column(Date)
    
    # Status
    status = Column(String(30), default="created")
    # created, advance_pending, in_progress, milestone_pending, completed, disputed, cancelled
    
    # Completion
    completion_certificate_url = Column(String(500))
    handover_date = Column(Date)
    
    # Dispute
    dispute_reason = Column(Text)
    dispute_raised_at = Column(DateTime)
    dispute_resolved_at = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Relationships
    contractor = relationship("Contractor", back_populates="work_orders")
    milestones = relationship("Milestone", back_populates="work_order")
    payments = relationship("Payment", back_populates="work_order")


class Milestone(Base):
    """Work order milestone."""
    __tablename__ = "milestones"
    
    id = Column(Integer, primary_key=True, index=True)
    milestone_id = Column(String(50), unique=True, index=True)
    work_order_id = Column(Integer, ForeignKey("work_orders.id"))
    
    # Milestone Info
    milestone_type = Column(String(50), nullable=False)
    milestone_name = Column(String(100), nullable=False)
    description = Column(Text)
    sequence = Column(Integer, nullable=False)
    
    # Payment
    payment_percent = Column(Float)
    payment_amount = Column(Float)
    
    # Status
    status = Column(String(30), default="pending")
    # pending, in_progress, completed, verification_pending, verified, rejected
    
    # Completion
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    # Verification
    photos = Column(JSON)  # List of photo URLs
    notes = Column(Text)
    verified_by = Column(Integer)
    verified_at = Column(DateTime)
    rejection_reason = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Relationships
    work_order = relationship("WorkOrder", back_populates="milestones")


class Payment(Base):
    """Payment for work order."""
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    payment_id = Column(String(50), unique=True, index=True)
    work_order_id = Column(Integer, ForeignKey("work_orders.id"))
    milestone_id = Column(Integer, ForeignKey("milestones.id"), nullable=True)
    
    # Payment Info
    payment_type = Column(String(30))  # advance, milestone, retention, final
    amount = Column(Float, nullable=False)
    
    # Status
    status = Column(String(30), default="pending")
    # pending, processing, completed, failed, refunded
    
    # Transaction
    transaction_id = Column(String(100))
    payment_method = Column(String(30))
    payment_gateway = Column(String(50))
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    paid_at = Column(DateTime)
    
    # Relationships
    work_order = relationship("WorkOrder", back_populates="payments")


class ContractorReview(Base):
    """Review for contractor."""
    __tablename__ = "contractor_reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    contractor_id = Column(Integer, ForeignKey("contractors.id"))
    project_id = Column(Integer, ForeignKey("projects.id"))
    work_order_id = Column(Integer, ForeignKey("work_orders.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Ratings
    overall_rating = Column(Integer, nullable=False)
    quality_rating = Column(Integer)
    timeliness_rating = Column(Integer)
    communication_rating = Column(Integer)
    value_rating = Column(Integer)
    
    # Feedback
    review_title = Column(String(200))
    review_text = Column(Text)
    would_recommend = Column(Boolean, default=True)
    
    # Media
    photos = Column(JSON)  # List of photo URLs
    
    # Response
    contractor_response = Column(Text)
    responded_at = Column(DateTime)
    
    # Moderation
    is_verified = Column(Boolean, default=False)
    is_visible = Column(Boolean, default=True)
    flagged = Column(Boolean, default=False)
    flag_reason = Column(String(200))
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Relationships
    contractor = relationship("Contractor", back_populates="reviews")


class DefectReport(Base):
    """Defect report for installation."""
    __tablename__ = "defect_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(String(50), unique=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    work_order_id = Column(Integer, ForeignKey("work_orders.id"))
    contractor_id = Column(Integer, ForeignKey("contractors.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Defect Info
    defect_type = Column(String(50), nullable=False)
    # leak, crack, blockage, malfunction, poor_quality, incomplete, other
    defect_description = Column(Text, nullable=False)
    defect_location = Column(String(200))
    severity = Column(String(20), default="medium")  # low, medium, high, critical
    
    # Evidence
    photos = Column(JSON)
    video_url = Column(String(500))
    
    # Dates
    detected_date = Column(Date, nullable=False)
    reported_at = Column(DateTime, server_default=func.now())
    
    # Status
    status = Column(String(30), default="reported")
    # reported, acknowledged, investigating, repair_scheduled, resolved, closed, disputed
    
    # Resolution
    resolution_notes = Column(Text)
    resolved_at = Column(DateTime)
    resolved_by = Column(Integer)
    
    # Warranty
    under_warranty = Column(Boolean, default=True)
    warranty_claim_id = Column(String(50))
    
    # Timestamps
    updated_at = Column(DateTime, onupdate=func.now())
