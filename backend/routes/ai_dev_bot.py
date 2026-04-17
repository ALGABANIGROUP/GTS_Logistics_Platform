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
    prefix="/ai/devbot",
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


@router.get('/overview')
async def get_devbot_overview():
    """
    Get development bot maintenance overview with seed data
    """
    from datetime import datetime, timedelta
    import random

    # Seed system health data
    system_health = {
        "memory": random.randint(45, 85),
        "cpu": random.randint(20, 70),
        "disk": random.randint(30, 90),
        "network": random.randint(10, 50),
        "uptime": "7d 14h 32m",
        "last_backup": (datetime.now() - timedelta(hours=random.randint(1, 24))).isoformat(),
        "active_connections": random.randint(5, 25)
    }

    # Seed performance data
    performance = [
        {"timestamp": (datetime.now() - timedelta(minutes=i*5)).isoformat(), "response_time": random.randint(50, 200), "throughput": random.randint(10, 50)}
        for i in range(20)
    ]

    # Seed logs
    log_types = ["INFO", "WARNING", "ERROR", "DEBUG"]
    log_messages = [
        "Memory optimization completed",
        "Database connection pool refreshed",
        "Cache invalidation triggered",
        "Background task completed",
        "API rate limit check passed",
        "Security scan completed",
        "Log rotation executed",
        "Health check passed"
    ]

    logs = [
        {
            "timestamp": (datetime.now() - timedelta(minutes=random.randint(1, 60))).isoformat(),
            "level": random.choice(log_types),
            "message": random.choice(log_messages),
            "source": random.choice(["system", "api", "database", "cache"])
        }
        for _ in range(10)
    ]

    # Seed suggestions
    suggestions = [
        {
            "id": f"sugg_{i+1}",
            "title": f"Optimization Suggestion {i+1}",
            "description": f"Consider implementing {random.choice(['caching', 'database indexing', 'async processing', 'memory pooling'])} to improve performance",
            "priority": random.choice(["high", "medium", "low"]),
            "estimated_impact": f"{random.randint(10, 40)}% improvement",
            "implementation_effort": random.choice(["low", "medium", "high"])
        }
        for i in range(5)
    ]

    # Seed bot status
    bot_status = {
        "active_bots": random.randint(8, 12),
        "idle_bots": random.randint(2, 5),
        "maintenance_mode": random.choice([True, False]),
        "last_maintenance": (datetime.now() - timedelta(hours=random.randint(1, 48))).isoformat(),
        "version": "2.1.4",
        "uptime_percentage": random.randint(95, 99)
    }

    return {
        "systemHealth": system_health,
        "performance": performance,
        "logs": logs,
        "suggestions": suggestions,
        "botStatus": bot_status
    }
