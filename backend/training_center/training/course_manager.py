from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from backend.training_center.core.models import TrainingLevel


class CourseManager:
    """Load and select courses for a given training path."""

    def __init__(self, *, data_dir: Path) -> None:
        self.data_dir = data_dir
        self.courses = self._load_courses()
        self._level_order = [
            TrainingLevel.BEGINNER.value,
            TrainingLevel.INTERMEDIATE.value,
            TrainingLevel.ADVANCED.value,
            TrainingLevel.EXPERT.value,
            TrainingLevel.MASTER.value,
        ]

    def _load_courses(self) -> list[dict[str, Any]]:
        with (self.data_dir / "courses.json").open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def list_courses(self, specialization: str | None = None) -> list[dict[str, Any]]:
        if not specialization:
            return list(self.courses)
        return [course for course in self.courses if course["specialization"] == specialization]

    async def select_courses(
        self,
        *,
        learning_path: dict[str, object],
        weak_points: list[str],
        target_level: str,
    ) -> list[dict[str, Any]]:
        specialization = str(learning_path["specialization"])
        target_index = self._resolve_level_index(target_level)
        current_index = self._resolve_level_index(str(learning_path["current_level"]))
        candidates = []
        for course in self.list_courses(specialization):
            course_level_index = self._resolve_level_index(course["level"])
            if current_index <= course_level_index <= target_index:
                score = 0
                if any(skill in course["skills_improved"] for skill in weak_points):
                    score += 10
                if set(course["skills_improved"]) & set(learning_path["focus_skills"]):
                    score += 5
                candidates.append((score, course_level_index, course))

        candidates.sort(key=lambda item: (-item[0], item[1], item[2]["id"]))
        selected = [item[2] for item in candidates[:5]]
        if not selected:
            selected = self.list_courses(specialization)[:2]
        return selected

    def _resolve_level_index(self, level: str) -> int:
        try:
            return self._level_order.index(level)
        except ValueError:
            return 0
