"""
RainForge Smart Allocation Engine
Assigns installers to jobs using configurable weights and multiple modes.
"""

from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import math
from datetime import datetime


class AllocationMode(str, Enum):
    USER_CHOICE = "user_choice"
    GOV_OPTIMIZED = "gov_optimized"
    EQUITABLE = "equitable"


@dataclass
class AllocationWeights:
    """Configurable weights for allocation scoring."""
    capacity: float = 0.20
    rpi: float = 0.30
    cost_band: float = 0.20
    distance: float = 0.15
    sla_history: float = 0.15
    
    def normalize(self) -> 'AllocationWeights':
        """Ensure weights sum to 1.0"""
        total = self.capacity + self.rpi + self.cost_band + self.distance + self.sla_history
        if total == 0:
            return AllocationWeights()
        return AllocationWeights(
            capacity=self.capacity / total,
            rpi=self.rpi / total,
            cost_band=self.cost_band / total,
            distance=self.distance / total,
            sla_history=self.sla_history / total
        )


@dataclass
class Installer:
    id: int
    name: str
    company: str
    lat: float
    lng: float
    rpi_score: float = 50.0
    capacity_available: int = 5  # Available slots this month
    capacity_max: int = 10
    avg_cost_factor: float = 1.0  # 1.0 = market rate
    sla_compliance_pct: float = 90.0
    jobs_completed: int = 0
    is_blacklisted: bool = False
    cert_level: str = "basic"


@dataclass
class Job:
    id: int
    address: str
    lat: float
    lng: float
    estimated_cost_inr: float
    complexity: str = "standard"  # simple, standard, complex


@dataclass
class AllocationResult:
    job_id: int
    installer_id: int
    installer_name: str
    score: float
    score_breakdown: Dict[str, float]
    alternatives: List[Dict[str, Any]] = field(default_factory=list)
    reason: str = ""


