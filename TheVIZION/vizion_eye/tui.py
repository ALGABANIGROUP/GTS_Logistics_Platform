# tui.py
# Simple live dashboard (ANSI) + Flow mode + "deadline doppler" beeps on Windows where possible.
import os, time, shutil, math
from datetime import datetime, timezone
from . import db

def _clear():
    # ANSI clear (works on modern Windows terminals)
    print("\x1b[2J\x1b[H", end="")

def _width():
    try:
        return shutil.get_terminal_size().columns
    except:
        return 100

def _fmt_eta(spent, total):
    if total is None: return "-"
    rem = max(0.0, total - (spent or 0))
    return f"{int(rem)}m"

def _doppler(due_ts):
    if not due_ts: return None, None
    try:
        due = datetime.fromisoformat(due_ts.replace("Z","")).astimezone(timezone.utc)
    except:
        return None, None
    now = datetime.now(timezone.utc)
    delta_min = (due - now).total_seconds()/60.0
    if delta_min <= 0:
        return 0, "OVERDUE"
    # beep interval shortens as deadline approaches: from 90s .. to 5s
    interval = max(5.0, min(90.0, delta_min))
    return interval, f"{int(delta_min)}m to deadline"

def _beep():
    try:
        import winsound
        winsound.Beep(880, 120)  # pitch ms
    except Exception:
        print("\a", end="")  # fallback bell

def run_dashboard(refresh_sec=1.0):
    db.ensure_db()
    next_beep_by_task = {}
    flow_task = os.environ.get("VIZION_EYE_FLOW_TASK")

    while True:
        rows = db.list_tasks()
        rsum, spent_total = db.summary_counts()
        w = _width()
        _clear()
        print(" The VIZION — Live Ops Eye ".center(w, "═"))
        print(f"Open:{rsum['open_cnt'] or 0}  In-Progress:{rsum['prog_cnt'] or 0}  Done:{rsum['done_cnt'] or 0}   Spent:{int(spent_total or 0)}m")
        print("-"*w)
        print(f"{'ID':<4} {'Title':<30} {'Cat':<10} {'Pr':<2} {'Status':<12} {'Spent':<6} {'ETA(rem)':<9} {'Due':<16} {'Note':<20}")
        print("-"*w)

        now = time.time()
        for r in rows[:30]:  # show top 30
            eta_total = db.best_eta_minutes(r)
            eta_str = _fmt_eta(r["spent_min"], eta_total)
            due_str = (r["due_ts"] or "")[:16]
            note_hint = (r["notes"] or "").splitlines()[-1] if r["notes"] else ""
            title = (r["title"][:27] + "...") if len(r["title"])>30 else r["title"]
            note_short = (note_hint[:17] + "...") if len(note_hint)>20 else note_hint

            print(f"{r['id']:<4} {title:<30} {r['category'][:10]:<10} {r['priority']:<2} {r['status']:<12} {int(r['spent_min'] or 0):<6} {eta_str:<9} {due_str:<16} {note_short:<20}")

            # Doppler: schedule beeps as deadline approaches
            interval, label = _doppler(r["due_ts"])
            if interval:
                due_key = f"{r['id']}"
                last = next_beep_by_task.get(due_key, 0)
                if now >= last:
                    _beep()
                    next_beep_by_task[due_key] = now + interval

        print("-"*w)
        if flow_task:
            print(f"FLOW MODE: Task #{flow_task} — distractions off, micro-breaks every 25m")

        time.sleep(refresh_sec)
