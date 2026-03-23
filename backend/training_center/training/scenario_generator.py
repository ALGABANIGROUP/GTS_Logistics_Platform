from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Any

from backend.training_center.core.models import TrainingLevel


class ScenarioGenerator:
    """Generate realistic scenarios from reusable templates."""

    def __init__(self, *, data_dir: Path, seed: int | None = None) -> None:
        self.data_dir = data_dir
        self._random = random.Random(seed)
        self.scenario_templates = self._load_scenarios()

    def _load_scenarios(self) -> list[dict[str, Any]]:
        with (self.data_dir / "scenarios.json").open("r", encoding="utf-8") as handle:
            return json.load(handle)

    async def generate_scenarios(
        self,
        *,
        specialization: str,
        level: TrainingLevel,
        course_topics: list[str],
    ) -> list[dict[str, Any]]:
        templates = [item for item in self.scenario_templates if item["specialization"] == specialization]
        level_factor = {
            TrainingLevel.BEGINNER.value: 0.7,
            TrainingLevel.INTERMEDIATE.value: 0.85,
            TrainingLevel.ADVANCED.value: 1.0,
            TrainingLevel.EXPERT.value: 1.15,
            TrainingLevel.MASTER.value: 1.25,
        }[level.value]
        chosen = templates[: min(3, len(templates))]
        scenarios = []
        for template in chosen:
            template_steps = []
            for index, step in enumerate(template["template_steps"], start=1):
                template_steps.append(
                    {
                        "type": step["type"],
                        "description": step["description"],
                        "difficulty_modifier": max(0, int(template["difficulty"] * level_factor) - 5),
                        "order": index,
                    }
                )
            scenarios.append(
                {
                    "id": template["id"],
                    "name": template["name"],
                    "specialization": template["specialization"],
                    "difficulty": min(10, max(1, int(round(template["difficulty"] * level_factor)))),
                    "duration_minutes": template["duration_minutes"],
                    "required_skills": template["required_skills"],
                    "related_topics": course_topics[:2],
                    "steps": template_steps,
                }
            )
        return scenarios
