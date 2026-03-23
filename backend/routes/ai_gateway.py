# backend/routes/ai_gateway.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any, Dict

from backend.ai.openai_safe_client import get_openai_client

router = APIRouter(prefix="/ai", tags=["AI-Gateway"])


class AskPayload(BaseModel):
    query: str
    context: Dict[str, Any] = {}


async def _fallback_llm_response(query: str) -> Dict[str, Any]:
    client = get_openai_client()
    if client is None:
        raise HTTPException(status_code=503, detail="LLM client unavailable")
    prompt = f"System: You are GTS internal assistant.\nUser: {query}"
    completion = await client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "system", "content": prompt}],
        max_tokens=250,
    )
    answer = completion.choices[0].message.content
    return {"ok": True, "answer": answer.strip()}


async def some_finance_llm_handler(payload: AskPayload) -> Dict[str, Any]:
    return await _fallback_llm_response(payload.query)


async def some_documents_llm_handler(payload: AskPayload) -> Dict[str, Any]:
    return await _fallback_llm_response(payload.query)


async def some_freight_llm_handler(payload: AskPayload) -> Dict[str, Any]:
    return await _fallback_llm_response(payload.query)


@router.post("/ask")
async def ai_ask(payload: AskPayload):
    q = (payload.query or "").lower()
    if any(k in q for k in ["finance", "expense", "revenue", "profit"]):
        return await some_finance_llm_handler(payload)
    if any(k in q for k in ["document", "expire", "notify", "extend"]):
        return await some_documents_llm_handler(payload)
    if any(k in q for k in ["load", "shipment", "broker", "truckerpath"]):
        return await some_freight_llm_handler(payload)
    return await _fallback_llm_response(payload.query)
