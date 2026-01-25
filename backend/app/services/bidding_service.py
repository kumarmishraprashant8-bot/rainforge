"""
RainForge Bidding Service
Handles competitive bidding, scoring, and bid awarding.
"""

from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid


class BidStatus(str, Enum):
    PENDING = "pending"
    AWARDED = "awarded"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


@dataclass
class BidScoreWeights:
    """Weights for bid composite scoring."""
    price: float = 0.35
    timeline: float = 0.20
    warranty: float = 0.15
    rpi: float = 0.30
    
    def normalize(self) -> 'BidScoreWeights':
        total = self.price + self.timeline + self.warranty + self.rpi
        if total == 0:
            return BidScoreWeights()
        return BidScoreWeights(
            price=self.price / total,
            timeline=self.timeline / total,
            warranty=self.warranty / total,
            rpi=self.rpi / total
        )


@dataclass
class Bid:
    id: str
    job_id: int
    installer_id: int
    installer_name: str
    installer_rpi: float
    price: float
    timeline_days: int
    warranty_months: int
    notes: Optional[str] = None
    score: float = 0.0
    status: BidStatus = BidStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Job:
    id: int
    estimated_cost: float
    max_timeline_days: int = 30
    min_warranty_months: int = 12


class BiddingService:
    """
    Manages competitive bidding process for RWH jobs.
    """
    
    # In-memory bid storage (would be DB in production)
    _bids: Dict[str, Bid] = {}
    _job_bids: Dict[int, List[str]] = {}  # job_id -> list of bid_ids
    _job_status: Dict[int, str] = {}  # job_id -> open/closed
    
    DEFAULT_WEIGHTS = BidScoreWeights()
    
    @classmethod
    def open_bidding(cls, job_id: int, deadline_hours: int = 72) -> Dict:
        """Open a job for competitive bidding."""
        cls._job_status[job_id] = "open"
        cls._job_bids[job_id] = []
        
        return {
            "job_id": job_id,
            "status": "open",
            "deadline_hours": deadline_hours,
            "message": f"Job #{job_id} is now open for bids"
        }
    
    @classmethod
    def close_bidding(cls, job_id: int) -> Dict:
        """Close bidding for a job."""
        cls._job_status[job_id] = "closed"
        bid_count = len(cls._job_bids.get(job_id, []))
        
        return {
            "job_id": job_id,
            "status": "closed",
            "total_bids": bid_count
        }
    
    @classmethod
    def submit_bid(
        cls,
        job_id: int,
        installer_id: int,
        installer_name: str,
        installer_rpi: float,
        price: float,
        timeline_days: int,
        warranty_months: int = 12,
        notes: Optional[str] = None
    ) -> Bid:
        """Submit a bid for a job."""
        
        if cls._job_status.get(job_id) != "open":
            raise ValueError(f"Job {job_id} is not open for bidding")
        
        # Check for duplicate bid from same installer
        existing_bids = cls._job_bids.get(job_id, [])
        for bid_id in existing_bids:
            if cls._bids[bid_id].installer_id == installer_id:
                raise ValueError(f"Installer {installer_id} has already bid on this job")
        
        bid = Bid(
            id=str(uuid.uuid4())[:8],
            job_id=job_id,
            installer_id=installer_id,
            installer_name=installer_name,
            installer_rpi=installer_rpi,
            price=price,
            timeline_days=timeline_days,
            warranty_months=warranty_months,
            notes=notes
        )
        
        cls._bids[bid.id] = bid
        if job_id not in cls._job_bids:
            cls._job_bids[job_id] = []
        cls._job_bids[job_id].append(bid.id)
        
        return bid
    
    @classmethod
    def calculate_bid_score(
        cls,
        bid: Bid,
        job: Job,
        weights: Optional[BidScoreWeights] = None
    ) -> float:
        """Calculate composite score for a bid."""
        w = (weights or cls.DEFAULT_WEIGHTS).normalize()
        
        # Price score: Lower is better, normalized against estimate
        price_ratio = bid.price / job.estimated_cost if job.estimated_cost > 0 else 1
        price_score = max(0, min(100, (2 - price_ratio) * 50))  # 50% below = 100, 50% above = 0
        
        # Timeline score: Faster is better
        timeline_ratio = bid.timeline_days / job.max_timeline_days if job.max_timeline_days > 0 else 1
        timeline_score = max(0, min(100, (2 - timeline_ratio) * 50))
        
        # Warranty score: Longer is better
        warranty_ratio = bid.warranty_months / job.min_warranty_months if job.min_warranty_months > 0 else 1
        warranty_score = min(100, warranty_ratio * 50)  # 2x warranty = 100
        
        # RPI score: Direct use
        rpi_score = bid.installer_rpi
        
        # Weighted composite
        composite = (
            price_score * w.price +
            timeline_score * w.timeline +
            warranty_score * w.warranty +
            rpi_score * w.rpi
        )
        
        return round(composite, 2)
    
    @classmethod
    def rank_bids(
        cls,
        job_id: int,
        job: Job,
        weights: Optional[BidScoreWeights] = None
    ) -> List[Dict]:
        """Get ranked list of bids for a job."""
        bid_ids = cls._job_bids.get(job_id, [])
        
        ranked = []
        for bid_id in bid_ids:
            bid = cls._bids.get(bid_id)
            if bid and bid.status == BidStatus.PENDING:
                score = cls.calculate_bid_score(bid, job, weights)
                bid.score = score
                
                ranked.append({
                    "bid_id": bid.id,
                    "installer_id": bid.installer_id,
                    "installer_name": bid.installer_name,
                    "installer_rpi": bid.installer_rpi,
                    "price": bid.price,
                    "timeline_days": bid.timeline_days,
                    "warranty_months": bid.warranty_months,
                    "score": score,
                    "created_at": bid.created_at.isoformat()
                })
        
        # Sort by score descending
        ranked.sort(key=lambda x: x["score"], reverse=True)
        
        # Add rank
        for i, item in enumerate(ranked):
            item["rank"] = i + 1
        
        return ranked
    
    @classmethod
    def award_bid(cls, bid_id: str, awarded_by: int = 0) -> Dict:
        """Award a bid to an installer."""
        if bid_id not in cls._bids:
            raise ValueError(f"Bid {bid_id} not found")
        
        bid = cls._bids[bid_id]
        
        if bid.status != BidStatus.PENDING:
            raise ValueError(f"Bid {bid_id} cannot be awarded (status: {bid.status})")
        
        # Award this bid
        bid.status = BidStatus.AWARDED
        
        # Reject all other bids for this job
        for other_bid_id in cls._job_bids.get(bid.job_id, []):
            if other_bid_id != bid_id:
                cls._bids[other_bid_id].status = BidStatus.REJECTED
        
        # Close bidding
        cls._job_status[bid.job_id] = "closed"
        
        return {
            "bid_id": bid_id,
            "job_id": bid.job_id,
            "installer_id": bid.installer_id,
            "installer_name": bid.installer_name,
            "awarded_price": bid.price,
            "timeline_days": bid.timeline_days,
            "warranty_months": bid.warranty_months,
            "message": f"Bid awarded to {bid.installer_name}"
        }
    
    @classmethod
    def get_bids_for_job(cls, job_id: int) -> List[Bid]:
        """Get all bids for a job."""
        bid_ids = cls._job_bids.get(job_id, [])
        return [cls._bids[bid_id] for bid_id in bid_ids if bid_id in cls._bids]
    
    @classmethod
    def withdraw_bid(cls, bid_id: str, installer_id: int) -> Dict:
        """Allow installer to withdraw their bid."""
        if bid_id not in cls._bids:
            raise ValueError(f"Bid {bid_id} not found")
        
        bid = cls._bids[bid_id]
        
        if bid.installer_id != installer_id:
            raise ValueError("Only the bidding installer can withdraw")
        
        if bid.status != BidStatus.PENDING:
            raise ValueError("Only pending bids can be withdrawn")
        
        bid.status = BidStatus.WITHDRAWN
        
        return {"bid_id": bid_id, "status": "withdrawn"}
    
    @classmethod
    def clear_demo_data(cls):
        """Clear all demo data."""
        cls._bids = {}
        cls._job_bids = {}
        cls._job_status = {}


