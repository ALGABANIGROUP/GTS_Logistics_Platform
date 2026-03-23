from __future__ import annotations

from .knowledge_base import KnowledgeBase
from .models import BotSpecialization, TrainingLevel


class LearningPathManager:
    """Resolve specialization-aware learning paths and level progression."""

    def __init__(self, knowledge_base: KnowledgeBase | None = None) -> None:
        self.knowledge_base = knowledge_base or KnowledgeBase()

    def get_path(
        self,
        *,
        specialization: BotSpecialization,
        current_level: TrainingLevel,
        goal: str | None = None,
    ) -> dict[str, object]:
        target_level = self.knowledge_base.next_level(current_level)
        focus_skills = self.knowledge_base.specialization_focus(specialization)
        return {
            "specialization": specialization.value,
            "current_level": current_level.value,
            "target_level": target_level.value,
            "goal": goal or self.knowledge_base.infer_goal(specialization, []),
            "focus_skills": focus_skills,
        }
