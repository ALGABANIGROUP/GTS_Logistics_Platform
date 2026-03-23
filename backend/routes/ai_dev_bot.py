from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import os
from importlib import import_module
from importlib.util import find_spec
from dotenv import load_dotenv
from backend.utils.role_protected import RoleChecker

admin_or_manager_required = RoleChecker(["admin", "manager"])
load_dotenv()
router = APIRouter(
    prefix="/ai/dev_bot",
    tags=["AI Dev & Maintenance Bot"],
    dependencies=[Depends(admin_or_manager_required)],
)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("Missing OPENAI_API_KEY in environment")

if find_spec("openai") is None:
    raise RuntimeError("The `openai` package is required for /ai/dev_bot but is not installed.")

openai_module = import_module("openai")
client = openai_module.OpenAI(api_key=OPENAI_API_KEY)

class IssueInput(BaseModel):
    bot_name: str
    title: str
    description: str

class AIResponse(BaseModel):
    summary: str
    root_cause: str
    solution: str

async def analyze_with_ai(prompt: str) -> str:
    try:
        response = client.chat.completions.create(model='gpt-4', messages=[{'role': 'system', 'content': 'You are an expert software development assistant and bug fixer.'}, {'role': 'user', 'content': prompt}], max_tokens=500, temperature=0.7)
        content = response.choices[0].message.content
        return content.strip() if content else 'No structured response.'
    except Exception as e:
        print(f'❌ AI Error: {e}')
        raise HTTPException(status_code=500, detail='AI analysis failed')

@router.post('/analyze', response_model=AIResponse)
async def analyze_issue(issue: IssueInput):
    prompt = f'\nYou are the AI Dev & Maintenance Bot. Analyze the following issue and return a structured response with:\n1. Summary of the problem.\n2. Likely root cause.\n3. Suggested fix.\n\nBot Name: {issue.bot_name}\nTitle: {issue.title}\nDescription: {issue.description}\n'
    ai_output = await analyze_with_ai(prompt)
    lines = ai_output.splitlines()
    summary = next((line.replace('Summary:', '').strip() for line in lines if line.lower().startswith('summary')), 'N/A')
    root_cause = next((line.replace('Root cause:', '').strip() for line in lines if 'root' in line.lower()), 'N/A')
    solution = next((line.replace('Solution:', '').strip() for line in lines if 'solution' in line.lower()), 'N/A')
    return AIResponse(summary=summary, root_cause=root_cause, solution=solution)
