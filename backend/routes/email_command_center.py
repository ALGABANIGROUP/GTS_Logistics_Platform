from fastapi import APIRouter
from datetime import datetime

router = APIRouter(prefix="/api/v1/email", tags=["Email Command Center"])

@router.get("/monitoring/stats")
def get_monitoring_stats():
    return {
        "total_emails": 1245,
        "processed": 1200,
        "failed": 45,
        "bots_active": 5,
        "last_update": datetime.now().isoformat()
    }

@router.get("/mappings")
def get_email_mappings():
    return {
        "mappings": [
            {"email_pattern": "support@gts.com", "bot_name": "SupportBot"},
            {"email_pattern": "finance@gts.com", "bot_name": "FinanceBot"},
            {"email_pattern": "info@gts.com", "bot_name": "InfoBot"}
        ]
    }

@router.get("/execution-history")
def get_execution_history(limit: int = 50):
    return {
        "executions": [
            {"id": 1, "email_from": "client1@example.com", "subject": "Invoice Request", "bot_name": "FinanceBot", "status": "completed", "response": "Invoice sent", "timestamp": datetime.now().isoformat()},
            {"id": 2, "email_from": "client2@example.com", "subject": "Support Needed", "bot_name": "SupportBot", "status": "pending", "response": None, "timestamp": datetime.now().isoformat()}
        ]
    }

@router.get("/mailboxes")
def get_mailboxes():
    return {
        "mailboxes": [
            {"id": 1, "email_address": "support@gts.com", "bot_name": "SupportBot"},
            {"id": 2, "email_address": "finance@gts.com", "bot_name": "FinanceBot"}
        ]
    }

@router.get("/threads")
def get_threads():
    return {
        "threads": [
            {"id": 101, "subject": "Invoice Request", "participants": ["client1@example.com", "finance@gts.com"], "status": "open"},
            {"id": 102, "subject": "Support Needed", "participants": ["client2@example.com", "support@gts.com"], "status": "pending"}
        ]
    }
