# backend/routes/training_center.py
"""
Training Center Routes - Educational and training resources
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/training", tags=["training"])

# Models
class TrainingModule(BaseModel):
    id: Optional[str] = None
    title: str
    description: str
    category: str  # "onboarding", "compliance", "technical", "soft_skills"
    duration_minutes: int
    content_url: str
    required: bool = False
    created_at: datetime = Field(default_factory=datetime.now)

class TrainingProgress(BaseModel):
    user_id: str
    module_id: str
    status: str  # "not_started", "in_progress", "completed"
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    score: Optional[float] = None

class TrainingAssessment(BaseModel):
    module_id: str
    answers: dict
    user_id: str

# Mock data storage (replace with database)
training_modules = []
user_progress = []

@router.get("/modules", response_model=List[TrainingModule])
async def get_training_modules(
    category: Optional[str] = None,
    required_only: bool = False
):
    """Get available training modules"""
    modules = training_modules
    if category:
        modules = [m for m in modules if m.category == category]
    if required_only:
        modules = [m for m in modules if m.required]
    return modules

@router.post("/modules", response_model=TrainingModule)
async def create_training_module(module: TrainingModule):
    """Create new training module (admin only)"""
    module.id = f"mod_{len(training_modules) + 1}"
    training_modules.append(module)
    logger.info(f"Created training module: {module.title}")
    return module

@router.get("/progress/{user_id}", response_model=List[TrainingProgress])
async def get_user_progress(user_id: str):
    """Get user's training progress"""
    return [p for p in user_progress if p.user_id == user_id]

@router.post("/start/{module_id}")
async def start_training(module_id: str, user_id: str):
    """Start a training module"""
    progress = TrainingProgress(
        user_id=user_id,
        module_id=module_id,
        status="in_progress",
        started_at=datetime.now()
    )
    user_progress.append(progress)
    return {"status": "started", "module_id": module_id}

@router.post("/complete/{module_id}")
async def complete_training(module_id: str, user_id: str, assessment: Optional[TrainingAssessment] = None):
    """Complete a training module"""
    for progress in user_progress:
        if progress.user_id == user_id and progress.module_id == module_id:
            progress.status = "completed"
            progress.completed_at = datetime.now()
            if assessment:
                # Evaluate assessment
                progress.score = await evaluate_assessment(assessment)
            return {"status": "completed", "module_id": module_id}

    raise HTTPException(status_code=404, detail="Training session not found")

async def evaluate_assessment(assessment: TrainingAssessment) -> float:
    """Evaluate assessment answers"""
    # Implement assessment evaluation logic
    return 85.0  # Placeholder


@router.get("/reports/{session_id}")
async def get_report(session_id: str):
    report = _trainer.get_report(session_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return {"success": True, "report": report}


@router.get("/stats")
async def get_stats():
    return {"success": True, "stats": _trainer.get_stats()}
