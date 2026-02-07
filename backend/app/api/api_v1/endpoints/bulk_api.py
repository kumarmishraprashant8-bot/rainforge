"""
RainForge Bulk Upload API
=========================
Handles CSV uploads for bulk site processing (10-10,000 sites).

Owners: Prashant Mishra & Ishita Parmar
"""

import uuid
import io
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks, Query
from pydantic import BaseModel

router = APIRouter()

# In-memory job storage (use Redis/DB in production)
_jobs = {}


class BulkJobResponse(BaseModel):
    job_id: str
    status: str
    rows_total: int
    rows_processed: int
    rows_success: int
    rows_failed: int
    created_at: str
    message: str


class BulkJobStatus(BaseModel):
    job_id: str
    status: str  # pending, processing, completed, failed
    progress_percent: float
    rows_total: int
    rows_processed: int
    rows_success: int
    rows_failed: int
    errors: list
    created_at: str
    completed_at: Optional[str] = None
    download_url: Optional[str] = None


def process_bulk_job(job_id: str, csv_content: str):
    """Background task to process bulk CSV."""
    from app.worker.tasks.bulk_processor import BulkProcessor
    
    processor = BulkProcessor()
    result = processor.process_csv(csv_content, job_id)
    
    # Update job status
    _jobs[job_id].update({
        "status": result["status"],
        "rows_processed": result["rows_processed"],
        "rows_success": result.get("rows_success", 0),
        "rows_failed": result.get("rows_failed", 0),
        "results": result.get("results", []),
        "completed_at": datetime.now().isoformat()
    })


@router.post("/upload", response_model=BulkJobResponse)
async def upload_bulk_csv(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    """
    Upload a CSV file for bulk processing.
    
    CSV must have columns:
    - site_id (required, unique)
    - address OR lat+lng (at least one)
    - roof_area_sqm (optional, default 100)
    - roof_material (optional, default 'concrete')
    - state, city, people, floors (optional)
    
    Returns job_id for status tracking.
    """
    
    # Validate file type
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV")
    
    # Read content
    content = await file.read()
    try:
        csv_content = content.decode('utf-8')
    except UnicodeDecodeError:
        csv_content = content.decode('latin-1')
    
    # Count rows
    lines = csv_content.strip().split('\n')
    rows_total = len(lines) - 1  # Exclude header
    
    if rows_total < 1:
        raise HTTPException(status_code=400, detail="CSV must have at least 1 data row")
    
    if rows_total > 10000:
        raise HTTPException(status_code=400, detail="Maximum 10,000 rows allowed per upload")
    
    # Create job
    job_id = str(uuid.uuid4())
    _jobs[job_id] = {
        "job_id": job_id,
        "status": "processing",
        "rows_total": rows_total,
        "rows_processed": 0,
        "rows_success": 0,
        "rows_failed": 0,
        "errors": [],
        "created_at": datetime.now().isoformat(),
        "completed_at": None,
        "results": []
    }
    
    # Start background processing
    background_tasks.add_task(process_bulk_job, job_id, csv_content)
    
    return BulkJobResponse(
        job_id=job_id,
        status="processing",
        rows_total=rows_total,
        rows_processed=0,
        rows_success=0,
        rows_failed=0,
        created_at=_jobs[job_id]["created_at"],
        message=f"Processing {rows_total} sites. Check status at /bulk/status/{job_id}"
    )


@router.get("/status/{job_id}", response_model=BulkJobStatus)
async def get_job_status(job_id: str):
    """
    Get status of a bulk processing job.
    """
    if job_id not in _jobs:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    job = _jobs[job_id]
    
    progress = 0
    if job["rows_total"] > 0:
        progress = (job["rows_processed"] / job["rows_total"]) * 100
    
    download_url = None
    if job["status"] == "completed":
        download_url = f"/api/bulk/{job_id}/download.zip"
    
    return BulkJobStatus(
        job_id=job_id,
        status=job["status"],
        progress_percent=round(progress, 1),
        rows_total=job["rows_total"],
        rows_processed=job["rows_processed"],
        rows_success=job["rows_success"],
        rows_failed=job["rows_failed"],
        errors=job.get("errors", [])[:10],  # First 10 errors
        created_at=job["created_at"],
        completed_at=job.get("completed_at"),
        download_url=download_url
    )


@router.get("/{job_id}/results")
async def get_job_results(
    job_id: str,
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100)
):
    """
    Get paginated results of a completed job.
    """
    if job_id not in _jobs:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    job = _jobs[job_id]
    results = job.get("results", [])
    
    # Paginate
    start = (page - 1) * per_page
    end = start + per_page
    page_results = results[start:end]
    
    return {
        "job_id": job_id,
        "page": page,
        "per_page": per_page,
        "total": len(results),
        "results": page_results
    }


@router.get("/{job_id}/download.zip")
async def download_results_zip(job_id: str):
    """
    Download ZIP file with PDFs for each processed site.
    """
    if job_id not in _jobs:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    job = _jobs[job_id]
    
    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail="Job not completed yet")
    
    # TODO: Generate actual ZIP with PDFs
    # For now, return placeholder
    raise HTTPException(status_code=501, detail="ZIP generation not yet implemented")
