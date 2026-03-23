from __future__ import annotations

from .models import BotSpecialization, TrainingLevel


class KnowledgeBase:
    """Reusable training metadata and specialization helpers."""

    def __init__(self) -> None:
        self._level_order = [
            TrainingLevel.BEGINNER,
            TrainingLevel.INTERMEDIATE,
            TrainingLevel.ADVANCED,
            TrainingLevel.EXPERT,
            TrainingLevel.MASTER,
        ]

    def next_level(self, current_level: TrainingLevel) -> TrainingLevel:
        try:
            index = self._level_order.index(current_level)
        except ValueError:
            return TrainingLevel.INTERMEDIATE
        return self._level_order[min(index + 1, len(self._level_order) - 1)]

    def specialization_focus(self, specialization: BotSpecialization) -> list[str]:
        mapping = {
            BotSpecialization.SECURITY: ["incident_detection", "containment", "threat_analysis"],
            BotSpecialization.LOGISTICS: ["routing", "recovery_planning", "shipment_visibility"],
            BotSpecialization.CUSTOMER_SERVICE: ["de_escalation", "issue_resolution", "communication"],
            BotSpecialization.OPERATIONS: ["workflow_coordination", "resource_balancing", "exception_handling"],
            BotSpecialization.FINANCE: ["financial_accuracy", "risk_controls", "reconciliation"],
            BotSpecialization.LEGAL: ["policy_interpretation", "compliance_review", "case_analysis"],
            BotSpecialization.SALES: ["negotiation", "qualification", "follow_up"],
            BotSpecialization.MANAGEMENT: ["decision_quality", "oversight", "prioritization"],
            BotSpecialization.SYSTEM: ["observability", "reliability", "incident_response"],
            BotSpecialization.TRAINING: ["assessment", "curriculum_design", "simulation_control"],
        }
        return mapping.get(specialization, ["judgement", "communication", "reliability"])

    def infer_goal(self, specialization: BotSpecialization, weak_points: list[str]) -> str:
        if weak_points:
            if specialization == BotSpecialization.SECURITY:
                return "Improve detection and response under coordinated security incidents."
            if specialization == BotSpecialization.LOGISTICS:
                return "Improve crisis handling for shipment disruption scenarios."
            if specialization == BotSpecialization.CUSTOMER_SERVICE:
                return "Improve customer recovery and de-escalation performance."
            if specialization == BotSpecialization.OPERATIONS:
                return "Improve workflow prioritization and service continuity."
        return f"Advance {specialization.value.replace('_', ' ')} readiness to the next level."

    def default_skills(self, specialization: BotSpecialization) -> dict[str, float]:
        return {skill: 55.0 for skill in self.specialization_focus(specialization)}

    def milestone_title(self, course_name: str) -> str:
        return f"Complete {course_name}"