# ============== DEMO ==============

def demo_bidding():
    """Demo the bidding system."""
    from app.services.allocation_engine import get_demo_installers
    
    BiddingService.clear_demo_data()
    
    job = Job(id=101, estimated_cost=96000, max_timeline_days=30)
    installers = get_demo_installers()[:5]
    
    # Open bidding
    BiddingService.open_bidding(job.id)
    
    # Submit bids
    for i, inst in enumerate(installers):
        price = 96000 * (0.85 + i * 0.05)  # Varying prices
        timeline = 20 + i * 3
        warranty = 12 + (i % 3) * 6
        
        BiddingService.submit_bid(
            job_id=job.id,
            installer_id=inst.id,
            installer_name=inst.name,
            installer_rpi=inst.rpi_score,
            price=price,
            timeline_days=timeline,
            warranty_months=warranty
        )
    
    # Rank bids
    ranked = BiddingService.rank_bids(job.id, job)
    
    print("Bid Rankings:")
    for bid in ranked:
        print(f"  #{bid['rank']}: {bid['installer_name']} - ₹{bid['price']:.0f} - Score: {bid['score']}")
    
    # Award top bid
    if ranked:
        result = BiddingService.award_bid(ranked[0]["bid_id"])
        print(f"\nAwarded to: {result['installer_name']}")
    
    return ranked


if __name__ == "__main__":
    demo_bidding()
