# main.py  -- The VIZION Backend (DB-backed, ASCII-only)
from __future__ import annotations

import os
import json
import shutil
from typing import List, Dict

from fastapi import FastAPI, UploadFile, File, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse, Response
from pydantic import BaseModel
from dotenv import load_dotenv
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete

import httpx

# --- our app deps / models
from dependencies import get_db, init_db
from models import PerformanceLog, PublishLog, VizionEvent  # NEW: VizionEvent

# --- optional file watcher
try:
    from utils.file_watch import start_file_watcher  # NEW
except Exception:  # pragma: no cover
    start_file_watcher = None

# -----------------------------
# Boot
# -----------------------------
load_dotenv()

APP_TITLE = os.getenv("APP_TITLE", "The VIZION Backend")
APP_VERSION = os.getenv("APP_VERSION", "0.2.0")
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173",
).split(",")

app = FastAPI(title=APP_TITLE, version=APP_VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in ALLOWED_ORIGINS if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Pydantic DTOs
# -----------------------------
class ProjectInput(BaseModel):
    project_name: str

class IntelInput(BaseModel):
    project_name: str
    competitors: List[str]

class LinkInput(BaseModel):
    platform: str
    url: str

class EngagementInput(BaseModel):
    platform: str
    url: str
    tone: str = "bold"

class AutoPublishInput(BaseModel):
    project_name: str
    content_text: str
    platforms: List[str]

class PerformanceLogIn(BaseModel):
    project_name: str
    platform: str
    likes: int
    comments: int
    shares: int
    views: int
    engagement_score: float
    timestamp: str | None = None  # optional ISO string

class PublishLogIn(BaseModel):
    project_name: str
    platform: str
    status: str = "posted"
    preview_link: str = ""
    note: str = ""

# NEW: simple event input for generic events (file change, etc.)
class LogEventIn(BaseModel):
    event: str
    message: str = ""
    meta: dict | None = None


# -----------------------------
# AI helpers
# -----------------------------
def _use_openai() -> bool:
    return bool(os.getenv("OPENAI_API_KEY"))

def _ai_reply(prompt: str, max_tokens: int = 300) -> str:
    if not _use_openai():
        return "[AI disabled] " + prompt.strip()[:120] + " ..."
    try:
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        model = os.getenv("VIZION_OPENAI_MODEL", "gpt-4o-mini")
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
        )
        return (resp.choices[0].message.content or "").strip()
    except Exception as e:
        return f"[AI error] {e}"


# -----------------------------
# Startup: create tables + start watchers
# -----------------------------
@app.on_event("startup")
async def _startup():
    await init_db()

    # optional local file watcher (guarded by env + try/except)
    if os.getenv("VIZION_EYE_ENABLE", "1").lower() not in ("0", "false", "no"):
        if start_file_watcher:
            try:
                # watcher can read its own env; call bare or with root if supported
                root = os.getenv("VIZION_EYE_PATH") or os.getcwd()
                try:
                    # prefer signature with root if available
                    start_file_watcher(root)  # type: ignore[arg-type]
                except TypeError:
                    start_file_watcher()  # fallback to no-arg
            except Exception as e:  # pragma: no cover
                print(f"[vizion] file watcher not started: {e}")


# -----------------------------
# Root, favicon, health
# -----------------------------
@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs", status_code=307)

@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return Response(status_code=204)

@app.get("/health")
def health():
    return {"ok": True, "service": APP_TITLE}


# -----------------------------
# Content & Intel
# -----------------------------
@app.post("/generate-content")
def generate_content(data: ProjectInput) -> Dict[str, str]:
    prompt = (
        f"Write a short catchy marketing slogan (2-3 lines) for an AI-powered product named '{data.project_name}'. "
        f"Make it modern and creative."
    )
    msg = _ai_reply(prompt, max_tokens=120)
    return {"message": msg}

@app.post("/analyze-competitors")
def analyze_competitors(data: IntelInput) -> Dict[str, str]:
    comp = ", ".join(data.competitors)
    prompt = (
        f"Analyze competitive landscape for project '{data.project_name}'. "
        f"Competitors: {comp}. Provide insights and suggestions to outperform them."
    )
    report = _ai_reply(prompt, max_tokens=350)
    return {"report": report}

