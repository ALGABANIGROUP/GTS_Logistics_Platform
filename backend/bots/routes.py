from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from backend.database.connection import get_db
from backend.database import crud
from backend.bots import models
from backend.bots.commands import process_human_command, execute_technical_command_bg

router = APIRouter()

@router.post("/{bot_code}/execute")
async def execute_bot_manual(
    bot_code: str,
    command: models.CommandCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    bot = crud.get_bot_by_code(db, bot_code)
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    if not bot.is_active:
        raise HTTPException(status_code=400, detail="Bot is not active")

    processed = process_human_command(
        human_command=command.human_command,
        suggested_bot=bot_code,
        parameters=command.parameters or {}
    )
    technical_command = processed["technical_command"]

    db_command = crud.create_command(db, {
        "bot_code": bot_code,
        "human_command": command.human_command,
        "technical_command": technical_command,
        "command_type": command.command_type.value,
        "priority": command.priority,
        "user_id": command.user_id,
        "status": "pending"
    })

    background_tasks.add_task(
        execute_technical_command_bg,
        db_command.id,
        technical_command
    )

    return {
        "message": "Command accepted and queued for execution",
        "command_id": db_command.id,
        "technical_command": technical_command
    }

