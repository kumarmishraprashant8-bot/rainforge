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


# ============== WOW MOMENT #3: PUBLIC TRANSPARENCY ==============

# Enhanced ward stats with fraud prevention metrics
_ward_stats = {
    "NDMC-14": {
        "name": "Connaught Place", 
        "systems": 312, 
        "captured": 18400000, 
        "spent": 15600000,
        "fraud_prevented": 9,
        "subsidy_utilized": 7800000,
        "lat": 28.6304,
        "lng": 77.2177
    },
    "SDMC-07": {
        "name": "Saket", 
        "systems": 245, 
        "captured": 12800000, 
        "spent": 11200000,
        "fraud_prevented": 5,
        "subsidy_utilized": 5600000,
        "lat": 28.5245,
        "lng": 77.2066
    },
    "EDMC-03": {
        "name": "Shahdara", 
        "systems": 189, 
        "captured": 9500000, 
        "spent": 8100000,
        "fraud_prevented": 7,
        "subsidy_utilized": 4050000,
        "lat": 28.6731,
        "lng": 77.2896
    },
    "NDMC-28": {
        "name": "Rohini Sector 5", 
        "systems": 276, 
        "captured": 15200000, 
        "spent": 13400000,
        "fraud_prevented": 4,
        "subsidy_utilized": 6700000,
        "lat": 28.7041,
        "lng": 77.1025
    },
    "SDMC-15": {
        "name": "Dwarka Sector 12", 
        "systems": 198, 
        "captured": 11200000, 
        "spent": 9800000,
        "fraud_prevented": 6,
        "subsidy_utilized": 4900000,
        "lat": 28.5921,
        "lng": 77.0463
    },
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


# ============== WOW MOMENT #3: PUBLIC DASHBOARD ENDPOINTS ==============

@router.get("/ward/{ward_id}/stats")
def get_ward_stats(ward_id: str):
    """
    🔥 WOW MOMENT #3: Public Transparency - Ward-Level Stats
    
    Returns comprehensive ward statistics for public transparency.
    No authentication required - citizen access.
    """
    if ward_id not in _ward_stats:
        raise HTTPException(status_code=404, detail=f"Ward {ward_id} not found")
    
    w = _ward_stats[ward_id]
    co2_avoided = w["captured"] * 0.0007  # ~0.7g CO2 per liter
    
    return {
        "ward": ward_id,
        "ward_name": w["name"],
        "systems_installed": w["systems"],
        "active_systems": int(w["systems"] * 0.95),  # 95% active
        "water_captured_liters": w["captured"],
        "water_captured_display": f"{w['captured']/1000000:.1f}M liters",
        "fraud_prevented_cases": w["fraud_prevented"],
        "subsidy_utilized_inr": w["subsidy_utilized"],
        "subsidy_display": f"₹{w['subsidy_utilized']/100000:.1f} Lakhs",
        "co2_avoided_kg": round(co2_avoided, 0),
        "beneficiaries": w["systems"] * 4,  # Avg 4 per household
        "coordinates": {"lat": w["lat"], "lng": w["lng"]},
        "transparency_label": "Public Transparency Dashboard (RTI-Ready)",
        "last_updated": datetime.utcnow().isoformat()
    }


@router.get("/city/stats")
def get_city_stats():
    """Get aggregated city-level statistics."""
    total_systems = sum(w["systems"] for w in _ward_stats.values())
    total_captured = sum(w["captured"] for w in _ward_stats.values())
    total_spent = sum(w["spent"] for w in _ward_stats.values())
    total_fraud = sum(w["fraud_prevented"] for w in _ward_stats.values())
    total_subsidy = sum(w["subsidy_utilized"] for w in _ward_stats.values())
    co2_avoided = total_captured * 0.0007
    
    return {
        "city": "New Delhi",
        "total_wards": len(_ward_stats),
        "systems_installed": total_systems,
        "active_systems": int(total_systems * 0.95),
        "water_captured_liters": total_captured,
        "water_captured_display": f"{total_captured/1000000:.1f}M liters",
        "fraud_prevented_cases": total_fraud,
        "subsidy_utilized_inr": total_subsidy,
        "co2_avoided_kg": round(co2_avoided, 0),
        "funds_spent_inr": total_spent,
        "beneficiaries": total_systems * 4,
        "wards": [
            {
                "ward_id": k,
                "ward_name": v["name"],
                "systems": v["systems"],
                "captured": v["captured"],
                "fraud_prevented": v["fraud_prevented"]
            }
            for k, v in _ward_stats.items()
        ],
        "transparency_label": "Public Transparency Dashboard (RTI-Ready)"
    }


# ============== WOW MOMENT #4: RTI EXPORT ==============

@router.get("/city/export")
def export_city_data():
    """
    🔥 WOW MOMENT #4: One-Click RTI Export
    
    Returns RTI-ready data package with:
    - sites.csv: All site data in CSV format
    - sites.geojson: GeoJSON for mapping
    - audit_trail.csv: Verification audit trail
    - metadata: Export information
    
    Response is JSON with embedded file contents.
    Frontend should download as ZIP.
    """
    # Build sites CSV
    sites_headers = ["ward_id", "ward_name", "systems_installed", "water_captured_liters", "subsidy_utilized_inr", "fraud_prevented", "co2_avoided_kg", "lat", "lng"]
    sites_rows = [",".join(sites_headers)]
    
    for ward_id, w in _ward_stats.items():
        co2 = round(w["captured"] * 0.0007, 0)
        row = [
            ward_id,
            w["name"],
            str(w["systems"]),
            str(w["captured"]),
            str(w["subsidy_utilized"]),
            str(w["fraud_prevented"]),
            str(co2),
            str(w["lat"]),
            str(w["lng"])
        ]
        sites_rows.append(",".join(row))
    
    sites_csv = "\n".join(sites_rows)
    
    # Build GeoJSON
    features = []
    for ward_id, w in _ward_stats.items():
        feature = {
            "type": "Feature",
            "properties": {
                "ward_id": ward_id,
                "name": w["name"],
                "systems": w["systems"],
                "captured_liters": w["captured"],
                "fraud_prevented": w["fraud_prevented"]
            },
            "geometry": {
                "type": "Point",
                "coordinates": [w["lng"], w["lat"]]
            }
        }
        features.append(feature)
    
    geojson = {
        "type": "FeatureCollection",
        "features": features
    }
    
    # Build audit trail CSV
    audit_headers = ["timestamp", "action", "ward_id", "details", "user"]
    audit_rows = [",".join(audit_headers)]
    
    # Mock audit entries
    import json as json_lib
    audit_entries = [
        {"ts": "2026-02-04T10:00:00Z", "action": "VERIFICATION_APPROVED", "ward": "NDMC-14", "details": "System ID SYS-001 verified", "user": "admin_01"},
        {"ts": "2026-02-04T09:30:00Z", "action": "FRAUD_DETECTED", "ward": "SDMC-07", "details": "Photo reuse detected - payment frozen", "user": "system"},
        {"ts": "2026-02-04T09:00:00Z", "action": "SUBSIDY_RELEASED", "ward": "NDMC-14", "details": "₹25,000 released for SYS-002", "user": "finance_01"},
        {"ts": "2026-02-03T16:00:00Z", "action": "INSTALLATION_COMPLETE", "ward": "EDMC-03", "details": "Installation verified for SYS-003", "user": "installer_07"},
        {"ts": "2026-02-03T14:00:00Z", "action": "FRAUD_PREVENTED", "ward": "NDMC-28", "details": "GPS mismatch - verification rejected", "user": "system"},
    ]
    
    for a in audit_entries:
        row = [a["ts"], a["action"], a["ward"], a["details"], a["user"]]
        audit_rows.append(",".join(row))
    
    audit_csv = "\n".join(audit_rows)
    
    return {
        "export_type": "RTI_PACKAGE",
        "generated_at": datetime.utcnow().isoformat(),
        "files": {
            "sites.csv": sites_csv,
            "sites.geojson": geojson,
            "audit_trail.csv": audit_csv
        },
        "metadata": {
            "city": "New Delhi",
            "total_wards": len(_ward_stats),
            "total_systems": sum(w["systems"] for w in _ward_stats.values()),
            "format": "RTI-Ready Export Package",
            "download_note": "📦 Download RTI-Ready Data (ZIP)"
        }
    }


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