@app.post("/analyze-link")
def analyze_link(data: LinkInput) -> Dict[str, str]:
    prompt = (
        f"Analyze this {data.platform} link: {data.url}. "
        f"Estimate audience type, engagement, and give 3 marketing tips to boost performance."
    )
    analysis = _ai_reply(prompt, max_tokens=220)
    return {"analysis": analysis}

@app.post("/engage-link")
def engage_link(data: EngagementInput) -> Dict[str, str]:
    prompt = (
        f"You are a growth strategist. Analyze {data.platform} content: {data.url}. "
        f"Return: 1) one bold comment idea, 2) best interaction time, 3) suggested hashtags. "
        f"Use smart marketing language. Tone: {data.tone}."
    )
    plan = _ai_reply(prompt, max_tokens=300)
    return {"engagement_plan": plan}


# -----------------------------
# Uploads
# -----------------------------
@app.post("/upload-media")
def upload_media(file: UploadFile = File(...)):
    try:
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return {"status": "uploaded", "filename": file.filename, "path": file_path}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"upload failed: {e}"})


# -----------------------------
# Logs (DB)
# -----------------------------
@app.post("/log-performance")
async def log_performance(data: PerformanceLogIn, db: AsyncSession = Depends(get_db)):
    row = PerformanceLog(
        project_name=data.project_name,
        platform=data.platform,
        likes=data.likes,
        comments=data.comments,
        shares=data.shares,
        views=data.views,
        engagement_score=data.engagement_score,
    )
    db.add(row)
    await db.commit()
    return {"status": "logged"}

@app.get("/logs")
async def get_logs(limit: int = Query(20, ge=1, le=200), db: AsyncSession = Depends(get_db)):
    q = (
        select(PerformanceLog)
        .order_by(PerformanceLog.timestamp.desc(), PerformanceLog.id.desc())
        .limit(limit)
    )
    rows = (await db.execute(q)).scalars().all()
    items = [
        {
            "id": r.id,
            "project_name": r.project_name,
            "platform": r.platform,
            "likes": r.likes,
            "comments": r.comments,
            "shares": r.shares,
            "views": r.views,
            "engagement_score": r.engagement_score,
            "timestamp": r.timestamp.isoformat() if r.timestamp else None,
        }
        for r in rows
    ]
    return {"count": len(items), "items": items}


# -----------------------------
# Alerts (DB)
# -----------------------------
@app.get("/generate-alerts")
async def generate_alerts(db: AsyncSession = Depends(get_db)) -> Dict[str, List[str]]:
    q = select(PerformanceLog).order_by(PerformanceLog.timestamp.desc()).limit(200)
    logs = (await db.execute(q)).scalars().all()

    alerts: List[str] = []
    for log in logs:
        if log.views == 0:
            alerts.append(f"No views on {log.platform}. Check the post or tracking.")
        elif log.engagement_score < 2:
            alerts.append(f"Low engagement on {log.platform} - only {log.engagement_score:.2f}%.")
        elif log.likes > 100 and log.shares > 20:
            alerts.append(f"Great traction on {log.platform}! Consider boosting this post.")
        elif log.comments > 50:
            alerts.append(f"High comment activity on {log.platform} - Engage with your audience!")

    if not alerts:
        alerts.append("All platforms are within normal performance range.")
    return {"alerts": alerts}

