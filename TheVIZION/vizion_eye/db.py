# db.py
# SQLite schema: tasks/sessions/errors/estimates/events + FTS5 + triggers + generated columns
import sqlite3
import json
import os
import hashlib
from datetime import datetime, timezone
from . import DB_PATH

def iso_now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    # Enable useful extensions
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    conn.execute("PRAGMA temp_store=MEMORY;")
    conn.execute("PRAGMA cache_size=-40000;")  # ~40MB cache
    # JSON1 & FTS5 are included in modern SQLite builds used by Python
    return conn

SCHEMA = r"""
CREATE TABLE IF NOT EXISTS tasks (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    title             TEXT NOT NULL,
    description       TEXT DEFAULT '',
    category          TEXT DEFAULT '',
    priority          INTEGER DEFAULT 3,          -- 1=high,3=normal,5=low
    status            TEXT DEFAULT 'open',        -- open|in_progress|done
    expected_minutes  INTEGER,                    -- optional baseline ETA
    due_ts            TEXT,                       -- ISO timestamp
    metadata          TEXT DEFAULT '{}',          -- JSON
    notes             TEXT DEFAULT '',
    created_at        TEXT NOT NULL,
    updated_at        TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sessions (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id      INTEGER NOT NULL,
    start_ts     TEXT NOT NULL,
    stop_ts      TEXT,
    -- generated duration in minutes (when stop_ts exists)
    duration_min REAL GENERATED ALWAYS AS (
        CASE WHEN stop_ts IS NULL THEN NULL
             ELSE (julianday(stop_ts) - julianday(start_ts)) * 24.0 * 60.0
        END
    ) STORED,
    FOREIGN KEY(task_id) REFERENCES tasks(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS errors (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id  INTEGER NOT NULL,
    level    TEXT DEFAULT 'error',    -- info|warning|error|critical
    message  TEXT NOT NULL,
    ts       TEXT NOT NULL,
    FOREIGN KEY(task_id) REFERENCES tasks(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS estimates (
    task_id    INTEGER PRIMARY KEY,
    o          REAL NOT NULL,  -- optimistic
    m          REAL NOT NULL,  -- most likely
    p          REAL NOT NULL,  -- pessimistic
    pert_mean  REAL GENERATED ALWAYS AS ((o + 4.0*m + p) / 6.0) STORED,
    sigma      REAL GENERATED ALWAYS AS ((p - o) / 6.0) STORED,
    FOREIGN KEY(task_id) REFERENCES tasks(id) ON DELETE CASCADE
);

-- Event log with hash-chain for tamper-evidence
CREATE TABLE IF NOT EXISTS events (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    kind       TEXT NOT NULL,            -- created|completed|reopened|start|stop|error|note|open|close|custom
    task_id    INTEGER,
    meta       TEXT DEFAULT '{}',        -- JSON payload
    ts         TEXT NOT NULL,
    prev_hash  TEXT,
    event_hash TEXT
);

-- FTS for tasks text search (title/description/notes)
CREATE VIRTUAL TABLE IF NOT EXISTS tasks_fts USING fts5(
    title, description, notes, content='tasks', content_rowid='id'
);

-- Synchronize FTS on INSERT/UPDATE/DELETE
CREATE TRIGGER IF NOT EXISTS tasks_ai AFTER INSERT ON tasks BEGIN
    INSERT INTO tasks_fts(rowid, title, description, notes)
    VALUES (new.id, new.title, new.description, new.notes);
END;
CREATE TRIGGER IF NOT EXISTS tasks_au AFTER UPDATE ON tasks BEGIN
    INSERT INTO tasks_fts(tasks_fts, rowid, title, description, notes)
    VALUES('delete', old.id, old.title, old.description, old.notes);
    INSERT INTO tasks_fts(rowid, title, description, notes)
    VALUES (new.id, new.title, new.description, new.notes);
END;
CREATE TRIGGER IF NOT EXISTS tasks_ad AFTER DELETE ON tasks BEGIN
    INSERT INTO tasks_fts(tasks_fts, rowid, title, description, notes)
    VALUES('delete', old.id, old.title, old.description, old.notes);
END;

-- Touch task.updated_at on session insert/update & error insert
CREATE TRIGGER IF NOT EXISTS sessions_ai AFTER INSERT ON sessions BEGIN
    UPDATE tasks SET updated_at = strftime('%Y-%m-%dT%H:%M:%SZ','now') WHERE id = new.task_id;
END;
CREATE TRIGGER IF NOT EXISTS sessions_au AFTER UPDATE ON sessions BEGIN
    UPDATE tasks SET updated_at = strftime('%Y-%m-%dT%H:%M:%SZ','now') WHERE id = new.task_id;
END;
CREATE TRIGGER IF NOT EXISTS errors_ai AFTER INSERT ON errors BEGIN
    UPDATE tasks SET updated_at = strftime('%Y-%m-%dT%H:%M:%SZ','now') WHERE id = new.task_id;
END;
"""

