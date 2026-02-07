"""
Carbon NFT Marketplace API
Endpoints for carbon credit tokenization and trading
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/carbon", tags=["carbon", "nft", "marketplace"])


# ==================== SCHEMAS ====================
class MintNFTRequest(BaseModel):
    owner_id: str
    owner_name: str
    site_id: str
    co2_offset_kg: float
    water_saved_liters: float
    verification_date: Optional[datetime] = None
    location: str = ""
    project_name: str = ""


class ListForSaleRequest(BaseModel):
    token_id: str
    price_inr: float
    owner_id: str


class BuyNFTRequest(BaseModel):
    token_id: str
    buyer_id: str
    buyer_name: str


class TransferRequest(BaseModel):
    token_id: str
    from_owner_id: str
    to_owner_id: str
    to_owner_name: str


class RetireRequest(BaseModel):
    token_id: str
    owner_id: str
    reason: str = ""


# ==================== ENDPOINTS ====================
@router.post("/mint")
def mint_carbon_nft(data: MintNFTRequest):
    """Mint a new carbon credit NFT"""
    from app.services.carbon_nft import get_carbon_nft_service
    service = get_carbon_nft_service()
    
    nft = service.mint_carbon_nft(
        owner_id=data.owner_id,
        owner_name=data.owner_name,
        site_id=data.site_id,
        co2_offset_kg=data.co2_offset_kg,
        water_saved_liters=data.water_saved_liters,
        verification_date=data.verification_date or datetime.now(),
        location=data.location,
        project_name=data.project_name
    )
    
    return {
        "success": True,
        "token_id": nft.token_id,
        "nft": {
            "token_id": nft.token_id,
            "co2_offset_kg": nft.co2_offset_kg,
            "water_saved_liters": nft.water_saved_liters,
            "status": nft.status.value,
            "minted_at": nft.minted_at.isoformat()
        }
    }


@router.get("/nft/{token_id}")
def get_nft(token_id: str):
    """Get NFT details by token ID"""
    from app.services.carbon_nft import get_carbon_nft_service
    service = get_carbon_nft_service()
    
    nft = service.get_nft(token_id)
    if not nft:
        raise HTTPException(status_code=404, detail="NFT not found")
    
    return {
        "token_id": nft.token_id,
        "owner_id": nft.owner_id,
        "owner_name": nft.owner_name,
        "co2_offset_kg": nft.co2_offset_kg,
        "water_saved_liters": nft.water_saved_liters,
        "status": nft.status.value,
        "price_inr": nft.price_inr,
        "minted_at": nft.minted_at.isoformat(),
        "metadata": nft.metadata
    }


@router.get("/portfolio/{owner_id}")
def get_portfolio(owner_id: str):
    """Get all NFTs owned by a user"""
    from app.services.carbon_nft import get_carbon_nft_service
    service = get_carbon_nft_service()
    
    nfts = service.get_portfolio(owner_id)
    return {
        "owner_id": owner_id,
        "count": len(nfts),
        "total_co2_offset_kg": sum(n.co2_offset_kg for n in nfts),
        "nfts": [{
            "token_id": n.token_id,
            "co2_offset_kg": n.co2_offset_kg,
            "status": n.status.value,
            "price_inr": n.price_inr
        } for n in nfts]
    }


@router.post("/list-for-sale")
def list_for_sale(data: ListForSaleRequest):
    """List an NFT for sale on the marketplace"""
    from app.services.carbon_nft import get_carbon_nft_service
    service = get_carbon_nft_service()
    
    try:
        order = service.list_for_sale(data.token_id, data.price_inr, data.owner_id)
        return {"success": True, "order_id": order.order_id, "price_inr": order.price_inr}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/buy")
def buy_nft(data: BuyNFTRequest):
    """Buy an NFT from the marketplace"""
    from app.services.carbon_nft import get_carbon_nft_service
    service = get_carbon_nft_service()
    
    try:
        nft = service.buy_nft(data.token_id, data.buyer_id, data.buyer_name)
        return {
            "success": True,
            "token_id": nft.token_id,
            "new_owner": nft.owner_name,
            "status": nft.status.value
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/transfer")
def transfer_nft(data: TransferRequest):
    """Transfer an NFT to another user"""
    from app.services.carbon_nft import get_carbon_nft_service
    service = get_carbon_nft_service()
    
    try:
        nft = service.transfer_nft(
            data.token_id,
            data.from_owner_id,
            data.to_owner_id,
            data.to_owner_name
        )
        return {"success": True, "token_id": nft.token_id, "new_owner": nft.owner_name}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/retire")
def retire_credit(data: RetireRequest):
    """Retire a carbon credit (remove from circulation)"""
    from app.services.carbon_nft import get_carbon_nft_service
    service = get_carbon_nft_service()
    
    try:
        nft, cert = service.retire_credit(data.token_id, data.owner_id, data.reason)
        return {
            "success": True,
            "token_id": nft.token_id,
            "certificate_id": cert.certificate_id,
            "co2_retired_kg": cert.co2_offset_kg,
            "certificate_url": cert.certificate_url
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/marketplace")
def get_marketplace_listings(
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    min_co2: Optional[float] = Query(None)
):
    """Get all active marketplace listings"""
    from app.services.carbon_nft import get_carbon_nft_service
    service = get_carbon_nft_service()
    
    orders = service.get_marketplace_listings()
    
    # Apply filters
    if min_price is not None:
        orders = [o for o in orders if o.price_inr >= min_price]
    if max_price is not None:
        orders = [o for o in orders if o.price_inr <= max_price]
    if min_co2 is not None:
        orders = [o for o in orders if o.co2_offset_kg >= min_co2]
    
    return {
        "count": len(orders),
        "listings": [{
            "order_id": o.order_id,
            "token_id": o.token_id,
            "seller_id": o.seller_id,
            "price_inr": o.price_inr,
            "co2_offset_kg": o.co2_offset_kg,
            "listed_at": o.listed_at.isoformat()
        } for o in orders]
    }


@router.get("/marketplace/stats")
def get_marketplace_stats():
    """Get marketplace statistics"""
    from app.services.carbon_nft import get_carbon_nft_service
    service = get_carbon_nft_service()
    return service.get_marketplace_stats()


@router.get("/transactions/{token_id}")
def get_transaction_history(token_id: str):
    """Get transaction history for an NFT"""
    from app.services.carbon_nft import get_carbon_nft_service
    service = get_carbon_nft_service()
    
    transactions = service.get_transaction_history(token_id)
    return {
        "token_id": token_id,
        "count": len(transactions),
        "transactions": [{
            "transaction_id": t.transaction_id,
            "transaction_type": t.transaction_type.value,
            "from_owner": t.from_owner_id,
            "to_owner": t.to_owner_id,
            "timestamp": t.timestamp.isoformat()
        } for t in transactions]
    }


@router.get("/certificate/{token_id}")
def get_certificate(token_id: str):
    """Get retirement certificate for an NFT"""
    from app.services.carbon_nft import get_carbon_nft_service
    service = get_carbon_nft_service()
    
    cert = service.get_certificate(token_id)
    if not cert:
        raise HTTPException(status_code=404, detail="Certificate not found (NFT may not be retired)")
    
    return {
        "certificate_id": cert.certificate_id,
        "token_id": cert.token_id,
        "owner_name": cert.owner_name,
        "co2_offset_kg": cert.co2_offset_kg,
        "retirement_date": cert.retirement_date.isoformat(),
        "certificate_url": cert.certificate_url
    }
