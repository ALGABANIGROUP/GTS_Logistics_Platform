from __future__ import annotations

from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class CommandType(str, Enum):
    MANUAL = "manual"
    SCHEDULED = "scheduled"
    SYSTEM = "system"


class CommandCreate(BaseModel):
    human_command: str = Field(..., min_length=1)
    parameters: Optional[Dict[str, Any]] = None
    command_type: CommandType = CommandType.MANUAL
    priority: int = 1
    user_id: Optional[int] = None