def ensure_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with connect() as c:
        c.executescript(SCHEMA)

def _get_prev_hash(c):
    row = c.execute("SELECT event_hash FROM events ORDER BY id DESC LIMIT 1").fetchone()
    return row["event_hash"] if row and row["event_hash"] else None

def _compute_hash(prev_hash, kind, task_id, meta, ts):
    payload = json.dumps({"kind": kind, "task_id": task_id, "meta": meta, "ts": ts}, sort_keys=True)
    base = (prev_hash or "").encode("utf-8") + payload.encode("utf-8")
    return hashlib.sha256(base).hexdigest()

def log_event(kind, task_id=None, meta=None):
    ensure_db()
    meta = meta or {}
    ts = iso_now()
    with connect() as c:
        prev_hash = _get_prev_hash(c)
        h = _compute_hash(prev_hash, kind, task_id, meta, ts)
        c.execute("INSERT INTO events(kind, task_id, meta, ts, prev_hash, event_hash) VALUES (?,?,?,?,?,?)",
                  (kind, task_id, json.dumps(meta, ensure_ascii=False), ts, prev_hash, h))

# CRUD helpers (used by CLI/TUI)
def add_task(title, description="", category="", priority=3, expected_minutes=None, due_ts=None, metadata=None):
    ensure_db()
    ts = iso_now()
    with connect() as c:
        c.execute("""INSERT INTO tasks(title,description,category,priority,status,expected_minutes,due_ts,metadata,created_at,updated_at)
                     VALUES (?,?,?,?, 'open', ?, ?, ?, ?, ?)""",
                  (title, description, category, priority, expected_minutes, due_ts, json.dumps(metadata or {}), ts, ts))
        task_id = c.execute("SELECT last_insert_rowid() AS id").fetchone()["id"]
    log_event("created", task_id, {"title": title})
    return task_id

def set_due(task_id, due_ts):
    ensure_db()
    with connect() as c:
        c.execute("UPDATE tasks SET due_ts=?, updated_at=? WHERE id=?", (due_ts, iso_now(), task_id))
    log_event("due_set", task_id, {"due_ts": due_ts})

def set_estimate(task_id, o, m, p):
    ensure_db()
    with connect() as c:
        c.execute("INSERT INTO estimates(task_id,o,m,p) VALUES(?,?,?,?) ON CONFLICT(task_id) DO UPDATE SET o=excluded.o, m=excluded.m, p=excluded.p", (task_id, o, m, p))
    log_event("estimate_set", task_id, {"o": o, "m": m, "p": p})

def start_session(task_id):
    ensure_db()
    with connect() as c:
        run = c.execute("SELECT id FROM sessions WHERE task_id=? AND stop_ts IS NULL", (task_id,)).fetchone()
        if run: raise RuntimeError("Session already running for this task.")
        c.execute("INSERT INTO sessions(task_id,start_ts) VALUES (?,?)", (task_id, iso_now()))
        c.execute("UPDATE tasks SET status='in_progress', updated_at=? WHERE id=?", (iso_now(), task_id))
    log_event("start", task_id)

def stop_session(task_id):
    ensure_db()
    with connect() as c:
        sess = c.execute("SELECT * FROM sessions WHERE task_id=? AND stop_ts IS NULL ORDER BY id DESC LIMIT 1", (task_id,)).fetchone()
        if not sess: raise RuntimeError("No running session for this task.")
        c.execute("UPDATE sessions SET stop_ts=? WHERE id=?", (iso_now(), sess["id"]))
    log_event("stop", task_id)

def complete_task(task_id):
    ensure_db()
    with connect() as c:
        # close any running session
        sess = c.execute("SELECT id FROM sessions WHERE task_id=? AND stop_ts IS NULL", (task_id,)).fetchone()
        if sess:
            c.execute("UPDATE sessions SET stop_ts=? WHERE id=?", (iso_now(), sess["id"]))
        c.execute("UPDATE tasks SET status='done', updated_at=? WHERE id=?", (iso_now(), task_id))
    log_event("completed", task_id)

