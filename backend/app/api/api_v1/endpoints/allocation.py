"""
RainForge P0 Allocation, Auction & Bidding API Endpoints
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime, timedelta

from app.services.allocation_engine import (
    AllocationEngine, AllocationMode, AllocationWeights, 
    Job, Installer, get_demo_installers
)
from app.services.bidding_service import BiddingService, BidScoreWeights, Job as BidJob
from app.services.rpi_calculator import RPICalculator, generate_demo_rpi
from app.models.database import get_db, Auction, Bid as DbBid

router = APIRouter()


# ============== REQUEST/RESPONSE MODELS ==============

class AllocationRequest(BaseModel):
    job_id: int
    address: str
    lat: float = 28.6139
    lng: float = 77.2090
    estimated_cost: float = 96000
    mode: str = "gov_optimized"
    force_installer_id: Optional[int] = None


class AllocationWeightsUpdate(BaseModel):
    capacity: float = 0.20
    rpi: float = 0.30
    cost_band: float = 0.20
    distance: float = 0.15
    sla_history: float = 0.15


class BidSubmission(BaseModel):
    job_id: int
    installer_id: int
    installer_name: str
    installer_rpi: float = 80.0
    price: float
    timeline_days: int
    warranty_months: int = 12
    notes: Optional[str] = None


class OpenBidRequest(BaseModel):
    deadline_hours: int = 72


# ============== ALLOCATION ENDPOINTS ==============

@router.post("/allocate")
def allocate_job(request: AllocationRequest):
    """
    Run allocation engine to recommend installer for a job.
    """
    try:
        job = Job(
            id=request.job_id,
            address=request.address,
            lat=request.lat,
            lng=request.lng,
            estimated_cost_inr=request.estimated_cost
        )
        
        installers = get_demo_installers()
        mode = AllocationMode(request.mode)
        
        result = AllocationEngine.allocate(
            job=job,
            installers=installers,
            mode=mode,
            force_installer_id=request.force_installer_id
        )
        
        return {
            "job_id": result.job_id,
            "recommended_installer": {
                "id": result.installer_id,
                "name": result.installer_name,
                "score": result.score
            },
            "score_breakdown": result.score_breakdown,
            "alternatives": result.alternatives,
            "reason": AllocationEngine.explain_allocation(result),
            "mode": mode.value
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/allocation-weights")
def get_allocation_weights():
    """Get current allocation weights."""
    weights = AllocationEngine.get_weights()
    return {
        "capacity": weights.capacity,
        "rpi": weights.rpi,
        "cost_band": weights.cost_band,
        "distance": weights.distance,
        "sla_history": weights.sla_history
    }


@router.put("/allocation-weights")
def update_allocation_weights(weights: AllocationWeightsUpdate):
    """Admin endpoint to update allocation weights."""
    new_weights = AllocationWeights(
        capacity=weights.capacity,
        rpi=weights.rpi,
        cost_band=weights.cost_band,
        distance=weights.distance,
        sla_history=weights.sla_history
    )
    AllocationEngine.set_admin_weights(new_weights)
    
    normalized = new_weights.normalize()
    return {
        "message": "Weights updated",
        "normalized_weights": {
            "capacity": round(normalized.capacity, 3),
            "rpi": round(normalized.rpi, 3),
            "cost_band": round(normalized.cost_band, 3),
            "distance": round(normalized.distance, 3),
            "sla_history": round(normalized.sla_history, 3)
        }
    }


# ============== BIDDING ENDPOINTS ==============

@router.post("/jobs/{job_id}/open-bid")
def open_bidding(job_id: int, request: OpenBidRequest):
    """Open a job for competitive bidding."""
    result = BiddingService.open_bidding(job_id, request.deadline_hours)
    return result


@router.post("/jobs/{job_id}/close-bid")
def close_bidding(job_id: int):
    """Close bidding for a job."""
    result = BiddingService.close_bidding(job_id)
    return result


@router.post("/bids")
def submit_bid(bid: BidSubmission):
    """Submit a bid for a job."""
    try:
        result = BiddingService.submit_bid(
            job_id=bid.job_id,
            installer_id=bid.installer_id,
            installer_name=bid.installer_name,
            installer_rpi=bid.installer_rpi,
            price=bid.price,
            timeline_days=bid.timeline_days,
            warranty_months=bid.warranty_months,
            notes=bid.notes
        )
        return {
            "bid_id": result.id,
            "job_id": result.job_id,
            "installer_id": result.installer_id,
            "price": result.price,
            "status": result.status.value,
            "message": "Bid submitted successfully"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/bids")
def get_bids(job_id: int):
    """Get all bids for a job with ranking."""
    job = BidJob(id=job_id, estimated_cost=96000)  # Demo values
    ranked = BiddingService.rank_bids(job_id, job)
    return {
        "job_id": job_id,
        "total_bids": len(ranked),
        "bids": ranked
    }


@router.post("/bids/{bid_id}/award")
def award_bid(bid_id: str):
    """Award a bid to an installer."""
    try:
        result = BiddingService.award_bid(bid_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/bids/{bid_id}/withdraw")
def withdraw_bid(bid_id: str, installer_id: int):
    """Withdraw a bid."""
    try:
        result = BiddingService.withdraw_bid(bid_id, installer_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============== RPI ENDPOINTS ==============

@router.get("/installers/{installer_id}/rpi")
def get_installer_rpi(installer_id: int):
    """Get RPI score and breakdown for an installer."""
    rpi_data = generate_demo_rpi(installer_id)
    return rpi_data


@router.get("/installers")
def list_installers():
    """List all installers with RPI scores."""
    installers = get_demo_installers()
    result = []
    for inst in installers:
        rpi = generate_demo_rpi(inst.id)
        result.append({
            "id": inst.id,
            "name": inst.name,
            "company": inst.company,
            "lat": inst.lat,
            "lng": inst.lng,
            "rpi_score": rpi["score"],
            "rpi_grade": rpi["grade"],
            "badge_color": rpi["badge_color"],
            "capacity_available": inst.capacity_available,
            "sla_compliance_pct": inst.sla_compliance_pct,
            "is_blacklisted": inst.is_blacklisted
        })
    return {"installers": result}


# ============== P0 AUCTION ENDPOINTS ==============

@router.post("/auction/create")
def create_auction(
    job_id: int,
    assessment_id: str,
    deadline_hours: int = 72,
    min_bid_inr: Optional[float] = None,
    max_bid_inr: Optional[float] = None,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    P0: Create auction for a job with deadline.
    """
    open_until = datetime.now() + timedelta(hours=deadline_hours)
    
    auction = Auction(
        job_id=job_id,
        assessment_id=assessment_id,
        open_until=open_until,
        min_bid_amount=min_bid_inr,
        max_bid_amount=max_bid_inr,
        required_certifications=["RWH_CERTIFIED"],
        weighting={"price": 0.4, "rpi": 0.4, "timeline": 0.2}
    )
    
    db.add(auction)
    db.commit()
    db.refresh(auction)
    
    return {
        "auction_id": auction.id,
        "job_id": job_id,
        "status": auction.status,
        "open_until": open_until.isoformat(),
        "deadline_hours": deadline_hours,
        "message": "Auction created successfully. Open for bidding."
    }


