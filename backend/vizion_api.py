# vizion_api.py
import asyncio
import os
import json
from datetime import datetime
from typing import Optional, List, Dict, Any, AsyncGenerator

from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body
from pydantic import BaseModel, Field

from sqlalchemy import String, Text, Integer, ForeignKey, select, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

# Import Base and models from vizion_models
from backend.vizion_models import Base, Task, TaskSession as Session, TaskNote as Note, TaskEvent as Event

_vizion_schema_ready = False
_vizion_schema_lock = asyncio.Lock()

# public initializer to be called from main.py
async def init_vizion():
    try:
        # Use main database initialization
        from backend.config import init_db
        await init_db()
    except Exception as e:
        # Fallback: try to initialize database directly
        from backend.vizion_models import Base
        from sqlalchemy.ext.asyncio import create_async_engine
        import os
        
        database_url = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./gts_logistics.db")
        engine = create_async_engine(database_url, echo=False)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    from backend.database.session import get_async_session
    async for session in get_async_session():
        yield session


async def ensure_vizion_schema() -> None:
    global _vizion_schema_ready

    if _vizion_schema_ready:
        return

    async with _vizion_schema_lock:
        if _vizion_schema_ready:
            return

        from backend.database.session import async_session_maker

        maker = async_session_maker()
        engine = maker.kw.get("bind")
        if engine is None:
            raise RuntimeError("VIZION database engine is unavailable")

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        _vizion_schema_ready = True


def now_iso() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat()

# -----------------------------------------------------------------------------
# Helpers (time/ETA/spent)
# -----------------------------------------------------------------------------
async def has_running_session(db: AsyncSession, task_id: int) -> bool:
    q = select(Session.id).where(Session.task_id == task_id, Session.end_ts.is_(None)).limit(1)
    r = await db.execute(q)
    return r.scalar_one_or_none() is not None