def reopen_task(task_id):
    ensure_db()
    with connect() as c:
        c.execute("UPDATE tasks SET status='open', updated_at=? WHERE id=?", (iso_now(), task_id))
    log_event("reopened", task_id)

def add_note(task_id, text):
    ensure_db()
    with connect() as c:
        cur = c.execute("SELECT notes FROM tasks WHERE id=?", (task_id,)).fetchone()
        old = (cur["notes"] or "") if cur else ""
        stamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
        new_notes = (old + f"\n[{stamp}] " + text).strip()
        c.execute("UPDATE tasks SET notes=?, updated_at=? WHERE id=?", (new_notes, iso_now(), task_id))
    log_event("note", task_id, {"text": text})

def log_error(task_id, level, message):
    ensure_db()
    with connect() as c:
        c.execute("INSERT INTO errors(task_id,level,message,ts) VALUES (?,?,?,?)", (task_id, level, message, iso_now()))
    log_event("error", task_id, {"level": level, "message": message})

def list_tasks(status=None, category=None):
    ensure_db()
    filters, params = [], []
    if status:
        filters.append("t.status=?"); params.append(status)
    if category:
        filters.append("t.category=?"); params.append(category)
    where = f"WHERE {' AND '.join(filters)}" if filters else ""
    q = f"""
    SELECT t.*,
           (SELECT IFNULL(SUM(duration_min),0) FROM sessions s WHERE s.task_id=t.id) AS spent_min,
           (SELECT pert_mean FROM estimates e WHERE e.task_id=t.id) AS pert_mean
    FROM tasks t {where}
    ORDER BY CASE t.status WHEN 'open' THEN 0 WHEN 'in_progress' THEN 1 ELSE 2 END,
             t.priority, t.created_at DESC
    """
    with connect() as c:
        return c.execute(q, params).fetchall()

def task_detail(task_id):
    ensure_db()
    with connect() as c:
        t = c.execute("""
            SELECT t.*,
                   (SELECT IFNULL(SUM(duration_min),0) FROM sessions s WHERE s.task_id=t.id) AS spent_min,
                   (SELECT pert_mean FROM estimates e WHERE e.task_id=t.id) AS pert_mean,
                   (SELECT sigma FROM estimates e WHERE e.task_id=t.id) AS sigma
            FROM tasks t WHERE t.id=?""", (task_id,)).fetchone()
        sessions = c.execute("SELECT * FROM sessions WHERE task_id=? ORDER BY id DESC LIMIT 20", (task_id,)).fetchall()
        errors = c.execute("SELECT * FROM errors WHERE task_id=? ORDER BY id DESC LIMIT 20", (task_id,)).fetchall()
    return t, sessions, errors

def search_tasks(query):
    ensure_db()
    with connect() as c:
        return c.execute("SELECT rowid AS id, title FROM tasks_fts WHERE tasks_fts MATCH ? ORDER BY rank", (query,)).fetchall()

def summary_counts():
    ensure_db()
    with connect() as c:
        r = c.execute("""SELECT
            SUM(CASE WHEN status='open' THEN 1 ELSE 0 END) AS open_cnt,
            SUM(CASE WHEN status='in_progress' THEN 1 ELSE 0 END) AS prog_cnt,
            SUM(CASE WHEN status='done' THEN 1 ELSE 0 END) AS done_cnt
        FROM tasks""").fetchone()
        spent = c.execute("SELECT IFNULL(SUM(duration_min),0) AS spent FROM sessions").fetchone()["spent"]
    return r, spent

def best_eta_minutes(row):
    # prefer PERT; else expected; else category average of done tasks
    if row["pert_mean"]:
        return float(row["pert_mean"])
    if row["expected_minutes"]:
        return float(row["expected_minutes"])
    # fallback by category
    with connect() as c:
        vals = c.execute("""
            SELECT IFNULL(SUM(duration_min),0) AS total
            FROM tasks tt
            JOIN sessions ss ON ss.task_id=tt.id
            WHERE tt.category=? AND tt.status='done'
            GROUP BY tt.id
        """, (row["category"],)).fetchall()
    arr = [float(v["total"]) for v in vals]
    return sum(arr)/len(arr) if arr else None
