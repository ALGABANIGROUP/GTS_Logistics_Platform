# backend/routes/trainer_bot.py
from fastapi import APIRouter, HTTPException, Depends, status, Query
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging
from pydantic import BaseModel, Field

from backend.database.session import get_async_session
from backend.security.auth import get_current_user

router = APIRouter(prefix="/api/v1/trainer", tags=["Trainer Bot"])
logger = logging.getLogger(__name__)


# ==================== Models ====================
class Course(BaseModel):
    id: str
    title: str
    description: str
    category: str  # safety, compliance, operations, soft_skills, technical
    duration_hours: int
    difficulty: str  # beginner, intermediate, advanced
    status: str  # draft, published, archived
    enrolled_users: int
    completion_rate: float
    created_at: str


class TrainingModule(BaseModel):
    id: str
    course_id: str
    title: str
    content_type: str  # video, document, quiz, simulation
    duration_minutes: int
    order: int


class UserProgress(BaseModel):
    user_id: int
    user_email: str
    course_id: str
    progress_percent: float
    completed_modules: List[str]
    last_accessed: str
    status: str  # not_started, in_progress, completed
    score: Optional[float]


# ==================== Seed Data ====================
COURSES = [
    {
        "id": "course_001",
        "title": "Commercial Vehicle Safety Inspection",
        "description": "Learn how to properly inspect commercial vehicles for safety compliance",
        "category": "safety",
        "duration_hours": 4,
        "difficulty": "beginner",
        "status": "published",
        "enrolled_users": 156,
        "completion_rate": 87.5,
        "created_at": "2026-01-15T00:00:00",
        "modules": [
            {"id": "mod_001", "title": "Pre-Trip Inspection", "content_type": "video", "duration_minutes": 45, "order": 1},
            {"id": "mod_002", "title": "Brake Systems Check", "content_type": "video", "duration_minutes": 30, "order": 2},
            {"id": "mod_003", "title": "Lights and Signals", "content_type": "quiz", "duration_minutes": 20, "order": 3}
        ]
    },
    {
        "id": "course_002",
        "title": "HOS Compliance for Drivers",
        "description": "Hours of Service regulations and ELD compliance training",
        "category": "compliance",
        "duration_hours": 3,
        "difficulty": "beginner",
        "status": "published",
        "enrolled_users": 234,
        "completion_rate": 92.3,
        "created_at": "2026-01-20T00:00:00",
        "modules": [
            {"id": "mod_004", "title": "HOS Basics", "content_type": "video", "duration_minutes": 40, "order": 1},
            {"id": "mod_005", "title": "ELD Requirements", "content_type": "document", "duration_minutes": 25, "order": 2},
            {"id": "mod_006", "title": "HOS Scenarios", "content_type": "simulation", "duration_minutes": 35, "order": 3}
        ]
    },
    {
        "id": "course_003",
        "title": "Dangerous Goods Transportation",
        "description": "Safe handling and transportation of hazardous materials",
        "category": "safety",
        "duration_hours": 8,
        "difficulty": "advanced",
        "status": "published",
        "enrolled_users": 89,
        "completion_rate": 76.4,
        "created_at": "2026-02-01T00:00:00",
        "modules": [
            {"id": "mod_007", "title": "Classification of DG", "content_type": "video", "duration_minutes": 60, "order": 1},
            {"id": "mod_008", "title": "Packaging and Labeling", "content_type": "document", "duration_minutes": 45, "order": 2},
            {"id": "mod_009", "title": "Emergency Response", "content_type": "simulation", "duration_minutes": 50, "order": 3}
        ]
    },
    {
        "id": "course_004",
        "title": "Customer Service Excellence",
        "description": "Best practices for customer interaction and problem resolution",
        "category": "soft_skills",
        "duration_hours": 2,
        "difficulty": "beginner",
        "status": "published",
        "enrolled_users": 312,
        "completion_rate": 94.2,
        "created_at": "2026-02-10T00:00:00"
    },
    {
        "id": "course_005",
        "title": "Fleet Management Fundamentals",
        "description": "Core concepts of fleet operations and maintenance",
        "category": "operations",
        "duration_hours": 6,
        "difficulty": "intermediate",
        "status": "draft",
        "enrolled_users": 0,
        "completion_rate": 0,
        "created_at": "2026-03-01T00:00:00"
    }
]

