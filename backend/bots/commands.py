from datetime import datetime
import time, asyncio
from backend.database.connection import SessionLocal
from backend.services import crud
from backend.bots.command_parser import parse_command


def process_human_command(
    human_command: str,
    suggested_bot: str | None = None,
    parameters: dict | None = None,
) -> dict:
    parsed = parse_command(human_command or "")
    bot_name = parsed.get("bot_name") or suggested_bot or "general_manager"
    task_type = parsed.get("task_type") or "run"
    params = dict(parsed.get("params") or {})
    if parameters:
        params.update(parameters)
    technical_command = {
        "bot": bot_name,
        "action": task_type,
        "parameters": params,
    }
    return {
        "ok": bool(parsed.get("ok")),
        "technical_command": technical_command,
        "parsed": parsed,
    }

async def execute_technical_command_bg(command_id: int, technical_command: dict):
    db = SessionLocal()
    start = time.time()
    try:
        await asyncio.sleep(1)  # simulate async execution delay
        execution_time_ms = int((time.time() - start) * 1000)

        result = {
            "success": True,
            "bot": technical_command.get("bot"),
            "action": technical_command.get("action"),
            "data": technical_command.get("parameters", {}),
            "execution_time_ms": execution_time_ms,
        }

        crud.update_command(db, command_id, {
            "status": "completed",
            "result": result,
            "executed_at": datetime.utcnow(),
            "execution_time_ms": execution_time_ms
        })
    except Exception as e:
        execution_time_ms = int((time.time() - start) * 1000)
        crud.update_command(db, command_id, {
            "status": "failed",
            "error_message": str(e),
            "executed_at": datetime.utcnow(),
            "execution_time_ms": execution_time_ms
        })
    finally:
        db.close()

