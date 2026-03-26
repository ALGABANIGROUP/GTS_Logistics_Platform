from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from backend.security.auth import get_current_user
from backend.database.session import wrap_session_factory
from backend.models.bot_os import HumanCommand
from backend.bots import get_bot_os

logger = logging.getLogger("orchestration.routes")

# Enhanced logging setup for operations and performance
operation_logger = logging.getLogger("operation_tracking")
performance_logger = logging.getLogger("performance_monitoring")

# Create logs directory if it doesn't exist
import os
os.makedirs("logs", exist_ok=True)

# Configure operation logger
operation_handler = logging.FileHandler("logs/operations.log")
operation_handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - OPERATION:%(operation_id)s - %(message)s'
))
operation_logger.addHandler(operation_handler)
operation_logger.setLevel(logging.INFO)

# Configure performance logger
performance_handler = logging.FileHandler("logs/performance.log")
performance_handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
))
performance_logger.addHandler(performance_handler)
performance_logger.setLevel(logging.INFO)

router = APIRouter(prefix="/api/v1/orchestration", tags=["Orchestration"])


# Enhanced logging functions
def log_operation_event(operation_id: str, event_type: str, message: str, extra_data: Dict[str, Any] = None):
    """Log operation events with structured data."""
    log_data = {
        'operation_id': operation_id,
        'event_type': event_type,
        'message': message,
        'timestamp': datetime.now().isoformat(),
        'extra_data': extra_data or {}
    }

    operation_logger.info(f"[{event_type}] {message}", extra={'operation_id': operation_id})
    logger.info(f"Operation {operation_id}: {event_type} - {message}")


def log_performance_metric(metric_name: str, value: float, operation_id: str = None, extra_data: Dict[str, Any] = None):
    """Log performance metrics."""
    log_data = {
        'metric_name': metric_name,
        'value': value,
        'operation_id': operation_id,
        'timestamp': datetime.now().isoformat(),
        'extra_data': extra_data or {}
    }

    performance_logger.info(f"[{metric_name}] Value: {value}", extra=log_data)
    logger.info(f"Performance metric {metric_name}: {value}")


def log_bot_activity(bot_id: str, activity: str, operation_id: str = None, duration: float = None):
    """Log bot activities."""
    message = f"Bot {bot_id}: {activity}"
    if duration:
        message += f" (Duration: {duration:.2f}s)"
    if operation_id:
        message += f" [Operation: {operation_id}]"

    operation_logger.info(message)
    logger.info(message)


class OperationData(BaseModel):
    type: str = Field(..., description="Type of operation (e.g., new_customer, shipping_request)")
    name: str = Field(..., description="Name of the operation")
    description: Optional[str] = None
    priority: str = Field(default="normal", description="Priority level: low, normal, high, urgent")
    customerName: Optional[str] = None
    customerContact: Optional[str] = None
    estimatedTime: Optional[int] = None  # in minutes


class OperationUpdate(BaseModel):
    status: Optional[str] = None
    progress: Optional[int] = None
    assignedBots: Optional[List[str]] = None
    notes: Optional[str] = None


class WorkflowStep(BaseModel):
    bot: str
    action: str
    duration: int  # in minutes


class Workflow(BaseModel):
    id: str
    name: str
    description: str
    steps: List[WorkflowStep]
    estimatedTime: int


class BotInfo(BaseModel):
    id: str
    name: str
    icon: str
    description: str
    status: str
    priority: int
    department: str
    capabilities: List[str]
    dependencies: List[str]


class OperationStats(BaseModel):
    totalOperations: int
    activeOperations: int
    completedToday: int
    averageProcessingTime: float
    botUtilization: Dict[str, Dict[str, Any]]


# Operational data for demonstration - in real implementation, this would come from database
MOCK_BOTS = [
    {
        "id": "customer_service",
        "name": "Customer Service",
        "icon": "👥",
        "description": "Handles customer reception and routing",
        "status": "active",
        "priority": 1,
        "department": "frontend",
        "capabilities": ["reception", "query_handling", "routing"],
        "dependencies": []
    },
    {
        "id": "operations_bot",
        "name": "Operations Manager",
        "icon": "👨‍💼",
        "description": "Central coordination between all bots",
        "status": "active",
        "priority": 10,
        "department": "management",
        "capabilities": ["coordination", "monitoring", "reporting", "escalation"],
        "dependencies": ["customer_service", "sales_bot"]
    },
    {
        "id": "general_manager",
        "name": "General Manager",
        "icon": "👔",
        "description": "Overall supervision and reports",
        "status": "active",
        "priority": 100,
        "department": "executive",
        "capabilities": ["oversight", "decision_making", "strategic_planning"],
        "dependencies": ["operations_bot", "all"]
    },
    {
        "id": "ai_dispatcher",
        "name": "AI Dispatcher",
        "icon": "🚨",
        "description": "Intelligent request distribution",
        "status": "active",
        "priority": 2,
        "department": "ai",
        "capabilities": ["intelligent_routing", "load_balancing", "priority_management"],
        "dependencies": ["operations_bot"]
    },
    {
        "id": "sales_bot",
        "name": "Sales",
        "icon": "💰",
        "description": "Order processing and quotations",
        "status": "active",
        "priority": 3,
        "department": "sales",
        "capabilities": ["order_processing", "quotation", "customer_followup"],
        "dependencies": ["customer_service"]
    },
    {
        "id": "legal_bot",
        "name": "Legal Advisor",
        "icon": "⚖️",
        "description": "Legal review and contracts",
        "status": "active",
        "priority": 4,
        "department": "legal",
        "capabilities": ["contract_review", "compliance_check", "legal_advice"],
        "dependencies": ["sales_bot"]
    },
    {
        "id": "freight_bot",
        "name": "Freight & Logistics",
        "icon": "🚚",
        "description": "Shipping and delivery management",
        "status": "active",
        "priority": 5,
        "department": "operations",
        "capabilities": ["shipping", "logistics", "tracking"],
        "dependencies": ["sales_bot", "legal_bot"]
    },
    {
        "id": "security_bot",
        "name": "Security",
        "icon": "🛡️",
        "description": "Cybersecurity and protection",
        "status": "active",
        "priority": 6,
        "department": "security",
        "capabilities": ["security_check", "fraud_detection", "access_control"],
        "dependencies": ["customer_service"]
    },
    {
        "id": "documents_manager",
        "name": "Documents Manager",
        "icon": "📄",
        "description": "Document management and archiving",
        "status": "active",
        "priority": 7,
        "department": "admin",
        "capabilities": ["document_management", "archiving", "version_control"],
        "dependencies": ["all"]
    },
    {
        "id": "maintenance_dev",
        "name": "Maintenance & Development",
        "icon": "🔧",
        "description": "System maintenance and development",
        "status": "active",
        "priority": 8,
        "department": "tech",
        "capabilities": ["system_maintenance", "updates", "bug_fixes"],
        "dependencies": ["all"]
    },
    {
        "id": "information_coordinator",
        "name": "Information Coordinator",
        "icon": "🧠",
        "description": "Information coordination and AI",
        "status": "active",
        "priority": 9,
        "department": "ai",
        "capabilities": ["data_analysis", "intelligence", "coordination"],
        "dependencies": ["all"]
    },
    {
        "id": "partner_bot",
        "name": "Partners",
        "icon": "🤝",
        "description": "Partner relationship management",
        "status": "active",
        "priority": 11,
        "department": "partnership",
        "capabilities": ["partner_management", "collaboration", "contracts"],
        "dependencies": ["sales_bot"]
    },
    {
        "id": "safety_bot",
        "name": "Safety",
        "icon": "⚠️",
        "description": "Safety and quality control",
        "status": "active",
        "priority": 12,
        "department": "quality",
        "capabilities": ["safety_checks", "quality_control", "compliance"],
        "dependencies": ["operations_bot"]
    },
    {
        "id": "system_bot",
        "name": "System Monitor",
        "icon": "⚙️",
        "description": "System performance monitoring",
        "status": "active",
        "priority": 13,
        "department": "tech",
        "capabilities": ["system_monitoring", "performance", "alerts"],
        "dependencies": ["all"]
    }
]

MOCK_WORKFLOWS = [
    {
        "id": "new_customer",
        "name": "New Customer",
        "description": "Complete flow for onboarding a new customer",
        "steps": [
            {"bot": "customer_service", "action": "welcome", "duration": 5},
            {"bot": "security_bot", "action": "security_check", "duration": 10},
            {"bot": "sales_bot", "action": "needs_assessment", "duration": 15},
            {"bot": "legal_bot", "action": "contract_setup", "duration": 20},
            {"bot": "operations_bot", "action": "coordination", "duration": 10},
            {"bot": "general_manager", "action": "final_approval", "duration": 5}
        ],
        "estimatedTime": 65
    },
    {
        "id": "shipping_request",
        "name": "Shipping Request",
        "description": "Processing a new shipping request",
        "steps": [
            {"bot": "customer_service", "action": "receive_request", "duration": 5},
            {"bot": "sales_bot", "action": "quotation", "duration": 10},
            {"bot": "legal_bot", "action": "contract_review", "duration": 15},
            {"bot": "freight_bot", "action": "shipping_planning", "duration": 20},
            {"bot": "operations_bot", "action": "execution", "duration": 10},
            {"bot": "safety_bot", "action": "safety_check", "duration": 5}
        ],
        "estimatedTime": 65
    },
    {
        "id": "partner_onboarding",
        "name": "Partner Onboarding",
        "description": "Adding a new partner to the system",
        "steps": [
            {"bot": "partner_bot", "action": "initial_contact", "duration": 10},
            {"bot": "legal_bot", "action": "agreement_drafting", "duration": 25},
            {"bot": "operations_bot", "action": "integration_planning", "duration": 15},
            {"bot": "general_manager", "action": "approval", "duration": 5},
            {"bot": "documents_manager", "action": "documentation", "duration": 10}
        ],
        "estimatedTime": 65
    }
]

# Operations storage - in real implementation, use database
mock_operations = []
operation_counter = 1


@router.get("/bots", response_model=List[BotInfo])
async def get_bots(user: Dict[str, Any] = Depends(get_current_user)):
    """Get all available bots with their information."""
    return MOCK_BOTS


@router.get("/workflows", response_model=List[Workflow])
async def get_workflows(user: Dict[str, Any] = Depends(get_current_user)):
    """Get all available workflows."""
    return MOCK_WORKFLOWS


@router.post("/operations")
async def start_operation(
    operation_data: OperationData,
    user: Dict[str, Any] = Depends(get_current_user)
):
    """Start a new operation with enhanced logging."""
    global operation_counter

    start_time = datetime.now()
    operation_id = f"OP-{start_time.strftime('%Y%m%d')}-{operation_counter:04d}"
    operation_counter += 1

    operation = {
        "id": operation_id,
        "type": operation_data.type,
        "name": operation_data.name,
        "description": operation_data.description,
        "priority": operation_data.priority,
        "customerName": operation_data.customerName,
        "customerContact": operation_data.customerContact,
        "estimatedTime": operation_data.estimatedTime,
        "status": "active",
        "progress": 0,
        "startTime": start_time.isoformat(),
        "assignedBots": [],
        "createdBy": user.get("id"),
        "logs": [],
        "currentStep": 0,
        "performanceMetrics": {
            "startTime": start_time.isoformat(),
            "botAssignments": [],
            "stepDurations": []
        }
    }

    # Assign bots based on operation type
    assigned_bots = _assign_bots_to_operation(operation_data.type)
    operation["assignedBots"] = assigned_bots

    mock_operations.append(operation)

    # Enhanced logging
    log_operation_event(
        operation_id,
        "operation_started",
        f"Started operation: {operation_data.name} by user {user.get('id')}",
        {
            "operation_type": operation_data.type,
            "priority": operation_data.priority,
            "assigned_bots": assigned_bots,
            "estimated_time": operation_data.estimatedTime,
            "customer": operation_data.customerName
        }
    )

    # Log bot assignments
    for bot_id in assigned_bots:
        log_bot_activity(bot_id, "assigned_to_operation", operation_id)

    # Performance logging
    log_performance_metric("operation_creation_time", 0.0, operation_id, {"user_id": user.get("id")})

    return {
        "success": True,
        "message": "Operation started successfully",
        "operation": operation
    }


@router.get("/operations/active")
async def get_active_operations(
    status_filter: Optional[str] = None,
    type_filter: Optional[str] = None,
    user: Dict[str, Any] = Depends(get_current_user)
):
    """Get active operations with optional filters."""
    operations = mock_operations.copy()

    if status_filter:
        operations = [op for op in operations if op["status"] == status_filter]

    if type_filter:
        operations = [op for op in operations if op["type"] == type_filter]

    return {
        "success": True,
        "operations": operations,
        "count": len(operations)
    }


@router.put("/operations/{operation_id}")
async def update_operation(
    operation_id: str,
    updates: OperationUpdate,
    user: Dict[str, Any] = Depends(get_current_user)
):
    """Update an operation's status or details with enhanced logging."""
    operation = next((op for op in mock_operations if op["id"] == operation_id), None)
    if not operation:
        log_operation_event(operation_id, "operation_not_found", f"Attempted to update non-existent operation by user {user.get('id')}")
        raise HTTPException(status_code=404, detail="Operation not found")

    update_start = datetime.now()
    previous_status = operation.get("status")

    # Update the operation
    for key, value in updates.dict(exclude_unset=True).items():
        operation[key] = value

    operation["updatedAt"] = datetime.now().isoformat()
    operation["updatedBy"] = user.get("id")

    # Enhanced logging for status changes
    if updates.status and updates.status != previous_status:
        log_operation_event(
            operation_id,
            "status_changed",
            f"Status changed from '{previous_status}' to '{updates.status}' by user {user.get('id')}",
            {
                "previous_status": previous_status,
                "new_status": updates.status,
                "updated_by": user.get("id")
            }
        )

        # Log bot activities for status changes
        for bot_id in operation.get("assignedBots", []):
            log_bot_activity(bot_id, f"operation_status_changed_to_{updates.status}", operation_id)

    # Handle completion with detailed logging
    if updates.status == "completed":
        completion_time = datetime.now()
        operation["completedAt"] = completion_time.isoformat()

        # Calculate performance metrics
        start_time = datetime.fromisoformat(operation["startTime"])
        total_duration = (completion_time - start_time).total_seconds()

        log_performance_metric("operation_total_duration", total_duration, operation_id, {
            "operation_type": operation.get("type"),
            "priority": operation.get("priority"),
            "assigned_bots_count": len(operation.get("assignedBots", []))
        })

        _finalize_operation(operation)

        log_operation_event(
            operation_id,
            "operation_completed",
            f"Operation completed successfully in {total_duration:.2f} seconds",
            {
                "total_duration": total_duration,
                "completed_by": user.get("id"),
                "completion_time": completion_time.isoformat()
            }
        )

    # Log general updates
    update_duration = (datetime.now() - update_start).total_seconds()
    log_performance_metric("operation_update_time", update_duration, operation_id)

    return {
        "success": True,
        "message": "Operation updated successfully",
        "operation": operation
    }


@router.get("/statistics/bots")
async def get_bot_statistics(user: Dict[str, Any] = Depends(get_current_user)):
    """Get statistics for all bots."""
    # Calculate aggregate statistics
    total_operations = len(mock_operations)
    active_operations = len([op for op in mock_operations if op["status"] == "active"])
    completed_today = len([
        op for op in mock_operations
        if op.get("completedAt") and
        datetime.fromisoformat(op["completedAt"]).date() == datetime.now().date()
    ])

    # Calculate average processing time
    completed_ops = [op for op in mock_operations if op.get("completedAt")]
    avg_time = 0
    if completed_ops:
        total_time = sum(
            (datetime.fromisoformat(op["completedAt"]) - datetime.fromisoformat(op["startTime"])).total_seconds() / 60
            for op in completed_ops
        )
        avg_time = total_time / len(completed_ops)

    # Bot utilization
    bot_stats = {}
    for bot in MOCK_BOTS:
        bot_operations = [op for op in mock_operations if bot["id"] in op.get("assignedBots", [])]
        bot_stats[bot["id"]] = {
            "totalOperations": len(bot_operations),
            "activeOperations": len([op for op in bot_operations if op["status"] == "active"]),
            "completedOperations": len([op for op in bot_operations if op["status"] == "completed"]),
            "utilization": (len(bot_operations) / max(total_operations, 1)) * 100
        }

    return {
        "success": True,
        "statistics": {
            "totalOperations": total_operations,
            "activeOperations": active_operations,
            "completedToday": completed_today,
            "averageProcessingTime": avg_time,
            "botUtilization": bot_stats
        }
    }


@router.post("/reports")
async def generate_report(
    report_type: str,
    data: Dict[str, Any] = None,
    user: Dict[str, Any] = Depends(get_current_user)
):
    """Generate a report."""
    report_id = f"REPORT-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    report = {
        "id": report_id,
        "type": report_type,
        "data": data or {},
        "generatedAt": datetime.now().isoformat(),
        "generatedBy": user.get("id")
    }

    # In real implementation, save to database
    logger.info(f"Generated report: {report_id} of type: {report_type}")

    return {
        "success": True,
        "message": "Report generated successfully",
        "report": report
    }


@router.post("/notify")
async def notify_bots(
    bot_ids: List[str],
    message: str,
    user: Dict[str, Any] = Depends(get_current_user)
):
    """Send notifications to specific bots."""
    # In real implementation, this would send actual notifications
    logger.info(f"Notifying bots {bot_ids}: {message}")

    return {
        "success": True,
        "message": f"Notifications sent to {len(bot_ids)} bots",
        "notifications": [{"botId": bot_id, "message": message, "sentAt": datetime.now().isoformat()} for bot_id in bot_ids]
    }


@router.get("/operations/{operation_id}/logs")
async def get_operation_logs(
    operation_id: str,
    limit: int = 50,
    user: Dict[str, Any] = Depends(get_current_user)
):
    """Get detailed logs for a specific operation."""
    operation = next((op for op in mock_operations if op["id"] == operation_id), None)
    if not operation:
        raise HTTPException(status_code=404, detail="Operation not found")

    logs = operation.get("logs", [])
    # Return most recent logs first, limited by limit parameter
    recent_logs = logs[-limit:] if logs else []

    log_operation_event(
        operation_id,
        "logs_accessed",
        f"Operation logs accessed by user {user.get('id')}",
        {"logs_count": len(recent_logs), "limit": limit}
    )

    return {
        "success": True,
        "operation_id": operation_id,
        "logs": recent_logs,
        "total_logs": len(logs),
        "returned_count": len(recent_logs)
    }


@router.get("/logs/system")
async def get_system_logs(
    log_type: str = "operations",
    hours: int = 24,
    limit: int = 100,
    user: Dict[str, Any] = Depends(get_current_user)
):
    """Get system-wide logs."""
    # In a real implementation, this would query the log files or database
    # For now, return aggregated operation logs

    cutoff_time = datetime.now() - timedelta(hours=hours)
    relevant_operations = []

    for operation in mock_operations:
        op_start = datetime.fromisoformat(operation["startTime"])
        if op_start >= cutoff_time:
            relevant_operations.append({
                "operation_id": operation["id"],
                "type": operation["type"],
                "status": operation["status"],
                "start_time": operation["startTime"],
                "logs_count": len(operation.get("logs", [])),
                "recent_logs": operation.get("logs", [])[-5:]  # Last 5 logs
            })

    # Sort by start time, most recent first
    relevant_operations.sort(key=lambda x: x["start_time"], reverse=True)
    limited_results = relevant_operations[:limit]

    logger.info(f"System logs accessed by user {user.get('id')} - Type: {log_type}, Hours: {hours}, Results: {len(limited_results)}")

    return {
        "success": True,
        "log_type": log_type,
        "time_range_hours": hours,
        "operations": limited_results,
        "total_operations": len(relevant_operations),
        "returned_count": len(limited_results)
    }


def _assign_bots_to_operation(operation_type: str) -> List[str]:
    """Assign appropriate bots based on operation type."""
    assignments = {
        "new_customer": ["customer_service", "security_bot", "sales_bot", "legal_bot"],
        "shipping_request": ["customer_service", "sales_bot", "legal_bot", "freight_bot", "safety_bot"],
        "partner_onboarding": ["partner_bot", "legal_bot", "operations_bot", "general_manager"]
    }

    bots = assignments.get(operation_type, ["operations_bot", "ai_dispatcher"])

    # Always include operations bot
    if "operations_bot" not in bots:
        bots.append("operations_bot")

    return bots


def _log_operation_activity(operation_id: str, activity_type: str, message: str, extra_data: Dict[str, Any] = None):
    """Log activity for an operation with enhanced logging."""
    operation = next((op for op in mock_operations if op["id"] == operation_id), None)
    if operation:
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": activity_type,
            "message": message,
            "extra_data": extra_data or {}
        }
        operation["logs"].append(log_entry)

    # Use enhanced logging
    log_operation_event(operation_id, activity_type, message, extra_data)


def _finalize_operation(operation: Dict[str, Any]):
    """Finalize a completed operation with comprehensive logging."""
    operation_id = operation["id"]

    # Calculate processing time
    start_time = datetime.fromisoformat(operation["startTime"])
    end_time = datetime.fromisoformat(operation["completedAt"])
    processing_time = (end_time - start_time).total_seconds() / 60

    # Log completion details
    log_operation_event(
        operation_id,
        "operation_finalized",
        f"Operation finalized - Processing time: {processing_time:.1f} minutes",
        {
            "processing_time_minutes": processing_time,
            "start_time": operation["startTime"],
            "end_time": operation["completedAt"],
            "operation_type": operation.get("type"),
            "assigned_bots": operation.get("assignedBots", []),
            "total_logs": len(operation.get("logs", []))
        }
    )

    # Log bot performance
    for bot_id in operation.get("assignedBots", []):
        log_bot_activity(
            bot_id,
            "operation_completed",
            operation_id,
            processing_time * 60  # Convert to seconds
        )

    # Performance metrics
    log_performance_metric("operation_processing_time", processing_time, operation_id, {
        "operation_type": operation.get("type"),
        "bot_count": len(operation.get("assignedBots", []))
    })

    # In real implementation, update bot statistics, send notifications, etc.
    logger.info(f"Operation {operation_id} completed successfully - Duration: {processing_time:.1f} minutes")
