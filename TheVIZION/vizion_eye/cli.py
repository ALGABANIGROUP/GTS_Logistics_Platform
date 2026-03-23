# cli.py
# Commands: add/list/start/stop/done/reopen/note/err/estimate/due/summary/export/search/dashboard/flow
import argparse, os, csv, sys
from . import db
from .tui import run_dashboard

def _print_list(rows):
    print(f"{'ID':<4} {'Title':<30} {'Cat':<10} {'Pr':<2} {'Status':<12} {'Spent':<6} {'ETA(total)':<10} {'Due':<16}")
    print("-"*100)
    for r in rows:
        eta_total = db.best_eta_minutes(r)
        eta_total_str = f"{int(eta_total)}m" if eta_total is not None else "-"
        print(f"{r['id']:<4} {r['title'][:30]:<30} {r['category'][:10]:<10} {r['priority']:<2} {r['status']:<12} {int(r['spent_min'] or 0):<6} {eta_total_str:<10} {(r['due_ts'] or '')[:16]:<16}")

def cmd_add(a):
    task_id = db.add_task(a.title, a.description, a.category, a.priority, a.expected, a.due)
    print(f"✅ Task #{task_id} created")

def cmd_list(a):
    rows = db.list_tasks(a.status, a.category)
    _print_list(rows)

def cmd_start(a):
    db.start_session(a.id)
    print(f"▶️ Started task #{a.id}")

def cmd_stop(a):
    db.stop_session(a.id)
    print(f"⏹️ Stopped task #{a.id}")

def cmd_done(a):
    db.complete_task(a.id)
    print(f"✅ Completed task #{a.id}")

def cmd_reopen(a):
    db.reopen_task(a.id)
    print(f"↩️ Reopened task #{a.id}")

def cmd_note(a):
    db.add_note(a.id, a.text)
    print(f"📝 Note added to task #{a.id}")

def cmd_err(a):
    db.log_error(a.id, a.level, a.message)
    print(f"⚠️ Error logged for task #{a.id} [{a.level}]")

def cmd_estimate(a):
    db.set_estimate(a.id, a.o, a.m, a.p)
    print(f"📐 PERT set for task #{a.id} (o={a.o}, m={a.m}, p={a.p})")

def cmd_due(a):
    db.set_due(a.id, a.due)
    print(f"⏰ Due set for task #{a.id}: {a.due}")

def cmd_summary(a):
    rsum, spent = db.summary_counts()
    print(f"Open:{rsum['open_cnt'] or 0}  In-Progress:{rsum['prog_cnt'] or 0}  Done:{rsum['done_cnt'] or 0}")
    print(f"Total minutes spent: {int(spent or 0)}")

def cmd_export(a):
    os.makedirs(a.outdir, exist_ok=True)
    # Export three tables + events
    with db.connect() as c:
        for name in ["tasks","sessions","errors","estimates","events"]:
            rows = c.execute(f"SELECT * FROM {name}").fetchall()
            path = os.path.join(a.outdir, f"{name}.csv")
            with open(path, "w", newline="", encoding="utf-8") as f:
                if rows:
                    w = csv.DictWriter(f, fieldnames=rows[0].keys())
                    w.writeheader()
                    for r in rows: w.writerow(dict(r))
            print(f"Exported {path}")

def cmd_search(a):
    rows = db.search_tasks(a.query)
    if not rows:
        print("No matches.")
        return
    for r in rows[:20]:
        print(f"#{r['id']}: {r['title']}")

def cmd_dashboard(a):
    run_dashboard(refresh_sec=a.refresh)

def cmd_flow(a):
    if a.action == "start":
        os.environ["VIZION_EYE_FLOW_TASK"] = str(a.id)
        db.start_session(a.id)
        print(f"🌊 FLOW started on task #{a.id}. Micro-breaks suggested every 25 minutes.")
        print("Open another terminal and run: python -m vizion_eye.cli dashboard")
    elif a.action == "stop":
        tid = os.environ.pop("VIZION_EYE_FLOW_TASK", None)
        if a.id:
            db.stop_session(a.id)
            print(f"🌊 FLOW stopped on task #{a.id}.")
        elif tid:
            db.stop_session(int(tid))
            print(f"🌊 FLOW stopped on task #{tid}.")
        else:
            print("No flow task found.")

def build():
    p = argparse.ArgumentParser(prog="vizion-eye", description="The VIZION — Local Ops Eye")
    sub = p.add_subparsers(dest="cmd")

    s = sub.add_parser("add");
    s.add_argument("title");
    s.add_argument("-d","--description", default="")
    s.add_argument("-c","--category", default="")
    s.add_argument("-p","--priority", type=int, default=3)
    s.add_argument("-e","--expected", type=int, default=None)
    s.add_argument("--due", default=None, help='ISO date "YYYY-MM-DD HH:MM" or ISO8601')
    s.set_defaults(func=cmd_add)

    s = sub.add_parser("list")
    s.add_argument("-s","--status", choices=["open","in_progress","done"])
    s.add_argument("-c","--category")
    s.set_defaults(func=cmd_list)

    s = sub.add_parser("start"); s.add_argument("id", type=int); s.set_defaults(func=cmd_start)
    s = sub.add_parser("stop");  s.add_argument("id", type=int); s.set_defaults(func=cmd_stop)
    s = sub.add_parser("done");  s.add_argument("id", type=int); s.set_defaults(func=cmd_done)
    s = sub.add_parser("reopen"); s.add_argument("id", type=int); s.set_defaults(func=cmd_reopen)

    s = sub.add_parser("note"); s.add_argument("id", type=int); s.add_argument("text"); s.set_defaults(func=cmd_note)
    s = sub.add_parser("err"); s.add_argument("id", type=int); s.add_argument("--level", default="error", choices=["info","warning","error","critical"]); s.add_argument("--message", required=True); s.set_defaults(func=cmd_err)

    s = sub.add_parser("estimate"); s.add_argument("id", type=int); s.add_argument("--o", type=float, required=True); s.add_argument("--m", type=float, required=True); s.add_argument("--p", type=float, required=True); s.set_defaults(func=cmd_estimate)

    s = sub.add_parser("due"); s.add_argument("id", type=int); s.add_argument("due"); s.set_defaults(func=cmd_due)

    s = sub.add_parser("summary"); s.set_defaults(func=cmd_summary)
    s = sub.add_parser("export"); s.add_argument("-o","--outdir", default="./export"); s.set_defaults(func=cmd_export)

    s = sub.add_parser("search"); s.add_argument("query"); s.set_defaults(func=cmd_search)

    s = sub.add_parser("dashboard"); s.add_argument("-r","--refresh", type=float, default=1.0); s.set_defaults(func=cmd_dashboard)

    s = sub.add_parser("flow"); s.add_argument("action", choices=["start","stop"]); s.add_argument("id", type=int, nargs="?"); s.set_defaults(func=cmd_flow)
    return p

def main(argv=None):
    db.ensure_db()
    parser = build()
    args = parser.parse_args(argv)
    if not args.cmd:
        parser.print_help(); return
    args.func(args)

if __name__ == "__main__":
    main()
