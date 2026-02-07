"""
RainForge Demo API - Complete Endpoints
All required endpoints for hackathon demo
"""

from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Form, Query
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import uuid
import hashlib
import json
import os

from app.models.database import (
    get_db, Assessment, Job, Auction, Bid, Verification, Escrow, 
    Installer, Telemetry, SubsidyRule, Ward, AuditLog,
    AssessmentStatus, AuctionStatus, BidStatus, JobStatus, 
    VerificationStatus, EscrowStatus
)

router = APIRouter()

# ==================== SCHEMAS ====================

class AssessmentRequest(BaseModel):
    site_id: str = Field(..., example="SITE001")
    address: str = Field(..., example="Municipal School Sector 5, Goa")
    lat: float = Field(..., example=15.0)
    lng: float = Field(..., example=73.0)
    roof_area_sqm: float = Field(..., gt=0, example=120)
    roof_material: str = Field("concrete", example="concrete")
    demand_l_per_day: Optional[float] = Field(None, example=200)
    floors: int = Field(1, ge=1, le=20)
    people: int = Field(4, ge=1)
    state: Optional[str] = Field(None, example="Goa")
    city: Optional[str] = Field(None, example="Panaji")


class Scenario(BaseModel):
    name: str
    tank_liters: int
    cost_inr: float
    capture_liters: float
    coverage_days: int
    roi_years: float


class AssessmentResponse(BaseModel):
    assessment_id: str
    site_id: str
    annual_rainfall_mm: float
    annual_yield_liters: float
    scenarios: Dict[str, Scenario]
    recommended_scenario: str
    subsidy_pct: float
    subsidy_amount_inr: float
    co2_avoided_kg: float
    pdf_url: str
    verify_url: str
    created_at: datetime


class MultimodalAssessmentRequest(BaseModel):
    """Optional mode and fields for Feature A - multi-modal assessment."""
    address: str = Field(..., example="123 Gandhi Road, New Delhi")
    mode: Optional[str] = Field(None, description="address | satellite-only | photo")
    lat: Optional[float] = Field(None, ge=-90, le=90)
    lng: Optional[float] = Field(None, ge=-180, le=180)
    roof_area_sqm: Optional[float] = Field(None, gt=0)
    roof_material: Optional[str] = Field(None)
    state: Optional[str] = Field(None)
    city: Optional[str] = Field(None)
    people: int = Field(4, ge=1)
    floors: int = Field(1, ge=1)
    site_id: Optional[str] = Field(None)


class AuctionCreateRequest(BaseModel):
    job_id: str
    deadline_hours: int = Field(72, ge=1, le=168)
    min_bid_inr: Optional[float] = None
    max_bid_inr: Optional[float] = None


class BidRequest(BaseModel):
    installer_id: int
    price_inr: float = Field(..., gt=0)
    timeline_days: int = Field(..., ge=1, le=180)
    warranty_months: int = Field(12, ge=6, le=60)
    notes: Optional[str] = None


class AllocationRequest(BaseModel):
    job_ids: List[str]
    mode: str = Field("gov_optimized", pattern="^(gov_optimized|equitable|user_choice)$")
    force_installer_id: Optional[int] = None


class EscrowReleaseRequest(BaseModel):
    milestone_id: str
    verification_id: Optional[str] = None


class VerificationResponse(BaseModel):
    verification_id: str
    job_id: str
    status: str
    fraud_score: float
    fraud_flags: List[str]
    geo_distance_m: Optional[float]
    recommendation: str
    audit_trail: List[Dict[str, Any]]


# ==================== UTILITIES ====================

# Runoff coefficients by material
RUNOFF_COEFFICIENTS = {
    "concrete": 0.85,
    "rcc": 0.85,
    "metal": 0.90,
    "tiles": 0.75,
    "tile": 0.75,
    "thatched": 0.60,
    "asbestos": 0.80,
}

# City rainfall data (mm/year) - seeded for demo
CITY_RAINFALL = {
    "delhi": 700,
    "new delhi": 700,
    "mumbai": 2200,
    "bangalore": 970,
    "bengaluru": 970,
    "chennai": 1400,
    "hyderabad": 800,
    "kolkata": 1600,
    "pune": 1100,
    "jaipur": 650,
    "goa": 3000,
    "panaji": 3000,
    "kochi": 3200,
    "thiruvananthapuram": 1800,
    "ahmedabad": 800,
    "lucknow": 900,
    "default": 1000,
}

# State subsidies (seeded for demo)
STATE_SUBSIDIES = {
    "delhi": {"pct": 50, "max": 50000},
    "maharashtra": {"pct": 35, "max": 75000},
    "karnataka": {"pct": 40, "max": 40000},
    "tamil nadu": {"pct": 30, "max": 35000},
    "telangana": {"pct": 45, "max": 60000},
    "rajasthan": {"pct": 60, "max": 100000},
    "goa": {"pct": 50, "max": 50000},
    "kerala": {"pct": 50, "max": 75000},
    "gujarat": {"pct": 40, "max": 50000},
    "uttar pradesh": {"pct": 25, "max": 25000},
}


def generate_id(prefix: str) -> str:
    """Generate unique ID like ASM-20260203-ABC123."""
    date_part = datetime.utcnow().strftime("%Y%m%d")
    random_part = uuid.uuid4().hex[:6].upper()
    return f"{prefix}-{date_part}-{random_part}"


def get_rainfall(city: str, state: str) -> float:
    """Get annual rainfall for location."""
    city_lower = city.lower() if city else ""
    return CITY_RAINFALL.get(city_lower, CITY_RAINFALL.get("default", 1000))


def get_subsidy(state: str) -> Dict[str, Any]:
    """Get subsidy info for state."""
    state_lower = state.lower() if state else ""
    return STATE_SUBSIDIES.get(state_lower, {"pct": 0, "max": 0})


def calculate_yield(roof_area_sqm: float, rainfall_mm: float, material: str) -> float:
    """Calculate annual water collection in liters."""
    coeff = RUNOFF_COEFFICIENTS.get(material.lower(), 0.85)
    return roof_area_sqm * (rainfall_mm / 1000) * coeff * 1000