class AllocationEngine:
    """
    Government-grade installer allocation engine.
    Supports multiple modes: User Choice, Gov Optimized, Equitable Distribution.
    """
    
    # Default weights
    DEFAULT_WEIGHTS = AllocationWeights()
    
    # Stored weights (would persist to DB in production)
    _admin_weights: AllocationWeights = None
    
    @classmethod
    def set_admin_weights(cls, weights: AllocationWeights):
        """Admin control to update allocation weights."""
        cls._admin_weights = weights.normalize()
    
    @classmethod
    def get_weights(cls) -> AllocationWeights:
        """Get current allocation weights."""
        return cls._admin_weights or cls.DEFAULT_WEIGHTS
    
    @staticmethod
    def haversine_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """Calculate distance in km between two coordinates."""
        R = 6371  # Earth radius in km
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lng = math.radians(lng2 - lng1)
        
        a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lng/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c
    
    @classmethod
    def calculate_capacity_score(cls, installer: Installer) -> float:
        """Score based on available capacity. Higher capacity = higher score."""
        if installer.capacity_max == 0:
            return 0.0
        utilization = 1 - (installer.capacity_available / installer.capacity_max)
        # Prefer installers with more available capacity
        return max(0, min(100, installer.capacity_available * 10))
    
    @classmethod
    def calculate_rpi_score(cls, installer: Installer) -> float:
        """RPI score is already 0-100."""
        return installer.rpi_score
    
    @classmethod
    def calculate_cost_band_score(cls, installer: Installer, job: Job) -> float:
        """Score based on cost competitiveness. Lower cost = higher score."""
        # Assuming avg_cost_factor: 0.8 = 20% below market, 1.2 = 20% above
        if installer.avg_cost_factor <= 0:
            return 50.0
        # Invert so lower cost = higher score
        score = 100 - (installer.avg_cost_factor - 0.8) * 100
        return max(0, min(100, score))
    
    @classmethod
    def calculate_distance_score(cls, installer: Installer, job: Job) -> float:
        """Score based on proximity. Closer = higher score."""
        distance = cls.haversine_distance(installer.lat, installer.lng, job.lat, job.lng)
        # Max 50km gets 100, beyond 100km gets 0
        score = max(0, 100 - (distance * 2))
        return score
    
    @classmethod
    def calculate_sla_score(cls, installer: Installer) -> float:
        """Score based on SLA compliance history."""
        return installer.sla_compliance_pct
    
    @classmethod
    def score_installer(
        cls, 
        installer: Installer, 
        job: Job, 
        weights: AllocationWeights
    ) -> Dict[str, Any]:
        """Calculate composite score for an installer."""
        
        capacity_score = cls.calculate_capacity_score(installer)
        rpi_score = cls.calculate_rpi_score(installer)
        cost_score = cls.calculate_cost_band_score(installer, job)
        distance_score = cls.calculate_distance_score(installer, job)
        sla_score = cls.calculate_sla_score(installer)
        
        # Weighted composite
        composite = (
            capacity_score * weights.capacity +
            rpi_score * weights.rpi +
            cost_score * weights.cost_band +
            distance_score * weights.distance +
            sla_score * weights.sla_history
        )
        
        return {
            "installer_id": installer.id,
            "installer_name": installer.name,
            "composite_score": round(composite, 2),
            "breakdown": {
                "capacity": round(capacity_score * weights.capacity, 2),
                "rpi": round(rpi_score * weights.rpi, 2),
                "cost_band": round(cost_score * weights.cost_band, 2),
                "distance": round(distance_score * weights.distance, 2),
                "sla_history": round(sla_score * weights.sla_history, 2)
            },
            "raw_scores": {
                "capacity": round(capacity_score, 1),
                "rpi": round(rpi_score, 1),
                "cost_band": round(cost_score, 1),
                "distance": round(distance_score, 1),
                "sla_history": round(sla_score, 1)
            }
        }
    
    @classmethod
    def allocate(
        cls,
        job: Job,
        installers: List[Installer],
        mode: AllocationMode = AllocationMode.GOV_OPTIMIZED,
        custom_weights: Optional[AllocationWeights] = None,
        force_installer_id: Optional[int] = None
    ) -> AllocationResult:
        """
        Main allocation method.
        
        Args:
            job: The job to allocate
            installers: List of available installers
            mode: Allocation strategy
            custom_weights: Override default weights
            force_installer_id: Admin override to force specific installer
        
        Returns:
            AllocationResult with recommended installer and alternatives
        """
        
        # Filter out blacklisted installers
        eligible = [i for i in installers if not i.is_blacklisted]
        
        if not eligible:
            raise ValueError("No eligible installers available")
        
        # Force assignment (admin override)
        if force_installer_id:
            forced = next((i for i in eligible if i.id == force_installer_id), None)
            if forced:
                return AllocationResult(
                    job_id=job.id,
                    installer_id=forced.id,
                    installer_name=forced.name,
                    score=100.0,
                    score_breakdown={"forced_assignment": 100.0},
                    reason="Admin force assignment"
                )
            raise ValueError(f"Installer {force_installer_id} not found or blacklisted")
        
        # Determine weights based on mode
        if custom_weights:
            weights = custom_weights.normalize()
        elif mode == AllocationMode.GOV_OPTIMIZED:
            # Prioritize RPI and SLA
            weights = AllocationWeights(
                capacity=0.15,
                rpi=0.35,
                cost_band=0.15,
                distance=0.15,
                sla_history=0.20
            )
        elif mode == AllocationMode.EQUITABLE:
            # Prioritize capacity to spread work evenly
            weights = AllocationWeights(
                capacity=0.40,
                rpi=0.20,
                cost_band=0.15,
                distance=0.15,
                sla_history=0.10
            )
        else:  # USER_CHOICE
            weights = cls.get_weights()
        
        # Score all installers
        scored = []
        for installer in eligible:
            result = cls.score_installer(installer, job, weights)
            scored.append(result)
        
        # Sort by composite score (descending)
        scored.sort(key=lambda x: x["composite_score"], reverse=True)
        
        if not scored:
            raise ValueError("No installers could be scored")
        
        # Top recommendation
        top = scored[0]
        
        # Build alternatives (next 4)
        alternatives = [
            {
                "installer_id": s["installer_id"],
                "installer_name": s["installer_name"],
                "score": s["composite_score"],
                "rank": i + 2
            }
            for i, s in enumerate(scored[1:5])
        ]
        
        return AllocationResult(
            job_id=job.id,
            installer_id=top["installer_id"],
            installer_name=top["installer_name"],
            score=top["composite_score"],
            score_breakdown=top["breakdown"],
            alternatives=alternatives,
            reason=f"Highest score under {mode.value} mode"
        )
    
    @classmethod
    def explain_allocation(cls, result: AllocationResult) -> str:
        """Generate human-readable explanation of allocation decision."""
        breakdown = result.score_breakdown
        
        factors = []
        if breakdown.get("rpi", 0) > 5:
            factors.append(f"strong RPI score ({breakdown['rpi']:.1f})")
        if breakdown.get("distance", 0) > 5:
            factors.append(f"proximity ({breakdown['distance']:.1f})")
        if breakdown.get("capacity", 0) > 5:
            factors.append(f"available capacity ({breakdown['capacity']:.1f})")
        if breakdown.get("cost_band", 0) > 5:
            factors.append(f"competitive pricing ({breakdown['cost_band']:.1f})")
        if breakdown.get("sla_history", 0) > 5:
            factors.append(f"reliable SLA history ({breakdown['sla_history']:.1f})")
        
        if not factors:
            return f"{result.installer_name} was selected as the best available option."
        
        return f"{result.installer_name} was selected due to: {', '.join(factors)}."


