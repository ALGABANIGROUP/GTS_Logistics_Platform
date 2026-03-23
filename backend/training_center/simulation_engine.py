from __future__ import annotations

import asyncio
import random
from datetime import datetime, timezone
from typing import Any


class SimulationEngine:
    """Create repeatable simulation runs for bot training."""

    def __init__(self, *, seed: int | None = None) -> None:
        self._random = random.Random(seed)
        self.active_simulations: dict[str, dict[str, Any]] = {}
        self.simulation_history: list[dict[str, Any]] = []

    async def run_scenario(self, bot_name: str, scenario: dict[str, Any]) -> dict[str, Any]:
        simulation_id = f"sim_{bot_name}_{scenario['id']}_{self._random.randint(1000, 9999)}"
        state = {
            "bot_name": bot_name,
            "scenario": scenario["id"],
            "started_at": datetime.now(timezone.utc).isoformat(),
            "status": "running",
            "steps_completed": [],
        }
        self.active_simulations[simulation_id] = state

        steps_result: list[dict[str, Any]] = []
        for step in scenario.get("steps", []):
            result = await self.execute_step(bot_name, step)
            steps_result.append(result)
            state["steps_completed"].append(step["type"])
            if not result["success"]:
                break

        score = self.calculate_score(steps_result, scenario)
        report = {
            "simulation_id": simulation_id,
            "bot_name": bot_name,
            "scenario_id": scenario["id"],
            "scenario_name": scenario["name"],
            "difficulty": scenario["difficulty"],
            "steps_completed": len(steps_result),
            "total_steps": len(scenario.get("steps", [])),
            "score": score,
            "feedback": self.generate_feedback(steps_result),
            "completed_at": datetime.now(timezone.utc).isoformat(),
        }

        state["status"] = "completed"
        state["report"] = report
        self.simulation_history.append(report)
        return report

    async def execute_step(self, bot_name: str, step: dict[str, Any]) -> dict[str, Any]:
        await asyncio.sleep(0)
        success_rate = self._resolve_success_rate(bot_name, step)
        success = self._random.randint(1, 100) <= success_rate
        return {
            "step": step,
            "success": success,
            "response_time_seconds": round(self._random.uniform(0.1, 3.0), 2),
            "accuracy": success_rate if success else self._random.randint(20, 55),
            "response": self.simulate_bot_response(step),
        }

    def _resolve_success_rate(self, bot_name: str, step: dict[str, Any]) -> int:
        base = 82
        if "security" in bot_name.lower():
            if step.get("type") in {"phishing", "credential_steal", "ddos", "mitigation_test"}:
                base += 8
        if "service" in bot_name.lower() and step.get("type") == "angry_customer":
            base += 6
        difficulty_factor = int(step.get("difficulty_modifier", 0))
        return max(35, min(98, base - difficulty_factor))

    def simulate_bot_response(self, step: dict[str, Any]) -> str:
        responses = {
            "phishing": [
                "Flagged the suspicious sender and isolated the message.",
                "Triggered safe analysis for the phishing payload.",
            ],
            "ddos": [
                "Applied traffic filtering and rate limiting.",
                "Redirected suspicious traffic for mitigation.",
            ],
            "credential_steal": [
                "Revoked exposed credentials and started incident containment.",
                "Locked the impacted identity and alerted security.",
            ],
            "delay": [
                "Issued a customer update and recalculated ETA.",
                "Escalated the lane disruption and prepared alternatives.",
            ],
            "angry_customer": [
                "Acknowledged frustration and moved to structured recovery.",
                "De-escalated the conversation and confirmed next steps.",
            ],
        }
        return self._random.choice(responses.get(step.get("type", "general"), ["Handled the simulated event."]))

    @staticmethod
    def calculate_score(steps_result: list[dict[str, Any]], scenario: dict[str, Any]) -> int:
        if not steps_result:
            return 0
        accuracy_sum = sum(step["accuracy"] for step in steps_result)
        average_accuracy = accuracy_sum / len(steps_result)
        success_count = sum(1 for step in steps_result if step["success"])
        success_rate = (success_count / max(1, len(scenario.get("steps", [])))) * 100
        return int((average_accuracy * 0.6) + (success_rate * 0.4))

    @staticmethod
    def generate_feedback(steps_result: list[dict[str, Any]]) -> str:
        if not steps_result:
            return "No simulation steps were executed."
        successful = sum(1 for step in steps_result if step["success"])
        total = len(steps_result)
        ratio = successful / total
        if ratio == 1:
            return "Excellent performance. The bot handled every simulated event successfully."
        if ratio >= 0.8:
            return "Strong performance. Most simulated events were handled correctly."
        if ratio >= 0.6:
            return "Acceptable performance. Response quality needs improvement under pressure."
        return "Weak performance. The bot needs targeted remedial training."
