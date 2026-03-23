"""API endpoints for intelligent email bot processing system."""
from __future__ import annotations

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel

# Import email system
from backend.email_service.intelligent_processor import IntelligentEmailProcessor
from backend.email_service.intelligent_router import IntelligentEmailRouter
from backend.email_service.bos_integration import EmailBotIntegration
from backend.email_service.monitoring import EmailBotMonitor

# Router setup
router = APIRouter(prefix="/api/v1/email", tags=["email-bot"])

# Initialize components
email_processor = IntelligentEmailProcessor()
email_router = IntelligentEmailRouter()
email_monitor = EmailBotMonitor()
bos_integration = EmailBotIntegration()


# ============================================================================
# Pydantic Models
# ============================================================================

class EmailMessage(BaseModel):
    """Email message schema."""
    id: Optional[str] = None
    from_: str
    to: str
    subject: str
    body: str
    attachments: Optional[List[str]] = None


class BotMapping(BaseModel):
    """Email-to-bot mapping configuration."""
    email_account: str
    primary_bot: str
    backup_bot: Optional[str] = None
    workflows: List[str] = []
    auto_execute: bool = True
    requires_approval: bool = False
    priority: str = "medium"


class ProcessingResult(BaseModel):
    """Email processing result."""
    success: bool
    email_id: Optional[str] = None
    bot: str
    workflow: str
    auto_executed: bool
    priority: str


# ============================================================================
# Email Processing Endpoints
# ============================================================================

@router.post("/process", response_model=ProcessingResult)
async def process_email(email: EmailMessage) -> Dict[str, Any]:
    """
    Process incoming email and route to appropriate bot.
    
    - **email**: Email message with from, to, subject, body
    
    Returns processing result with assigned bot and workflow.
    """
    try:
        # Process email through intelligent processor
        processor_result = email_processor.process_incoming_email(email.dict())

        if not processor_result.get("success"):
            raise HTTPException(
                status_code=400,
                detail={"error": "processing_failed", "reason": processor_result.get("error")}
            )

        # Route to BOS bot
        routing_result = await bos_integration.route_email_to_bot(email.dict())

        # Track in monitoring
        bot_name = routing_result.get("bot") or "unknown"
        email_monitor.track_processing(
            bot_name=bot_name,
            email_id=email.id,
            result=routing_result
        )

        return {
            "success": True,
            "email_id": email.id,
            "bot": routing_result.get("bot"),
            "workflow": routing_result.get("workflow"),
            "auto_executed": routing_result.get("executed", False),
            "priority": routing_result.get("priority", "medium")
        }

    except Exception as e:
        email_monitor.track_processing("unknown", email.id, {"success": False, "error": str(e)})
        raise HTTPException(status_code=500, detail={"error": "processing_error", "message": str(e)})


@router.post("/route-workflow")
async def route_workflow(email: EmailMessage) -> Dict[str, Any]:
    """
    Route email through workflow engine.
    
    - **email**: Email message
    
    Returns workflow execution results.
    """
    try:
        result = email_router.route_and_process(email.dict())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": "routing_failed", "message": str(e)})


@router.post("/batch-process")
async def batch_process_emails(emails: List[EmailMessage]) -> Dict[str, Any]:
    """
    Process batch of emails simultaneously.
    
    - **emails**: List of email messages
    
    Returns batch processing results.
    """
    if not emails:
        raise HTTPException(status_code=400, detail="No emails provided")

    if len(emails) > 100:
        raise HTTPException(status_code=400, detail="Maximum 100 emails per batch")

    results = []
    for email in emails:
        try:
            result = await process_email(email)
            results.append(result)
        except Exception as e:
            results.append({
                "success": False,
                "email_id": email.id,
                "error": str(e)
            })

    successful = sum(1 for r in results if r.get("success"))
    failed = len(results) - successful

    return {
        "batch_id": None,  # Could generate UUID
        "total": len(results),
        "successful": successful,
        "failed": failed,
        "results": results
    }


# ============================================================================
# Bot Mapping Management
# ============================================================================

@router.get("/bot-mappings")
async def get_bot_mappings() -> Dict[str, Any]:
    """Get all email-to-bot mappings."""
    mappings = bos_integration.email_to_bot_mapping
    return {
        "total": len(mappings),
        "mappings": [
            {
                "email": email,
                "primary_bot": config.get("primary_bot"),
                "backup_bot": config.get("backup_bot"),
                "workflows": config.get("workflows", []),
                "auto_execute": config.get("auto_execute"),
                "requires_approval": config.get("requires_approval"),
                "priority": config.get("priority")
            }
            for email, config in mappings.items()
        ]
    }


