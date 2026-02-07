"""
Academy API Endpoints
Training courses and certifications for installers.
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List, Dict

from app.services.academy_service import get_academy_service

router = APIRouter(prefix="/academy", tags=["Academy"])


class EnrollRequest(BaseModel):
    user_id: str
    course_id: str

class ProgressUpdateRequest(BaseModel):
    enrollment_id: str
    module_id: str
    quiz_score: Optional[int] = None

class ExamSubmitRequest(BaseModel):
    user_id: str
    course_id: str
    answers: List[Dict]


@router.get("/courses")
async def get_courses(level: Optional[str] = None):
    """Get course catalog."""
    service = get_academy_service()
    return await service.get_course_catalog(level)

@router.get("/courses/{course_id}")
async def get_course_details(course_id: str):
    """Get course details with modules."""
    service = get_academy_service()
    return await service.get_course_details(course_id)

@router.post("/enroll")
async def enroll_in_course(request: EnrollRequest):
    """Enroll in a course."""
    service = get_academy_service()
    return await service.enroll(request.user_id, request.course_id)

@router.post("/progress")
async def update_progress(request: ProgressUpdateRequest):
    """Update course progress."""
    service = get_academy_service()
    return await service.update_progress(
        request.enrollment_id, request.module_id, request.quiz_score
    )

@router.post("/exam")
async def submit_exam(request: ExamSubmitRequest):
    """Submit certification exam."""
    service = get_academy_service()
    return await service.take_certification_exam(
        request.user_id, request.course_id, request.answers
    )

@router.get("/certifications/{user_id}")
async def get_certifications(user_id: str):
    """Get user's certifications."""
    service = get_academy_service()
    return await service.get_user_certifications(user_id)

@router.get("/verify/{cert_id}")
async def verify_certification(cert_id: str):
    """Verify a certification."""
    service = get_academy_service()
    return await service.verify_certification(cert_id)
