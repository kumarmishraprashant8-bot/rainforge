"""
RainForge Database Models
SQLite for demo, Postgres for production (via DATABASE_URL env var)
"""

import os
from datetime import datetime
from typing import Optional, List
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, Text, JSON, ForeignKey, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import enum

# Database URL - SQLite for demo, Postgres for production
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./rainforge_demo.db")

# Handle Postgres URL format from some providers
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    echo=os.getenv("DEBUG", "false").lower() == "true"
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Enums
class AssessmentStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    PDF_GENERATED = "pdf_generated"


class AuctionStatus(str, enum.Enum):
    OPEN = "open"
    CLOSED = "closed"
    AWARDED = "awarded"
    CANCELLED = "cancelled"


class BidStatus(str, enum.Enum):
    SUBMITTED = "submitted"
    REJECTED = "rejected"
    AWARDED = "awarded"
    WITHDRAWN = "withdrawn"


class JobStatus(str, enum.Enum):
    PENDING = "pending"
    ALLOCATED = "allocated"
    IN_PROGRESS = "in_progress"
    VERIFICATION_PENDING = "verification_pending"
    COMPLETED = "completed"
    DISPUTED = "disputed"


class VerificationStatus(str, enum.Enum):
    PENDING = "pending"
    AUTO_APPROVED = "auto_approved"
    MANUAL_REVIEW = "manual_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    FRAUD_FLAGGED = "fraud_flagged"


class EscrowStatus(str, enum.Enum):
    PENDING = "pending"
    FUNDED = "funded"
    PARTIAL_RELEASED = "partial_released"
    FULLY_RELEASED = "fully_released"
    REFUNDED = "refunded"


# Models
class Installer(Base):
    __tablename__ = "installers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    company = Column(String(100))
    email = Column(String(100))
    phone = Column(String(20))
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    rpi_score = Column(Float, default=50.0)  # RainForge Performance Index 0-100
    capacity_available = Column(Integer, default=5)
    capacity_max = Column(Integer, default=10)
    avg_cost_factor = Column(Float, default=1.0)  # Multiplier vs baseline
    sla_compliance_pct = Column(Float, default=90.0)
    jobs_completed = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    is_blacklisted = Column(Boolean, default=False)
    cert_level = Column(String(20), default="basic")  # basic, certified, premium
    service_areas = Column(String(500))  # Comma-separated cities/states
    warranty_months = Column(Integer, default=12)
    specialization = Column(String(100))  # residential, commercial, all
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    bids = relationship("Bid", back_populates="installer")
    jobs = relationship("Job", back_populates="installer")


class Assessment(Base):
    __tablename__ = "assessments"
    
    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(String(50), unique=True, index=True)  # ASM-20260203-001
    site_id = Column(String(50), index=True)
    address = Column(String(500))
    lat = Column(Float)
    lng = Column(Float)
    
    # Inputs
    roof_area_sqm = Column(Float, nullable=False)
    roof_material = Column(String(50))  # concrete, metal, tiles, thatched
    demand_l_per_day = Column(Float)
    floors = Column(Integer, default=1)
    people = Column(Integer, default=4)
    state = Column(String(50))
    city = Column(String(100))
    
    # Outputs - stored as JSON for flexibility
    scenarios = Column(JSON)  # {cost_optimized, max_capture, dry_season}
    annual_rainfall_mm = Column(Float)
    annual_yield_liters = Column(Float)
    recommended_tank_liters = Column(Integer)
    total_cost_inr = Column(Float)
    subsidy_pct = Column(Float)
    subsidy_amount_inr = Column(Float)
    net_cost_inr = Column(Float)
    roi_years = Column(Float)
    co2_avoided_kg = Column(Float)
    
    # Status
    status = Column(SQLEnum(AssessmentStatus), default=AssessmentStatus.PENDING)
    pdf_url = Column(String(500))
    qr_verification_code = Column(String(100))  # UUID for /verify/{id}
    
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer)
    
    # Relationships
    job = relationship("Job", back_populates="assessment", uselist=False)


class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String(50), unique=True, index=True)  # JOB-20260203-001
    assessment_id = Column(Integer, ForeignKey("assessments.id"))
    installer_id = Column(Integer, ForeignKey("installers.id"))
    
    status = Column(SQLEnum(JobStatus), default=JobStatus.PENDING)
    allocation_mode = Column(String(20))  # gov_optimized, equitable, user_choice
    allocation_score = Column(Float)
    
    # Financials
    agreed_price_inr = Column(Float)
    timeline_days = Column(Integer)
    warranty_months = Column(Integer)
    
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    assessment = relationship("Assessment", back_populates="job")
    installer = relationship("Installer", back_populates="jobs")
    auction = relationship("Auction", back_populates="job", uselist=False)
    escrow = relationship("Escrow", back_populates="job", uselist=False)
    verifications = relationship("Verification", back_populates="job")