async def spent_minutes(db: AsyncSession, task_id: int) -> int:
    # ended sessions
    q1 = select(func.coalesce(func.sum(Session.duration_minutes), 0)).where(
        Session.task_id == task_id, Session.duration_minutes.is_not(None)
    )
    ended_sum = int((await db.execute(q1)).scalar_one() or 0)

    # running sessions -> add (now - start)
    q2 = select(Session.start_ts).where(Session.task_id == task_id, Session.end_ts.is_(None))
    rows = (await db.execute(q2)).all()
    add_running = 0
    now = datetime.utcnow()
    for (start_iso,) in rows:
        try:
            start = datetime.fromisoformat(start_iso)
        except Exception:
            continue
        delta = now - start
        add_running += int(delta.total_seconds() // 60)
    return ended_sum + add_running

async def category_avg_minutes(db: AsyncSession, category: str) -> Optional[int]:
    # avg of total spent for DONE tasks in same category
    # derive total spent using ended sessions only
    # (simple way: compute per task in SQL)
    sub = select(
        Task.id.label("tid"),
        func.coalesce(func.sum(Session.duration_minutes), 0).label("spent")
    ).join(Session, Session.task_id == Task.id, isouter=True).where(
        Task.category == category,
        Task.status == "done"
    ).group_by(Task.id).subquery()

    q = select(func.avg(sub.c.spent))
    val = (await db.execute(q)).scalar_one_or_none()
    return int(val) if val is not None else None

async def eta_minutes(db: AsyncSession, task: Task) -> Optional[int]:
    spent = await spent_minutes(db, task.id)
    if task.expected_minutes is not None:
        return max(task.expected_minutes - spent, 0)
    if task.category:
        avg_m = await category_avg_minutes(db, task.category)
        if avg_m is not None:
            return max(avg_m - spent, 0)
    return None

async def emit_event(db: AsyncSession, event: str, message: str = "", meta: Optional[Dict[str, Any]] = None):
    ev = Event(ts=now_iso(), event=event, message=message, meta_json=json.dumps(meta or {}))
    db.add(ev)
    await db.commit()

def task_to_dict(raw: Task, status_display: Optional[str] = None, spent_min: Optional[int] = None,
                 eta_min: Optional[int] = None) -> Dict[str, Any]:
    return {
        "id": raw.id,
        "title": raw.title,
        "status": status_display or raw.status,
        "priority": raw.priority,
        "category": raw.category,
        "eta_min": eta_min,
        "spent_min": spent_min,
        "updated_at": raw.updated_at,
        "due_ts": raw.due_ts,
    }

# -----------------------------------------------------------------------------
# Schemas
# -----------------------------------------------------------------------------
class CreateTaskIn(BaseModel):
    title: str
    category: str | None = ""
    priority: int = 3
    description: str | None = ""
    expected: int | None = Field(None, description="Expected minutes (optional)")
    due_ts: str | None = None

class NoteIn(BaseModel):
    text: str

class EventsOut(BaseModel):
    ts: str
    event: str
    message: str | None = ""
    meta: Dict[str, Any] = {}

# -----------------------------------------------------------------------------
# Router
# -----------------------------------------------------------------------------
router = APIRouter(tags=["vizion"])

@router.get("/board")
async def viz_board(
    category: str | None = Query(None),
    order: str = Query("priority", pattern="^(priority|updated|due)$"),
    include_eta: bool = Query(True),
    db: AsyncSession = Depends(get_db),
):
    await ensure_vizion_schema()
    # fetch tasks
    q = select(Task)
    if category:
        q = q.where(Task.category == category)
    match order:
        case "updated":
            q = q.order_by(Task.updated_at.desc())
        case "due":
            q = q.order_by(Task.due_ts.is_(None)).order_by(Task.due_ts.asc())
        case _:
            q = q.order_by(Task.priority.asc(), Task.updated_at.desc())
    tasks = (await db.execute(q)).scalars().all()

    board: Dict[str, List[Dict[str, Any]]] = {"todo": [], "in_progress": [], "done": []}
    counts = {"open": 0, "in_progress": 0, "done": 0, "spent_minutes": 0}

    for t in tasks:
        running = await has_running_session(db, t.id)
        disp_status = "in_progress" if running else t.status
        sp = await spent_minutes(db, t.id)
        counts["spent_minutes"] += sp
        et = await eta_minutes(db, t) if include_eta else None
        item = task_to_dict(t, status_display=disp_status, spent_min=sp, eta_min=et)
        if disp_status == "done":
            board["done"].append(item)
            counts["done"] += 1
        elif disp_status == "in_progress":
            board["in_progress"].append(item)
            counts["in_progress"] += 1
        else:
            board["todo"].append(item)
            counts["open"] += 1

    return {"board": board, "counts": counts, "generated_at": now_iso()}

@router.get("/summary")
async def viz_summary(db: AsyncSession = Depends(get_db)):
    await ensure_vizion_schema()
    q = select(Task)
    tasks = (await db.execute(q)).scalars().all()
    open_c = 0
    done_c = 0
    inprog_c = 0
    spent_total = 0
    for t in tasks:
        running = await has_running_session(db, t.id)
        if t.status == "done":
            done_c += 1
        elif running:
            inprog_c += 1
        else:
            open_c += 1
        spent_total += await spent_minutes(db, t.id)
    return {"summary": {"open": open_c, "in_progress": inprog_c, "done": done_c, "spent_minutes": spent_total}}

@router.get("/events")
async def viz_events(limit: int = Query(50, ge=1, le=500), db: AsyncSession = Depends(get_db)):
    await ensure_vizion_schema()
    q = select(Event).order_by(Event.id.desc()).limit(limit)
    rows = (await db.execute(q)).scalars().all()
    out: List[EventsOut] = []
    for r in rows:
        try:
            meta = json.loads(r.meta_json or "{}")
        except Exception:
            meta = {}
        out.append(EventsOut(ts=r.ts, event=r.event, message=r.message, meta=meta))
    return {"events": out}

@router.post("/tasks")
async def viz_create_task(payload: CreateTaskIn, db: AsyncSession = Depends(get_db)):
    await ensure_vizion_schema()
    t = Task(
        title=payload.title.strip(),
        description=(payload.description or "").strip(),
        category=(payload.category or "").strip(),
        priority=int(payload.priority),
        expected_minutes=payload.expected,
        status="open",
        created_at=now_iso(),
        updated_at=now_iso(),
        due_ts=payload.due_ts,
    )
    db.add(t)
    await db.commit()
    await db.refresh(t)
    await emit_event(db, "task.created", t.title, {"task_id": t.id})
    return task_to_dict(t, status_display=t.status, spent_min=0, eta_min=payload.expected)

@router.post("/tasks/{task_id}/start")
async def viz_start_task(task_id: int = Path(..., ge=1), db: AsyncSession = Depends(get_db)):
    await ensure_vizion_schema()
    t = (await db.execute(select(Task).where(Task.id == task_id))).scalar_one_or_none()
    if not t:
        raise HTTPException(404, "Task not found")
    # if there is already a running session for this task, ignore
    if await has_running_session(db, task_id):
        return {"status": "already_running"}
    s = Session(task_id=task_id, start_ts=now_iso(), end_ts=None, duration_minutes=None, note="")
    db.add(s)
    t.updated_at = now_iso()
    await db.commit()
    await emit_event(db, "task.started", t.title, {"task_id": t.id})
    return {"status": "started"}

@router.post("/tasks/{task_id}/stop")
async def viz_stop_task(task_id: int = Path(..., ge=1), db: AsyncSession = Depends(get_db)):
    await ensure_vizion_schema()
    t = (await db.execute(select(Task).where(Task.id == task_id))).scalar_one_or_none()
    if not t:
        raise HTTPException(404, "Task not found")
    s = (await db.execute(
        select(Session).where(Session.task_id == task_id, Session.end_ts.is_(None)).order_by(Session.id.desc()).limit(1)
    )).scalar_one_or_none()
    if not s:
        return {"status": "no_running"}
    # close it
    end = datetime.utcnow()
    start = datetime.fromisoformat(s.start_ts)
    dur = max(int((end - start).total_seconds() // 60), 0)
    s.end_ts = end.replace(microsecond=0).isoformat()
    s.duration_minutes = dur
    t.updated_at = now_iso()
    await db.commit()
    await emit_event(db, "task.stopped", t.title, {"task_id": t.id, "duration_min": dur})
    return {"status": "stopped", "duration_min": dur}

@router.post("/tasks/{task_id}/done")
async def viz_done_task(task_id: int = Path(..., ge=1), db: AsyncSession = Depends(get_db)):
    await ensure_vizion_schema()
    t = (await db.execute(select(Task).where(Task.id == task_id))).scalar_one_or_none()
    if not t:
        raise HTTPException(404, "Task not found")
    t.status = "done"
    t.updated_at = now_iso()
    await db.commit()
    await emit_event(db, "task.completed", t.title, {"task_id": t.id})
    return {"status": "done"}

# fallback path the frontend may call if /done returns 404/405
@router.post("/tasks/{task_id}/complete")
async def viz_complete_task(task_id: int = Path(..., ge=1), db: AsyncSession = Depends(get_db)):
    return await viz_done_task(task_id, db)

@router.post("/tasks/{task_id}/reopen")
async def viz_reopen_task(task_id: int = Path(..., ge=1), db: AsyncSession = Depends(get_db)):
    await ensure_vizion_schema()
    t = (await db.execute(select(Task).where(Task.id == task_id))).scalar_one_or_none()
    if not t:
        raise HTTPException(404, "Task not found")
    t.status = "open"
    t.updated_at = now_iso()
    await db.commit()
    await emit_event(db, "task.reopened", t.title, {"task_id": t.id})
    return {"status": "reopened"}

@router.post("/tasks/{task_id}/notes")
async def viz_add_note(task_id: int, payload: NoteIn, db: AsyncSession = Depends(get_db)):
    await ensure_vizion_schema()
    t = (await db.execute(select(Task).where(Task.id == task_id))).scalar_one_or_none()
    if not t:
        raise HTTPException(404, "Task not found")
    n = Note(task_id=task_id, ts=now_iso(), text=(payload.text or "").strip())
    db.add(n)
    t.updated_at = now_iso()
    await db.commit()
    await emit_event(db, "task.note", t.title, {"task_id": t.id, "text": payload.text})
    return {"status": "noted"}
