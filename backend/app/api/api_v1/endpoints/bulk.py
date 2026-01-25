"""
RainForge Bulk Assessment API Endpoints
"""

from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import List
from app.schemas.schemas import (
    BulkUploadRequest, BulkAssessmentResponse, ScenarioMode
)
from app.services.bulk import BulkAssessmentService

router = APIRouter()


@router.post("/upload", response_model=BulkAssessmentResponse)
async def upload_bulk_assessment(request: BulkUploadRequest):
    """
    Process bulk assessment from JSON payload.
    """
    sites = [site.dict() for site in request.sites]
    result = BulkAssessmentService.process_batch(
        sites=sites,
        scenario=request.scenario,
        batch_name=request.batch_name
    )
    return result


@router.post("/upload-csv")
async def upload_csv(file: UploadFile = File(...), scenario: str = "cost_optimized"):
    """
    Upload CSV file for bulk assessment.
    """
    try:
        content = await file.read()
        csv_text = content.decode("utf-8")
        sites = BulkAssessmentService.parse_csv(csv_text)
        
        if not sites:
            raise HTTPException(status_code=400, detail="No valid sites found in CSV")
        
        scenario_mode = ScenarioMode(scenario)
        result = BulkAssessmentService.process_batch(
            sites=sites,
            scenario=scenario_mode,
            batch_name=file.filename or "CSV Upload"
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/sample-csv")
async def get_sample_csv():
    """
    Get sample CSV template for bulk upload.
    """
    return {
        "filename": "rainforge_bulk_template.csv",
        "content": BulkAssessmentService.generate_sample_csv(),
        "columns": ["site_id", "address", "roof_area_sqm", "roof_material", "lat", "lng"]
    }


@router.get("/{batch_id}")
async def get_batch_results(batch_id: str):
    """
    Get results for a specific batch (mock - would need database in production).
    """
    # Mock response
    return {
        "batch_id": batch_id,
        "status": "completed",
        "message": "Batch results retrieved",
        "note": "In production, this would fetch from database"
    }
