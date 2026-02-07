"""
Carbon NFT Service
Tokenizes carbon credits as blockchain-compatible NFTs.
Provides trading marketplace and certificate generation.
"""
import logging
import hashlib
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import uuid

logger = logging.getLogger(__name__)


class NFTStatus(str, Enum):
    """NFT lifecycle status."""
    MINTED = "minted"
    LISTED = "listed"
    SOLD = "sold"
    TRANSFERRED = "transferred"
    RETIRED = "retired"


class CarbonStandard(str, Enum):
    """Carbon credit verification standards."""
    GOLD_STANDARD = "gold_standard"
    VCS = "verified_carbon_standard"
    CDM = "clean_development_mechanism"
    RAINFORGE = "rainforge_verified"


@dataclass
class CarbonNFT:
    """Carbon credit NFT representation."""
    token_id: str
    owner_id: str
    owner_name: str
    site_id: str
    co2_offset_kg: float
    co2_offset_tonnes: float
    water_saved_liters: float
    vintage_year: int
    standard: CarbonStandard
    status: NFTStatus
    metadata_uri: str
    certificate_hash: str
    mint_timestamp: datetime
    price_inr: Optional[float] = None
    price_usd: Optional[float] = None
    transaction_history: List[Dict] = field(default_factory=list)


@dataclass
class TradeOrder:
    """Carbon credit trade order."""
    order_id: str
    token_id: str
    seller_id: str
    buyer_id: Optional[str]
    price_inr: float
    price_usd: float
    order_type: str  # sell, buy
    status: str  # open, filled, cancelled
    created_at: datetime
    filled_at: Optional[datetime] = None


@dataclass
class CarbonCertificate:
    """Printable carbon credit certificate."""
    certificate_id: str
    token_id: str
    owner_name: str
    site_address: str
    co2_offset_tonnes: float
    water_saved_liters: float
    issue_date: datetime
    valid_until: datetime
    qr_code_data: str
    verification_url: str