@router.post("/auction/{auction_id}/bid")
def submit_auction_bid(
    auction_id: int,
    installer_id: int,
    price_inr: float,
    timeline_days: int,
    warranty_months: int = 12,
    notes: Optional[str] = None,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    P0: Submit bid for an auction.
    """
    auction = db.query(Auction).filter(Auction.id == auction_id).first()
    
    if not auction:
        raise HTTPException(status_code=404, detail="Auction not found")
    
    if auction.status != "open":
        raise HTTPException(status_code=400, detail="Auction is not open for bidding")
    
    if datetime.now() > auction.open_until:
        raise HTTPException(status_code=400, detail="Auction deadline has passed")
    
    # Create bid
    bid = DbBid(
        project_id=auction.job_id,
        installer_id=None,  # UUID type in schema, needs adjustment
        bid_amount=price_inr,
        timeline_days=timeline_days,
        warranty_months=warranty_months,
        scope_of_work=notes,
        status="submitted"
    )
    
    db.add(bid)
    db.commit()
    db.refresh(bid)
    
    return {
        "bid_id": bid.id,
        "auction_id": auction_id,
        "installer_id": installer_id,
        "price_inr": price_inr,
        "timeline_days": timeline_days,
        "status": "submitted",
        "message": "Bid submitted successfully"
    }


@router.post("/auction/{auction_id}/award")
def award_auction(
    auction_id: int,
    winning_bid_id: int,
    admin_notes: Optional[str] = None,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    P0: Award auction to winning bidder and create escrow.
    """
    auction = db.query(Auction).filter(Auction.id == auction_id).first()
    
    if not auction:
        raise HTTPException(status_code=404, detail="Auction not found")
    
    bid = db.query(DbBid).filter(DbBid.id == winning_bid_id).first()
    
    if not bid:
        raise HTTPException(status_code=404, detail="Bid not found")
    
    # Update auction status
    auction.status = "awarded"
    auction.winning_bid_id = winning_bid_id
    auction.awarded_at = datetime.now()
    
    # Update bid status
    bid.status = "awarded"
    bid.is_awarded = True
    
    db.commit()
    
    return {
        "auction_id": auction_id,
        "winning_bid_id": winning_bid_id,
        "installer_id": bid.installer_id,
        "awarded_amount": bid.bid_amount,
        "status": "awarded",
        "awarded_at": auction.awarded_at.isoformat(),
        "message": "Auction awarded successfully. Escrow will be created."
    }
