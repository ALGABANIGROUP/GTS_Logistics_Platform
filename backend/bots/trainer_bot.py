"""
Trainer Bot runtime wrapper.
Exposes the existing training center through the shared AI bot runtime.
"""

from __future__ import annotations

from typing import Any, Dict, Optional


class TrainerBotRuntime:
    """Shared-runtime wrapper around the training center domain."""

    def __init__(self) -> None:
        self.name = "trainer_bot"
        self.display_name = "AI Trainer Bot"
        self.description = "Training readiness, assessments, plans, simulations, and certification workflows"
        self.version = "2.0.0"
        self.mode = "training_center"
        self.is_active = True

    @property
    def trainer(self):
        from backend.routes.training_center import _trainer

        return _trainer

    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        context = payload.get("context") or {}
        action = (
            payload.get("action")
            or context.get("action")
            or payload.get("meta", {}).get("action")
            or "status"
        )

        if action == "status":
            return await self.status()
        if action == "config":
            return await self.config()
        if action == "dashboard":
            return await self.dashboard()
        if action == "list_trainable_bots":
            return {"ok": True, "bots": self.trainer.list_trainable_bots()}
        if action == "register_bot":
            return await self.register_bot(
                str(context.get("bot_key") or payload.get("bot_key") or ""),
                str(context.get("level") or payload.get("level") or "beginner"),
                str(context.get("version") or payload.get("version") or "1.0"),
            )
        if action == "assess_bot":
            return await self.assess_bot(str(context.get("bot_key") or payload.get("bot_key") or ""))
        if action == "create_training_plan":
            return await self.create_training_plan(
                str(context.get("bot_key") or payload.get("bot_key") or ""),
                context.get("goal") or payload.get("goal"),
            )
        if action == "start_training_session":
            return await self.start_training_session(str(context.get("plan_id") or payload.get("plan_id") or ""))
        if action == "list_reports":
            bot_key = context.get("bot_key") or payload.get("bot_key")
            return {
                "ok": True,
                "reports": [
                    report
                    for report in self.trainer.list_reports()
                    if not bot_key or report.get("bot_key") == self.trainer.bot_connector.normalize_bot_key(str(bot_key))
                ],
            }
        return await self.status()

    async def process_message(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        context = context or {}
        if context.get("action"):
            return await self.run({"context": context})

        text = (message or "").lower()
        if "report" in text:
            return {"ok": True, "reports": self.trainer.list_reports()[:10]}
        if "plan" in text:
            return {"ok": True, "plans": [plan.to_dict() for plan in self.trainer.training_plans.values()]}
        if "bot" in text:
            return {"ok": True, "bots": self.trainer.list_trainable_bots()}
        return await self.dashboard()

    async def status(self) -> Dict[str, Any]:
        stats = self.trainer.get_stats()
        return {
            "ok": True,
            "bot": self.name,
            "display_name": self.display_name,
            "version": self.version,
            "mode": self.mode,
            "is_active": self.is_active,
            "registered_bots": stats.get("registered_bots", 0),
            "sessions_run": stats.get("sessions_run", 0),
            "reports_generated": stats.get("reports_generated", 0),
            "average_score": stats.get("average_score", 0),
            "active_sessions": stats.get("active_sessions", 0),
            "message": "Training center is online.",
        }

    async def config(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "version": self.version,
            "mode": self.mode,
            "capabilities": [
                "dashboard",
                "list_trainable_bots",
                "register_bot",
                "assess_bot",
                "create_training_plan",
                "start_training_session",
                "list_reports",
            ],
            "levels": ["beginner", "intermediate", "advanced", "expert", "master"],
            "specializations": sorted(
                {
                    bot.get("specialization")
                    for bot in self.trainer.list_trainable_bots()
                    if bot.get("specialization")
                }
            ),
        }

    async def dashboard(self) -> Dict[str, Any]:
        stats = self.trainer.get_stats()
        reports = self.trainer.list_reports()[:8]
        bots = self.trainer.list_trainable_bots()
        return {
            "ok": True,
            "trainer": await self.status(),
            "stats": stats,
            "trainable_bots": bots,
            "registered_profiles": [profile.to_dict() for profile in self.trainer.bots_in_training.values()],
            "plans": [plan.to_dict() for plan in self.trainer.training_plans.values()],
            "recent_reports": reports,
            "courses_count": len(self.trainer.course_manager.list_courses()),
        }

    async def register_bot(self, bot_key: str, level: str, version: str) -> Dict[str, Any]:
        profile = await self.trainer.register_bot(bot_key, level=level, version=version)
        return {"ok": True, "profile": profile}

    async def assess_bot(self, bot_key: str) -> Dict[str, Any]:
        assessment = await self.trainer.assess_bot_capabilities(bot_key)
        return {"ok": True, "assessment": assessment}

    async def create_training_plan(self, bot_key: str, goal: Optional[str]) -> Dict[str, Any]:
        plan = await self.trainer.create_training_plan(bot_key, goal)
        return {"ok": True, "plan": plan}

    async def start_training_session(self, plan_id: str) -> Dict[str, Any]:
        result = await self.trainer.start_training_session(plan_id)
        return {"ok": True, **result}