USER_TRAINING_PROGRESS = [
    {
        "user_id": 1,
        "user_email": "superadmin@gts.com",
        "course_id": "course_001",
        "progress_percent": 100,
        "completed_modules": ["mod_001", "mod_002", "mod_003"],
        "last_accessed": "2026-04-01T10:30:00",
        "status": "completed",
        "score": 95.5
    },
    {
        "user_id": 1,
        "user_email": "superadmin@gts.com",
        "course_id": "course_002",
        "progress_percent": 65,
        "completed_modules": ["mod_004"],
        "last_accessed": "2026-04-05T14:20:00",
        "status": "in_progress",
        "score": None
    },
    {
        "user_id": 2,
        "user_email": "admin@gts.com",
        "course_id": "course_001",
        "progress_percent": 100,
        "completed_modules": ["mod_001", "mod_002", "mod_003"],
        "last_accessed": "2026-03-28T09:15:00",
        "status": "completed",
        "score": 98.0
    },
    {
        "user_id": 3,
        "user_email": "dispatcher@gts.com",
        "course_id": "course_004",
        "progress_percent": 45,
        "completed_modules": [],
        "last_accessed": "2026-04-03T11:00:00",
        "status": "in_progress",
        "score": None
    }
]

TRAINING_STATS = {
    "total_courses": len(COURSES),
    "published_courses": len([c for c in COURSES if c["status"] == "published"]),
    "total_enrollments": sum(c["enrolled_users"] for c in COURSES),
    "average_completion_rate": 87.6,
    "active_learners": 45,
    "certifications_issued": 128,
    "popular_categories": {
        "safety": 2,
        "compliance": 1,
        "operations": 1,
        "soft_skills": 1
    }
}

SIMULATIONS = [
    {
        "id": "sim_001",
        "name": "Emergency Braking Scenario",
        "type": "driving",
        "difficulty": "intermediate",
        "duration_minutes": 15,
        "completions": 234,
        "avg_score": 87.5
    },
    {
        "id": "sim_002",
        "name": "Hazardous Spill Response",
        "type": "safety",
        "difficulty": "advanced",
        "duration_minutes": 20,
        "completions": 89,
        "avg_score": 76.2
    },
    {
        "id": "sim_003",
        "name": "Customer Complaint Handling",
        "type": "soft_skills",
        "difficulty": "beginner",
        "duration_minutes": 10,
        "completions": 312,
        "avg_score": 91.3
    }
]


# ==================== API Endpoints ====================

@router.get("/test")
async def test_trainer_endpoint():
    """Test endpoint that doesn't require authentication"""
    return {"status": "ok", "message": "Trainer bot router is working"}

