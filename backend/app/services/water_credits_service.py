"""
Water Credits Service
Tradeable water savings certificates for industrial compliance.
"""

import logging
import uuid
from datetime import datetime
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class CreditStatus(str, Enum):
    ACTIVE = "active"
    LISTED = "listed"
    SOLD = "sold"
    RETIRED = "retired"


@dataclass
class WaterCredit:
    credit_id: str
    owner_id: str
    project_id: str
    water_saved_liters: float
    credit_units: float  # 1 unit = 1000 liters
    issued_at: datetime
    valid_until: datetime
    status: CreditStatus
    price_per_unit: Optional[float] = None
    
    def to_dict(self) -> Dict:
        return {
            "credit_id": self.credit_id,
            "water_saved_liters": self.water_saved_liters,
            "credit_units": self.credit_units,
            "status": self.status.value,
            "price_per_unit": self.price_per_unit,
            "issued_at": self.issued_at.isoformat()
        }


@dataclass
class WaterCreditOrder:
    order_id: str
    credit_id: str
    seller_id: str
    buyer_id: Optional[str]
    units: float
    price_per_unit: float
    total_price: float
    status: str
    created_at: datetime


class WaterCreditsService:
    """Tradeable water savings certificates marketplace."""
    
    def __init__(self):
        self._credits: Dict[str, WaterCredit] = {}
        self._orders: Dict[str, WaterCreditOrder] = {}
        self._user_credits: Dict[str, List[str]] = {}
        
        # Pricing
        self._base_price_per_kl = 25  # ₹25 per 1000 liters
        
        logger.info("💧 Water Credits Service initialized")
    
    async def issue_credits(self, user_id: str, project_id: str,
                           water_saved_liters: float) -> Dict[str, Any]:
        """Issue water credits based on verified water savings."""
        if water_saved_liters < 1000:
            return {"success": False, "error": "Minimum 1000 liters required"}
        
        credit_units = water_saved_liters / 1000
        credit_id = f"WC-{uuid.uuid4().hex[:10].upper()}"
        
        credit = WaterCredit(
            credit_id=credit_id,
            owner_id=user_id,
            project_id=project_id,
            water_saved_liters=water_saved_liters,
            credit_units=credit_units,
            issued_at=datetime.now(),
            valid_until=datetime.now().replace(year=datetime.now().year + 2),
            status=CreditStatus.ACTIVE
        )
        
        self._credits[credit_id] = credit
        self._user_credits.setdefault(user_id, []).append(credit_id)
        
        logger.info(f"💧 Issued {credit_units} water credits to {user_id}")
        
        return {
            "success": True,
            "credit": credit.to_dict(),
            "estimated_value": credit_units * self._base_price_per_kl
        }
    
    async def list_for_sale(self, credit_id: str, user_id: str,
                           price_per_unit: float) -> Dict[str, Any]:
        credit = self._credits.get(credit_id)
        if not credit or credit.owner_id != user_id:
            return {"success": False, "error": "Credit not found"}
        
        if credit.status != CreditStatus.ACTIVE:
            return {"success": False, "error": "Credit not available for sale"}
        
        credit.status = CreditStatus.LISTED
        credit.price_per_unit = price_per_unit
        
        order_id = f"WCO-{uuid.uuid4().hex[:10].upper()}"
        order = WaterCreditOrder(
            order_id=order_id,
            credit_id=credit_id,
            seller_id=user_id,
            buyer_id=None,
            units=credit.credit_units,
            price_per_unit=price_per_unit,
            total_price=credit.credit_units * price_per_unit,
            status="listed",
            created_at=datetime.now()
        )
        self._orders[order_id] = order
        
        return {"success": True, "order_id": order_id, "total_price": order.total_price}
    
    async def buy_credits(self, order_id: str, buyer_id: str) -> Dict[str, Any]:
        order = self._orders.get(order_id)
        if not order or order.status != "listed":
            return {"success": False, "error": "Order not available"}
        
        credit = self._credits[order.credit_id]
        
        # Transfer ownership
        old_owner = credit.owner_id
        credit.owner_id = buyer_id
        credit.status = CreditStatus.ACTIVE
        credit.price_per_unit = None
        
        order.buyer_id = buyer_id
        order.status = "completed"
        
        # Update user tracking
        if old_owner in self._user_credits:
            self._user_credits[old_owner].remove(credit.credit_id)
        self._user_credits.setdefault(buyer_id, []).append(credit.credit_id)
        
        return {
            "success": True,
            "credit": credit.to_dict(),
            "total_paid": order.total_price
        }
    
    async def retire_credits(self, credit_id: str, user_id: str,
                            reason: str = "") -> Dict[str, Any]:
        """Retire credits for compliance/water-positive certification."""
        credit = self._credits.get(credit_id)
        if not credit or credit.owner_id != user_id:
            return {"success": False, "error": "Credit not found"}
        
        credit.status = CreditStatus.RETIRED
        
        return {
            "success": True,
            "message": f"Retired {credit.credit_units} water credits",
            "retirement_certificate": f"/api/v1/water-credits/{credit_id}/certificate"
        }
    
    async def get_marketplace_listings(self, min_units: float = 0,
                                       max_price: float = 1000) -> Dict[str, Any]:
        listings = []
        for order in self._orders.values():
            if order.status != "listed":
                continue
            if order.units >= min_units and order.price_per_unit <= max_price:
                credit = self._credits[order.credit_id]
                listings.append({
                    "order_id": order.order_id,
                    "units": order.units,
                    "price_per_unit": order.price_per_unit,
                    "total_price": order.total_price,
                    "water_saved_liters": credit.water_saved_liters
                })
        
        listings.sort(key=lambda x: x["price_per_unit"])
        return {"success": True, "listings": listings}
    
    async def get_user_portfolio(self, user_id: str) -> Dict[str, Any]:
        credit_ids = self._user_credits.get(user_id, [])
        credits = [self._credits[cid].to_dict() for cid in credit_ids]
        
        total_units = sum(c["credit_units"] for c in credits)
        total_value = total_units * self._base_price_per_kl
        
        return {
            "success": True,
            "credits": credits,
            "total_units": total_units,
            "estimated_value": total_value
        }


_service: Optional[WaterCreditsService] = None

def get_water_credits_service() -> WaterCreditsService:
    global _service
    if _service is None:
        _service = WaterCreditsService()
    return _service