class Auction(Base):
    __tablename__ = "auctions"
    
    id = Column(Integer, primary_key=True, index=True)
    auction_id = Column(String(50), unique=True, index=True)  # AUC-20260203-001
    job_id = Column(Integer, ForeignKey("jobs.id"))
    
    status = Column(SQLEnum(AuctionStatus), default=AuctionStatus.OPEN)
    deadline = Column(DateTime)
    min_bid_inr = Column(Float)
    max_bid_inr = Column(Float)
    
    winning_bid_id = Column(Integer, ForeignKey("bids.id"))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    closed_at = Column(DateTime)
    
    # Relationships
    job = relationship("Job", back_populates="auction")
    bids = relationship("Bid", back_populates="auction", foreign_keys="Bid.auction_id")


class Bid(Base):
    __tablename__ = "bids"
    
    id = Column(Integer, primary_key=True, index=True)
    bid_id = Column(String(50), unique=True, index=True)  # BID-20260203-001
    auction_id = Column(Integer, ForeignKey("auctions.id"))
    installer_id = Column(Integer, ForeignKey("installers.id"))
    
    price_inr = Column(Float, nullable=False)
    timeline_days = Column(Integer, nullable=False)
    warranty_months = Column(Integer, default=12)
    notes = Column(Text)
    
    score = Column(Float)  # Composite score for ranking
    status = Column(SQLEnum(BidStatus), default=BidStatus.SUBMITTED)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    auction = relationship("Auction", back_populates="bids", foreign_keys=[auction_id])
    installer = relationship("Installer", back_populates="bids")


class Verification(Base):
    __tablename__ = "verifications"
    
    id = Column(Integer, primary_key=True, index=True)
    verification_id = Column(String(50), unique=True, index=True)  # VER-20260203-001
    job_id = Column(Integer, ForeignKey("jobs.id"))
    
    # Photos
    photo_paths = Column(JSON)  # List of file paths
    photo_hashes = Column(JSON)  # SHA256 hashes for duplicate detection
    
    # Geo data
    submitted_lat = Column(Float)
    submitted_lng = Column(Float)
    exif_lat = Column(Float)
    exif_lng = Column(Float)
    geo_distance_m = Column(Float)  # Distance between submitted and EXIF
    
    # Fraud detection
    fraud_score = Column(Float, default=0.0)  # 0.0 = clean, 1.0 = fraud
    fraud_flags = Column(JSON)  # List of detected issues
    
    status = Column(SQLEnum(VerificationStatus), default=VerificationStatus.PENDING)
    reviewer_id = Column(Integer)
    review_notes = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    reviewed_at = Column(DateTime)
    
    # Relationships
    job = relationship("Job", back_populates="verifications")


class Escrow(Base):
    __tablename__ = "escrows"
    
    id = Column(Integer, primary_key=True, index=True)
    escrow_id = Column(String(50), unique=True, index=True)  # ESC-20260203-001
    job_id = Column(Integer, ForeignKey("jobs.id"))
    
    total_amount_inr = Column(Float, nullable=False)
    status = Column(SQLEnum(EscrowStatus), default=EscrowStatus.PENDING)
    
    # Milestones (stored as JSON for flexibility)
    milestones = Column(JSON)  # [{id, name, pct, amount, status, released_at}]
    
    funded_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    job = relationship("Job", back_populates="escrow")


class Telemetry(Base):
    __tablename__ = "telemetry"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, index=True)
    device_id = Column(String(50))
    
    timestamp = Column(DateTime, nullable=False)
    sensor_type = Column(String(50))  # tank_level, flow_meter, water_quality, battery
    value = Column(Float)
    unit = Column(String(20))
    
    # Metadata
    battery_pct = Column(Float)
    signal_rssi = Column(Integer)
    
    created_at = Column(DateTime, default=datetime.utcnow)


class SubsidyRule(Base):
    __tablename__ = "subsidy_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    state_code = Column(String(10), index=True)
    state_name = Column(String(100))
    scheme_name = Column(String(200))
    subsidy_pct = Column(Float)
    max_subsidy_inr = Column(Float)
    eligible_building_types = Column(String(200))
    min_roof_sqm = Column(Float)
    max_roof_sqm = Column(Float)
    valid_from = Column(DateTime)
    valid_until = Column(DateTime)
    source_url = Column(String(500))
    is_active = Column(Boolean, default=True)


class Ward(Base):
    __tablename__ = "wards"
    
    id = Column(Integer, primary_key=True, index=True)
    ward_id = Column(String(50), unique=True, index=True)
    ward_name = Column(String(200))
    city = Column(String(100))
    state = Column(String(50))
    population = Column(Integer)
    area_sqkm = Column(Float)
    geojson = Column(JSON)  # GeoJSON polygon
    
    # Aggregates (updated periodically)
    total_projects = Column(Integer, default=0)
    verified_projects = Column(Integer, default=0)
    total_capture_liters = Column(Float, default=0)
    total_investment_inr = Column(Float, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)


class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String(50))  # assessment, verification, escrow, etc.
    entity_id = Column(String(50))
    action = Column(String(50))
    actor_id = Column(Integer)
    actor_type = Column(String(20))  # user, system, installer
    details = Column(JSON)
    ip_address = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)


# Database initialization
def init_db():
    """Create all tables."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Dependency for getting database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
