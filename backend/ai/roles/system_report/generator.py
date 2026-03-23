# backend/ai/system_report/generator.py

from datetime import datetime
from typing import Dict, Any

from backend.main import ai_registry


async def generate_system_report() -> Dict[str, Any]:
    """
    Collects data from core bots and returns a unified system report.
    """
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    # Fetch from AI bots
    general = await ai_registry.get("general_manager").run({})
    finance = await ai_registry.get("finance_bot").run({})
    documents = await ai_registry.get("documents_manager").run({"action": "status"})
    operations = await ai_registry.get("operations_manager").run({})

    # Assemble report
    report = {
        "timestamp": now,
        "finance": finance.get("summary"),
        "documents": documents.get("data"),
        "operations": operations,
        "general": general.get("report"),
    }

    return {
        "ok": True,
        "report": report,
    }
