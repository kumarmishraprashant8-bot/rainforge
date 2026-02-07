"""
Contractor Marketplace Service
Quote management, work orders, milestones, and ratings.
"""

from datetime import datetime, date, timedelta
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
import logging
import random
import string

logger = logging.getLogger(__name__)


@dataclass
class ContractorProfile:
    """Contractor profile."""
    id: str
    company_name: str
    owner_name: str
    phone: str
    city: str
    state: str
    years_experience: int = 0
    projects_completed: int = 0
    average_rating: float = 0.0
    total_reviews: int = 0
    verified: bool = False
    certifications: List[str] = field(default_factory=list)
    service_areas: List[str] = field(default_factory=list)


class ContractorMarketplaceService:
    """
    Service for managing contractor marketplace.
    
    Features:
    - Contractor registration and verification
    - Quote requests and responses
    - Work order management
    - Milestone tracking with photo verification
    - Payment processing
    - Review and rating system
    - Defect reporting and warranty claims
    """
    
    def __init__(self):
        self.contractors: Dict[str, Dict] = {}
        self.quote_requests: Dict[str, Dict] = {}
        self.quotes: Dict[str, Dict] = {}
        self.work_orders: Dict[str, Dict] = {}
        self.milestones: Dict[str, Dict] = {}
        self.reviews: Dict[str, Dict] = {}
        self.defect_reports: Dict[str, Dict] = {}
        
        # Seed some demo contractors
        self._seed_demo_contractors()
    
    def _seed_demo_contractors(self):
        """Seed demo contractor data."""
        demo_contractors = [
            {
                "id": "CTR001",
                "company_name": "AquaHarvest Solutions",
                "owner_name": "Rajesh Kumar",
                "phone": "+919876543210",
                "email": "rajesh@aquaharvest.in",
                "city": "Bangalore",
                "state": "Karnataka",
                "years_experience": 8,
                "projects_completed": 150,
                "average_rating": 4.7,
                "total_reviews": 89,
                "verified": True,
                "certifications": ["ISO 9001", "Government Empanelled"],
                "service_areas": ["Bangalore", "Mysore", "Mangalore"]
            },
            {
                "id": "CTR002",
                "company_name": "JalSanchay Enterprises",
                "owner_name": "Suresh Patel",
                "phone": "+919888777666",
                "email": "suresh@jalsanchay.com",
                "city": "Ahmedabad",
                "state": "Gujarat",
                "years_experience": 12,
                "projects_completed": 280,
                "average_rating": 4.8,
                "total_reviews": 156,
                "verified": True,
                "certifications": ["GRIHA Certified", "IGBC Approved"],
                "service_areas": ["Ahmedabad", "Surat", "Vadodara", "Rajkot"]
            },
            {
                "id": "CTR003",
                "company_name": "RainCatch India",
                "owner_name": "Priya Sharma",
                "phone": "+919777888999",
                "email": "priya@raincatch.in",
                "city": "Chennai",
                "state": "Tamil Nadu",
                "years_experience": 6,
                "projects_completed": 95,
                "average_rating": 4.5,
                "total_reviews": 52,
                "verified": True,
                "certifications": ["TNPCB Registered"],
                "service_areas": ["Chennai", "Coimbatore", "Madurai"]
            },
        ]
        
        for contractor in demo_contractors:
            self.contractors[contractor["id"]] = contractor
    
    # ==================== CONTRACTOR MANAGEMENT ====================
    
    def register_contractor(
        self,
        company_name: str,
        owner_name: str,
        phone: str,
        email: str,
        city: str,
        state: str,
        years_experience: int = 0,
        certifications: List[str] = None,
        service_areas: List[str] = None
    ) -> Dict[str, Any]:
        """Register a new contractor."""
        
        contractor_id = f"CTR{random.randint(100, 999)}"
        
        contractor = {
            "id": contractor_id,
            "company_name": company_name,
            "owner_name": owner_name,
            "phone": phone,
            "email": email,
            "city": city,
            "state": state,
            "years_experience": years_experience,
            "projects_completed": 0,
            "average_rating": 0.0,
            "total_reviews": 0,
            "verified": False,
            "status": "pending_verification",
            "certifications": certifications or [],
            "service_areas": service_areas or [city],
            "created_at": datetime.utcnow().isoformat()
        }
        
        self.contractors[contractor_id] = contractor
        logger.info(f"Registered contractor: {contractor_id}")
        
        return contractor
    
    def get_contractor(self, contractor_id: str) -> Optional[Dict]:
        """Get contractor by ID."""
        return self.contractors.get(contractor_id)
    
    def search_contractors(
        self,
        city: Optional[str] = None,
        state: Optional[str] = None,
        min_rating: float = 0,
        verified_only: bool = True
    ) -> List[Dict]:
        """Search contractors by criteria."""
        
        results = []
        
        for contractor in self.contractors.values():
            # Filter by verification
            if verified_only and not contractor.get("verified"):
                continue
            
            # Filter by rating
            if contractor.get("average_rating", 0) < min_rating:
                continue
            
            # Filter by location
            if city and city not in contractor.get("service_areas", []):
                continue
            
            if state and contractor.get("state") != state:
                continue
            
            results.append(contractor)
        
        # Sort by rating
        results.sort(key=lambda x: x.get("average_rating", 0), reverse=True)
        
        return results
    
    # ==================== QUOTE MANAGEMENT ====================
    
    def create_quote_request(
        self,
        project_id: int,
        user_id: int,
        property_address: str,
        city: str,
        state: str,
        roof_area_sqm: float,
        tank_capacity_liters: int,
        requirements_description: str,
        contact_name: str,
        contact_phone: str,
        includes_recharge: bool = False,
        preferred_start_date: Optional[date] = None,
        budget_min: Optional[float] = None,
        budget_max: Optional[float] = None
    ) -> Dict[str, Any]:
        """Create a quote request."""
        
        request_id = f"QR-{project_id}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
        quote_request = {
            "request_id": request_id,
            "project_id": project_id,
            "user_id": user_id,
            
            # Property
            "property_address": property_address,
            "city": city,
            "state": state,
            
            # Scope
            "roof_area_sqm": roof_area_sqm,
            "tank_capacity_liters": tank_capacity_liters,
            "includes_recharge": includes_recharge,
            "requirements_description": requirements_description,
            
            # Preferences
            "preferred_start_date": preferred_start_date.isoformat() if preferred_start_date else None,
            "budget_min_inr": budget_min,
            "budget_max_inr": budget_max,
            
            # Contact
            "contact_name": contact_name,
            "contact_phone": contact_phone,
            
            # Status
            "status": "open",
            "quotes_received": 0,
            
            # Timestamps
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(days=7)).isoformat()
        }
        
        self.quote_requests[request_id] = quote_request
        
        # Notify matching contractors (in production, send actual notifications)
        matching_contractors = self.search_contractors(city=city, state=state)
        logger.info(f"Quote request {request_id} created. Notifying {len(matching_contractors)} contractors.")
        
        return quote_request
    
    def submit_quote(
        self,
        quote_request_id: str,
        contractor_id: str,
        material_cost: float,
        labor_cost: float,
        estimated_days: int,
        proposed_start_date: date,
        scope_of_work: str,
        materials_included: List[str],
        warranty_months: int = 12,
        payment_terms: str = "20% advance, 80% on completion"
    ) -> Dict[str, Any]:
        """Submit a quote for a request."""
        
        if quote_request_id not in self.quote_requests:
            raise ValueError(f"Quote request not found: {quote_request_id}")
        
        if contractor_id not in self.contractors:
            raise ValueError(f"Contractor not found: {contractor_id}")
        
        quote_request = self.quote_requests[quote_request_id]
        contractor = self.contractors[contractor_id]
        
        quote_id = f"Q-{contractor_id}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
        total_cost = material_cost + labor_cost
        
        quote = {
            "quote_id": quote_id,
            "quote_request_id": quote_request_id,
            "contractor_id": contractor_id,
            "contractor_name": contractor["company_name"],
            "project_id": quote_request["project_id"],
            
            # Pricing
            "material_cost": material_cost,
            "labor_cost": labor_cost,
            "total_cost": total_cost,
            
            # Timeline
            "estimated_days": estimated_days,
            "proposed_start_date": proposed_start_date.isoformat(),
            "proposed_end_date": (proposed_start_date + timedelta(days=estimated_days)).isoformat(),
            
            # Scope
            "scope_of_work": scope_of_work,
            "materials_included": materials_included,
            
            # Terms
            "warranty_months": warranty_months,
            "payment_terms": payment_terms,
            "advance_percent": 20,
            
            # Validity
            "validity_days": 15,
            "valid_until": (date.today() + timedelta(days=15)).isoformat(),
            
            # Status
            "status": "submitted",
            
            # Timestamps
            "created_at": datetime.utcnow().isoformat()
        }
        
        self.quotes[quote_id] = quote
        
        # Update quote request
        quote_request["quotes_received"] += 1
        
        logger.info(f"Quote {quote_id} submitted for request {quote_request_id}")
        
        return quote
    
    def get_quotes_for_request(self, quote_request_id: str) -> List[Dict]:
        """Get all quotes for a request."""
        return [
            q for q in self.quotes.values()
            if q["quote_request_id"] == quote_request_id
        ]
    
    def accept_quote(self, quote_id: str) -> Dict[str, Any]:
        """Accept a quote and create work order."""
        
        if quote_id not in self.quotes:
            raise ValueError(f"Quote not found: {quote_id}")
        
        quote = self.quotes[quote_id]
        
        if quote["status"] != "submitted":
            raise ValueError(f"Quote cannot be accepted. Current status: {quote['status']}")
        
        # Update quote status
        quote["status"] = "accepted"
        quote["accepted_at"] = datetime.utcnow().isoformat()
        
        # Create work order
        work_order = self.create_work_order(quote)
        
        # Reject other quotes for same request
        for q in self.quotes.values():
            if q["quote_request_id"] == quote["quote_request_id"] and q["quote_id"] != quote_id:
                q["status"] = "rejected"
        
        # Close quote request
        quote_request = self.quote_requests.get(quote["quote_request_id"])
        if quote_request:
            quote_request["status"] = "closed"
            quote_request["closed_at"] = datetime.utcnow().isoformat()
        
        return work_order
    
    # ==================== WORK ORDER MANAGEMENT ====================
    
    def create_work_order(self, quote: Dict) -> Dict[str, Any]:
        """Create work order from accepted quote."""
        
        work_order_id = f"WO-{quote['project_id']}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
        advance_percent = quote.get("advance_percent", 20)
        retention_percent = 10
        advance_amount = quote["total_cost"] * advance_percent / 100
        retention_amount = quote["total_cost"] * retention_percent / 100
        
        # Create default milestones
        milestones = self._create_default_milestones(
            work_order_id,
            quote["total_cost"],
            advance_percent,
            retention_percent
        )
        
        work_order = {
            "work_order_id": work_order_id,
            "quote_id": quote["quote_id"],
            "contractor_id": quote["contractor_id"],
            "contractor_name": quote["contractor_name"],
            "project_id": quote["project_id"],
            
            # Contract
            "agreed_amount": quote["total_cost"],
            "advance_amount": advance_amount,
            "advance_paid": False,
            "retention_amount": retention_amount,
            
            # Payment Terms
            "advance_percent": advance_percent,
            "retention_percent": retention_percent,
            
            # Timeline
            "expected_start_date": quote["proposed_start_date"],
            "expected_end_date": quote["proposed_end_date"],
            
            # Status
            "status": "created",
            
            # Milestones
            "milestones": milestones,
            
            # Timestamps
            "created_at": datetime.utcnow().isoformat()
        }
        
        self.work_orders[work_order_id] = work_order
        
        # Store milestones separately for easy access
        for m in milestones:
            self.milestones[m["milestone_id"]] = m
        
        logger.info(f"Work order {work_order_id} created")
        
        return work_order
    
    def _create_default_milestones(
        self,
        work_order_id: str,
        total_amount: float,
        advance_percent: int,
        retention_percent: int
    ) -> List[Dict]:
        """Create default milestones for work order."""
        
        # Remaining after advance and retention
        remaining_percent = 100 - advance_percent - retention_percent
        
        milestones = [
            {
                "milestone_id": f"{work_order_id}-M1",
                "work_order_id": work_order_id,
                "sequence": 1,
                "milestone_type": "advance",
                "milestone_name": "Advance Payment",
                "description": "Advance payment before work starts",
                "payment_percent": advance_percent,
                "payment_amount": total_amount * advance_percent / 100,
                "status": "pending"
            },
            {
                "milestone_id": f"{work_order_id}-M2",
                "work_order_id": work_order_id,
                "sequence": 2,
                "milestone_type": "gutter_installation",
                "milestone_name": "Gutter & Pipe Installation",
                "description": "Complete gutter and downpipe installation",
                "payment_percent": remaining_percent * 0.3,
                "payment_amount": total_amount * remaining_percent * 0.3 / 100,
                "status": "pending"
            },
            {
                "milestone_id": f"{work_order_id}-M3",
                "work_order_id": work_order_id,
                "sequence": 3,
                "milestone_type": "filter_installation",
                "milestone_name": "Filter Installation",
                "description": "Install filters and first flush diverter",
                "payment_percent": remaining_percent * 0.2,
                "payment_amount": total_amount * remaining_percent * 0.2 / 100,
                "status": "pending"
            },
            {
                "milestone_id": f"{work_order_id}-M4",
                "work_order_id": work_order_id,
                "sequence": 4,
                "milestone_type": "tank_installation",
                "milestone_name": "Tank Installation",
                "description": "Install storage tank and connections",
                "payment_percent": remaining_percent * 0.3,
                "payment_amount": total_amount * remaining_percent * 0.3 / 100,
                "status": "pending"
            },
            {
                "milestone_id": f"{work_order_id}-M5",
                "work_order_id": work_order_id,
                "sequence": 5,
                "milestone_type": "testing",
                "milestone_name": "Testing & Handover",
                "description": "Complete testing and system handover",
                "payment_percent": remaining_percent * 0.2,
                "payment_amount": total_amount * remaining_percent * 0.2 / 100,
                "status": "pending"
            },
            {
                "milestone_id": f"{work_order_id}-M6",
                "work_order_id": work_order_id,
                "sequence": 6,
                "milestone_type": "retention",
                "milestone_name": "Retention Release",
                "description": "Retention amount released after 30 days",
                "payment_percent": retention_percent,
                "payment_amount": total_amount * retention_percent / 100,
                "status": "pending"
            }
        ]
        
        return milestones
    
    def update_milestone(
        self,
        milestone_id: str,
        status: str,
        photos: List[str] = None,
        notes: str = ""
    ) -> Dict[str, Any]:
        """Update milestone status."""
        
        if milestone_id not in self.milestones:
            raise ValueError(f"Milestone not found: {milestone_id}")
        
        milestone = self.milestones[milestone_id]
        
        milestone["status"] = status
        milestone["photos"] = photos or []
        milestone["notes"] = notes
        milestone["updated_at"] = datetime.utcnow().isoformat()
        
        if status == "completed":
            milestone["completed_at"] = datetime.utcnow().isoformat()
        
        # Update work order status
        work_order = self.work_orders.get(milestone["work_order_id"])
        if work_order:
            completed_count = sum(
                1 for m in work_order["milestones"]
                if m["status"] == "completed" or m["status"] == "verified"
            )
            
            if completed_count == len(work_order["milestones"]):
                work_order["status"] = "completed"
                work_order["completed_at"] = datetime.utcnow().isoformat()
            elif completed_count > 0:
                work_order["status"] = "in_progress"
        
        logger.info(f"Milestone {milestone_id} updated to {status}")
        
        return milestone
    
    def verify_milestone(
        self,
        milestone_id: str,
        verified_by: str,
        approved: bool,
        rejection_reason: str = ""
    ) -> Dict[str, Any]:
        """Verify a completed milestone."""
        
        if milestone_id not in self.milestones:
            raise ValueError(f"Milestone not found: {milestone_id}")
        
        milestone = self.milestones[milestone_id]
        
        if milestone["status"] != "completed":
            raise ValueError("Milestone must be completed before verification")
        
        if approved:
            milestone["status"] = "verified"
            milestone["verified_by"] = verified_by
            milestone["verified_at"] = datetime.utcnow().isoformat()
        else:
            milestone["status"] = "rejected"
            milestone["rejection_reason"] = rejection_reason
        
        return milestone
    
    # ==================== REVIEWS & RATINGS ====================
    
    def submit_review(
        self,
        contractor_id: str,
        project_id: int,
        work_order_id: str,
        user_id: int,
        overall_rating: int,
        quality_rating: int,
        timeliness_rating: int,
        communication_rating: int,
        value_rating: int,
        review_text: str,
        would_recommend: bool = True,
        photos: List[str] = None
    ) -> Dict[str, Any]:
        """Submit a review for contractor."""
        
        if contractor_id not in self.contractors:
            raise ValueError(f"Contractor not found: {contractor_id}")
        
        review_id = f"REV-{contractor_id}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
        review = {
            "review_id": review_id,
            "contractor_id": contractor_id,
            "project_id": project_id,
            "work_order_id": work_order_id,
            "user_id": user_id,
            
            # Ratings
            "overall_rating": overall_rating,
            "quality_rating": quality_rating,
            "timeliness_rating": timeliness_rating,
            "communication_rating": communication_rating,
            "value_rating": value_rating,
            
            # Feedback
            "review_text": review_text,
            "would_recommend": would_recommend,
            "photos": photos or [],
            
            # Moderation
            "is_verified": True,  # Auto-verified for completed work orders
            "is_visible": True,
            
            "created_at": datetime.utcnow().isoformat()
        }
        
        self.reviews[review_id] = review
        
        # Update contractor ratings
        self._update_contractor_ratings(contractor_id)
        
        logger.info(f"Review {review_id} submitted for contractor {contractor_id}")
        
        return review
    
    def _update_contractor_ratings(self, contractor_id: str):
        """Update contractor aggregate ratings."""
        
        contractor_reviews = [
            r for r in self.reviews.values()
            if r["contractor_id"] == contractor_id and r["is_visible"]
        ]
        
        if not contractor_reviews:
            return
        
        contractor = self.contractors[contractor_id]
        
        # Calculate averages
        contractor["total_reviews"] = len(contractor_reviews)
        contractor["average_rating"] = round(
            sum(r["overall_rating"] for r in contractor_reviews) / len(contractor_reviews),
            1
        )
        contractor["quality_rating"] = round(
            sum(r["quality_rating"] for r in contractor_reviews) / len(contractor_reviews),
            1
        )
        contractor["timeliness_rating"] = round(
            sum(r["timeliness_rating"] for r in contractor_reviews) / len(contractor_reviews),
            1
        )
        contractor["communication_rating"] = round(
            sum(r["communication_rating"] for r in contractor_reviews) / len(contractor_reviews),
            1
        )
        contractor["value_rating"] = round(
            sum(r["value_rating"] for r in contractor_reviews) / len(contractor_reviews),
            1
        )
    
    # ==================== DEFECT REPORTING ====================
    
    def report_defect(
        self,
        project_id: int,
        work_order_id: str,
        user_id: int,
        defect_type: str,
        defect_description: str,
        defect_location: str,
        severity: str = "medium",
        photos: List[str] = None,
        detected_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """Report a defect in installation."""
        
        work_order = self.work_orders.get(work_order_id)
        contractor_id = work_order["contractor_id"] if work_order else None
        
        report_id = f"DEF-{project_id}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
        defect_report = {
            "report_id": report_id,
            "project_id": project_id,
            "work_order_id": work_order_id,
            "contractor_id": contractor_id,
            "user_id": user_id,
            
            # Defect Info
            "defect_type": defect_type,
            "defect_description": defect_description,
            "defect_location": defect_location,
            "severity": severity,
            
            # Evidence
            "photos": photos or [],
            
            # Dates
            "detected_date": (detected_date or date.today()).isoformat(),
            "reported_at": datetime.utcnow().isoformat(),
            
            # Status
            "status": "reported",
            
            # Warranty
            "under_warranty": self._check_warranty(work_order_id) if work_order else False
        }
        
        self.defect_reports[report_id] = defect_report
        
        # Notify contractor
        logger.info(f"Defect report {report_id} submitted")
        
        return defect_report
    
    def _check_warranty(self, work_order_id: str) -> bool:
        """Check if work order is still under warranty."""
        work_order = self.work_orders.get(work_order_id)
        if not work_order or not work_order.get("completed_at"):
            return False
        
        completed_date = datetime.fromisoformat(work_order["completed_at"])
        warranty_end = completed_date + timedelta(days=365)  # 1 year warranty
        
        return datetime.utcnow() < warranty_end
    
    def update_defect_status(
        self,
        report_id: str,
        status: str,
        resolution_notes: str = ""
    ) -> Dict[str, Any]:
        """Update defect report status."""
        
        if report_id not in self.defect_reports:
            raise ValueError(f"Defect report not found: {report_id}")
        
        report = self.defect_reports[report_id]
        report["status"] = status
        
        if status == "resolved":
            report["resolution_notes"] = resolution_notes
            report["resolved_at"] = datetime.utcnow().isoformat()
        
        return report


# Singleton instance
_marketplace_service: Optional[ContractorMarketplaceService] = None


def get_marketplace_service() -> ContractorMarketplaceService:
    """Get or create marketplace service instance."""
    global _marketplace_service
    if _marketplace_service is None:
        _marketplace_service = ContractorMarketplaceService()
    return _marketplace_service