@router.get("/dashboard")
async def get_trainer_dashboard(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get trainer bot dashboard data"""
    return {
        "stats": TRAINING_STATS,
        "recent_courses": [c for c in COURSES if c["status"] == "published"][:5],
        "active_courses": [c for c in COURSES if c["status"] == "published" and c["enrolled_users"] > 0],
        "popular_simulations": SIMULATIONS[:3],
        "user_progress_summary": {
            "total_users_training": len(set(p["user_id"] for p in USER_TRAINING_PROGRESS)),
            "completed_courses": len([p for p in USER_TRAINING_PROGRESS if p["status"] == "completed"]),
            "in_progress": len([p for p in USER_TRAINING_PROGRESS if p["status"] == "in_progress"])
        }
    }


@router.get("/courses")
async def get_courses(
    category: Optional[str] = None,
    status: Optional[str] = None,
    difficulty: Optional[str] = None,
    limit: int = 50,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get all training courses"""
    courses = COURSES.copy()

    if category:
        courses = [c for c in courses if c["category"] == category]
    if status:
        courses = [c for c in courses if c["status"] == status]
    if difficulty:
        courses = [c for c in courses if c["difficulty"] == difficulty]

    return {
        "courses": courses[:limit],
        "total": len(courses)
    }


@router.get("/courses/{course_id}")
async def get_course_details(
    course_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get detailed course information"""
    course = next((c for c in COURSES if c["id"] == course_id), None)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course


@router.get("/courses/{course_id}/modules")
async def get_course_modules(
    course_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get modules for a specific course"""
    course = next((c for c in COURSES if c["id"] == course_id), None)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    modules = course.get("modules", [])
    modules.sort(key=lambda x: x["order"])

    return {"modules": modules, "total": len(modules)}


@router.get("/progress")
async def get_user_progress(
    user_id: Optional[int] = None,
    course_id: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get user training progress"""
    user_role = current_user.get("role", "").lower()

    # Filter by user_id (only admins can see others)
    if user_id and user_role not in ["super_admin", "admin"]:
        user_id = current_user.get("id")
    elif not user_id:
        user_id = current_user.get("id")

    progress = [p for p in USER_TRAINING_PROGRESS if p["user_id"] == user_id]

    if course_id:
        progress = [p for p in progress if p["course_id"] == course_id]

    return {
        "progress": progress,
        "summary": {
            "completed": len([p for p in progress if p["status"] == "completed"]),
            "in_progress": len([p for p in progress if p["status"] == "in_progress"]),
            "not_started": len([c for c in COURSES if c["status"] == "published" and not any(p["course_id"] == c["id"] for p in progress)])
        }
    }


@router.post("/progress/{course_id}/start")
async def start_course(
    course_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Start a course for the current user"""
    course = next((c for c in COURSES if c["id"] == course_id), None)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    existing = next((p for p in USER_TRAINING_PROGRESS
                     if p["user_id"] == current_user.get("id") and p["course_id"] == course_id), None)

    if existing:
        return {"message": "Course already started", "progress": existing}

    new_progress = {
        "user_id": current_user.get("id"),
        "user_email": current_user.get("email"),
        "course_id": course_id,
        "progress_percent": 0,
        "completed_modules": [],
        "last_accessed": datetime.now().isoformat(),
        "status": "in_progress",
        "score": None
    }

    USER_TRAINING_PROGRESS.append(new_progress)

    return {"message": "Course started", "progress": new_progress}


@router.post("/progress/{course_id}/complete")
async def complete_module(
    course_id: str,
    module_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Mark a module as completed"""
    progress = next((p for p in USER_TRAINING_PROGRESS
                     if p["user_id"] == current_user.get("id") and p["course_id"] == course_id), None)

    if not progress:
        raise HTTPException(status_code=404, detail="Course not started")

    if module_id not in progress["completed_modules"]:
        progress["completed_modules"].append(module_id)

        # Calculate progress percentage
        course = next((c for c in COURSES if c["id"] == course_id), None)
        if course and "modules" in course:
            total_modules = len(course["modules"])
            progress["progress_percent"] = (len(progress["completed_modules"]) / total_modules) * 100
            progress["last_accessed"] = datetime.now().isoformat()

            if progress["progress_percent"] == 100:
                progress["status"] = "completed"

    return {"message": "Module completed", "progress": progress}


@router.get("/simulations")
async def get_simulations(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get all training simulations"""
    return {"simulations": SIMULATIONS, "total": len(SIMULATIONS)}


@router.get("/certifications")
async def get_user_certifications(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get user certifications"""
    completed_courses = [p for p in USER_TRAINING_PROGRESS
                         if p["user_id"] == current_user.get("id") and p["status"] == "completed"]

    certifications = []
    for progress in completed_courses:
        course = next((c for c in COURSES if c["id"] == progress["course_id"]), None)
        if course:
            certifications.append({
                "course_id": course["id"],
                "course_title": course["title"],
                "issued_date": progress["last_accessed"],
                "score": progress.get("score", 85.0),
                "certificate_url": f"/certificates/{course['id']}_{current_user.get('id')}.pdf"
            })

    return {"certifications": certifications, "total": len(certifications)}


@router.get("/stats")
async def get_training_stats(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get training statistics (admin only)"""
    user_role = current_user.get("role", "").lower()
    if user_role not in ["super_admin", "admin"]:
        raise HTTPException(status_code=403, detail="Admin access required")

    return TRAINING_STATS


@router.post("/courses")
async def create_course(
    course: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Create a new course (admin only)"""
    user_role = current_user.get("role", "").lower()
    if user_role not in ["super_admin", "admin"]:
        raise HTTPException(status_code=403, detail="Admin access required")

    new_id = f"course_{len(COURSES) + 1:03d}"
    new_course = {
        "id": new_id,
        **course,
        "enrolled_users": 0,
        "completion_rate": 0,
        "created_at": datetime.now().isoformat(),
        "status": "draft"
    }

    COURSES.append(new_course)
    logger.info(f"Course created: {new_id} by {current_user.get('email')}")

    return new_course