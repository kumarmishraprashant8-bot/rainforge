"""
RainForge Public Dashboard & AMC API Endpoints
"""

from fastapi import APIRouter, HTTPException
from typing import Optional, List
from pydantic import BaseModel
from datetime import date, datetime
import uuid
import random


router = APIRouter()


# ============== IN-MEMORY STORAGE ==============

_amc_packages = {
    "bronze": {
        "id": "AMC-BRONZE",
        "name": "Bronze Care",
        "tier": "bronze",
        "price_yearly": 2500,
        "features": [
            "Annual inspection",
            "Filter replacement",
            "Basic cleaning",
            "Phone support"
        ],
        "is_active": True
    },
    "silver": {
        "id": "AMC-SILVER",
        "name": "Silver Shield",
        "tier": "silver",
        "price_yearly": 5000,
        "features": [
            "Bi-annual inspection",
            "Filter replacement",
            "Tank cleaning",
            "Minor repairs included",
            "Priority phone support",
            "Water quality testing"
        ],
        "is_active": True
    },
    "gold": {
        "id": "AMC-GOLD",
        "name": "Gold Premium",
        "tier": "gold",
        "price_yearly": 8500,
        "features": [
            "Quarterly inspection",
            "All replacements included",
            "Complete maintenance",
            "All repairs included",
            "24/7 emergency support",
            "Water quality testing",
            "Performance guarantee",
            "Insurance coverage"
        ],
        "is_active": True
    }
}

_warranties = {}
_outcome_contracts = {}


# ============== WARD STATS DATA ==============

_ward_stats = {
    "W001": {"name": "Connaught Place", "systems": 45, "captured": 2500000, "spent": 4500000},
    "W002": {"name": "Karol Bagh", "systems": 32, "captured": 1800000, "spent": 3200000},
    "W003": {"name": "Rohini Sector 5", "systems": 67, "captured": 3800000, "spent": 6700000},
    "W004": {"name": "Dwarka Sector 12", "systems": 54, "captured": 3100000, "spent": 5400000},
    "W005": {"name": "Lajpat Nagar", "systems": 28, "captured": 1500000, "spent": 2800000},
}


# ============== REQUEST MODELS ==============

class WarrantyCreate(BaseModel):
    job_id: int
    amc_package_id: Optional[str] = None
    duration_months: int = 12
    auto_renew: bool = False


class OutcomeContractCreate(BaseModel):
    job_id: int
    target_capture_liters: int
    monitoring_months: int = 12


# ============== PUBLIC DASHBOARD ENDPOINTS ==============

@router.get("/ward/{ward_id}/stats")
def get_ward_stats(ward_id: str):
    """Get public statistics for a ward."""
    if ward_id not in _ward_stats:
        raise HTTPException(status_code=404, detail=f"Ward {ward_id} not found")
    
    w = _ward_stats[ward_id]
    co2_avoided = w["captured"] * 0.0007  # ~0.7g CO2 per liter
    
    return {
        "ward_id": ward_id,
        "ward_name": w["name"],
        "total_systems": w["systems"],
        "active_systems": int(w["systems"] * 0.92),  # 92% active
        "total_captured_liters": w["captured"],
        "total_captured_display": f"{w['captured']/1000000:.1f}M L",
        "co2_avoided_kg": round(co2_avoided, 1),
        "funds_spent_inr": w["spent"],
        "funds_spent_display": f"₹{w['spent']/100000:.1f}L",
        "beneficiaries": w["systems"] * 4,  # Avg 4 per household
        "last_updated": datetime.utcnow().isoformat()
    }


@router.get("/city/stats")
def get_city_stats():
    """Get aggregated city-level statistics."""
    total_systems = sum(w["systems"] for w in _ward_stats.values())
    total_captured = sum(w["captured"] for w in _ward_stats.values())
    total_spent = sum(w["spent"] for w in _ward_stats.values())
    co2_avoided = total_captured * 0.0007
    
    return {
        "city": "New Delhi",
        "total_wards": len(_ward_stats),
        "total_systems": total_systems,
        "active_systems": int(total_systems * 0.92),
        "total_captured_liters": total_captured,
        "total_captured_display": f"{total_captured/1000000:.1f}M L",
        "co2_avoided_kg": round(co2_avoided, 1),
        "funds_spent_inr": total_spent,
        "funds_spent_display": f"₹{total_spent/100000:.1f}L",
        "beneficiaries": total_systems * 4,
        "wards": [
            {
                "ward_id": k,
                "ward_name": v["name"],
                "systems": v["systems"],
                "captured": v["captured"]
            }
            for k, v in _ward_stats.items()
        ]
    }


@router.get("/city/export")
def export_city_data(format: str = "json"):
    """Export city data as JSON or simplified CSV format."""
    data = []
    for ward_id, w in _ward_stats.items():
        data.append({
            "ward_id": ward_id,
            "ward_name": w["name"],
            "systems": w["systems"],
            "captured_liters": w["captured"],
            "spent_inr": w["spent"],
            "co2_avoided_kg": round(w["captured"] * 0.0007, 1),
            "lat": 28.6139 + random.uniform(-0.1, 0.1),  # Mock geo
            "lng": 77.2090 + random.uniform(-0.1, 0.1)
        })
    
    if format == "csv":
        headers = list(data[0].keys())
        csv_lines = [",".join(headers)]
        for row in data:
            csv_lines.append(",".join(str(row[h]) for h in headers))
        return {"format": "csv", "content": "\n".join(csv_lines)}
    
    return {"format": "json", "data": data}


