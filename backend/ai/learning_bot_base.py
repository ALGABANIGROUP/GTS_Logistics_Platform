from __future__ import annotations

import traceback
from datetime import datetime
from typing import Any, Dict, List, Optional

from backend.ai.ai_bots import BaseAIBot
from backend.ai.data_collection_service import data_collection_service
from backend.ai.learning_engine import bot_learning_engine


class ReusableLearningBot(BaseAIBot):
    description = "Reusable learning bot"
    learning_frequency = "daily"
    learning_intensity = "medium"

    def __init__(self) -> None:
        super().__init__()
        self.sessions: Dict[str, Dict[str, Any]] = {}

    async def process_action(
        self,
        action: str,
        session_id: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        started_at = datetime.utcnow()
        resolved_session_id = session_id or self._generate_session_id(action)
        session = self.sessions.setdefault(
            resolved_session_id,
            {
                "id": resolved_session_id,
                "action": action,
                "created_at": datetime.utcnow().isoformat(),
                "history": [],
            },
        )

        try:
            result = await self._execute_action(action, kwargs)
            session["history"].append(
                {
                    "type": "success",
                    "action": action,
                    "payload": kwargs,
                    "result": result,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )
            response_time_ms = (datetime.utcnow() - started_at).total_seconds() * 1000
            self.record_execution_success(
                response_time_ms=response_time_ms,
                accuracy=float(result.get("accuracy", 0.95) or 0.95),
            )
            return {
                **result,
                "session_id": resolved_session_id,
                "processed_at": datetime.utcnow().isoformat(),
            }
        except Exception as exc:
            session["history"].append(
                {
                    "type": "error",
                    "action": action,
                    "payload": kwargs,
                    "error": str(exc),
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )
            self.record_execution_error(
                error_type=type(exc).__name__,
                error_message=str(exc),
                severity=0.9,
                traceback=traceback.format_exc(),
            )
            raise

    def submit_feedback(
        self,
        session_id: str,
        rating: int,
        comment: Optional[str] = None,
        user_id: Optional[str] = None,
        feedback_type: str = "general",
    ) -> Dict[str, Any]:
        self.collect_feedback(
            rating=rating,
            session_id=session_id,
            comment=comment,
            user_id=user_id,
            feedback_type=feedback_type,
        )
        return {"status": "success", "rating": rating, "session_id": session_id}

    def get_stats(self) -> Dict[str, Any]:
        profile = bot_learning_engine.get_bot_profile(self.name) or {}
        feedback = data_collection_service.get_bot_feedback(self.name, limit=100)
        performance = data_collection_service.get_bot_performance_history(self.name, limit=100)
        errors = data_collection_service.get_bot_error_logs(self.name, limit=20)
        return {
            "bot_id": self.name,
            "sessions": len(self.sessions),
            "average_rating": self._calc_average(feedback, "rating"),
            "average_response_time_ms": self._calc_average(performance, "response_time"),
            "learning_profile": profile,
            "recent_feedback": feedback[:10],
            "recent_errors": errors[:10],
        }

    def _calc_average(self, items: List[Dict[str, Any]], key: str) -> float:
        values = [item.get(key) for item in items if item.get(key) is not None]
        if not values:
            return 0.0
        return round(sum(values) / len(values), 2)

    def _generate_session_id(self, action: str) -> str:
        return f"{self.name}_{action}_{int(datetime.utcnow().timestamp())}"

    async def _execute_action(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError

