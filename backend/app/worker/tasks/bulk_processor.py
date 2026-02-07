"""
RainForge Bulk Processor Task
=============================
Celery task for processing bulk CSV uploads (10 - 10,000 sites).

Owners: Prashant Mishra & Ishita Parmar
"""

import csv
import io
import json
import zipfile
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

from app.worker.celery_app import celery_app
from app.services.calculation_engine import CalculationEngine, AssessmentResult


# CSV Column Specification
REQUIRED_COLUMNS = ["site_id"]
LOCATION_COLUMNS = ["address", "lat", "lng"]  # At least address OR lat+lng required
OPTIONAL_COLUMNS = [
    "roof_area_sqm", "roof_material", "floors", "roof_slope_deg",
    "storage_pref", "state", "city", "monthly_bill", "people", 
    "tank_size_override_l", "building_type"
]

VALID_ROOF_MATERIALS = ["concrete", "metal", "tiles", "asphalt", "slate", "green"]
VALID_STORAGE_PREFS = ["tank", "recharge", "hybrid"]


@dataclass
class RowResult:
    """Result for a single row in bulk processing."""
    row_number: int
    site_id: str
    status: str  # success, error, warning
    assessment_id: Optional[int] = None
    error_message: Optional[str] = None
    warnings: Optional[List[str]] = None
    summary: Optional[Dict[str, Any]] = None


class BulkProcessor:
    """Processes bulk CSV uploads with validation and assessment."""
    
    def __init__(self):
        self.engine = CalculationEngine()
        self.geocoder = None  # Will be injected
    
    def validate_row(self, row: Dict[str, str], row_number: int, seen_site_ids: set) -> tuple[bool, List[str], Dict]:
        """
        Validate a single row from the CSV.
        Returns: (is_valid, errors, parsed_data)
        """
        errors = []
        warnings = []
        parsed = {}
        
        # 1. Check site_id
        site_id = row.get("site_id", "").strip()
        if not site_id:
            errors.append("Missing required field: site_id")
        elif site_id in seen_site_ids:
            errors.append(f"Duplicate site_id: {site_id}")
        else:
            parsed["site_id"] = site_id
        
        # 2. Check location (address OR lat+lng)
        lat = row.get("lat", "").strip()
        lng = row.get("lng", "").strip()
        address = row.get("address", "").strip()
        
        has_coords = bool(lat and lng)
        has_address = bool(address)
        
        if not has_coords and not has_address:
            errors.append("Must provide either 'address' or both 'lat' and 'lng'")
        elif has_coords:
            try:
                parsed["lat"] = float(lat)
                parsed["lng"] = float(lng)
                if not (-90 <= parsed["lat"] <= 90):
                    errors.append("Invalid latitude (must be -90 to 90)")
                if not (-180 <= parsed["lng"] <= 180):
                    errors.append("Invalid longitude (must be -180 to 180)")
            except ValueError:
                errors.append("Invalid lat/lng format (must be numeric)")
        
        if has_address:
            parsed["address"] = address
            if not has_coords:
                warnings.append("Address requires geocoding - may slow processing")
        
        # 3. Check roof_area_sqm
        roof_area = row.get("roof_area_sqm", "").strip()
        if roof_area:
            try:
                parsed["roof_area_sqm"] = float(roof_area)
                if parsed["roof_area_sqm"] <= 0:
                    errors.append("roof_area_sqm must be > 0")
                elif parsed["roof_area_sqm"] > 100000:
                    errors.append("roof_area_sqm must be <= 100,000")
            except ValueError:
                errors.append("Invalid roof_area_sqm format (must be numeric)")
        else:
            parsed["roof_area_sqm"] = 100.0  # Default
            warnings.append("Using default roof_area_sqm: 100")
        
        # 4. Check roof_material
        roof_material = row.get("roof_material", "concrete").strip().lower()
        if roof_material and roof_material not in VALID_ROOF_MATERIALS:
            warnings.append(f"Unknown roof_material '{roof_material}', using 'concrete'")
            roof_material = "concrete"
        parsed["roof_material"] = roof_material
        
        # 5. Parse optional fields
        for field in ["floors", "people"]:
            value = row.get(field, "").strip()
            if value:
                try:
                    parsed[field] = int(value)
                except ValueError:
                    warnings.append(f"Invalid {field} format, using default")
        
        for field in ["monthly_bill", "roof_slope_deg", "tank_size_override_l"]:
            value = row.get(field, "").strip()
            if value:
                try:
                    parsed[field] = float(value)
                except ValueError:
                    warnings.append(f"Invalid {field} format, ignoring")
        
        for field in ["state", "city", "building_type"]:
            value = row.get(field, "").strip()
            if value:
                parsed[field] = value
        
        # Storage preference
        storage_pref = row.get("storage_pref", "tank").strip().lower()
        if storage_pref not in VALID_STORAGE_PREFS:
            warnings.append(f"Unknown storage_pref '{storage_pref}', using 'tank'")
            storage_pref = "tank"
        parsed["storage_pref"] = storage_pref
        
        is_valid = len(errors) == 0
        return is_valid, errors + warnings if not is_valid else warnings, parsed
    
    def process_row(self, parsed_data: Dict, row_number: int) -> RowResult:
        """Process a validated row and run assessment."""
        try:
            # Run assessment
            result = self.engine.run_full_assessment(
                roof_area_sqm=parsed_data.get("roof_area_sqm", 100),
                roof_material=parsed_data.get("roof_material", "concrete"),
                lat=parsed_data.get("lat"),
                lng=parsed_data.get("lng"),
                city=parsed_data.get("city"),
                state=parsed_data.get("state"),
                floors=parsed_data.get("floors", 1),
                people=parsed_data.get("people", 4),
                scenario="cost_optimized"
            )
            
            return RowResult(
                row_number=row_number,
                site_id=parsed_data["site_id"],
                status="success",
                assessment_id=None,  # Would be set after DB insert
                summary={
                    "annual_yield_l": result.annual_yield_l,
                    "tank_recommendation_l": result.tank_recommendation_l,
                    "estimated_cost": result.estimated_cost,
                    "net_cost": result.net_cost,
                    "roi_years": result.roi_years,
                    "reliability_pct": result.reliability_pct
                }
            )
        except Exception as e:
            return RowResult(
                row_number=row_number,
                site_id=parsed_data.get("site_id", "unknown"),
                status="error",
                error_message=str(e)
            )
    
    def process_csv(self, csv_content: str, job_id: str) -> Dict[str, Any]:
        """
        Process entire CSV content.
        Returns job summary with results.
        """
        results = []
        errors = []
        seen_site_ids = set()
        
        try:
            reader = csv.DictReader(io.StringIO(csv_content))
            rows = list(reader)
        except Exception as e:
            return {
                "job_id": job_id,
                "status": "failed",
                "error": f"CSV parsing error: {str(e)}",
                "rows_total": 0,
                "rows_processed": 0,
                "rows_failed": 0
            }
        
        total_rows = len(rows)
        processed = 0
        failed = 0
        success = 0
        
        for i, row in enumerate(rows, start=1):
            # Validate
            is_valid, issues, parsed = self.validate_row(row, i, seen_site_ids)
            
            if not is_valid:
                results.append(RowResult(
                    row_number=i,
                    site_id=row.get("site_id", ""),
                    status="error",
                    error_message="; ".join(issues)
                ))
                failed += 1
            else:
                if parsed.get("site_id"):
                    seen_site_ids.add(parsed["site_id"])
                
                # Process
                result = self.process_row(parsed, i)
                if result.status == "error":
                    failed += 1
                else:
                    success += 1
                results.append(result)
            
            processed += 1
        
        return {
            "job_id": job_id,
            "status": "completed",
            "rows_total": total_rows,
            "rows_processed": processed,
            "rows_success": success,
            "rows_failed": failed,
            "results": [asdict(r) for r in results]
        }