@router.get("/bot-mappings/{email_account}")
async def get_email_mapping(email_account: str) -> Dict[str, Any]:
    """Get mapping for specific email account."""
    bot = bos_integration.get_bot_for_email(email_account)
    if not bot:
        raise HTTPException(status_code=404, detail="Email account not mapped")

    config = bos_integration.email_to_bot_mapping.get(email_account)
    if not config:
        raise HTTPException(status_code=404, detail="Email account not configured")
    
    return {
        "email_account": email_account,
        "primary_bot": config.get("primary_bot"),
        "backup_bot": config.get("backup_bot"),
        "workflows": config.get("workflows", []),
        "auto_execute": config.get("auto_execute"),
        "requires_approval": config.get("requires_approval"),
        "priority": config.get("priority")
    }


@router.post("/bot-mappings")
async def add_bot_mapping(mapping: BotMapping) -> Dict[str, Any]:
    """Add or update email-to-bot mapping."""
    try:
        bos_integration.add_custom_mapping(
            mapping.email_account,
            {
                "primary_bot": mapping.primary_bot,
                "backup_bot": mapping.backup_bot,
                "workflows": mapping.workflows,
                "auto_execute": mapping.auto_execute,
                "requires_approval": mapping.requires_approval,
                "priority": mapping.priority
            }
        )
        return {
            "success": True,
            "email_account": mapping.email_account,
            "primary_bot": mapping.primary_bot,
            "message": "Mapping added successfully"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": "mapping_failed", "message": str(e)})


@router.get("/bots/{bot_name}/emails")
async def get_bot_email_accounts(bot_name: str) -> Dict[str, Any]:
    """Get all email accounts handled by specific bot."""
    accounts = bos_integration.get_email_accounts_for_bot(bot_name)
    return {
        "bot": bot_name,
        "email_accounts": accounts,
        "total": len(accounts)
    }


# ============================================================================
# Monitoring & Analytics
# ============================================================================

@router.get("/bot-monitoring/stats")
async def get_monitoring_stats() -> Dict[str, Any]:
    """Get email processing statistics."""
    report = email_monitor.generate_report(period="daily")
    return report


@router.get("/monitoring/bot-stats/{bot_name}")
async def get_bot_stats(bot_name: str) -> Dict[str, Any]:
    """Get statistics for specific bot."""
    bot_stats = email_monitor.metrics.get("bot_performance", {}).get(bot_name)
    if not bot_stats:
        raise HTTPException(status_code=404, detail="No stats for bot")

    return {
        "bot": bot_name,
        "processed": bot_stats.get("processed", 0),
        "success_rate": bot_stats.get("success_rate", 0.0),
        "auto_resolution_rate": bot_stats.get("auto_resolution_rate", 0.0)
    }


@router.get("/bot-execution-history")
async def get_execution_history(limit: int = Query(50, ge=1, le=500)) -> Dict[str, Any]:
    """Get email-to-bot execution history."""
    history = bos_integration.get_execution_history(limit=limit)
    return {
        "total": len(history),
        "limit": limit,
        "history": history
    }


@router.get("/bot-execution-history/{email_id}")
async def get_email_execution(email_id: str) -> Dict[str, Any]:
    """Get execution history for specific email."""
    history = bos_integration.execution_history
    execution = next((e for e in history if e.get("email_id") == email_id), None)

    if not execution:
        raise HTTPException(status_code=404, detail="Email execution not found")

    return execution


# ============================================================================
# Configuration & Admin
# ============================================================================

@router.get("/config/health")
async def email_system_health() -> Dict[str, Any]:
    """Check health of email processing system."""
    return {
        "status": "healthy",
        "components": {
            "processor": "active",
            "router": "active",
            "monitor": "active",
            "bos_integration": "active"
        },
        "emails_processed": email_monitor.metrics["total_processed"],
        "success_rate": email_monitor._calculate_success_rate(),
        "auto_resolution_rate": email_monitor._calculate_auto_resolution_rate()
    }


@router.get("/config/workflows")
async def get_available_workflows() -> Dict[str, Any]:
    """Get all available workflows."""
    workflows = {
        "shipment": ["extract_details", "find_carriers", "generate_quotes", "send_response"],
        "invoice": ["extract_data", "validate", "record", "schedule_payment", "archive"],
        "support": ["classify", "route", "respond"],
        "safety": ["log_incident", "notify_team"],
        "security": ["assess", "investigate", "escalate"]
    }
    return {"workflows": workflows}


@router.post("/reset-stats")
async def reset_monitoring_stats() -> Dict[str, Any]:
    """Reset monitoring statistics (admin only)."""
    email_monitor.metrics = {
        "total_processed": 0,
        "successful": 0,
        "failed": 0,
        "auto_resolved": 0,
        "human_escalated": 0,
        "avg_processing_time": 0,
        "bot_performance": {},
    }
    return {"success": True, "message": "Stats reset"}


__all__ = ["router"]