@app.get("/analyze-performance")
async def analyze_performance_insights(db: AsyncSession = Depends(get_db)):
    q = select(PerformanceLog).order_by(PerformanceLog.timestamp.desc()).limit(100)
    logs = (await db.execute(q)).scalars().all()

    if not logs:
        return {"insights": "No performance data available yet."}

    best = max(logs, key=lambda x: x.engagement_score)
    totals = (await db.execute(
        select(
            func.sum(PerformanceLog.views),
            func.sum(PerformanceLog.likes),
            func.sum(PerformanceLog.comments),
            func.sum(PerformanceLog.shares),
        )
    )).one()

    total_views, total_likes, total_comments, total_shares = [int(t or 0) for t in totals]

    heuristics = (
        f"Best platform by engagement: {best.platform} ({best.engagement_score:.2f}%). "
        f"Totals - Views: {total_views}, Likes: {total_likes}, Comments: {total_comments}, Shares: {total_shares}."
    )

    if _use_openai():
        context = "Recent logs:\n" + "\n".join(
            f"- {l.project_name} on {l.platform} | Likes:{l.likes} Comments:{l.comments} Shares:{l.shares} "
            f"Views:{l.views} Engagement:{l.engagement_score:.2f}%"
            for l in logs[:10]
        )
        prompt = (
            "Analyze the following social media performance logs and give strategic insights. "
            "Suggest which platform is performing best, which type of engagement is strongest, "
            "and how to improve weak areas.\n\n" + context
        )
        ai = _ai_reply(prompt, max_tokens=300)
        return {"insights": ai, "summary": heuristics}

    return {"insights": heuristics}


# -----------------------------
# Publish logs (DB)
# -----------------------------
@app.post("/log-publish")
async def log_publish(data: PublishLogIn, db: AsyncSession = Depends(get_db)):
    row = PublishLog(
        project_name=data.project_name,
        platform=data.platform,
        status=data.status,
        preview_link=data.preview_link,
        note=data.note,
    )
    db.add(row)
    await db.commit()
    return {"status": "publish-logged"}

@app.get("/publish-logs")
async def get_publish_logs(limit: int = Query(50, ge=1, le=500), db: AsyncSession = Depends(get_db)):
    q = (
        select(PublishLog)
        .order_by(PublishLog.timestamp.desc(), PublishLog.id.desc())
        .limit(limit)
    )
    rows = (await db.execute(q)).scalars().all()
    items = [
        {
            "id": r.id,
            "project_name": r.project_name,
            "platform": r.platform,
            "status": r.status,
            "preview_link": r.preview_link,
            "note": r.note,
            "timestamp": r.timestamp.isoformat() if r.timestamp else None,
        }
        for r in rows
    ]
    return {"count": len(items), "items": items}


# -----------------------------
# Auto publish (mock) -> logs to DB
# -----------------------------
@app.post("/auto-publish")
def auto_publish(data: AutoPublishInput) -> List[Dict[str, str]]:
    results: List[Dict[str, str]] = []

    def publish_to(platform: str) -> Dict[str, str]:
        item = {
            "project_name": data.project_name,
            "platform": platform,
            "status": "posted",
            "preview_link": f"https://example.com/{platform.lower()}/content_id",
        }
        try:
            with httpx.Client(timeout=2.0) as client:
                client.post(
                    "http://127.0.0.1:8001/log-publish",
                    json={
                        "project_name": data.project_name,
                        "platform": platform,
                        "status": "posted",
                        "preview_link": item["preview_link"],
                        "note": "",
                    },
                )
        except Exception:
            item["status"] = "posted (log failed)"
        return item

    for p in data.platforms:
        results.append(publish_to(p))

    return results


# -----------------------------
# Admin: clear all logs (DEV ONLY)
# -----------------------------
@app.post("/admin/clear-logs")
async def admin_clear_logs(db: AsyncSession = Depends(get_db)):
    await db.execute(delete(PerformanceLog))
    await db.execute(delete(PublishLog))
    await db.commit()
    return {"status": "cleared"}


# -----------------------------
# Generic events: log endpoint (used by file watcher, etc.)
# -----------------------------
@app.post("/vizion/events/log")
async def vizion_events_log(data: LogEventIn, db: AsyncSession = Depends(get_db)):
    row = VizionEvent(
        event=data.event,
        message=data.message,
        meta=json.dumps(data.meta) if data.meta is not None else None,
    )
    db.add(row)
    await db.commit()
    return {"status": "ok"}


# -----------------------------
# The VIZION: mount local task manager API
# -----------------------------
from vizion_api import router as vizion_router, init_vizion  # NEW (already exists in your repo)
app.include_router(vizion_router)                              # exposes /vizion/* routes
app.add_event_handler("startup", init_vizion)                  # ensures vizion tables/init
