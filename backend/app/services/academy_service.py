"""
Installer Academy Service
Training platform with courses, certifications, and continuing education.
"""

import logging
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class CourseLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class CertificationStatus(str, Enum):
    IN_PROGRESS = "in_progress"
    EXAM_PENDING = "exam_pending"
    CERTIFIED = "certified"
    EXPIRED = "expired"


@dataclass
class Course:
    course_id: str
    title: str
    description: str
    level: CourseLevel
    duration_hours: float
    modules: List[Dict]
    passing_score: int = 70
    
    def to_dict(self) -> Dict:
        return {
            "course_id": self.course_id,
            "title": self.title,
            "description": self.description,
            "level": self.level.value,
            "duration_hours": self.duration_hours,
            "modules_count": len(self.modules)
        }


@dataclass
class Enrollment:
    enrollment_id: str
    user_id: str
    course_id: str
    enrolled_at: datetime
    progress_percent: float = 0
    completed_modules: List[str] = field(default_factory=list)
    quiz_scores: Dict[str, int] = field(default_factory=dict)
    completed_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict:
        return {
            "enrollment_id": self.enrollment_id,
            "course_id": self.course_id,
            "progress_percent": self.progress_percent,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }


@dataclass
class Certification:
    cert_id: str
    user_id: str
    course_id: str
    issued_at: datetime
    valid_until: datetime
    status: CertificationStatus
    score: int
    certificate_url: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            "cert_id": self.cert_id,
            "course_id": self.course_id,
            "issued_at": self.issued_at.isoformat(),
            "valid_until": self.valid_until.isoformat(),
            "status": self.status.value,
            "score": self.score
        }


