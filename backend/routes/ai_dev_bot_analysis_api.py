from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
import os
from dotenv import load_dotenv
from openai import OpenAI
from backend.utils.role_protected import RoleChecker
admin_or_manager_required = RoleChecker(['admin', 'manager'])
load_dotenv()
router = APIRouter(dependencies=[Depends(admin_or_manager_required)])
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    raise RuntimeError('Missing OPENAI_API_KEY in environment variables')
client = OpenAI(api_key=OPENAI_API_KEY)

class AIAnalyzeRequest(BaseModel):
    title: str
    description: str

class AIAnalyzeResponse(BaseModel):
    suggestion: str
    confidence: Optional[float] = None

@router.post('/ai/dev_bot/analyze', response_model=AIAnalyzeResponse)
async def analyze_issue(data: AIAnalyzeRequest):
    try:
        prompt = f'\nYou are an expert Python/React debugging assistant.\nAnalyze the following issue and suggest the most efficient and safe way to fix it.\n\nTitle: {data.title}\nDescription: {data.description}\n\nRespond with a concise solution proposal and any related notes.\n'
        response = client.chat.completions.create(model='gpt-4', messages=[{'role': 'system', 'content': 'You are a software debugging assistant.'}, {'role': 'user', 'content': prompt}], temperature=0.4, max_tokens=500)
        content = response.choices[0].message.content
        suggestion_text = content.strip() if content else 'No suggestion provided.'
        return AIAnalyzeResponse(suggestion=suggestion_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'AI analysis failed: {str(e)}')