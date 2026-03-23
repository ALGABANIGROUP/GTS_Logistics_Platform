from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class BotSpecialization(str, Enum):
    SECURITY = "security"
    LOGISTICS = "logistics"
    CUSTOMER_SERVICE = "customer_service"
    OPERATIONS = "operations"
    FINANCE = "finance"
    LEGAL = "legal"
    SALES = "sales"
    MANAGEMENT = "management"
    SYSTEM = "system"
    TRAINING = "training"
    GENERAL = "general"


class TrainingLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"
    MASTER = "master"


@dataclass
class BotProfile:
    bot_key: str
    bot_name: str
    specialization: BotSpecialization
    version: str = "1.0"
    current_level: TrainingLevel = TrainingLevel.BEGINNER
    description: str = ""
    source_category: str = ""
    strengths: list[str] = field(default_factory=list)
    weak_points: list[str] = field(default_factory=list)
    skills: dict[str, float] = field(default_factory=dict)
    training_history: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class TrainingPlan:
    plan_id: str
    bot_key: str
    bot_name: str
    specialization: str
    current_level: str
    target_level: str
    goal: str
    created_at: str
    duration_days: int
    total_hours: int
    courses: list[dict[str, Any]]
    milestones: list[dict[str, Any]]
    target_skills: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class TrainingSession:
    session_id: str
    plan_id: str
    bot_key: str
    bot_name: str
    status: str
    started_at: str
    completed_at: str | None = None
    progress: list[str] = field(default_factory=list)
    completed_courses: list[dict[str, Any]] = field(default_factory=list)
    final_score: float | None = None
    certificate: dict[str, Any] | None = None
    improvements: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class CertificateRecord:
    certificate_id: str
    bot_key: str
    bot_name: str
    level_achieved: str
    final_score: float
    issued_at: str
    courses_completed: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class TrainingReport:
    session_id: str
    plan_id: str
    bot_key: str
    bot_name: str
    specialization: str
    trainer_name: str
    started_at: str
    completed_at: str
    final_score: float
    grade: str
    recommendations: list[str]
    completed_courses: list[dict[str, Any]]
    improvements: dict[str, Any]
    certificate: dict[str, Any] | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
