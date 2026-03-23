from __future__ import annotations

import os
from importlib import import_module
from importlib.util import find_spec
from typing import Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

router = APIRouter()
load_dotenv()

class ChatMessage(BaseModel):
    message: str

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY is required for /chatbot/ask.")

if find_spec("openai") is None:
    raise RuntimeError("The `openai` package is required for /chatbot/ask.")

openai_module = import_module("openai")
AsyncOpenAI = getattr(openai_module, "AsyncOpenAI", None)
if AsyncOpenAI is None:
    raise RuntimeError("AsyncOpenAI is not available in the installed openai package.")

openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)


@router.post("/chatbot/ask")
async def ask_chatbot(message: ChatMessage) -> Dict[str, Optional[str]]:
    try:
        response = await openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": message.message}],
            temperature=0.7,
            max_tokens=200,
        )
        reply: Optional[str] = (
            response.choices[0].message.content if response and response.choices else None
        )
        return {"response": reply}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
