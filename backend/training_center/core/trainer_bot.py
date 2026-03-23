from __future__ import annotations

import asyncio
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Any

from backend.training_center.core.knowledge_base import KnowledgeBase
from backend.training_center.core.learning_paths import LearningPathManager
from backend.training_center.core.models import (
    BotProfile,
    CertificateRecord,
    TrainingLevel,
    TrainingPlan,
    TrainingReport,
    TrainingSession,
)
from backend.training_center.integration.bot_connector import BotConnector
from backend.training_center.integration.real_time_monitor import RealTimeMonitor
from backend.training_center.reports.report_generator import ReportGenerator
from backend.training_center.simulation_engine import SimulationEngine
from backend.training_center.training.assessment_system import AssessmentSystem
from backend.training_center.training.course_manager import CourseManager
from backend.training_center.training.scenario_generator import ScenarioGenerator


class TrainerBot:
    """Advanced trainer bot for structured bot readiness workflows."""

    def __init__(
        self,
        *,
        name: str = "AI Trainer Bot",
        data_dir: Path | None = None,
        reports_dir: Path | None = None,
        seed: int | None = None,
    ) -> None:
        package_dir = Path(__file__).resolve().parent.parent
        self.name = name
        self.data_dir = data_dir or (package_dir / "data")
        self.reports_dir = reports_dir or (package_dir / "reports")
        self.knowledge_base = KnowledgeBase()
        self.learning_paths = LearningPathManager(self.knowledge_base)
        self.course_manager = CourseManager(data_dir=self.data_dir)
        self.scenario_generator = ScenarioGenerator(data_dir=self.data_dir, seed=seed)
        self.assessment_system = AssessmentSystem(seed=seed)
        self.simulation_engine = SimulationEngine(seed=seed)
        self.bot_connector = BotConnector()
        self.report_generator = ReportGenerator(reports_dir=self.reports_dir)
        self.real_time_monitor = RealTimeMonitor()
        self.bots_in_training: dict[str, BotProfile] = {}
        self.training_plans: dict[str, TrainingPlan] = {}
        self.training_sessions: dict[str, TrainingSession] = {}

    def list_trainable_bots(self) -> list[dict[str, Any]]:
        return self.bot_connector.list_trainable_bots()

    async def register_bot(self, bot_key: str, *, level: str | None = None, version: str | None = None) -> dict[str, Any]:
        bot = self.bot_connector.get_bot(bot_key)
        if not bot:
            raise ValueError(f"Unknown bot key: {bot_key}")
        current_level = self._parse_level(level or TrainingLevel.BEGINNER.value)
        profile = BotProfile(
            bot_key=bot["canonical_key"],
            bot_name=bot["name"],
            specialization=bot["specialization"],
            version=version or "1.0",
            current_level=current_level,
            description=bot.get("description", ""),
            source_category=bot.get("category", ""),
            skills=self.knowledge_base.default_skills(bot["specialization"]),
        )
        profile.updated_at = datetime.utcnow().isoformat()
        self.bots_in_training[profile.bot_key] = profile
        return profile.to_dict()

    async def assess_bot_capabilities(self, bot_key: str) -> dict[str, Any]:
        profile = self._get_registered_bot(bot_key)
        baseline = await self.assessment_system.run_basic_assessment(profile)
        strengths, weak_points = self._analyze_skills(baseline["skills"])
        profile.skills = baseline["skills"]
        profile.strengths = strengths
        profile.weak_points = weak_points
        profile.updated_at = datetime.utcnow().isoformat()
        return {
            "bot_key": profile.bot_key,
            "bot_name": profile.bot_name,
            "overall_score": baseline["overall_score"],
            "strengths": strengths,
            "weak_points": weak_points,
            "recommended_level": self._recommend_level(baseline["overall_score"]).value,
            "skills_breakdown": baseline["skills"],
        }

    async def create_training_plan(self, bot_key: str, goal: str | None = None) -> dict[str, Any]:
        profile = self._get_registered_bot(bot_key)
        if not profile.skills:
            await self.assess_bot_capabilities(bot_key)
        learning_path = self.learning_paths.get_path(
            specialization=profile.specialization,
            current_level=profile.current_level,
            goal=goal or self.knowledge_base.infer_goal(profile.specialization, profile.weak_points),
        )
        courses = await self.course_manager.select_courses(
            learning_path=learning_path,
            weak_points=profile.weak_points,
            target_level=str(learning_path["target_level"]),
        )
        plan_id = self._make_id(f"{profile.bot_key}_plan")
        milestones = [
            {
                "milestone": index,
                "title": self.knowledge_base.milestone_title(course["name"]),
                "expected_score": max(course["passing_score"], 70 + min(index * 4, 20)),
            }
            for index, course in enumerate(courses, start=1)
        ]
        plan = TrainingPlan(
            plan_id=plan_id,
            bot_key=profile.bot_key,
            bot_name=profile.bot_name,
            specialization=profile.specialization.value,
            current_level=profile.current_level.value,
            target_level=str(learning_path["target_level"]),
            goal=str(learning_path["goal"]),
            created_at=datetime.utcnow().isoformat(),
            duration_days=max(1, len(courses)),
            total_hours=sum(int(course["duration_hours"]) for course in courses),
            courses=courses,
            milestones=milestones,
            target_skills=list(dict.fromkeys(profile.weak_points + list(learning_path["focus_skills"]))),
        )
        self.training_plans[plan_id] = plan
        return plan.to_dict()

    async def start_training_session(self, plan_id: str) -> dict[str, Any]:
        plan = self.training_plans.get(plan_id)
        if not plan:
            raise ValueError(f"Unknown plan id: {plan_id}")
        profile = self._get_registered_bot(plan.bot_key)
        session_id = self._make_id(f"{profile.bot_key}_session")
        session = TrainingSession(
            session_id=session_id,
            plan_id=plan.plan_id,
            bot_key=profile.bot_key,
            bot_name=profile.bot_name,
            status="running",
            started_at=datetime.utcnow().isoformat(),
        )
        self.training_sessions[session_id] = session
        self.real_time_monitor.track(session_id, session.to_dict())

        for course in plan.courses:
            session.progress.append(f"Started course {course['id']}: {course['name']}")
            await asyncio.sleep(0)
            theory_score = round(
                sum(profile.skills.get(skill, 55.0) for skill in course["skills_improved"]) / max(1, len(course["skills_improved"])),
                2,
            )
            scenarios = await self.scenario_generator.generate_scenarios(
                specialization=plan.specialization,
                level=profile.current_level,
                course_topics=course["topics"],
            )
            practical_runs = []
            for scenario in scenarios:
                result = await self.simulation_engine.run_scenario(profile.bot_name, scenario)
                practical_runs.append(result)
            practical_score = round(sum(item["score"] for item in practical_runs) / max(1, len(practical_runs)), 2)
            test_result = await self.assessment_system.run_course_test(profile, course)
            final_course_score = round((theory_score * 0.3) + (practical_score * 0.4) + (test_result["score"] * 0.3), 2)
            course_result = {
                "course_id": course["id"],
                "course_name": course["name"],
                "theory_score": theory_score,
                "practical_score": practical_score,
                "test_score": test_result["score"],
                "final_score": final_course_score,
                "simulation_count": len(practical_runs),
            }
            session.completed_courses.append(course_result)
            session.progress.append(f"Completed course {course['id']} with score {final_course_score}")
            self._apply_course_improvements(profile, course, final_course_score)
            self.real_time_monitor.track(session_id, session.to_dict())

        written_score = await self.assessment_system.written_test(profile, plan.specialization)
        final_practical_score = await self.assessment_system.final_practical_test(profile, plan.specialization)
        average_course_score = round(sum(item["final_score"] for item in session.completed_courses) / max(1, len(session.completed_courses)), 2)
        final_score = round((average_course_score * 0.45) + (written_score * 0.2) + (final_practical_score * 0.35), 2)
        improvements = self._calculate_improvements(profile, plan.target_skills)
        certificate = None
        if final_score >= 70:
            certificate_record = CertificateRecord(
                certificate_id=self._make_certificate_id(profile.bot_key),
                bot_key=profile.bot_key,
                bot_name=profile.bot_name,
                level_achieved=self._recommend_level(final_score).value,
                final_score=final_score,
                issued_at=datetime.utcnow().isoformat(),
                courses_completed=[item["course_name"] for item in session.completed_courses],
            )
            certificate = certificate_record.to_dict()

        report = TrainingReport(
            session_id=session.session_id,
            plan_id=plan.plan_id,
            bot_key=profile.bot_key,
            bot_name=profile.bot_name,
            specialization=plan.specialization,
            trainer_name=self.name,
            started_at=session.started_at,
            completed_at=datetime.utcnow().isoformat(),
            final_score=final_score,
            grade=self.assessment_system.get_grade(final_score),
            recommendations=self._recommendations(final_score),
            completed_courses=session.completed_courses,
            improvements=improvements,
            certificate=certificate,
        )
        self.report_generator.write_report(report.to_dict())
        session.status = "completed"
        session.completed_at = report.completed_at
        session.final_score = final_score
        session.improvements = improvements
        session.certificate = certificate
        profile.current_level = self._recommend_level(final_score)
        profile.training_history.append(session.session_id)
        profile.updated_at = datetime.utcnow().isoformat()
        self.real_time_monitor.track(session_id, session.to_dict())
        return {
            "session": session.to_dict(),
            "report": report.to_dict(),
        }

    def get_session(self, session_id: str) -> dict[str, Any] | None:
        snapshot = self.real_time_monitor.get(session_id)
        if snapshot:
            return snapshot
        session = self.training_sessions.get(session_id)
        return session.to_dict() if session else None

    def list_reports(self) -> list[dict[str, Any]]:
        return self.report_generator.list_reports()

    def get_report(self, session_id: str) -> dict[str, Any] | None:
        return self.report_generator.get_report(session_id)

    def get_stats(self) -> dict[str, Any]:
        reports = self.list_reports()
        average_score = round(sum(item["final_score"] for item in reports) / len(reports), 2) if reports else 0.0
        return {
            "registered_bots": len(self.bots_in_training),
            "plans_created": len(self.training_plans),
            "sessions_run": len(self.training_sessions),
            "reports_generated": len(reports),
            "average_score": average_score,
            "active_sessions": sum(1 for item in self.training_sessions.values() if item.status == "running"),
            "last_report_session_id": reports[0]["session_id"] if reports else None,
        }

    async def list_available_courses(self) -> list[dict[str, Any]]:
        return self.course_manager.list_courses()

    async def train_bot(self, bot_name: str, course_id: str) -> dict[str, Any]:
        profile = await self.register_bot("trainer_bot" if "trainer" in bot_name.lower() else "security_manager_bot")
        registered_key = profile["bot_key"]
        self.bots_in_training[registered_key].bot_name = bot_name
        await self.assess_bot_capabilities(registered_key)
        plan = await self.create_training_plan(registered_key)
        plan_obj = self.training_plans[plan["plan_id"]]
        selected_course = next((course for course in plan_obj.courses if course["id"] == course_id), None)
        if selected_course is None:
            selected_course = next((course for course in self.course_manager.list_courses() if course["id"] == course_id), None)
        if selected_course is None:
            selected_course = self.course_manager.list_courses()[0]
        plan_obj.courses = [selected_course]
        plan_obj.milestones = [
            {
                "milestone": 1,
                "title": self.knowledge_base.milestone_title(selected_course["name"]),
                "expected_score": selected_course["passing_score"],
            }
        ]
        result = await self.start_training_session(plan_obj.plan_id)
        report = result["report"]
        report["course_id"] = selected_course["id"]
        report["course_name"] = selected_course["name"]
        return report

    async def get_training_stats(self) -> dict[str, Any]:
        reports = self.list_reports()
        return {
            "total_trained_bots": len({item["bot_key"] for item in reports}),
            "average_score": self.get_stats()["average_score"],
            "courses_taught": sorted({item["completed_courses"][0]["course_id"] for item in reports if item["completed_courses"]}),
            "last_training": reports[-1] if reports else None,
        }

    def _get_registered_bot(self, bot_key: str) -> BotProfile:
        canonical = self.bot_connector.normalize_bot_key(bot_key)
        profile = self.bots_in_training.get(canonical)
        if not profile:
            raise ValueError(f"Bot is not registered for training: {bot_key}")
        return profile

    def _parse_level(self, value: str) -> TrainingLevel:
        normalized = str(value or "").strip().lower()
        try:
            return TrainingLevel(normalized)
        except ValueError:
            return TrainingLevel.BEGINNER

    def _analyze_skills(self, skills: dict[str, float]) -> tuple[list[str], list[str]]:
        ordered = sorted(skills.items(), key=lambda item: item[1], reverse=True)
        return [item[0] for item in ordered[:2]], [item[0] for item in ordered[-2:]]

    def _recommend_level(self, score: float) -> TrainingLevel:
        if score >= 95:
            return TrainingLevel.MASTER
        if score >= 88:
            return TrainingLevel.EXPERT
        if score >= 76:
            return TrainingLevel.ADVANCED
        if score >= 62:
            return TrainingLevel.INTERMEDIATE
        return TrainingLevel.BEGINNER

    def _apply_course_improvements(self, profile: BotProfile, course: dict[str, Any], score: float) -> None:
        for skill in course["skills_improved"]:
            current = profile.skills.get(skill, 55.0)
            updated = min(100.0, current + max(1.0, (score - current) * 0.25))
            profile.skills[skill] = round(updated, 2)

    def _calculate_improvements(self, profile: BotProfile, target_skills: list[str]) -> dict[str, Any]:
        return {skill: round(profile.skills.get(skill, 55.0) - 55.0, 2) for skill in target_skills}

    def _recommendations(self, score: float) -> list[str]:
        if score < 60:
            return [
                "Repeat the full path with additional mentor-led simulations.",
                "Focus on recognition accuracy before speed drills.",
            ]
        if score < 70:
            return [
                "Repeat high-risk scenarios with tighter response deadlines.",
                "Review weak skills before advancing to the next level.",
            ]
        if score < 85:
            return [
                "Schedule an advanced follow-up path in the same specialization.",
                "Run shadow simulations before wider rollout.",
            ]
        return [
            "Ready for controlled production readiness checks.",
            "Eligible for cross-bot mentoring drills.",
        ]

    @staticmethod
    def _make_id(prefix: str) -> str:
        return hashlib.md5(f"{prefix}_{datetime.utcnow().timestamp()}".encode("utf-8")).hexdigest()[:12]

    @staticmethod
    def _make_certificate_id(bot_key: str) -> str:
        return hashlib.sha1(f"{bot_key}_{datetime.utcnow().timestamp()}".encode("utf-8")).hexdigest()[:12].upper()