class CarbonNFTService:
    """
    Mock blockchain service for carbon credit NFTs.
    
    Features:
    - Mint NFTs from carbon credits
    - List on marketplace
    - Buy/sell/transfer
    - Generate certificates
    - Audit trail via transaction history
    """
    
    # Carbon credit pricing (per tonne CO2)
    PRICE_PER_TONNE_INR = 2500  # ~$30 USD
    PRICE_PER_TONNE_USD = 30
    
    # Platform fee
    PLATFORM_FEE_PERCENT = 2.5
    
    def __init__(self):
        self._nfts: Dict[str, CarbonNFT] = {}
        self._orders: Dict[str, TradeOrder] = {}
        self._certificates: Dict[str, CarbonCertificate] = {}
        self._user_balances: Dict[str, Dict[str, float]] = {}  # user_id -> {inr: x, usd: y}
        self._block_number = 1000  # Mock blockchain state
        
    def mint_carbon_nft(
        self,
        owner_id: str,
        owner_name: str,
        site_id: str,
        co2_offset_kg: float,
        water_saved_liters: float,
        standard: CarbonStandard = CarbonStandard.RAINFORGE
    ) -> CarbonNFT:
        """
        Mint a new carbon credit NFT.
        Requires minimum 100kg CO2 offset.
        """
        if co2_offset_kg < 100:
            raise ValueError("Minimum 100kg CO2 offset required to mint NFT")
        
        # Generate unique token ID
        token_id = f"RAIN-{datetime.now().year}-{uuid.uuid4().hex[:8].upper()}"
        
        # Calculate value
        co2_tonnes = co2_offset_kg / 1000
        price_inr = co2_tonnes * self.PRICE_PER_TONNE_INR
        price_usd = co2_tonnes * self.PRICE_PER_TONNE_USD
        
        # Generate metadata hash
        metadata = {
            "token_id": token_id,
            "owner": owner_name,
            "site_id": site_id,
            "co2_kg": co2_offset_kg,
            "water_liters": water_saved_liters,
            "standard": standard.value,
            "minted_at": datetime.now().isoformat()
        }
        metadata_json = json.dumps(metadata, sort_keys=True)
        certificate_hash = hashlib.sha256(metadata_json.encode()).hexdigest()
        
        # Create NFT
        nft = CarbonNFT(
            token_id=token_id,
            owner_id=owner_id,
            owner_name=owner_name,
            site_id=site_id,
            co2_offset_kg=co2_offset_kg,
            co2_offset_tonnes=co2_tonnes,
            water_saved_liters=water_saved_liters,
            vintage_year=datetime.now().year,
            standard=standard,
            status=NFTStatus.MINTED,
            metadata_uri=f"ipfs://rainforge/{certificate_hash[:16]}",
            certificate_hash=certificate_hash,
            mint_timestamp=datetime.now(),
            price_inr=price_inr,
            price_usd=price_usd,
            transaction_history=[{
                "type": "mint",
                "from": "0x0",
                "to": owner_id,
                "timestamp": datetime.now().isoformat(),
                "block": self._block_number
            }]
        )
        
        self._nfts[token_id] = nft
        self._block_number += 1
        
        logger.info(f"Minted NFT {token_id}: {co2_tonnes:.2f} tonnes CO2 for {owner_name}")
        
        return nft
    
    def list_for_sale(
        self,
        token_id: str,
        seller_id: str,
        price_inr: float
    ) -> TradeOrder:
        """List an NFT for sale on the marketplace."""
        nft = self._nfts.get(token_id)
        if not nft:
            raise ValueError(f"NFT {token_id} not found")
        
        if nft.owner_id != seller_id:
            raise ValueError("Only owner can list NFT for sale")
        
        if nft.status == NFTStatus.RETIRED:
            raise ValueError("Cannot sell retired credits")
        
        # Create sell order
        order_id = f"ORD-{uuid.uuid4().hex[:8].upper()}"
        price_usd = price_inr / 83  # Approximate conversion
        
        order = TradeOrder(
            order_id=order_id,
            token_id=token_id,
            seller_id=seller_id,
            buyer_id=None,
            price_inr=price_inr,
            price_usd=price_usd,
            order_type="sell",
            status="open",
            created_at=datetime.now()
        )
        
        self._orders[order_id] = order
        nft.status = NFTStatus.LISTED
        
        # Add to transaction history
        nft.transaction_history.append({
            "type": "listed",
            "order_id": order_id,
            "price_inr": price_inr,
            "timestamp": datetime.now().isoformat(),
            "block": self._block_number
        })
        self._block_number += 1
        
        return order
    
    def buy_nft(
        self,
        order_id: str,
        buyer_id: str,
        buyer_name: str
    ) -> CarbonNFT:
        """Purchase an NFT from the marketplace."""
        order = self._orders.get(order_id)
        if not order:
            raise ValueError(f"Order {order_id} not found")
        
        if order.status != "open":
            raise ValueError(f"Order is not open for purchase")
        
        nft = self._nfts.get(order.token_id)
        if not nft:
            raise ValueError("NFT not found")
        
        # Process payment (mock)
        platform_fee = order.price_inr * (self.PLATFORM_FEE_PERCENT / 100)
        seller_receives = order.price_inr - platform_fee
        
        # Transfer ownership
        old_owner = nft.owner_id
        nft.owner_id = buyer_id
        nft.owner_name = buyer_name
        nft.status = NFTStatus.SOLD
        
        # Update order
        order.buyer_id = buyer_id
        order.status = "filled"
        order.filled_at = datetime.now()
        
        # Add to transaction history
        nft.transaction_history.append({
            "type": "sale",
            "from": old_owner,
            "to": buyer_id,
            "price_inr": order.price_inr,
            "platform_fee_inr": platform_fee,
            "seller_received_inr": seller_receives,
            "timestamp": datetime.now().isoformat(),
            "block": self._block_number
        })
        self._block_number += 1
        
        logger.info(f"NFT {nft.token_id} sold to {buyer_name} for ₹{order.price_inr:,.0f}")
        
        return nft
    
    def transfer_nft(
        self,
        token_id: str,
        from_user_id: str,
        to_user_id: str,
        to_user_name: str
    ) -> CarbonNFT:
        """Transfer NFT to another user (no payment)."""
        nft = self._nfts.get(token_id)
        if not nft:
            raise ValueError(f"NFT {token_id} not found")
        
        if nft.owner_id != from_user_id:
            raise ValueError("Only owner can transfer NFT")
        
        if nft.status == NFTStatus.LISTED:
            raise ValueError("Cancel listing before transferring")
        
        # Transfer
        old_owner = nft.owner_id
        nft.owner_id = to_user_id
        nft.owner_name = to_user_name
        nft.status = NFTStatus.TRANSFERRED
        
        nft.transaction_history.append({
            "type": "transfer",
            "from": old_owner,
            "to": to_user_id,
            "timestamp": datetime.now().isoformat(),
            "block": self._block_number
        })
        self._block_number += 1
        
        return nft
    
    def retire_credits(self, token_id: str, owner_id: str, reason: str = "") -> CarbonNFT:
        """
        Retire carbon credits (permanently remove from circulation).
        Used when claiming the offset for carbon neutrality.
        """
        nft = self._nfts.get(token_id)
        if not nft:
            raise ValueError(f"NFT {token_id} not found")
        
        if nft.owner_id != owner_id:
            raise ValueError("Only owner can retire credits")
        
        nft.status = NFTStatus.RETIRED
        
        nft.transaction_history.append({
            "type": "retired",
            "by": owner_id,
            "reason": reason,
            "co2_retired_tonnes": nft.co2_offset_tonnes,
            "timestamp": datetime.now().isoformat(),
            "block": self._block_number
        })
        self._block_number += 1
        
        logger.info(f"Retired {nft.co2_offset_tonnes:.2f} tonnes CO2 (NFT: {token_id})")
        
        return nft
    
    def generate_certificate(
        self,
        token_id: str,
        site_address: str
    ) -> CarbonCertificate:
        """Generate a printable certificate for an NFT."""
        nft = self._nfts.get(token_id)
        if not nft:
            raise ValueError(f"NFT {token_id} not found")
        
        certificate_id = f"CERT-{uuid.uuid4().hex[:8].upper()}"
        
        # QR code data for verification
        qr_data = json.dumps({
            "cert_id": certificate_id,
            "token_id": token_id,
            "hash": nft.certificate_hash[:16],
            "co2_tonnes": nft.co2_offset_tonnes
        })
        
        certificate = CarbonCertificate(
            certificate_id=certificate_id,
            token_id=token_id,
            owner_name=nft.owner_name,
            site_address=site_address,
            co2_offset_tonnes=nft.co2_offset_tonnes,
            water_saved_liters=nft.water_saved_liters,
            issue_date=datetime.now(),
            valid_until=datetime(nft.vintage_year + 5, 12, 31),  # 5 year validity
            qr_code_data=qr_data,
            verification_url=f"https://rainforge.app/verify/{certificate_id}"
        )
        
        self._certificates[certificate_id] = certificate
        
        return certificate
    
    def get_marketplace_listings(
        self,
        min_tonnes: Optional[float] = None,
        max_price_inr: Optional[float] = None,
        standard: Optional[CarbonStandard] = None
    ) -> List[Dict[str, Any]]:
        """Get all active marketplace listings."""
        listings = []
        
        for order in self._orders.values():
            if order.status != "open":
                continue
            
            nft = self._nfts.get(order.token_id)
            if not nft:
                continue
            
            # Apply filters
            if min_tonnes and nft.co2_offset_tonnes < min_tonnes:
                continue
            if max_price_inr and order.price_inr > max_price_inr:
                continue
            if standard and nft.standard != standard:
                continue
            
            listings.append({
                "order_id": order.order_id,
                "token_id": nft.token_id,
                "seller_name": nft.owner_name,
                "co2_tonnes": nft.co2_offset_tonnes,
                "water_saved_liters": nft.water_saved_liters,
                "vintage_year": nft.vintage_year,
                "standard": nft.standard.value,
                "price_inr": order.price_inr,
                "price_usd": order.price_usd,
                "price_per_tonne_inr": order.price_inr / nft.co2_offset_tonnes,
                "listed_at": order.created_at.isoformat()
            })
        
        # Sort by price per tonne
        listings.sort(key=lambda x: x["price_per_tonne_inr"])
        
        return listings
    
    def get_user_portfolio(self, user_id: str) -> Dict[str, Any]:
        """Get user's carbon credit portfolio."""
        user_nfts = [nft for nft in self._nfts.values() if nft.owner_id == user_id]
        
        total_co2 = sum(nft.co2_offset_tonnes for nft in user_nfts)
        total_water = sum(nft.water_saved_liters for nft in user_nfts)
        total_value_inr = sum(nft.price_inr or 0 for nft in user_nfts)
        
        active_nfts = [n for n in user_nfts if n.status != NFTStatus.RETIRED]
        retired_nfts = [n for n in user_nfts if n.status == NFTStatus.RETIRED]
        listed_nfts = [n for n in user_nfts if n.status == NFTStatus.LISTED]
        
        return {
            "user_id": user_id,
            "total_nfts": len(user_nfts),
            "active_nfts": len(active_nfts),
            "listed_nfts": len(listed_nfts),
            "retired_nfts": len(retired_nfts),
            "total_co2_tonnes": total_co2,
            "total_water_saved_liters": total_water,
            "portfolio_value_inr": total_value_inr,
            "portfolio_value_usd": total_value_inr / 83,
            "nfts": [
                {
                    "token_id": nft.token_id,
                    "co2_tonnes": nft.co2_offset_tonnes,
                    "status": nft.status.value,
                    "vintage": nft.vintage_year,
                    "value_inr": nft.price_inr
                }
                for nft in user_nfts
            ]
        }
    
    def get_market_stats(self) -> Dict[str, Any]:
        """Get overall marketplace statistics."""
        all_nfts = list(self._nfts.values())
        all_orders = list(self._orders.values())
        
        total_minted_co2 = sum(nft.co2_offset_tonnes for nft in all_nfts)
        total_retired_co2 = sum(nft.co2_offset_tonnes for nft in all_nfts if nft.status == NFTStatus.RETIRED)
        
        filled_orders = [o for o in all_orders if o.status == "filled"]
        total_traded_volume = sum(o.price_inr for o in filled_orders)
        
        return {
            "total_nfts_minted": len(all_nfts),
            "total_co2_minted_tonnes": total_minted_co2,
            "total_co2_retired_tonnes": total_retired_co2,
            "active_listings": len([o for o in all_orders if o.status == "open"]),
            "total_trades": len(filled_orders),
            "total_traded_volume_inr": total_traded_volume,
            "total_traded_volume_usd": total_traded_volume / 83,
            "avg_price_per_tonne_inr": (
                total_traded_volume / sum(
                    self._nfts[o.token_id].co2_offset_tonnes 
                    for o in filled_orders 
                    if o.token_id in self._nfts
                ) if filled_orders else self.PRICE_PER_TONNE_INR
            ),
            "platform_fees_collected_inr": total_traded_volume * (self.PLATFORM_FEE_PERCENT / 100),
            "block_height": self._block_number
        }
    
    def verify_certificate(self, certificate_id: str) -> Dict[str, Any]:
        """Verify a certificate's authenticity."""
        certificate = self._certificates.get(certificate_id)
        if not certificate:
            return {
                "valid": False,
                "error": "Certificate not found"
            }
        
        nft = self._nfts.get(certificate.token_id)
        if not nft:
            return {
                "valid": False,
                "error": "Associated NFT not found"
            }
        
        return {
            "valid": True,
            "certificate_id": certificate.certificate_id,
            "token_id": certificate.token_id,
            "owner": certificate.owner_name,
            "co2_tonnes": certificate.co2_offset_tonnes,
            "water_saved_liters": certificate.water_saved_liters,
            "issue_date": certificate.issue_date.isoformat(),
            "valid_until": certificate.valid_until.isoformat(),
            "nft_status": nft.status.value,
            "blockchain_verified": True,
            "certificate_hash": nft.certificate_hash[:16]
        }


# Singleton
_service: Optional[CarbonNFTService] = None


def get_carbon_nft_service() -> CarbonNFTService:
    """Get or create the carbon NFT service singleton."""
    global _service
    if _service is None:
        _service = CarbonNFTService()
    return _service
