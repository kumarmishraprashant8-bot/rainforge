"""
Water Sharing Service - Neighborhood water sharing between RWH systems.
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import math
import uuid

logger = logging.getLogger(__name__)


class SharingStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class WaterAvailability(str, Enum):
    SURPLUS = "surplus"
    BALANCED = "balanced"
    DEFICIT = "deficit"
    CRITICAL = "critical"


@dataclass
class RWHSystem:
    system_id: str
    owner_id: str
    owner_name: str
    address: str
    latitude: float
    longitude: float
    tank_capacity_liters: float
    current_level_percent: float
    avg_daily_consumption: float
    sharing_enabled: bool = True
    willing_to_share: bool = True
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class SharingRequest:
    request_id: str
    requester_id: str
    requester_name: str
    provider_id: str
    provider_name: str
    liters: float
    price_per_liter: float
    status: SharingStatus
    message: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    actual_liters: Optional[float] = None


class WaterSharingService:
    MAX_DISTANCE_KM = 2.0
    
    def __init__(self):
        self._systems: Dict[str, RWHSystem] = {}
        self._requests: Dict[str, SharingRequest] = {}
        self._history: List[Dict] = []
    
    def register_system(self, owner_id: str, owner_name: str, address: str,
                       lat: float, lon: float, capacity: float) -> RWHSystem:
        system_id = f"sys_{uuid.uuid4().hex[:8]}"
        system = RWHSystem(system_id=system_id, owner_id=owner_id, owner_name=owner_name,
                          address=address, latitude=lat, longitude=lon,
                          tank_capacity_liters=capacity, current_level_percent=50.0,
                          avg_daily_consumption=200.0)
        self._systems[system_id] = system
        return system
    
    def _haversine(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        R = 6371
        dlat, dlon = math.radians(lat2-lat1), math.radians(lon2-lon1)
        a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(dlon/2)**2
        return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    def get_availability(self, system_id: str) -> WaterAvailability:
        sys = self._systems.get(system_id)
        if not sys: return WaterAvailability.BALANCED
        level = sys.current_level_percent
        if level >= 80: return WaterAvailability.SURPLUS
        if level >= 40: return WaterAvailability.BALANCED
        if level >= 20: return WaterAvailability.DEFICIT
        return WaterAvailability.CRITICAL
    
    def find_nearby(self, lat: float, lon: float, surplus_only: bool = False) -> List[Dict]:
        nearby = []
        for sys in self._systems.values():
            if not sys.sharing_enabled: continue
            dist = self._haversine(lat, lon, sys.latitude, sys.longitude)
            if dist <= self.MAX_DISTANCE_KM:
                avail = self.get_availability(sys.system_id)
                if surplus_only and avail != WaterAvailability.SURPLUS: continue
                available = sys.tank_capacity_liters * (sys.current_level_percent/100) - sys.avg_daily_consumption*3
                nearby.append({"system_id": sys.system_id, "owner": sys.owner_name, "address": sys.address,
                              "distance_km": round(dist, 2), "availability": avail.value,
                              "level_pct": sys.current_level_percent, "available_liters": max(0, available)})
        return sorted(nearby, key=lambda x: x["distance_km"])
    
    def request_water(self, requester_id: str, provider_id: str, liters: float, msg: str = "") -> SharingRequest:
        req = self._systems.get(requester_id)
        prov = self._systems.get(provider_id)
        if not req or not prov: raise ValueError("System not found")
        request = SharingRequest(request_id=f"req_{uuid.uuid4().hex[:8]}", requester_id=requester_id,
                                requester_name=req.owner_name, provider_id=provider_id,
                                provider_name=prov.owner_name, liters=liters, price_per_liter=0,
                                status=SharingStatus.PENDING, message=msg, created_at=datetime.now())
        self._requests[request.request_id] = request
        return request
    
    def respond(self, request_id: str, accept: bool) -> SharingRequest:
        req = self._requests.get(request_id)
        if not req: raise ValueError("Request not found")
        req.status = SharingStatus.ACCEPTED if accept else SharingStatus.CANCELLED
        return req
    
    def complete(self, request_id: str, actual_liters: float) -> SharingRequest:
        req = self._requests.get(request_id)
        if not req: raise ValueError("Request not found")
        req.status = SharingStatus.COMPLETED
        req.completed_at = datetime.now()
        req.actual_liters = actual_liters
        self._history.append({"provider": req.provider_name, "receiver": req.requester_name,
                             "liters": actual_liters, "completed": datetime.now().isoformat()})
        return req
    
    def get_leaderboard(self, limit: int = 10) -> List[Dict]:
        scores: Dict[str, float] = {}
        for h in self._history:
            scores[h["provider"]] = scores.get(h["provider"], 0) + h["liters"]
        return [{"name": n, "liters": l, "badge": "🏆" if l >= 10000 else "💧" if l >= 1000 else "💦"}
                for n, l in sorted(scores.items(), key=lambda x: -x[1])[:limit]]


_service: Optional[WaterSharingService] = None

def get_water_sharing_service() -> WaterSharingService:
    global _service
    if _service is None: _service = WaterSharingService()
    return _service