def calculate_scenarios(
    annual_yield: float,
    daily_demand: float,
    total_cost_base: float
) -> Dict[str, Dict]:
    """Generate 3 scenarios for assessment."""
    
    # Cost Optimized: Smallest viable tank (1 month monsoon storage)
    cost_tank = max(1000, int(annual_yield * 0.08))  # ~1 month monsoon
    cost_tank = (cost_tank // 500) * 500  # Round to 500L
    
    # Max Capture: Largest recommended (3 months storage)
    max_tank = max(2000, int(annual_yield * 0.25))
    max_tank = (max_tank // 1000) * 1000  # Round to 1000L
    
    # Dry Season: Optimized for low rainfall months (2 months storage)
    dry_tank = max(1500, int(daily_demand * 60))  # 60 days storage
    dry_tank = (dry_tank // 500) * 500
    
    def tank_cost(liters: int) -> float:
        # Base cost per liter: ₹15-25 depending on size
        per_liter = 20 - (liters / 10000) * 5
        per_liter = max(15, min(25, per_liter))
        return liters * per_liter + total_cost_base * 0.3
    
    def coverage_days(tank: int, demand: float) -> int:
        if demand <= 0:
            return 365
        return min(365, int(tank / demand))
    
    def roi_years(cost: float, annual_savings: float) -> float:
        if annual_savings <= 0:
            return 99.0
        return round(cost / annual_savings, 1)
    
    annual_savings = (annual_yield / 1000) * 50  # ₹50/kL water cost
    
    return {
        "cost_optimized": {
            "name": "Cost Optimized",
            "tank_liters": cost_tank,
            "cost_inr": round(tank_cost(cost_tank), 0),
            "capture_liters": int(annual_yield * 0.6),
            "coverage_days": coverage_days(cost_tank, daily_demand),
            "roi_years": roi_years(tank_cost(cost_tank), annual_savings * 0.6)
        },
        "max_capture": {
            "name": "Maximum Capture",
            "tank_liters": max_tank,
            "cost_inr": round(tank_cost(max_tank), 0),
            "capture_liters": int(annual_yield * 0.95),
            "coverage_days": coverage_days(max_tank, daily_demand),
            "roi_years": roi_years(tank_cost(max_tank), annual_savings * 0.95)
        },
        "dry_season": {
            "name": "Dry Season Optimized",
            "tank_liters": dry_tank,
            "cost_inr": round(tank_cost(dry_tank), 0),
            "capture_liters": int(annual_yield * 0.75),
            "coverage_days": coverage_days(dry_tank, daily_demand),
            "roi_years": roi_years(tank_cost(dry_tank), annual_savings * 0.75)
        }
    }


def calculate_rpi(installer: Installer) -> float:
    """Calculate RainForge Performance Index (0-100)."""
    # Components with weights
    timeliness = installer.sla_compliance_pct * 0.25
    capacity_util = (1 - installer.capacity_available / max(1, installer.capacity_max)) * 100 * 0.15
    cost_efficiency = (1 / max(0.5, installer.avg_cost_factor)) * 100 * 0.20
    experience = min(100, installer.jobs_completed * 2) * 0.20
    cert_bonus = {"basic": 60, "certified": 80, "premium": 100}.get(installer.cert_level, 60) * 0.10
    warranty_score = min(100, installer.warranty_months * 5) * 0.10
    
    rpi = timeliness + capacity_util + cost_efficiency + experience + cert_bonus + warranty_score
    return round(min(100, max(0, rpi)), 1)


# ==================== ENDPOINTS ====================

# ----- ASSESSMENT -----

@router.post("/assess", response_model=AssessmentResponse, tags=["Assessment"])
async def create_assessment(request: AssessmentRequest, db: Session = Depends(get_db)):
    """
    Create RWH assessment with 3 scenarios.
    Returns cost_optimized, max_capture, and dry_season recommendations.
    """
    assessment_id = generate_id("ASM")
    qr_code = str(uuid.uuid4())
    
    # Get rainfall data
    annual_rainfall = get_rainfall(request.city or "", request.state or "")
    
    # Calculate yield
    annual_yield = calculate_yield(
        request.roof_area_sqm, 
        annual_rainfall, 
        request.roof_material
    )
    
    # Calculate daily demand
    daily_demand = request.demand_l_per_day or (request.people * 135)  # 135 LPCD default
    
    # Base cost calculation
    base_cost = request.roof_area_sqm * 150  # ₹150/sqm for plumbing + filter
    
    # Generate 3 scenarios
    scenarios = calculate_scenarios(annual_yield, daily_demand, base_cost)
    
    # Get subsidy
    subsidy_info = get_subsidy(request.state or "")
    recommended = scenarios["max_capture"]
    subsidy_amount = min(
        recommended["cost_inr"] * subsidy_info["pct"] / 100,
        subsidy_info["max"]
    )
    
    # CO2 calculation: 0.255 kg CO2 per kL water saved
    co2_avoided = (annual_yield / 1000) * 0.255
    
    # Store in database
    assessment = Assessment(
        assessment_id=assessment_id,
        site_id=request.site_id,
        address=request.address,
        lat=request.lat,
        lng=request.lng,
        roof_area_sqm=request.roof_area_sqm,
        roof_material=request.roof_material,
        demand_l_per_day=daily_demand,
        floors=request.floors,
        people=request.people,
        state=request.state,
        city=request.city,
        scenarios=scenarios,
        annual_rainfall_mm=annual_rainfall,
        annual_yield_liters=annual_yield,
        recommended_tank_liters=scenarios["max_capture"]["tank_liters"],
        total_cost_inr=recommended["cost_inr"],
        subsidy_pct=subsidy_info["pct"],
        subsidy_amount_inr=subsidy_amount,
        net_cost_inr=recommended["cost_inr"] - subsidy_amount,
        roi_years=recommended["roi_years"],
        co2_avoided_kg=co2_avoided,
        status=AssessmentStatus.COMPLETED,
        qr_verification_code=qr_code
    )
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    
    # Create Job record
    job = Job(
        job_id=generate_id("JOB"),
        assessment_id=assessment.id,
        status=JobStatus.PENDING
    )
    db.add(job)
    db.commit()
    
    # Audit log
    audit = AuditLog(
        entity_type="assessment",
        entity_id=assessment_id,
        action="created",
        actor_type="system",
        details={"site_id": request.site_id, "scenarios": list(scenarios.keys())}
    )
    db.add(audit)
    db.commit()
    
    return AssessmentResponse(
        assessment_id=assessment_id,
        site_id=request.site_id,
        annual_rainfall_mm=annual_rainfall,
        annual_yield_liters=annual_yield,
        scenarios={k: Scenario(**v) for k, v in scenarios.items()},
        recommended_scenario="max_capture",
        subsidy_pct=subsidy_info["pct"],
        subsidy_amount_inr=subsidy_amount,
        co2_avoided_kg=round(co2_avoided, 2),
        pdf_url=f"/api/v1/assess/{assessment_id}/pdf",
        verify_url=f"/api/v1/verify/{qr_code}",
        created_at=assessment.created_at
    )


@router.post("/assessments", tags=["Assessment", "Multimodal"])
async def create_multimodal_assessment(
    request: MultimodalAssessmentRequest, db: Session = Depends(get_db)
):
    """
    Create assessment with optional input mode: address | satellite-only | photo.
    Returns same 1-page engineer PDF URL and a confidence score (Feature A).
    """
    from app.services.assessment_pipeline import (
        select_pipeline,
        run_pipeline,
    )
    mode = select_pipeline(request.mode)
    result = run_pipeline(
        mode=mode,
        address=request.address,
        lat=request.lat,
        lng=request.lng,
        roof_area_sqm=request.roof_area_sqm,
        roof_material=request.roof_material,
        state=request.state,
        city=request.city,
        people=request.people,
        floors=request.floors,
        site_id=request.site_id,
        db_session=db,
        pdf_base_path="assess",
    )
    return result


@router.get("/assess/{assessment_id}", tags=["Assessment"])
async def get_assessment(assessment_id: str, db: Session = Depends(get_db)):
    """Get assessment details by ID."""
    assessment = db.query(Assessment).filter(
        Assessment.assessment_id == assessment_id
    ).first()
    
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    return {
        "assessment_id": assessment.assessment_id,
        "site_id": assessment.site_id,
        "address": assessment.address,
        "lat": assessment.lat,
        "lng": assessment.lng,
        "roof_area_sqm": assessment.roof_area_sqm,
        "annual_rainfall_mm": assessment.annual_rainfall_mm,
        "annual_yield_liters": assessment.annual_yield_liters,
        "scenarios": assessment.scenarios,
        "subsidy_pct": assessment.subsidy_pct,
        "subsidy_amount_inr": assessment.subsidy_amount_inr,
        "net_cost_inr": assessment.net_cost_inr,
        "roi_years": assessment.roi_years,
        "co2_avoided_kg": assessment.co2_avoided_kg,
        "status": assessment.status.value,
        "pdf_url": f"/api/v1/assess/{assessment_id}/pdf",
        "verify_url": f"/api/v1/verify/{assessment.qr_verification_code}",
        "created_at": assessment.created_at.isoformat()
    }


@router.get("/assess/{assessment_id}/pdf", tags=["Assessment"])
async def get_assessment_pdf(assessment_id: str, db: Session = Depends(get_db)):
    """
    Generate and return assessment PDF.
    Includes QR code for verification and engineer signature block.
    """
    assessment = db.query(Assessment).filter(
        Assessment.assessment_id == assessment_id
    ).first()
    
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    # Import PDF generator
    from app.services.pdf_generator_demo import generate_assessment_pdf
    
    pdf_path = generate_assessment_pdf(assessment)
    
    # Update status
    assessment.status = AssessmentStatus.PDF_GENERATED
    assessment.pdf_url = pdf_path
    db.commit()
    
    from fastapi.responses import FileResponse
    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=f"RainForge_Assessment_{assessment_id}.pdf"
    )


# ----- AUCTION -----

@router.post("/auction/create", tags=["Auction"])
async def create_auction(request: AuctionCreateRequest, db: Session = Depends(get_db)):
    """Create a reverse auction for a job."""
    
    # Find job
    job = db.query(Job).filter(Job.job_id == request.job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Check if auction already exists
    existing = db.query(Auction).filter(Auction.job_id == job.id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Auction already exists for this job")
    
    auction_id = generate_id("AUC")
    deadline = datetime.utcnow() + timedelta(hours=request.deadline_hours)
    
    auction = Auction(
        auction_id=auction_id,
        job_id=job.id,
        status=AuctionStatus.OPEN,
        deadline=deadline,
        min_bid_inr=request.min_bid_inr or (job.assessment.net_cost_inr * 0.8 if job.assessment else 10000),
        max_bid_inr=request.max_bid_inr or (job.assessment.net_cost_inr * 1.5 if job.assessment else 100000)
    )
    db.add(auction)
    db.commit()
    db.refresh(auction)
    
    # Audit log
    audit = AuditLog(
        entity_type="auction",
        entity_id=auction_id,
        action="created",
        actor_type="system",
        details={"job_id": request.job_id, "deadline": deadline.isoformat()}
    )
    db.add(audit)
    db.commit()
    
    return {
        "auction_id": auction_id,
        "job_id": request.job_id,
        "status": "open",
        "deadline": deadline.isoformat(),
        "min_bid_inr": auction.min_bid_inr,
        "max_bid_inr": auction.max_bid_inr,
        "bids_count": 0
    }


@router.post("/auction/{auction_id}/bid", tags=["Auction"])
async def submit_bid(auction_id: str, request: BidRequest, db: Session = Depends(get_db)):
    """Submit a bid for an auction."""
    
    auction = db.query(Auction).filter(Auction.auction_id == auction_id).first()
    if not auction:
        raise HTTPException(status_code=404, detail="Auction not found")
    
    if auction.status != AuctionStatus.OPEN:
        raise HTTPException(status_code=400, detail="Auction is not open")
    
    if datetime.utcnow() > auction.deadline:
        raise HTTPException(status_code=400, detail="Auction deadline has passed")
    
    installer = db.query(Installer).filter(Installer.id == request.installer_id).first()
    if not installer:
        raise HTTPException(status_code=404, detail="Installer not found")
    
    if installer.is_blacklisted:
        raise HTTPException(status_code=400, detail="Installer is blacklisted")
    
    # Calculate bid score (lower is better for price, higher for quality)
    # Normalize to 0-100 scale
    price_score = 100 - min(100, (request.price_inr / auction.max_bid_inr) * 100)
    timeline_score = 100 - min(100, (request.timeline_days / 90) * 100)
    warranty_score = min(100, (request.warranty_months / 24) * 100)
    rpi_score = calculate_rpi(installer)
    
    # Composite score (higher is better)
    composite_score = (
        price_score * 0.35 +
        rpi_score * 0.30 +
        timeline_score * 0.20 +
        warranty_score * 0.15
    )
    
    bid_id = generate_id("BID")
    bid = Bid(
        bid_id=bid_id,
        auction_id=auction.id,
        installer_id=installer.id,
        price_inr=request.price_inr,
        timeline_days=request.timeline_days,
        warranty_months=request.warranty_months,
        notes=request.notes,
        score=composite_score,
        status=BidStatus.SUBMITTED
    )
    db.add(bid)
    db.commit()
    
    # Audit log
    audit = AuditLog(
        entity_type="bid",
        entity_id=bid_id,
        action="submitted",
        actor_type="installer",
        actor_id=installer.id,
        details={"auction_id": auction_id, "price": request.price_inr, "score": composite_score}
    )
    db.add(audit)
    db.commit()
    
    return {
        "bid_id": bid_id,
        "auction_id": auction_id,
        "installer_id": installer.id,
        "installer_name": installer.name,
        "price_inr": request.price_inr,
        "timeline_days": request.timeline_days,
        "warranty_months": request.warranty_months,
        "score": round(composite_score, 2),
        "status": "submitted"
    }


@router.get("/auction/{auction_id}/history", tags=["Auction"])
async def get_auction_history(auction_id: str, db: Session = Depends(get_db)):
    """Get auction details and all bids."""
    
    auction = db.query(Auction).filter(Auction.auction_id == auction_id).first()
    if not auction:
        raise HTTPException(status_code=404, detail="Auction not found")
    
    bids = db.query(Bid).filter(Bid.auction_id == auction.id).order_by(Bid.score.desc()).all()
    
    return {
        "auction_id": auction_id,
        "job_id": auction.job.job_id if auction.job else None,
        "status": auction.status.value,
        "deadline": auction.deadline.isoformat(),
        "bids_count": len(bids),
        "bids": [
            {
                "bid_id": b.bid_id,
                "installer_id": b.installer_id,
                "installer_name": b.installer.name if b.installer else None,
                "installer_rpi": b.installer.rpi_score if b.installer else None,
                "price_inr": b.price_inr,
                "timeline_days": b.timeline_days,
                "warranty_months": b.warranty_months,
                "score": round(b.score, 2),
                "status": b.status.value,
                "created_at": b.created_at.isoformat()
            }
            for b in bids
        ],
        "winning_bid_id": auction.winning_bid_id
    }


@router.post("/auction/{auction_id}/award", tags=["Auction"])
async def award_auction(auction_id: str, bid_id: str, db: Session = Depends(get_db)):
    """Award auction to a specific bid."""
    
    auction = db.query(Auction).filter(Auction.auction_id == auction_id).first()
    if not auction:
        raise HTTPException(status_code=404, detail="Auction not found")
    
    bid = db.query(Bid).filter(Bid.bid_id == bid_id).first()
    if not bid or bid.auction_id != auction.id:
        raise HTTPException(status_code=404, detail="Bid not found for this auction")
    
    # Update auction
    auction.status = AuctionStatus.AWARDED
    auction.winning_bid_id = bid.id
    auction.closed_at = datetime.utcnow()
    
    # Update bid
    bid.status = BidStatus.AWARDED
    
    # Update job
    job = auction.job
    job.installer_id = bid.installer_id
    job.status = JobStatus.ALLOCATED
    job.agreed_price_inr = bid.price_inr
    job.timeline_days = bid.timeline_days
    job.warranty_months = bid.warranty_months
    
    # Create escrow
    escrow = Escrow(
        escrow_id=generate_id("ESC"),
        job_id=job.id,
        total_amount_inr=bid.price_inr,
        status=EscrowStatus.PENDING,
        milestones=[
            {"id": "M1", "name": "Design Approval", "pct": 10, "amount": bid.price_inr * 0.10, "status": "pending"},
            {"id": "M2", "name": "Installation Complete", "pct": 70, "amount": bid.price_inr * 0.70, "status": "pending"},
            {"id": "M3", "name": "Final Verification", "pct": 20, "amount": bid.price_inr * 0.20, "status": "pending"}
        ]
    )
    db.add(escrow)
    db.commit()
    
    return {
        "auction_id": auction_id,
        "winning_bid_id": bid_id,
        "installer_id": bid.installer_id,
        "agreed_price_inr": bid.price_inr,
        "escrow_id": escrow.escrow_id,
        "status": "awarded"
    }


# ----- ALLOCATION -----

@router.post("/allocate", tags=["Allocation"])
async def allocate_jobs(request: AllocationRequest, db: Session = Depends(get_db)):
    """
    Allocate installers to jobs using specified mode.
    Modes: gov_optimized (best RPI + proximity), equitable (round-robin), user_choice (forced)
    """
    
    allocations = []
    
    for job_id in request.job_ids:
        job = db.query(Job).filter(Job.job_id == job_id).first()
        if not job:
            allocations.append({"job_id": job_id, "error": "Job not found"})
            continue
        
        if job.status != JobStatus.PENDING:
            allocations.append({"job_id": job_id, "error": f"Job status is {job.status.value}"})
            continue
        
        # Get available installers
        installers = db.query(Installer).filter(
            Installer.is_active == True,
            Installer.is_blacklisted == False,
            Installer.capacity_available > 0
        ).all()
        
        if not installers:
            allocations.append({"job_id": job_id, "error": "No available installers"})
            continue
        
        selected_installer = None
        allocation_score = 0
        
        if request.mode == "user_choice" and request.force_installer_id:
            # User forced selection
            selected_installer = next(
                (i for i in installers if i.id == request.force_installer_id), 
                None
            )
            allocation_score = calculate_rpi(selected_installer) if selected_installer else 0
            
        elif request.mode == "equitable":
            # Round-robin: select installer with most available capacity
            selected_installer = max(installers, key=lambda i: i.capacity_available)
            allocation_score = calculate_rpi(selected_installer)
            
        else:  # gov_optimized (default)
            # Score each installer and pick best
            scored = []
            for inst in installers:
                rpi = calculate_rpi(inst)
                capacity_score = (inst.capacity_available / max(1, inst.capacity_max)) * 20
                cost_score = (1 / max(0.5, inst.avg_cost_factor)) * 20
                
                # Distance scoring would use job.assessment.lat/lng vs installer.lat/lng
                # Simplified for demo
                total = rpi * 0.4 + capacity_score + cost_score
                scored.append((inst, total))
            
            scored.sort(key=lambda x: x[1], reverse=True)
            selected_installer, allocation_score = scored[0]
        
        if selected_installer:
            job.installer_id = selected_installer.id
            job.status = JobStatus.ALLOCATED
            job.allocation_mode = request.mode
            job.allocation_score = allocation_score
            
            selected_installer.capacity_available -= 1
            db.commit()
            
            allocations.append({
                "job_id": job_id,
                "installer_id": selected_installer.id,
                "installer_name": selected_installer.name,
                "installer_rpi": selected_installer.rpi_score,
                "allocation_score": round(allocation_score, 2),
                "mode": request.mode,
                "status": "allocated"
            })
        else:
            allocations.append({"job_id": job_id, "error": "No suitable installer found"})
    
    return {"allocations": allocations}


# ----- ESCROW -----

@router.post("/escrow/{job_id}/release", tags=["Escrow"])
async def release_escrow(job_id: str, request: EscrowReleaseRequest, db: Session = Depends(get_db)):
    """Release a milestone payment from escrow."""
    
    job = db.query(Job).filter(Job.job_id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    escrow = db.query(Escrow).filter(Escrow.job_id == job.id).first()
    if not escrow:
        raise HTTPException(status_code=404, detail="Escrow not found for this job")
    
    # Find milestone
    milestones = escrow.milestones or []
    milestone = next((m for m in milestones if m["id"] == request.milestone_id), None)
    
    if not milestone:
        raise HTTPException(status_code=404, detail="Milestone not found")
    
    if milestone["status"] == "released":
        raise HTTPException(status_code=400, detail="Milestone already released")
    
    # Update milestone
    milestone["status"] = "released"
    milestone["released_at"] = datetime.utcnow().isoformat()
    
    # Update escrow status
    released_count = sum(1 for m in milestones if m["status"] == "released")
    if released_count == len(milestones):
        escrow.status = EscrowStatus.FULLY_RELEASED
    elif released_count > 0:
        escrow.status = EscrowStatus.PARTIAL_RELEASED
    
    escrow.milestones = milestones
    db.commit()
    
    # Audit log
    audit = AuditLog(
        entity_type="escrow",
        entity_id=escrow.escrow_id,
        action="milestone_released",
        actor_type="system",
        details={"milestone_id": request.milestone_id, "amount": milestone["amount"]}
    )
    db.add(audit)
    db.commit()
    
    return {
        "escrow_id": escrow.escrow_id,
        "job_id": job_id,
        "milestone_id": request.milestone_id,
        "amount_released": milestone["amount"],
        "status": escrow.status.value,
        "milestones": milestones
    }


@router.get("/escrow/{job_id}", tags=["Escrow"])
async def get_escrow(job_id: str, db: Session = Depends(get_db)):
    """Get escrow details for a job."""
    
    job = db.query(Job).filter(Job.job_id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    escrow = db.query(Escrow).filter(Escrow.job_id == job.id).first()
    if not escrow:
        raise HTTPException(status_code=404, detail="Escrow not found")
    
    return {
        "escrow_id": escrow.escrow_id,
        "job_id": job_id,
        "total_amount_inr": escrow.total_amount_inr,
        "status": escrow.status.value,
        "milestones": escrow.milestones,
        "created_at": escrow.created_at.isoformat()
    }


# ----- VERIFICATION -----

@router.post("/verify", tags=["Verification"])
async def submit_verification(
    job_id: str = Form(...),
    lat: float = Form(...),
    lng: float = Form(...),
    photos: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """
    Submit verification with geo-tagged photos.
    Runs fraud detection pipeline:
    - EXIF geo-check vs submitted coordinates
    - SHA256 photo hash for duplicate detection
    - Distance/time anomaly detection
    """
    
    job = db.query(Job).filter(Job.job_id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    verification_id = generate_id("VER")
    
    # Create uploads directory
    upload_dir = f"uploads/{verification_id}"
    os.makedirs(upload_dir, exist_ok=True)
    
    photo_paths = []
    photo_hashes = []
    fraud_flags = []
    fraud_score = 0.0
    exif_lat, exif_lng = None, None
    geo_distance = None
    
    for i, photo in enumerate(photos):
        # Save photo
        file_path = f"{upload_dir}/photo_{i}_{photo.filename}"
        content = await photo.read()
        with open(file_path, "wb") as f:
            f.write(content)
        photo_paths.append(file_path)
        
        # Calculate hash for duplicate detection
        photo_hash = hashlib.sha256(content).hexdigest()
        photo_hashes.append(photo_hash)
        
        # Check for duplicate photos in other verifications
        existing = db.query(Verification).filter(
            Verification.photo_hashes.contains(photo_hash)
        ).first()
        if existing and existing.job_id != job.id:
            fraud_flags.append("photo_reuse_detected")
            fraud_score += 0.8
        
        # Extract EXIF data (simplified - would use PIL/exifread in production)
        try:
            from app.services.exif_parser import extract_gps_from_exif
            exif_data = extract_gps_from_exif(content)
            if exif_data:
                exif_lat = exif_data.get("lat")
                exif_lng = exif_data.get("lng")
                
                # Check geofence
                if exif_lat and exif_lng and job.assessment:
                    from app.services.fraud_detector_demo import calculate_distance
                    geo_distance = calculate_distance(
                        exif_lat, exif_lng,
                        job.assessment.lat, job.assessment.lng
                    )
                    
                    if geo_distance > 500:
                        fraud_flags.append("location_mismatch_severe")
                        fraud_score += 0.6
                    elif geo_distance > 200:
                        fraud_flags.append("location_mismatch_moderate")
                        fraud_score += 0.3
                    elif geo_distance > 50:
                        fraud_flags.append("location_warning")
                        fraud_score += 0.1
        except Exception:
            fraud_flags.append("exif_extraction_failed")
            fraud_score += 0.2
    
    # No EXIF data at all
    if not exif_lat and not exif_lng:
        fraud_flags.append("no_exif_gps")
        fraud_score += 0.4
    
    # Check distance between submitted and EXIF coords
    if exif_lat and exif_lng:
        from app.services.fraud_detector_demo import calculate_distance
        submitted_vs_exif = calculate_distance(lat, lng, exif_lat, exif_lng)
        if submitted_vs_exif > 100:
            fraud_flags.append("submitted_vs_exif_mismatch")
            fraud_score += 0.3
    
    # Cap fraud score at 1.0
    fraud_score = min(1.0, fraud_score)
    
    # Determine status based on fraud score
    if fraud_score >= 0.8:
        status = VerificationStatus.FRAUD_FLAGGED
        recommendation = "reject"
    elif fraud_score >= 0.5:
        status = VerificationStatus.MANUAL_REVIEW
        recommendation = "manual_review"
    elif fraud_score >= 0.2:
        status = VerificationStatus.PENDING
        recommendation = "review"
    else:
        status = VerificationStatus.AUTO_APPROVED
        recommendation = "auto_approve"
    
    # Store verification
    verification = Verification(
        verification_id=verification_id,
        job_id=job.id,
        photo_paths=photo_paths,
        photo_hashes=photo_hashes,
        submitted_lat=lat,
        submitted_lng=lng,
        exif_lat=exif_lat,
        exif_lng=exif_lng,
        geo_distance_m=geo_distance,
        fraud_score=fraud_score,
        fraud_flags=fraud_flags,
        status=status
    )
    db.add(verification)
    
    # Update job status
    if status == VerificationStatus.AUTO_APPROVED:
        job.status = JobStatus.COMPLETED
        job.completed_at = datetime.utcnow()
    else:
        job.status = JobStatus.VERIFICATION_PENDING
    
    db.commit()
    
    # Audit log
    audit = AuditLog(
        entity_type="verification",
        entity_id=verification_id,
        action="submitted",
        actor_type="installer",
        actor_id=job.installer_id,
        details={
            "photo_count": len(photos),
            "fraud_score": fraud_score,
            "fraud_flags": fraud_flags,
            "status": status.value
        }
    )
    db.add(audit)
    db.commit()
    
    return VerificationResponse(
        verification_id=verification_id,
        job_id=job_id,
        status=status.value,
        fraud_score=round(fraud_score, 2),
        fraud_flags=fraud_flags,
        geo_distance_m=geo_distance,
        recommendation=recommendation,
        audit_trail=[{
            "timestamp": datetime.utcnow().isoformat(),
            "action": "fraud_check_complete",
            "score": fraud_score,
            "flags": fraud_flags
        }]
    )


@router.get("/verify/{verification_code}", tags=["Verification"])
async def verify_assessment(verification_code: str, db: Session = Depends(get_db)):
    """
    Verify an assessment using QR code.
    Returns assessment details and audit trail.
    """
    
    # Find by QR code
    assessment = db.query(Assessment).filter(
        Assessment.qr_verification_code == verification_code
    ).first()
    
    if not assessment:
        # Try by verification_id
        verification = db.query(Verification).filter(
            Verification.verification_id == verification_code
        ).first()
        
        if verification:
            job = verification.job
            assessment = job.assessment if job else None
    
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    # Get audit trail
    audits = db.query(AuditLog).filter(
        AuditLog.entity_id == assessment.assessment_id
    ).order_by(AuditLog.created_at.desc()).all()
    
    return {
        "verified": True,
        "assessment_id": assessment.assessment_id,
        "site_id": assessment.site_id,
        "address": assessment.address,
        "created_at": assessment.created_at.isoformat(),
        "status": assessment.status.value,
        "annual_yield_liters": assessment.annual_yield_liters,
        "recommended_tank_liters": assessment.recommended_tank_liters,
        "net_cost_inr": assessment.net_cost_inr,
        "co2_avoided_kg": assessment.co2_avoided_kg,
        "audit_trail": [
            {
                "timestamp": a.created_at.isoformat(),
                "action": a.action,
                "entity": a.entity_type,
                "actor": a.actor_type,
                "details": a.details
            }
            for a in audits
        ]
    }


# ----- MONITORING -----

@router.get("/monitoring/{project_id}", tags=["Monitoring"])
async def get_monitoring_data(
    project_id: int,
    hours: int = Query(24, ge=1, le=168),
    db: Session = Depends(get_db)
):
    """Get telemetry data for a project."""
    
    cutoff = datetime.utcnow() - timedelta(hours=hours)
    
    readings = db.query(Telemetry).filter(
        Telemetry.project_id == project_id,
        Telemetry.timestamp >= cutoff
    ).order_by(Telemetry.timestamp.desc()).all()
    
    # Aggregate by sensor type
    tank_levels = [r for r in readings if r.sensor_type == "tank_level"]
    flow_readings = [r for r in readings if r.sensor_type == "flow_meter"]
    quality_readings = [r for r in readings if r.sensor_type == "water_quality"]
    
    # Calculate stats
    current_level = tank_levels[0].value if tank_levels else 0
    avg_level = sum(r.value for r in tank_levels) / len(tank_levels) if tank_levels else 0
    max_level = max((r.value for r in tank_levels), default=0)
    min_level = min((r.value for r in tank_levels), default=0)
    
    # Predict days until empty (simplified)
    daily_usage = sum(r.value for r in flow_readings) / (hours / 24) if flow_readings else 200
    days_until_empty = int(current_level / daily_usage) if daily_usage > 0 else 999
    
    # Alerts
    alerts = []
    if current_level > 4500:
        alerts.append({"type": "overflow_risk", "message": "Tank >90% full, overflow risk", "severity": "warning"})
    if current_level < 500:
        alerts.append({"type": "low_level", "message": "Tank <10% full", "severity": "critical"})
    
    return {
        "project_id": project_id,
        "period_hours": hours,
        "current_level": {
            "liters": current_level,
            "percent": round(current_level / 5000 * 100, 1),  # Assuming 5000L tank
            "last_updated": tank_levels[0].timestamp.isoformat() if tank_levels else None
        },
        "statistics": {
            "average_liters": round(avg_level, 0),
            "max_liters": max_level,
            "min_liters": min_level,
            "readings_count": len(tank_levels)
        },
        "trend_24h": [
            {
                "timestamp": r.timestamp.isoformat(),
                "value": r.value,
                "unit": r.unit
            }
            for r in tank_levels[:48]  # Max 48 readings
        ],
        "days_until_empty": days_until_empty,
        "alerts": alerts,
        "flow_total_liters": sum(r.value for r in flow_readings),
        "water_quality": {
            "ph": quality_readings[0].value if quality_readings else 7.0,
            "tds": 150  # Placeholder
        }
    }


# ----- PUBLIC DASHBOARD -----

@router.get("/public/dashboard", tags=["Public"])
async def get_public_dashboard(
    state: Optional[str] = None,
    ward_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get public transparency dashboard with ward-level aggregates."""
    
    # Get all completed assessments
    query = db.query(Assessment).filter(Assessment.status != AssessmentStatus.PENDING)
    
    if state:
        query = query.filter(Assessment.state == state)
    
    assessments = query.all()
    
    # Get wards
    wards = db.query(Ward).all()
    
    # Calculate totals
    total_projects = len(assessments)
    total_capture = sum(a.annual_yield_liters or 0 for a in assessments)
    total_investment = sum(a.total_cost_inr or 0 for a in assessments)
    total_co2 = sum(a.co2_avoided_kg or 0 for a in assessments)
    
    return {
        "summary": {
            "total_projects": total_projects,
            "total_capture_liters": round(total_capture, 0),
            "total_investment_inr": round(total_investment, 0),
            "co2_avoided_kg": round(total_co2, 2),
            "states_covered": len(set(a.state for a in assessments if a.state)),
            "avg_roi_years": round(
                sum(a.roi_years or 0 for a in assessments) / max(1, total_projects), 1
            )
        },
        "wards": [
            {
                "ward_id": w.ward_id,
                "ward_name": w.ward_name,
                "city": w.city,
                "total_projects": w.total_projects,
                "verified_projects": w.verified_projects,
                "total_capture_liters": w.total_capture_liters,
                "total_investment_inr": w.total_investment_inr
            }
            for w in wards
        ],
        "by_state": {
            state: len([a for a in assessments if a.state == state])
            for state in set(a.state for a in assessments if a.state)
        }
    }


@router.get("/public/export", tags=["Public"])
async def export_public_data(
    format: str = Query("csv", pattern="^(csv|geojson)$"),
    db: Session = Depends(get_db)
):
    """Export public data in CSV or GeoJSON format."""
    
    assessments = db.query(Assessment).filter(
        Assessment.status != AssessmentStatus.PENDING
    ).all()
    
    if format == "csv":
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "assessment_id", "site_id", "address", "state", "city",
            "roof_area_sqm", "annual_yield_liters", "recommended_tank_liters",
            "net_cost_inr", "roi_years", "co2_avoided_kg", "created_at"
        ])
        
        for a in assessments:
            writer.writerow([
                a.assessment_id, a.site_id, a.address, a.state, a.city,
                a.roof_area_sqm, a.annual_yield_liters, a.recommended_tank_liters,
                a.net_cost_inr, a.roi_years, a.co2_avoided_kg,
                a.created_at.isoformat() if a.created_at else ""
            ])
        
        from fastapi.responses import Response
        return Response(
            content=output.getvalue(),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=rainforge_public_data.csv"}
        )
    
    else:  # geojson
        features = []
        for a in assessments:
            if a.lat and a.lng:
                features.append({
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [a.lng, a.lat]
                    },
                    "properties": {
                        "assessment_id": a.assessment_id,
                        "site_id": a.site_id,
                        "address": a.address,
                        "annual_yield_liters": a.annual_yield_liters,
                        "net_cost_inr": a.net_cost_inr
                    }
                })
        
        return {
            "type": "FeatureCollection",
            "features": features
        }


# ----- INSTALLERS -----

@router.get("/installers", tags=["Installers"])
async def list_installers(
    active_only: bool = True,
    min_rpi: float = Query(0, ge=0, le=100),
    db: Session = Depends(get_db)
):
    """List installers with RPI scores."""
    
    query = db.query(Installer)
    
    if active_only:
        query = query.filter(Installer.is_active == True, Installer.is_blacklisted == False)
    
    if min_rpi > 0:
        query = query.filter(Installer.rpi_score >= min_rpi)
    
    installers = query.order_by(Installer.rpi_score.desc()).all()
    
    return {
        "installers": [
            {
                "id": i.id,
                "name": i.name,
                "company": i.company,
                "rpi_score": round(calculate_rpi(i), 1),
                "capacity_available": i.capacity_available,
                "capacity_max": i.capacity_max,
                "cert_level": i.cert_level,
                "warranty_months": i.warranty_months,
                "jobs_completed": i.jobs_completed,
                "sla_compliance_pct": i.sla_compliance_pct,
                "service_areas": i.service_areas.split(",") if i.service_areas else []
            }
            for i in installers
        ],
        "total": len(installers)
    }


@router.get("/installers/{installer_id}/rpi", tags=["Installers"])
async def get_installer_rpi(installer_id: int, db: Session = Depends(get_db)):
    """Get detailed RPI breakdown for an installer."""
    
    installer = db.query(Installer).filter(Installer.id == installer_id).first()
    if not installer:
        raise HTTPException(status_code=404, detail="Installer not found")
    
    # Calculate RPI components
    timeliness = installer.sla_compliance_pct * 0.25
    capacity_util = (1 - installer.capacity_available / max(1, installer.capacity_max)) * 100 * 0.15
    cost_efficiency = (1 / max(0.5, installer.avg_cost_factor)) * 100 * 0.20
    experience = min(100, installer.jobs_completed * 2) * 0.20
    cert_bonus = {"basic": 60, "certified": 80, "premium": 100}.get(installer.cert_level, 60) * 0.10
    warranty_score = min(100, installer.warranty_months * 5) * 0.10
    
    total_rpi = timeliness + capacity_util + cost_efficiency + experience + cert_bonus + warranty_score
    
    return {
        "installer_id": installer_id,
        "name": installer.name,
        "rpi_score": round(min(100, total_rpi), 1),
        "grade": "A" if total_rpi >= 90 else "B" if total_rpi >= 75 else "C" if total_rpi >= 60 else "D",
        "components": {
            "timeliness": {"value": installer.sla_compliance_pct, "weight": 0.25, "contribution": round(timeliness, 1)},
            "capacity_utilization": {"value": round((1 - installer.capacity_available / max(1, installer.capacity_max)) * 100, 1), "weight": 0.15, "contribution": round(capacity_util, 1)},
            "cost_efficiency": {"value": round((1 / max(0.5, installer.avg_cost_factor)) * 100, 1), "weight": 0.20, "contribution": round(cost_efficiency, 1)},
            "experience": {"value": installer.jobs_completed, "weight": 0.20, "contribution": round(experience, 1)},
            "certification": {"value": installer.cert_level, "weight": 0.10, "contribution": round(cert_bonus, 1)},
            "warranty": {"value": installer.warranty_months, "weight": 0.10, "contribution": round(warranty_score, 1)}
        }
    }


# ----- HEALTH CHECK -----

@router.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }


# ----- BATCH ASSESSMENT -----

class BatchAssessRequest(BaseModel):
    scenario: str = Field("cost_optimized", pattern="^(cost_optimized|max_capture|dry_season)$")

@router.post("/batch/assess", tags=["Assessment"])
async def batch_assess(
    file: UploadFile = File(...),
    scenario: str = Form("cost_optimized"),
    db: Session = Depends(get_db)
):
    """
    Batch assessment for CSV files (10-10,000 rows).
    Returns immediate results for demo mode.
    Required columns: site_id, address, roof_area_sqm, roof_material, lat, lng
    """
    import csv
    import io
    
    content = await file.read()
    decoded = content.decode('utf-8-sig')
    reader = csv.DictReader(io.StringIO(decoded))
    
    batch_id = generate_id("BATCH")
    results = []
    total_yield = 0
    total_cost = 0
    errors = []
    
    rows = list(reader)
    
    if len(rows) < 1:
        raise HTTPException(status_code=400, detail="CSV must have at least 1 row")
    if len(rows) > 10000:
        raise HTTPException(status_code=400, detail="CSV cannot exceed 10,000 rows")
    
    for i, row in enumerate(rows):
        try:
            site_id = row.get('site_id', f'SITE-{i+1:04d}')
            address = row.get('address', 'Unknown')
            roof_area = float(row.get('roof_area_sqm', 100))
            material = row.get('roof_material', 'concrete').lower()
            lat = float(row.get('lat', 28.6139))
            lng = float(row.get('lng', 77.2090))
            
            # Calculate yield
            rainfall_mm = 1200  # Default for Delhi region
            runoff_coeff = RUNOFF_COEFFICIENTS.get(material, 0.80)
            annual_yield = roof_area * rainfall_mm * runoff_coeff
            
            # Calculate scenario
            daily_demand = float(row.get('demand_l_per_day', 200))
            base_cost = roof_area * 450  # Base cost per sqm
            scenarios = calculate_scenarios(annual_yield, daily_demand, base_cost)
            
            selected_scenario = scenarios.get(scenario, scenarios['cost_optimized'])
            
            results.append({
                "row": i + 1,
                "site_id": site_id,
                "address": address,
                "roof_area_sqm": roof_area,
                "annual_yield_liters": round(annual_yield, 0),
                "tank_liters": selected_scenario['tank_liters'],
                "cost_inr": selected_scenario['cost_inr'],
                "roi_years": selected_scenario['roi_years'],
                "status": "success"
            })
            
            total_yield += annual_yield
            total_cost += selected_scenario['cost_inr']
            
        except Exception as e:
            errors.append({
                "row": i + 1,
                "site_id": row.get('site_id', f'ROW-{i+1}'),
                "error": str(e)
            })
    
    # Calculate subsidy (Delhi default 50%)
    subsidy_pct = 50
    net_cost = total_cost * (1 - subsidy_pct / 100)
    
    return {
        "batch_id": batch_id,
        "status": "completed",
        "total_rows": len(rows),
        "processed": len(results),
        "errors": len(errors),
        "scenario": scenario,
        "summary": {
            "total_annual_yield_liters": round(total_yield, 0),
            "total_cost_inr": round(total_cost, 0),
            "subsidy_pct": subsidy_pct,
            "net_cost_inr": round(net_cost, 0),
            "co2_avoided_kg": round(total_yield * 0.7 / 1000, 1),
            "avg_roi_years": round(sum(r['roi_years'] for r in results) / max(1, len(results)), 1)
        },
        "results": results[:100],  # Return first 100 for immediate response
        "errors": errors,
        "download_url": f"/api/v1/batch/{batch_id}/download"
    }


@router.get("/batch/sample-csv", tags=["Assessment"])
async def get_sample_csv():
    """Get sample CSV template for batch upload."""
    sample_content = """site_id,address,roof_area_sqm,roof_material,lat,lng,owner_id,floors,people
SITE001,Municipal School Sector 5,250,concrete,28.7041,77.1025,OWN001,2,150
SITE002,Community Health Center,180,tiles,28.5823,77.0500,OWN002,1,50
SITE003,District Court Complex,450,concrete,28.5244,77.2163,OWN003,3,200"""
    
    return {
        "content": sample_content,
        "filename": "rainforge_bulk_template.csv",
        "columns": ["site_id", "address", "roof_area_sqm", "roof_material", "lat", "lng", "owner_id", "floors", "people"],
        "required": ["site_id", "address", "roof_area_sqm", "roof_material", "lat", "lng"]
    }


# ----- TELEMETRY INGESTION -----

class TelemetryReading(BaseModel):
    device_id: str
    project_id: int
    timestamp: Optional[datetime] = None
    tank_level_liters: float
    battery_pct: Optional[float] = None
    signal_rssi: Optional[int] = None

@router.post("/telemetry", tags=["Telemetry"])
async def ingest_telemetry(reading: TelemetryReading, db: Session = Depends(get_db)):
    """
    HTTP endpoint for telemetry ingestion.
    Alternative to MQTT for devices that can't use MQTT.
    """
    
    telemetry = Telemetry(
        project_id=reading.project_id,
        device_id=reading.device_id,
        timestamp=reading.timestamp or datetime.utcnow(),
        sensor_type="tank_level",
        value=reading.tank_level_liters,
        unit="liters",
        battery_pct=reading.battery_pct,
        signal_rssi=reading.signal_rssi
    )
    db.add(telemetry)
    db.commit()
    db.refresh(telemetry)
    
    return {
        "success": True,
        "reading_id": telemetry.id,
        "project_id": reading.project_id,
        "timestamp": telemetry.timestamp.isoformat(),
        "value": reading.tank_level_liters
    }


@router.post("/telemetry/batch", tags=["Telemetry"])
async def ingest_telemetry_batch(readings: List[TelemetryReading], db: Session = Depends(get_db)):
    """Batch ingestion of multiple telemetry readings."""
    
    ingested = []
    for reading in readings:
        telemetry = Telemetry(
            project_id=reading.project_id,
            device_id=reading.device_id,
            timestamp=reading.timestamp or datetime.utcnow(),
            sensor_type="tank_level",
            value=reading.tank_level_liters,
            unit="liters",
            battery_pct=reading.battery_pct,
            signal_rssi=reading.signal_rssi
        )
        db.add(telemetry)
        ingested.append(reading.device_id)
    
    db.commit()
    
    return {
        "success": True,
        "ingested_count": len(ingested),
        "devices": list(set(ingested))
    }


# ============== DEMO MODE INFRASTRUCTURE ==============

@router.get("/health", tags=["System"])
async def health_check(db: Session = Depends(get_db)):
    """
    Health endpoint for demo and production monitoring.
    Returns status of all system components.
    """
    import os
    
    demo_mode = os.getenv("DEMO_MODE", "false").lower() == "true"
    
    # Check database
    try:
        db.execute("SELECT 1")
        db_status = "connected"
    except:
        db_status = "disconnected"
    
    # Check Redis (mock for demo)
    redis_status = "unavailable"  # Would check real Redis in production
    
    # Check MQTT (mock for demo)
    mqtt_status = "unavailable"  # Would check real MQTT in production
    
    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "database": db_status,
        "redis": redis_status,
        "mqtt": mqtt_status,
        "demo_mode": demo_mode,
        "demo_ribbon": "🎯 DEMO MODE – SAFE DATA" if demo_mode else None,
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }


@router.post("/admin/demo/reset", tags=["Admin"])
async def reset_demo_data(db: Session = Depends(get_db)):
    """
    🎯 DEMO INFRASTRUCTURE: Reset all demo data.
    
    Resets:
    - Verifications
    - Telemetry (last 24h regenerated)
    - Audit logs
    
    Re-seeds:
    - 50 sites/assessments
    - 6 installers
    - 6 fraud photo scenarios
    """
    import os
    from app.seed_data import seed_demo_data
    
    demo_mode = os.getenv("DEMO_MODE", "true").lower() == "true"
    
    if not demo_mode:
        raise HTTPException(
            status_code=403,
            detail="Demo reset only available in DEMO_MODE"
        )
    
    try:
        # Clear verification records
        db.query(Verification).delete()
        
        # Clear recent telemetry (keep some base data)
        recent_time = datetime.utcnow() - timedelta(hours=48)
        db.query(Telemetry).filter(Telemetry.timestamp > recent_time).delete()
        
        # Clear audit logs (but keep for demo story if needed)
        db.query(AuditLog).filter(AuditLog.action.like("%demo%")).delete()
        
        db.commit()
        
        # Re-seed demo data
        seed_demo_data(db)
        
        # Count what we have
        sites_count = db.query(Assessment).count()
        installers_count = db.query(Installer).count()
        
        # Create demo fraud verifications
        fraud_scenarios = [
            {"type": "genuine", "score": 0.05, "flags": []},
            {"type": "gps_mismatch", "score": 0.65, "flags": ["GPS_MISMATCH"]},
            {"type": "duplicate", "score": 0.75, "flags": ["DUPLICATE_PHOTO"]},
            {"type": "no_exif", "score": 0.35, "flags": ["EXIF_MISSING"]},
            {"type": "photoshop", "score": 0.55, "flags": ["SOFTWARE_MANIPULATION"]},
            {"type": "multi_fraud", "score": 0.92, "flags": ["DUPLICATE_PHOTO", "GPS_MISMATCH"]}
        ]
        
        for scenario in fraud_scenarios:
            verification = Verification(
                project_id=1,
                submission_type="installation_complete",
                status="rejected" if scenario["score"] >= 0.8 else "pending",
                fraud_score=scenario["score"],
                metadata={
                    "fraud_flags": scenario["flags"],
                    "scenario_type": scenario["type"],
                    "geo_distance_m": 487.3 if "GPS_MISMATCH" in scenario["flags"] else 12.5
                }
            )
            db.add(verification)
        
        db.commit()
        
        return {
            "seeded": True,
            "sites": sites_count,
            "installers": installers_count,
            "fraud_scenarios": len(fraud_scenarios),
            "message": "Demo data reset successfully",
            "demo_ribbon": "🎯 DEMO MODE – SAFE DATA",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Demo reset failed: {str(e)}"
        )


@router.get("/demo/status", tags=["Admin"])
async def get_demo_status(db: Session = Depends(get_db)):
    """Get current demo data status."""
    import os
    
    demo_mode = os.getenv("DEMO_MODE", "true").lower() == "true"
    
    return {
        "demo_mode": demo_mode,
        "demo_ribbon": "🎯 DEMO MODE – SAFE DATA" if demo_mode else None,
        "counts": {
            "assessments": db.query(Assessment).count(),
            "jobs": db.query(Job).count(),
            "installers": db.query(Installer).count(),
            "verifications": db.query(Verification).count(),
            "escrows": db.query(Escrow).count(),
            "telemetry_readings": db.query(Telemetry).count()
        },
        "fraud_scenarios_ready": db.query(Verification).filter(Verification.fraud_score > 0.5).count(),
        "timestamp": datetime.utcnow().isoformat()
    }

