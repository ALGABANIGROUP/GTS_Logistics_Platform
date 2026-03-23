# backend/vizion_fallback_db.py
import os
import sqlite3
import time
from typing import Any, Dict, List

DB_DIR = os.path.join(os.getcwd(), "_vizion")
DB_PATH = os.path.join(DB_DIR, "vizion.db")

SCHEMA = """
PRAGMA journal_mode=WAL;

CREATE TABLE IF NOT EXISTS events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ts INTEGER NOT NULL,
  event TEXT NOT NULL,
  message TEXT DEFAULT '',
  extra_json TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS progress (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ts INTEGER NOT NULL,
  area TEXT NOT NULL,
  done INTEGER NOT NULL,
  total INTEGER NOT NULL,
  note TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS tasks (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  description TEXT DEFAULT '',
  category TEXT DEFAULT '',
  priority INTEGER DEFAULT 0,
  status TEXT DEFAULT 'open',   -- open | in_progress | done
  created_ts INTEGER NOT NULL,
  updated_ts INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS task_sessions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  task_id INTEGER NOT NULL,
  start_ts INTEGER NOT NULL,
  stop_ts INTEGER,
  FOREIGN KEY(task_id) REFERENCES tasks(id)
);

CREATE TABLE IF NOT EXISTS task_notes (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  task_id INTEGER NOT NULL,
  ts INTEGER NOT NULL,
  text TEXT NOT NULL,
  FOREIGN KEY(task_id) REFERENCES tasks(id)
);
"""


def _row_to_dict(row: sqlite3.Row) -> Dict[str, Any]:
    return {k: row[k] for k in row.keys()}


class VizionFallbackDB:
    def __init__(self, path: str) -> None:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self) -> None:
        with self.conn:
            self.conn.executescript(SCHEMA)

    # ---------- Generic helpers ----------
    def log_event(self, event: str, message: str = "", **kwargs) -> None:
        ts = int(time.time())
        extra_json = str(kwargs) if kwargs else ""
        with self.conn:
            self.conn.execute(
                "INSERT INTO events (ts, event, message, extra_json) VALUES (?,?,?,?)",
                (ts, event, message, extra_json),
            )

    def progress(self, area: str, done: int, total: int, note: str = "") -> Dict[str, Any]:
        ts = int(time.time())
        with self.conn:
            self.conn.execute(
                "INSERT INTO progress (ts, area, done, total, note) VALUES (?,?,?,?,?)",
                (ts, area, done, total, note),
            )
        return {"area": area, "done": done, "total": total, "note": note}

    def summary(self) -> Dict[str, Any]:
        cur = self.conn.cursor()
        # events count
        cur.execute("SELECT COUNT(*) AS c FROM events")
        ev = cur.fetchone()["c"]
        # progress last
        cur.execute("SELECT area, done, total, note, ts FROM progress ORDER BY id DESC LIMIT 5")
        prog = [_row_to_dict(r) for r in cur.fetchall()]
        # task stats
        cur.execute("SELECT status, COUNT(*) AS c FROM tasks GROUP BY status")
        st = {r["status"]: r["c"] for r in cur.fetchall()}
        return {"events": ev, "progress_recent": prog, "tasks_by_status": st}

    # ---------- Tasks API ----------
    def add_task(self, title: str, description: str = "", category: str = "", priority: int = 0) -> Dict[str, Any]:
        now = int(time.time())
        with self.conn:
            cur = self.conn.execute(
                """INSERT INTO tasks (title, description, category, priority, status, created_ts, updated_ts)
                   VALUES (?,?,?,?, 'open', ?, ?)""",
                (title, description, category, priority, now, now),
            )
            task_id = cur.lastrowid
        if task_id is None:
            raise RuntimeError("Failed to create task: lastrowid is None")
        return self.task_detail(task_id=task_id)

    def tasks(self) -> List[Dict[str, Any]]:
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM tasks ORDER BY id DESC")
        return [_row_to_dict(r) for r in cur.fetchall()]

    def list_tasks(self) -> List[Dict[str, Any]]:
        return self.tasks()

    def get_tasks(self) -> List[Dict[str, Any]]:
        return self.tasks()

    def task_detail(self, task_id: int) -> Dict[str, Any]:
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM tasks WHERE id=?", (task_id,))
        row = cur.fetchone()
        if row is None:
            raise KeyError(f"Task {task_id} not found")
        return _row_to_dict(row)

    def start_session(self, task_id: int) -> Dict[str, Any]:
        now = int(time.time())
        with self.conn:
            self.conn.execute(
                "INSERT INTO task_sessions (task_id, start_ts) VALUES (?,?)",
                (task_id, now),
            )
            self.conn.execute(
                "UPDATE tasks SET status='in_progress', updated_ts=? WHERE id=?",
                (now, task_id),
            )
        return {"task_id": task_id, "started": now}

    def stop_session(self, task_id: int) -> Dict[str, Any]:
        now = int(time.time())
        with self.conn:
            # close latest open session
            self.conn.execute(
                """UPDATE task_sessions
                   SET stop_ts=?
                 WHERE id = (
                   SELECT id FROM task_sessions
                   WHERE task_id=? AND stop_ts IS NULL
                   ORDER BY id DESC LIMIT 1
                 )""",
                (now, task_id),
            )
            self.conn.execute(
                "UPDATE tasks SET updated_ts=? WHERE id=?",
                (now, task_id),
            )
        return {"task_id": task_id, "stopped": now}

    def complete_task(self, task_id: int) -> Dict[str, Any]:
        now = int(time.time())
        with self.conn:
            self.conn.execute(
                "UPDATE tasks SET status='done', updated_ts=? WHERE id=?",
                (now, task_id),
            )
        return self.task_detail(task_id=task_id)

    def reopen_task(self, task_id: int) -> Dict[str, Any]:
        now = int(time.time())
        with self.conn:
            self.conn.execute(
                "UPDATE tasks SET status='open', updated_ts=? WHERE id=?",
                (now, task_id),
            )
        return self.task_detail(task_id=task_id)

    def add_note(self, task_id: int, text: str) -> Dict[str, Any]:
        now = int(time.time())
        with self.conn:
            self.conn.execute(
                "INSERT INTO task_notes (task_id, ts, text) VALUES (?,?,?)",
                (task_id, now, text),
            )
        return {"task_id": task_id, "ts": now, "text": text}


# public entry used by main.py
def connect() -> VizionFallbackDB:
    return VizionFallbackDB(DB_PATH)