# Celery Task
@celery_app.task(bind=True, name="app.worker.tasks.bulk_processor.process_bulk_upload")
def process_bulk_upload(self, job_id: str, csv_content: str, user_id: str = None):
    """
    Celery task to process bulk CSV upload.
    
    Args:
        job_id: UUID of the bulk job
        csv_content: Raw CSV content as string
        user_id: User who initiated the job
    
    Returns:
        Job result summary
    """
    processor = BulkProcessor()
    
    # Update task state
    self.update_state(state="PROCESSING", meta={"job_id": job_id})
    
    try:
        result = processor.process_csv(csv_content, job_id)
        
        # TODO: Save results to database
        # TODO: Generate output ZIP with per-site PDFs
        # TODO: Update bulk_jobs table with completion
        
        return result
    except Exception as e:
        return {
            "job_id": job_id,
            "status": "failed",
            "error": str(e),
            "rows_total": 0,
            "rows_processed": 0,
            "rows_failed": 0
        }


@celery_app.task(name="app.worker.tasks.bulk_processor.cleanup_old_jobs")
def cleanup_old_jobs():
    """Clean up jobs older than 7 days."""
    # TODO: Implement cleanup logic
    pass


@celery_app.task(bind=True, name="app.worker.tasks.bulk_processor.generate_bulk_zip")
def generate_bulk_zip(self, job_id: str, results: List[Dict]):
    """
    Generate ZIP file with individual PDFs for each site.
    """
    # TODO: Implement ZIP generation
    pass