# ============== AMC ENDPOINTS ==============

@router.get("/amc-packages")
def list_amc_packages():
    """List available AMC packages."""
    return {
        "packages": list(_amc_packages.values())
    }


@router.get("/amc-packages/{package_id}")
def get_amc_package(package_id: str):
    """Get AMC package details."""
    if package_id not in _amc_packages:
        raise HTTPException(status_code=404, detail="Package not found")
    return _amc_packages[package_id]


@router.post("/warranties")
def create_warranty(request: WarrantyCreate):
    """Register warranty for a job."""
    warranty_id = f"WAR-{uuid.uuid4().hex[:8].upper()}"
    
    start_date = date.today()
    
    warranty = {
        "id": warranty_id,
        "job_id": request.job_id,
        "amc_package_id": request.amc_package_id,
        "amc_package": _amc_packages.get(request.amc_package_id.replace("AMC-", "").lower()) if request.amc_package_id else None,
        "start_date": start_date.isoformat(),
        "end_date": date(start_date.year + request.duration_months // 12, 
                        (start_date.month + request.duration_months % 12 - 1) % 12 + 1, 
                        start_date.day).isoformat(),
        "duration_months": request.duration_months,
        "auto_renew": request.auto_renew,
        "status": "active"
    }
    
    _warranties[warranty_id] = warranty
    
    return {
        "warranty_id": warranty_id,
        "message": "Warranty registered",
        "warranty": warranty
    }


@router.get("/warranties/job/{job_id}")
def get_warranty_for_job(job_id: int):
    """Get warranty for a job."""
    for w in _warranties.values():
        if w["job_id"] == job_id:
            return w
    raise HTTPException(status_code=404, detail=f"No warranty for job {job_id}")


# ============== OUTCOME CONTRACT ENDPOINTS ==============

@router.post("/outcome-contracts")
def create_outcome_contract(request: OutcomeContractCreate):
    """Create outcome-based contract for a job."""
    contract_id = f"OC-{uuid.uuid4().hex[:8].upper()}"
    
    start_date = date.today()
    end_date = date(start_date.year + request.monitoring_months // 12,
                   (start_date.month + request.monitoring_months % 12 - 1) % 12 + 1,
                   start_date.day)
    
    contract = {
        "id": contract_id,
        "job_id": request.job_id,
        "target_capture_liters": request.target_capture_liters,
        "actual_capture_liters": 0,
        "monitoring_start": start_date.isoformat(),
        "monitoring_end": end_date.isoformat(),
        "achievement_pct": 0.0,
        "status": "active",
        "final_payment_released": False
    }
    
    _outcome_contracts[contract_id] = contract
    
    return {
        "contract_id": contract_id,
        "message": "Outcome contract created",
        "contract": contract
    }


@router.post("/outcome-contracts/{contract_id}/update-capture")
def update_contract_capture(contract_id: str, captured_liters: int):
    """Update actual capture (from IoT or manual input)."""
    if contract_id not in _outcome_contracts:
        raise HTTPException(status_code=404, detail="Contract not found")
    
    contract = _outcome_contracts[contract_id]
    contract["actual_capture_liters"] = captured_liters
    contract["achievement_pct"] = round(captured_liters / contract["target_capture_liters"] * 100, 1)
    
    return {
        "contract_id": contract_id,
        "actual_capture_liters": captured_liters,
        "achievement_pct": contract["achievement_pct"],
        "target_met": contract["achievement_pct"] >= 100
    }


@router.post("/outcome-contracts/{contract_id}/resolve")
def resolve_contract(contract_id: str):
    """Resolve outcome contract and determine final payment eligibility."""
    if contract_id not in _outcome_contracts:
        raise HTTPException(status_code=404, detail="Contract not found")
    
    contract = _outcome_contracts[contract_id]
    
    target_met = contract["achievement_pct"] >= 100
    
    if target_met:
        contract["status"] = "completed_success"
        contract["final_payment_released"] = True
        message = "Target met! Final payment released."
    elif contract["achievement_pct"] >= 80:
        contract["status"] = "completed_partial"
        contract["final_payment_released"] = True
        message = f"Partial target ({contract['achievement_pct']}%) met. Prorated payment released."
    else:
        contract["status"] = "completed_failed"
        contract["final_payment_released"] = False
        message = f"Target not met ({contract['achievement_pct']}%). Final payment withheld."
    
    return {
        "contract_id": contract_id,
        "status": contract["status"],
        "achievement_pct": contract["achievement_pct"],
        "final_payment_released": contract["final_payment_released"],
        "message": message
    }


@router.get("/outcome-contracts/{contract_id}")
def get_contract(contract_id: str):
    """Get outcome contract details."""
    if contract_id not in _outcome_contracts:
        raise HTTPException(status_code=404, detail="Contract not found")
    return _outcome_contracts[contract_id]