# ============== DEMO DATA ==============

def get_demo_installers() -> List[Installer]:
    """Generate demo installer data."""
    return [
        Installer(id=1, name="Jal Mitra Solutions", company="Jal Mitra", lat=28.6139, lng=77.2090, 
                 rpi_score=92, capacity_available=8, sla_compliance_pct=95),
        Installer(id=2, name="AquaSave India", company="AquaSave", lat=28.5355, lng=77.3910,
                 rpi_score=85, capacity_available=5, sla_compliance_pct=88),
        Installer(id=3, name="RainCatch Delhi", company="RainCatch", lat=28.7041, lng=77.1025,
                 rpi_score=78, capacity_available=10, avg_cost_factor=0.85, sla_compliance_pct=82),
        Installer(id=4, name="EcoWater Systems", company="EcoWater", lat=28.4595, lng=77.0266,
                 rpi_score=88, capacity_available=3, avg_cost_factor=1.1, sla_compliance_pct=91),
        Installer(id=5, name="Varsha RWH", company="Varsha", lat=28.6692, lng=77.4538,
                 rpi_score=70, capacity_available=7, avg_cost_factor=0.9, sla_compliance_pct=75),
        Installer(id=6, name="BlueDrop Tech", company="BlueDrop", lat=28.5672, lng=77.3219,
                 rpi_score=95, capacity_available=2, avg_cost_factor=1.15, sla_compliance_pct=98),
        Installer(id=7, name="Monsoon Masters", company="Monsoon", lat=28.6304, lng=77.2177,
                 rpi_score=82, capacity_available=6, sla_compliance_pct=85),
        Installer(id=8, name="Jaldhara Services", company="Jaldhara", lat=28.4089, lng=77.3178,
                 rpi_score=65, capacity_available=9, avg_cost_factor=0.8, sla_compliance_pct=70),
        Installer(id=9, name="AquaTech Pro", company="AquaTech", lat=28.7271, lng=77.0946,
                 rpi_score=90, capacity_available=4, sla_compliance_pct=92),
        Installer(id=10, name="HarvestRain Co", company="HarvestRain", lat=28.5921, lng=77.2290,
                  rpi_score=75, capacity_available=5, avg_cost_factor=0.95, sla_compliance_pct=80),
    ]


def demo_allocation():
    """Demo the allocation engine."""
    installers = get_demo_installers()
    
    job = Job(
        id=101,
        address="Govt School Sector 15, Noida",
        lat=28.5355,
        lng=77.3910,
        estimated_cost_inr=96000
    )
    
    # Gov Optimized mode
    result = AllocationEngine.allocate(job, installers, AllocationMode.GOV_OPTIMIZED)
    
    print(f"Job: {job.address}")
    print(f"Recommended: {result.installer_name} (Score: {result.score})")
    print(f"Reason: {AllocationEngine.explain_allocation(result)}")
    print(f"Alternatives: {result.alternatives}")
    
    return result


if __name__ == "__main__":
    demo_allocation()
