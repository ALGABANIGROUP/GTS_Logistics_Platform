from __future__ import annotations

import asyncio
import random
from typing import Any


class AssessmentSystem:
    """Run baseline, course, and final assessments."""

    def __init__(self, *, seed: int | None = None) -> None:
        self._random = random.Random(seed)
        self.assessment_history: list[dict[str, Any]] = []
        self.test_bank = self._load_test_bank()

    def _load_test_bank(self) -> dict[str, list[str]]:
        return {
            "security": ["incident_detection", "threat_analysis", "containment"],
            "logistics": ["routing", "recovery_planning", "shipment_visibility"],
            "customer_service": ["communication", "de_escalation", "issue_resolution"],
            "operations": ["workflow_coordination", "resource_balancing", "exception_handling"],
        }

    async def run_basic_assessment(self, profile) -> dict[str, Any]:
        focus_skills = self.test_bank.get(profile.specialization.value, ["judgement", "communication", "reliability"])
        skills = {}
        for skill in focus_skills:
            skills[skill] = round(self._random.uniform(52, 86), 2)
            await asyncio.sleep(0)
        overall_score = round(sum(skills.values()) / len(skills), 2)
        result = {"bot_key": profile.bot_key, "phase": "baseline", "skills": skills, "overall_score": overall_score}
        self.assessment_history.append(result)
        return result

    async def run_course_test(self, profile, course: dict[str, Any]) -> dict[str, Any]:
        score = round(self._random.uniform(max(55, course["passing_score"] - 5), 96), 2)
        result = {"bot_key": profile.bot_key, "phase": "course", "course_id": course["id"], "score": score}
        self.assessment_history.append(result)
        return result

    async def written_test(self, profile, specialization: str) -> float:
        focus_skills = self.test_bank.get(specialization, ["judgement", "communication", "reliability"])
        base = sum(self._random.uniform(65, 94) for _ in focus_skills) / len(focus_skills)
        result = round(base, 2)
        self.assessment_history.append({"bot_key": profile.bot_key, "phase": "written", "score": result})
        return result

    async def final_practical_test(self, profile, specialization: str) -> float:
        challenge_scores = []
        for difficulty in (9, 8, 7):
            challenge_scores.append(max(0.0, self._random.uniform(72, 97) - difficulty))
            await asyncio.sleep(0)
        result = round(sum(challenge_scores) / len(challenge_scores), 2)
        self.assessment_history.append({"bot_key": profile.bot_key, "phase": "final_practical", "score": result})
        return result

    @staticmethod
    def get_grade(score: float) -> str:
        if score >= 90:
            return "Excellent"
        if score >= 80:
            return "Very Good"
        if score >= 70:
            return "Good"
        if score >= 60:
            return "Pass"
        return "Retraining Required"