class AcademyService:
    """Training and certification platform for RWH installers."""
    
    def __init__(self):
        self._courses: Dict[str, Course] = {}
        self._enrollments: Dict[str, Enrollment] = {}
        self._certifications: Dict[str, Certification] = {}
        self._user_enrollments: Dict[str, List[str]] = {}
        
        self._init_courses()
        logger.info("🎓 Academy Service initialized")
    
    def _init_courses(self):
        """Initialize course catalog."""
        courses = [
            Course(
                course_id="RWH-101",
                title="RWH Fundamentals",
                description="Introduction to rainwater harvesting principles and components",
                level=CourseLevel.BEGINNER,
                duration_hours=4,
                modules=[
                    {"id": "m1", "title": "Introduction to RWH", "duration_min": 30},
                    {"id": "m2", "title": "Components Overview", "duration_min": 45},
                    {"id": "m3", "title": "Site Assessment Basics", "duration_min": 60},
                    {"id": "m4", "title": "Safety Guidelines", "duration_min": 45},
                    {"id": "m5", "title": "Quiz & Certification", "duration_min": 30}
                ]
            ),
            Course(
                course_id="RWH-201",
                title="Installation Techniques",
                description="Hands-on installation procedures and best practices",
                level=CourseLevel.INTERMEDIATE,
                duration_hours=8,
                modules=[
                    {"id": "m1", "title": "Pre-installation Checklist", "duration_min": 40},
                    {"id": "m2", "title": "Gutter Installation", "duration_min": 60},
                    {"id": "m3", "title": "Filter Systems", "duration_min": 75},
                    {"id": "m4", "title": "Tank Installation", "duration_min": 90},
                    {"id": "m5", "title": "Plumbing Connections", "duration_min": 60},
                    {"id": "m6", "title": "Quality Testing", "duration_min": 45}
                ]
            ),
            Course(
                course_id="RWH-301",
                title="IoT & Smart Monitoring",
                description="Installing and configuring smart sensors and monitoring",
                level=CourseLevel.ADVANCED,
                duration_hours=6,
                modules=[
                    {"id": "m1", "title": "Sensor Types", "duration_min": 45},
                    {"id": "m2", "title": "Installation & Calibration", "duration_min": 90},
                    {"id": "m3", "title": "App Configuration", "duration_min": 60},
                    {"id": "m4", "title": "Troubleshooting", "duration_min": 75}
                ]
            ),
            Course(
                course_id="RWH-401",
                title="Commercial & Industrial RWH",
                description="Large-scale systems for commercial buildings",
                level=CourseLevel.EXPERT,
                duration_hours=12,
                modules=[
                    {"id": "m1", "title": "Scale Considerations", "duration_min": 60},
                    {"id": "m2", "title": "Hydraulic Design", "duration_min": 120},
                    {"id": "m3", "title": "Pumping Systems", "duration_min": 90},
                    {"id": "m4", "title": "Treatment Systems", "duration_min": 90},
                    {"id": "m5", "title": "Compliance & Codes", "duration_min": 60}
                ]
            )
        ]
        for course in courses:
            self._courses[course.course_id] = course
    
    async def get_course_catalog(self, level: Optional[str] = None) -> Dict[str, Any]:
        courses = list(self._courses.values())
        if level:
            courses = [c for c in courses if c.level.value == level]
        return {
            "success": True,
            "courses": [c.to_dict() for c in courses],
            "total": len(courses)
        }
    
    async def get_course_details(self, course_id: str) -> Dict[str, Any]:
        course = self._courses.get(course_id)
        if not course:
            return {"success": False, "error": "Course not found"}
        return {
            "success": True,
            "course": course.to_dict(),
            "modules": course.modules
        }
    
    async def enroll(self, user_id: str, course_id: str) -> Dict[str, Any]:
        if course_id not in self._courses:
            return {"success": False, "error": "Course not found"}
        
        enrollment_id = f"ENR-{uuid.uuid4().hex[:10].upper()}"
        enrollment = Enrollment(
            enrollment_id=enrollment_id,
            user_id=user_id,
            course_id=course_id,
            enrolled_at=datetime.now()
        )
        self._enrollments[enrollment_id] = enrollment
        self._user_enrollments.setdefault(user_id, []).append(enrollment_id)
        
        return {"success": True, "enrollment": enrollment.to_dict()}
    
    async def update_progress(self, enrollment_id: str, module_id: str,
                             quiz_score: Optional[int] = None) -> Dict[str, Any]:
        enrollment = self._enrollments.get(enrollment_id)
        if not enrollment:
            return {"success": False, "error": "Enrollment not found"}
        
        course = self._courses[enrollment.course_id]
        if module_id not in enrollment.completed_modules:
            enrollment.completed_modules.append(module_id)
        
        if quiz_score is not None:
            enrollment.quiz_scores[module_id] = quiz_score
        
        enrollment.progress_percent = len(enrollment.completed_modules) / len(course.modules) * 100
        
        if enrollment.progress_percent >= 100:
            enrollment.completed_at = datetime.now()
        
        return {
            "success": True,
            "progress": enrollment.progress_percent,
            "completed": enrollment.completed_at is not None
        }
    
    async def take_certification_exam(self, user_id: str, course_id: str,
                                     answers: List[Dict]) -> Dict[str, Any]:
        # Mock exam grading
        score = sum(1 for a in answers if a.get("correct", False)) / len(answers) * 100
        score = int(score)
        
        course = self._courses.get(course_id)
        passed = score >= course.passing_score
        
        if passed:
            cert_id = f"CERT-{uuid.uuid4().hex[:10].upper()}"
            cert = Certification(
                cert_id=cert_id,
                user_id=user_id,
                course_id=course_id,
                issued_at=datetime.now(),
                valid_until=datetime.now() + timedelta(days=365),
                status=CertificationStatus.CERTIFIED,
                score=score,
                certificate_url=f"/api/v1/academy/certificates/{cert_id}/download"
            )
            self._certifications[cert_id] = cert
            return {
                "success": True,
                "passed": True,
                "score": score,
                "certification": cert.to_dict()
            }
        
        return {"success": True, "passed": False, "score": score}
    
    async def get_user_certifications(self, user_id: str) -> Dict[str, Any]:
        certs = [c.to_dict() for c in self._certifications.values() 
                 if c.user_id == user_id]
        return {"success": True, "certifications": certs}
    
    async def verify_certification(self, cert_id: str) -> Dict[str, Any]:
        cert = self._certifications.get(cert_id)
        if not cert:
            return {"valid": False, "error": "Certificate not found"}
        
        is_valid = cert.status == CertificationStatus.CERTIFIED and \
                   cert.valid_until > datetime.now()
        
        return {
            "valid": is_valid,
            "certification": cert.to_dict() if is_valid else None
        }


_service: Optional[AcademyService] = None

def get_academy_service() -> AcademyService:
    global _service
    if _service is None:
        _service = AcademyService()
    return _service
