from __future__ import annotations

import asyncio
import gc
import os
import time
from pathlib import Path
from collections import Counter
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from httpx import ASGITransport, AsyncClient
from sqlalchemy import text

from backend.ai.data_collection_service import data_collection_service
from backend.ai.learning_bot_base import ReusableLearningBot
from backend.ai.learning_engine import bot_learning_engine
from backend.database.config import get_sessionmaker
from backend.services.db_maintenance import ensure_maintenance_indexes
from backend.services.platform_settings_store import update_platform_settings

try:
    import psutil  # type: ignore
except Exception:  # pragma: no cover
    psutil = None


class MaintenanceDevEnhancedBot(ReusableLearningBot):
    name = "maintenance_dev"
    description = "Advanced system maintenance with diagnostics and repair"
    learning_frequency = "hourly"
    learning_intensity = "high"

    def __init__(self) -> None:
        super().__init__()
        self.system_checks: Dict[str, Any] = {}
        self.health_history: List[Dict[str, Any]] = []
        self.known_issues: List[Dict[str, Any]] = []
        self.fixed_issues: List[Dict[str, Any]] = []
        self.last_full_scan: Optional[str] = None
        self.last_repair_summary: Optional[Dict[str, Any]] = None
        self.auto_repair_enabled = True
        self.repair_attempts = 0
        self.successful_repairs = 0
        self.repair_actions_attempted = 0
        self.repair_actions_succeeded = 0

    async def run_full_system_diagnostic(self, app: Any | None = None) -> Dict[str, Any]:
        start_time = time.time()
        results: Dict[str, Any] = {}
        issues: List[Dict[str, Any]] = []

        bots_status = await self._check_all_bots()
        results["bots"] = bots_status
        issues.extend(bots_status.get("issues", []))

        db_status = await self._check_database()
        results["database"] = db_status
        issues.extend(db_status.get("issues", []))

        api_status = await self._check_api_endpoints(app=app)
        results["api"] = api_status
        issues.extend(api_status.get("issues", []))

        security_status = await self._check_security()
        results["security"] = security_status
        issues.extend(security_status.get("issues", []))

        performance_status = await self._check_performance()
        results["performance"] = performance_status
        issues.extend(performance_status.get("issues", []))

        errors_status = await self._analyze_error_patterns()
        results["error_patterns"] = errors_status
        issues.extend(errors_status.get("issues", []))

        files_status = await self._check_files()
        results["files"] = files_status
        issues.extend(files_status.get("issues", []))

        settings_status = await self._check_platform_settings()
        results["settings"] = settings_status
        issues.extend(settings_status.get("issues", []))

        scan_time = time.time() - start_time
        self.last_full_scan = datetime.utcnow().isoformat()

        result = {
            "status": "healthy" if not issues else "issues_found",
            "scan_time_seconds": round(scan_time, 2),
            "scanned_at": self.last_full_scan,
            "components_checked": len(results),
            "issues_found": len(issues),
            "issues": issues[:20],
            "details": results,
            "recommendations": await self._generate_recommendations(issues, results),
        }

        self.system_checks[self.last_full_scan] = result
        self.health_history.append(
            {
                "timestamp": self.last_full_scan,
                "status": result["status"],
                "issues_found": result["issues_found"],
                "components_checked": result["components_checked"],
            }
        )
        self.health_history = self.health_history[-100:]
        self.known_issues.extend(issues[:20])
        self.known_issues = self.known_issues[-200:]

        self.record_execution_success(
            response_time_ms=int(scan_time * 1000),
            accuracy=0.95 if not issues else 0.85,
        )
        return result

    async def run_diagnostic(self, request: Dict[str, Any], app: Any | None = None) -> Dict[str, Any]:
        scan_type = request.get("type", "full")
        if scan_type == "full":
            return await self.run_full_system_diagnostic(app=app)
        if scan_type == "bots":
            return await self._check_all_bots()
        if scan_type == "database":
            return await self._check_database()
        if scan_type == "api":
            return await self._check_api_endpoints(app=app)
        if scan_type == "security":
            return await self._check_security()
        if scan_type == "performance":
            return await self._check_performance()
        if scan_type == "errors":
            return await self._analyze_error_patterns()
        return {"error": f"Unknown scan type: {scan_type}"}

    async def auto_repair(self, issue_ids: Optional[List[str]] = None, app: Any | None = None) -> Dict[str, Any]:
        self.repair_attempts += 1
        started_at = time.time()
        actions_taken: Dict[str, str] = {}

        diagnostic = await self.run_full_system_diagnostic(app=app)
        issues = diagnostic.get("issues", [])
        if issue_ids:
            issue_ids_set = set(issue_ids)
            issues = [
                issue
                for issue in issues
                if issue.get("component") in issue_ids_set or issue.get("repair_action") in issue_ids_set
            ]

        for bot_id, profile in bot_learning_engine.learning_profiles.items():
            if not profile.enabled:
                profile.enabled = True
                profile.next_learning_update = datetime.utcnow().isoformat()
                actions_taken[f"enable_{bot_id}"] = "Bot re-enabled"

        sample_cutoff = datetime.utcnow() - timedelta(days=30)
        removed_samples = 0
        for bot_id, samples in list(bot_learning_engine.data_samples.items()):
            kept_samples = []
            for sample in samples:
                sample_ts = getattr(sample, "timestamp", None)
                try:
                    if sample_ts and datetime.fromisoformat(sample_ts) >= sample_cutoff:
                        kept_samples.append(sample)
                    else:
                        removed_samples += 1
                except Exception:
                    kept_samples.append(sample)
            bot_learning_engine.data_samples[bot_id] = kept_samples
        if removed_samples:
            actions_taken["cleanup_samples"] = f"Removed {removed_samples} old learning samples"

        known_before = len(self.known_issues)
        self.known_issues = self.known_issues[-200:]
        self.health_history = self.health_history[-100:]
        self.system_checks = dict(list(self.system_checks.items())[-50:])
        if len(self.known_issues) != known_before:
            actions_taken["rotate_issue_history"] = "Trimmed known issue history"
        actions_taken["rotate_health_history"] = "Trimmed health history"

        directories = ["uploads", "logs", "temp"]
        for directory_name in directories:
            path = Path(directory_name)
            if not path.exists():
                path.mkdir(parents=True, exist_ok=True)
                actions_taken[f"create_{directory_name}"] = f"Created {directory_name} directory"

        cleaned_files = 0
        cleaned_bytes = 0
        cutoff_time = time.time() - (7 * 24 * 3600)
        for directory_name in ("temp", "logs"):
            path = Path(directory_name)
            if not path.exists():
                continue
            for file_path in path.glob("*"):
                if not file_path.is_file():
                    continue
                try:
                    if file_path.stat().st_mtime < cutoff_time:
                        cleaned_bytes += file_path.stat().st_size
                        file_path.unlink()
                        cleaned_files += 1
                except Exception:
                    continue
        if cleaned_files:
            actions_taken["cleanup_files"] = f"Removed {cleaned_files} old files ({round(cleaned_bytes / (1024 * 1024), 2)} MB)"

        collected = gc.collect()
        actions_taken["clear_cache"] = f"Garbage collected {collected} objects"

        maker = get_sessionmaker()
        try:
            async with maker() as session:
                db_issue = next((issue for issue in issues if issue.get("component") == "database"), None)
                if db_issue:
                    optimize_result = await ensure_maintenance_indexes()
                    actions_taken["optimize_database"] = f"Executed {len(optimize_result.get('executed', []))} database maintenance commands"
        except Exception as exc:
            actions_taken["optimize_database"] = f"Skipped: {exc}"

        try:
            async with maker() as session:
                settings_check = await self._check_platform_settings()
                missing_settings = next(
                    (issue for issue in settings_check.get("issues", []) if issue.get("repair_action") == "create_default_settings"),
                    None,
                )
                if missing_settings:
                    await update_platform_settings(
                        session,
                        {
                            "general": {
                                "platformName": "GTS Logistics Platform",
                                "timeZone": "UTC",
                                "currency": "USD",
                                "dateFormat": "YYYY-MM-DD",
                            },
                            "branding": {
                                "platformName": "GTS Logistics Platform",
                                "logoUrl": "",
                                "faviconUrl": "",
                            },
                            "theme": {
                                "primaryColor": "#2E71EE",
                                "background": "#0F1C2F",
                            },
                        },
                        updated_by="maintenance_dev",
                    )
                    actions_taken["create_settings"] = "Created default platform settings"
        except Exception as exc:
            actions_taken["create_settings"] = f"Skipped: {exc}"

        try:
            for bot_id, profile in bot_learning_engine.learning_profiles.items():
                if profile.error_count > 20:
                    profile.error_count = 0
                    actions_taken[f"reset_errors_{bot_id}"] = "Reset profile error counter"
        except Exception:
            pass

        attempted_count = len(actions_taken)
        repaired_count = sum(1 for value in actions_taken.values() if not value.startswith("Skipped:"))
        self.successful_repairs += repaired_count
        self.repair_actions_attempted += attempted_count
        self.repair_actions_succeeded += repaired_count
        for key, action in actions_taken.items():
            self.fixed_issues.append(
                {
                    "timestamp": datetime.utcnow().isoformat(),
                    "issue_id": key,
                    "action": action,
                }
            )
        self.fixed_issues = self.fixed_issues[-100:]
        result = {
            "status": "repair_completed" if actions_taken else "no_action",
            "actions_taken": actions_taken,
            "issues_found": len(issues),
            "issues_repaired": repaired_count,
            "actions_attempted": attempted_count,
            "repair_time_seconds": round(time.time() - started_at, 2),
            "success_rate": round((self.repair_actions_succeeded / max(1, self.repair_actions_attempted)) * 100, 2),
            "repair_attempts": self.repair_attempts,
            "message": f"Attempted to fix {repaired_count} issues",
        }
        self.last_repair_summary = result
        return result

    async def _check_all_bots(self) -> Dict[str, Any]:
        bots = bot_learning_engine.learning_profiles
        issues: List[Dict[str, Any]] = []
        details: Dict[str, Any] = {}

        for bot_id, profile in bots.items():
            sample_count = len(bot_learning_engine.data_samples.get(bot_id, []))
            bot_status = {
                "registered": True,
                "enabled": profile.enabled,
                "last_learning": profile.last_learning_update,
                "next_learning": profile.next_learning_update,
                "samples": sample_count,
                "adaptations": profile.adaptations_applied,
                "accuracy": profile.accuracy_score,
            }
            if not profile.enabled:
                issues.append(self._issue("low", f"bot_{bot_id}", f"Bot {bot_id} is disabled"))
            elif profile.accuracy_score and profile.accuracy_score < 0.7:
                issues.append(self._issue("medium", f"bot_{bot_id}", f"Bot {bot_id} has low accuracy ({profile.accuracy_score:.2f})"))
            elif profile.error_count > 10:
                issues.append(self._issue("high", f"bot_{bot_id}", f"Bot {bot_id} has {profile.error_count} errors"))
            details[bot_id] = bot_status

        return {
            "healthy": not issues,
            "total_bots": len(bots),
            "enabled_bots": sum(1 for p in bots.values() if p.enabled),
            "disabled_bots": sum(1 for p in bots.values() if not p.enabled),
            "issues": issues,
            "details": details,
        }

    async def _check_database(self) -> Dict[str, Any]:
        issues: List[Dict[str, Any]] = []
        details: Dict[str, Any] = {}
        maker = get_sessionmaker()
        try:
            async with maker() as session:
                start = time.time()
                await session.execute(text("SELECT 1"))
                latency = (time.time() - start) * 1000
                details["connection_latency_ms"] = round(latency, 2)

                tables = ["users", "shipments", "invoices", "email_messages"]
                table_sizes: Dict[str, int] = {}
                for table_name in tables:
                    try:
                        result = await session.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                        table_sizes[table_name] = int(result.scalar() or 0)
                    except Exception:
                        table_sizes[table_name] = -1
                details["table_sizes"] = table_sizes

                if latency > 100:
                    issues.append(self._issue("medium", "database", f"High database latency: {latency:.2f}ms"))
                for table_name, size in table_sizes.items():
                    if size > 100000:
                        issues.append(self._issue("low", f"database_{table_name}", f"Table {table_name} is very large ({size} rows)"))
        except Exception as exc:
            issues.append(self._issue("critical", "database", f"Database connection failed: {exc}"))

        return {"healthy": not issues, "issues": issues, "details": details}

    async def _check_api_endpoints(self, app: Any | None = None) -> Dict[str, Any]:
        endpoints = [
            ("/health", "GET"),
            ("/api/v1/weather", "GET"),
            ("/api/v1/customer-service/stats", "GET"),
            ("/api/v1/reports/stats", "GET"),
            ("/api/v1/maintenance-dev/stats", "GET"),
        ]
        issues: List[Dict[str, Any]] = []
        details: Dict[str, Any] = {}

        if app is None:
            return {
                "healthy": False,
                "total_endpoints": len(endpoints),
                "healthy_endpoints": 0,
                "issues": [self._issue("medium", "api", "Application instance not available for API diagnostic")],
                "details": {},
            }

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            for path, method in endpoints:
                try:
                    start = time.time()
                    response = await client.request(method, path)
                    latency = (time.time() - start) * 1000
                    healthy = response.status_code < 500
                    details[path] = {
                        "status_code": response.status_code,
                        "latency_ms": round(latency, 2),
                        "healthy": healthy,
                    }
                    if response.status_code >= 500:
                        issues.append(self._issue("high", f"api_{path}", f"API {path} returned {response.status_code}"))
                    elif latency > 500:
                        issues.append(self._issue("medium", f"api_{path}", f"API {path} slow ({latency:.2f}ms)"))
                except Exception as exc:
                    details[path] = {"healthy": False, "error": str(exc)}
                    issues.append(self._issue("critical", f"api_{path}", f"API {path} failed: {exc}"))

        return {
            "healthy": not any(issue["severity"] in {"critical", "high"} for issue in issues),
            "total_endpoints": len(endpoints),
            "healthy_endpoints": sum(1 for item in details.values() if item.get("healthy")),
            "issues": issues,
            "details": details,
        }

    async def _check_security(self) -> Dict[str, Any]:
        issues: List[Dict[str, Any]] = []
        details: Dict[str, Any] = {}
        maker = get_sessionmaker()

        try:
            async with maker() as session:
                no_role_result = await session.execute(text("SELECT COUNT(*) FROM users WHERE role IS NULL OR role = ''"))
                users_without_role = int(no_role_result.scalar() or 0)
                details["users_without_role"] = users_without_role
                if users_without_role > 0:
                    issues.append(self._issue("medium", "security", f"{users_without_role} users have no role assigned"))

                inactive_result = await session.execute(text("SELECT COUNT(*) FROM users WHERE is_active = false"))
                details["inactive_users"] = int(inactive_result.scalar() or 0)
        except Exception as exc:
            issues.append(self._issue("medium", "security", f"Security checks incomplete: {exc}"))

        details["debug_endpoints_review"] = ["docs", "redoc"]
        return {"healthy": not issues, "issues": issues, "details": details}

    async def _check_performance(self) -> Dict[str, Any]:
        issues: List[Dict[str, Any]] = []
        details: Dict[str, Any] = {}
        if psutil is None:
            return {
                "healthy": False,
                "issues": [self._issue("low", "performance", "psutil not available")],
                "details": {},
            }

        process = psutil.Process()
        memory_info = process.memory_info()
        details["memory_usage_mb"] = round(memory_info.rss / 1024 / 1024, 2)
        if details["memory_usage_mb"] > 500:
            issues.append(self._issue("medium", "performance", f"High memory usage: {details['memory_usage_mb']}MB"))

        cpu_percent = process.cpu_percent(interval=0.2)
        details["cpu_percent"] = cpu_percent
        if cpu_percent > 80:
            issues.append(self._issue("high", "performance", f"High CPU usage: {cpu_percent}%"))

        try:
            details["system_uptime_hours"] = round((time.time() - psutil.boot_time()) / 3600, 2)
        except Exception:
            details["system_uptime_hours"] = None

        return {"healthy": not issues, "issues": issues, "details": details}

    async def _check_files(self) -> Dict[str, Any]:
        issues: List[Dict[str, Any]] = []
        details: Dict[str, Any] = {}
        for directory_name in ("uploads", "logs", "temp"):
            path = Path(directory_name)
            if not path.exists():
                issues.append(
                    {
                        **self._issue("medium", f"files_{directory_name}", f"Directory {directory_name} does not exist"),
                        "repairable": True,
                        "repair_action": "create_directory",
                    }
                )
                details[directory_name] = {"exists": False}
                continue

            total_size = 0
            file_count = 0
            for file_path in path.rglob("*"):
                if file_path.is_file():
                    file_count += 1
                    try:
                        total_size += file_path.stat().st_size
                    except Exception:
                        continue
            size_mb = round(total_size / (1024 * 1024), 2)
            details[directory_name] = {"exists": True, "file_count": file_count, "size_mb": size_mb}
            if total_size > 1024 * 1024 * 1024:
                issues.append(
                    {
                        **self._issue("medium", f"files_{directory_name}", f"Directory {directory_name} is very large ({size_mb} MB)"),
                        "repairable": True,
                        "repair_action": "cleanup_files",
                    }
                )

        return {
            "healthy": not any(issue["severity"] in {"high", "critical"} for issue in issues),
            "issues": issues,
            "details": details,
        }

    async def _check_platform_settings(self) -> Dict[str, Any]:
        issues: List[Dict[str, Any]] = []
        details: Dict[str, Any] = {}
        maker = get_sessionmaker()
        try:
            async with maker() as session:
                count_result = await session.execute(text("SELECT COUNT(*) FROM platform_settings"))
                settings_count = int(count_result.scalar() or 0)
                details["settings_count"] = settings_count
                if settings_count == 0:
                    issues.append(
                        {
                            **self._issue("medium", "settings", "No platform settings found"),
                            "repairable": True,
                            "repair_action": "create_default_settings",
                        }
                    )
        except Exception as exc:
            issues.append(
                {
                    **self._issue("high", "settings", f"Error checking platform settings: {exc}"),
                    "repairable": False,
                }
            )

        return {
            "healthy": not any(issue["severity"] in {"high", "critical"} for issue in issues),
            "issues": issues,
            "details": details,
        }

    async def _analyze_error_patterns(self) -> Dict[str, Any]:
        issues: List[Dict[str, Any]] = []
        bot_errors: Dict[str, int] = {}
        error_counts: Counter[str] = Counter()

        for bot_id in bot_learning_engine.learning_profiles.keys():
            errors = data_collection_service.get_bot_error_logs(bot_id, limit=100)
            bot_errors[bot_id] = len(errors)
            for error in errors:
                error_counts[error.get("error_type", "unknown")] += 1

        total_errors = sum(bot_errors.values())
        if total_errors > 100:
            issues.append(
                {
                    **self._issue("high", "error_patterns", f"High error rate: {total_errors} errors total"),
                    "repairable": True,
                    "repair_action": "clear_error_logs",
                }
            )
        for bot_id, count in bot_errors.items():
            if count > 20:
                issues.append(
                    {
                        **self._issue("medium", f"bot_{bot_id}", f"Bot {bot_id} has {count} errors"),
                        "repairable": True,
                        "repair_action": "reset_bot_errors",
                    }
                )

        return {
            "healthy": not issues,
            "issues": issues,
            "details": {
                "errors_per_bot": bot_errors,
                "errors_by_type": dict(error_counts.most_common(10)),
            },
        }

    async def _generate_recommendations(self, issues: List[Dict[str, Any]], results: Dict[str, Any]) -> List[str]:
        recommendations: List[str] = []
        if not issues:
            return ["All systems are healthy. No action needed."]

        critical = [issue for issue in issues if issue.get("severity") == "critical"]
        high = [issue for issue in issues if issue.get("severity") == "high"]
        medium = [issue for issue in issues if issue.get("severity") == "medium"]
        if critical:
            recommendations.append(f"Urgent: {len(critical)} critical issues need immediate attention.")
        if high:
            recommendations.append(f"High priority: fix {len(high)} high severity issues.")
        if medium:
            recommendations.append(f"Medium priority: review {len(medium)} medium severity issues.")

        repairable = [issue for issue in issues if issue.get("repairable")]
        if repairable:
            recommendations.append(f"Auto-repair available for {len(repairable)} issues.")

        for issue in issues[:5]:
            prefix = "[repairable]" if issue.get("repairable") else "[manual]"
            recommendations.append(f"{prefix} {issue['component']}: {issue['message']}")

        if not results.get("database", {}).get("healthy", True):
            recommendations.append("Check database connectivity and migrations.")
        if results.get("api", {}).get("healthy_endpoints", 0) < results.get("api", {}).get("total_endpoints", 0):
            recommendations.append("Review API service health and authentication dependencies.")
        if results.get("performance", {}).get("details", {}).get("memory_usage_mb", 0) > 500:
            recommendations.append("Investigate memory pressure and optimize heavy queries or caches.")
        return recommendations

    @staticmethod
    def _issue(severity: str, component: str, message: str) -> Dict[str, str]:
        return {"severity": severity, "component": component, "message": message}


maintenance_dev_enhanced_bot = MaintenanceDevEnhancedBot()


async def maintenance_auto_repair_loop(interval_hours: int = 6) -> None:
    interval_seconds = max(1, interval_hours) * 3600
    while True:
        try:
            await maintenance_dev_enhanced_bot.auto_repair()
        except asyncio.CancelledError:
            raise
        except Exception:
            pass
        await asyncio.sleep(interval_seconds)
