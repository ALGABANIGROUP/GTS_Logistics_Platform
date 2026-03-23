from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter, Request
from pydantic import BaseModel

from backend.ai.maintenance_dev_enhanced import maintenance_dev_enhanced_bot

router = APIRouter(prefix="/api/v1/maintenance-dev", tags=["Maintenance Dev Enhanced"])


class DiagnosticRequest(BaseModel):
    type: str = "full"
    options: Optional[Dict[str, Any]] = None


class AutoRepairRequest(BaseModel):
    issue_ids: Optional[list[str]] = None


@router.post("/diagnostic")
async def run_diagnostic(request: DiagnosticRequest, http_request: Request) -> Dict[str, Any]:
    return await maintenance_dev_enhanced_bot.run_diagnostic(request.model_dump(), app=http_request.app)


@router.post("/auto-repair")
async def auto_repair(request: AutoRepairRequest, http_request: Request) -> Dict[str, Any]:
    return await maintenance_dev_enhanced_bot.auto_repair(request.issue_ids, app=http_request.app)


@router.get("/health-summary")
async def get_health_summary(http_request: Request) -> Dict[str, Any]:
    diagnostic = await maintenance_dev_enhanced_bot.run_full_system_diagnostic(app=http_request.app)
    return {
        "status": diagnostic["status"],
        "issues_found": diagnostic["issues_found"],
        "components_checked": diagnostic["components_checked"],
        "last_scan": diagnostic["scanned_at"],
        "recommendations": diagnostic["recommendations"][:3],
        "repair_success_rate": round(
            (
                maintenance_dev_enhanced_bot.repair_actions_succeeded
                / max(1, maintenance_dev_enhanced_bot.repair_actions_attempted)
            )
            * 100,
            2,
        ),
        "repair_attempts": maintenance_dev_enhanced_bot.repair_attempts,
        "last_repair": maintenance_dev_enhanced_bot.last_repair_summary,
    }


@router.get("/history")
async def get_diagnostic_history() -> Dict[str, Any]:
    return {
        "last_full_scan": maintenance_dev_enhanced_bot.last_full_scan,
        "health_history": maintenance_dev_enhanced_bot.health_history[-10:],
        "known_issues": maintenance_dev_enhanced_bot.known_issues[-20:],
        "fixed_issues": maintenance_dev_enhanced_bot.fixed_issues[-20:],
        "repair_attempts": maintenance_dev_enhanced_bot.repair_attempts,
        "repair_actions_attempted": maintenance_dev_enhanced_bot.repair_actions_attempted,
        "repair_actions_succeeded": maintenance_dev_enhanced_bot.repair_actions_succeeded,
        "last_repair": maintenance_dev_enhanced_bot.last_repair_summary,
    }
