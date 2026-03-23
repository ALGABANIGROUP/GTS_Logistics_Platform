"""
Safety Core Module
Training Manager System
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class TrainingManager:
    """Manages training programs, expirations, and training sessions."""

    def __init__(self):
        self.training_records = []
        self.training_programs = self._load_training_programs()

    def _load_training_programs(self) -> Dict[str, Any]:
        """Load built-in training program catalog."""
        return {
            "basic_safety": {
                "id": "TRN-001",
                "title": "Basic Safety Orientation",
                "duration_hours": 8,
                "required_frequency": "annual",
                "description": "Core workplace safety principles and hazard awareness",
            },
            "fire_safety": {
                "id": "TRN-002",
                "title": "Fire Safety and Evacuation",
                "duration_hours": 4,
                "required_frequency": "biannual",
                "description": "Fire prevention, alarm response, and evacuation procedures",
            },
            "first_aid": {
                "id": "TRN-003",
                "title": "First Aid Fundamentals",
                "duration_hours": 6,
                "required_frequency": "biannual",
                "description": "Emergency first aid skills and response protocols",
            },
            "equipment_operation": {
                "id": "TRN-004",
                "title": "Safe Equipment Operation",
                "duration_hours": 12,
                "required_frequency": "annual",
                "description": "Operational safety standards for company equipment",
            },
        }

    async def check_training_requirements(self) -> Dict[str, Any]:
        """Check expired and upcoming training requirements."""
        try:
            report = {
                "check_date": datetime.utcnow().isoformat(),
                "expired_training": [],
                "upcoming_expirations": [],
                "training_compliance_rate": 85.5,
            }

            # Sample expired records
            report["expired_training"] = [
                {
                    "employee": "Alex Johnson",
                    "course": "Basic Safety Orientation",
                    "expired_date": "2024-12-01",
                    "action_required": "Schedule mandatory retraining",
                }
            ]

            # Sample upcoming expirations
            report["upcoming_expirations"] = [
                {
                    "employee": "Maya Lee",
                    "course": "First Aid Fundamentals",
                    "expiry_date": "2026-02-15",
                    "days_remaining": 39,
                }
            ]

            return report

        except Exception as e:
            logger.error(f"Training requirements check failed: {str(e)}")
            return {"error": str(e)}

    async def schedule_training_course(
        self,
        course_id: str,
        participants: List[str],
        scheduled_date: str,
    ) -> Dict[str, Any]:
        """Schedule a training course session for participants."""
        try:
            program = self.training_programs.get(course_id)

            if not program:
                return {"error": f"Course {course_id} not found"}

            training_session = {
                "session_id": f"SES_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                "course_id": course_id,
                "course_title": program["title"],
                "participants": participants,
                "scheduled_date": scheduled_date,
                "duration_hours": program["duration_hours"],
                "status": "scheduled",
                "created_at": datetime.utcnow().isoformat(),
            }

            self.training_records.append(training_session)

            return training_session

        except Exception as e:
            logger.error(f"Training course scheduling failed: {str(e)}")
            return {"error": str(e)}

    async def complete_training_course(
        self, session_id: str, participants_completed: List[str]
    ) -> Dict[str, Any]:
        """Mark a scheduled training session as completed."""
        try:
            completion = {
                "completion_id": f"COMP_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                "session_id": session_id,
                "participants_completed": participants_completed,
                "completed_at": datetime.utcnow().isoformat(),
                "status": "completed",
            }

            return completion

        except Exception as e:
            logger.error(f"Training course completion failed: {str(e)}")
            return {"error": str(e)}
