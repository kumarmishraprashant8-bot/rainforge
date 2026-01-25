"""
RainForge Allocation & Bidding API Endpoints
"""

from fastapi import APIRouter, HTTPException
from typing import Optional, List
from pydantic import BaseModel
from app.services.allocation_engine import (
    AllocationEngine, AllocationMode, AllocationWeights, 
    Job, Installer, get_demo_installers
)
from app.services.bidding_service import BiddingService, BidScoreWeights, Job as BidJob
from app.services.rpi_calculator import RPICalculator, generate_demo_rpi

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
