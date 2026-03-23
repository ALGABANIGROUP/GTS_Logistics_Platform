"""Monitoring utilities for email bot performance."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict


class EmailBotMonitor:
	def __init__(self) -> None:
		self.metrics: Dict[str, Any] = {
			"total_processed": 0,
			"successful": 0,
			"failed": 0,
			"auto_resolved": 0,
			"human_escalated": 0,
			"avg_processing_time": 0,
			"bot_performance": {},
		}

	def track_processing(self, bot_name: str, email_id: str | None, result: Dict[str, Any]) -> None:
		self.metrics["total_processed"] += 1
		if result.get("success"):
			self.metrics["successful"] += 1
			if result.get("auto_response_sent") or result.get("auto_reply_sent"):
				self.metrics["auto_resolved"] += 1
		else:
			self.metrics["failed"] += 1
			if result.get("needs_human_review"):
				self.metrics["human_escalated"] += 1

		if bot_name not in self.metrics["bot_performance"]:
			self.metrics["bot_performance"][bot_name] = {
				"processed": 0,
				"success_rate": 0.0,
				"auto_resolution_rate": 0.0,
			}
		bot_stats = self.metrics["bot_performance"][bot_name]
		bot_stats["processed"] += 1

	def generate_report(self, period: str = "daily") -> Dict[str, Any]:
		return {
			"period": period,
			"timestamp": datetime.utcnow(),
			"summary": {
				"total_emails": self.metrics["total_processed"],
				"success_rate": self._calculate_success_rate(),
				"auto_resolution_rate": self._calculate_auto_resolution_rate(),
				"avg_response_time": self.metrics["avg_processing_time"],
			},
			"bot_performance": self.metrics["bot_performance"],
			"top_categories": [],
			"issues": [],
		}

	def _calculate_success_rate(self) -> float:
		if self.metrics["total_processed"] == 0:
			return 0.0
		return (self.metrics["successful"] / self.metrics["total_processed"]) * 100

	def _calculate_auto_resolution_rate(self) -> float:
		if self.metrics["total_processed"] == 0:
			return 0.0
		return (self.metrics["auto_resolved"] / self.metrics["total_processed"]) * 100
# moved from backend/email/monitoring.py
