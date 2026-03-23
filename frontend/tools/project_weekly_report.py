#!/usr/bin/env python3
# file: tools/project_weekly_report.py
# Python stdlib only. No external deps.
import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# -------- Utility --------
EXT_BUCKETS = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".css": "css",
    ".scss": "css",
    ".html": "html",
    ".md": "markdown",
    ".sql": "sql",
    ".yml": "yaml",
    ".yaml": "yaml",
    ".json": "json",
    ".ini": "config",
    ".env": "config",
}

FASTAPI_DECORATOR_RE = re.compile(r'@(?:router|app)\.(get|post|put|delete|patch)\(\s*["\']([^"\']+)["\']', re.IGNORECASE)
REACT_ROUTE_RE = re.compile(r'Route\s+path\s*=\s*["\']([^"\']+)["\']', re.IGNORECASE)
TODO_RE = re.compile(r'\b(TODO|FIXME|BUG|HACK)\b', re.IGNORECASE)

TEXT_EXTS = {".py",".js",".jsx",".ts",".tsx",".css",".scss",".html",".md",".sql",".yml",".yaml",".json",".ini",".env",".txt",".csv"}

def human_dt(ts: float) -> str:
    return dt.datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M")

def safe_rel(base: Path, p: Path) -> str:
    try:
        return str(p.relative_to(base))
    except Exception:
        return str(p)

def count_lines(path: Path) -> int:
    try:
        with path.open("r", encoding="utf-8", errors="ignore") as f:
            return sum(1 for _ in f)
    except Exception:
        return 0

def is_text_file(path: Path) -> bool:
    return path.suffix.lower() in TEXT_EXTS

def run_git(*args: str, cwd: Optional[Path]) -> Optional[str]:
    try:
        out = subprocess.check_output(["git", *args], cwd=str(cwd), stderr=subprocess.DEVNULL)
        return out.decode("utf-8", errors="ignore").strip()
    except Exception:
        return None

def collect_files(root: Path) -> List[Path]:
    files = []
    for p in root.rglob("*"):
        if p.is_file():
            files.append(p)
    return files

def since_filter(files: List[Path], since_days: int) -> List[Path]:
    if since_days <= 0:
        return files
    cutoff = dt.datetime.now().timestamp() - since_days * 86400
    return [p for p in files if p.stat().st_mtime >= cutoff]

def bucket_ext(ext: str) -> str:
    return EXT_BUCKETS.get(ext.lower(), ext.lower().lstrip(".") or "other")

# -------- Analyzers --------
def analyze_codebase(root: Path, label: str, since_days: int) -> Dict:
    all_files = collect_files(root)
    recent_files = since_filter(all_files, since_days)

    ext_counts = Counter()
    ext_lines = Counter()
    total_lines = 0
    text_files = [p for p in all_files if is_text_file(p)]

    for p in text_files:
        ext = p.suffix.lower()
        bucket = bucket_ext(ext)
        loc = count_lines(p)
        ext_counts[bucket] += 1
        ext_lines[bucket] += loc
        total_lines += loc

    # endpoints: FastAPI
    api_routes = []
    for p in [x for x in text_files if x.suffix.lower()==".py"]:
        try:
            content = p.read_text(encoding="utf-8", errors="ignore")
            for m in FASTAPI_DECORATOR_RE.finditer(content):
                method, path = m.group(1).upper(), m.group(2)
                api_routes.append({
                    "file": str(p),
                    "method": method,
                    "path": path
                })
        except Exception:
            pass

    # routes: React
    react_routes = []
    for p in [x for x in text_files if x.suffix.lower() in (".jsx",".tsx",".js",".ts")]:
        try:
            content = p.read_text(encoding="utf-8", errors="ignore")
            for m in REACT_ROUTE_RE.finditer(content):
                react_routes.append({
                    "file": str(p),
                    "path": m.group(1)
                })
        except Exception:
            pass

    # TODO/FIXME
    todos = []
    for p in text_files:
        try:
            for i, line in enumerate(p.read_text(encoding="utf-8", errors="ignore").splitlines(), start=1):
                if TODO_RE.search(line):
                    todos.append({"file": str(p), "line": i, "text": line.strip()[:200]})
        except Exception:
            pass

    # recent changes
    recent = []
    for p in recent_files:
        recent.append({
            "file": str(p),
            "modified": human_dt(p.stat().st_mtime),
            "size_kb": round(p.stat().st_size/1024, 1)
        })

    # git summary
    git_info = {}
    branch = run_git("rev-parse", "--abbrev-ref", "HEAD", cwd=root)
    last_commit = run_git("log", "-1", "--pretty=%h %ad %s", "--date=short", cwd=root)
    since_arg = f"--since={since_days}.days" if since_days>0 else None
    if since_arg:
        diffstat = run_git("log", since_arg, "--pretty=tformat:", "--numstat", cwd=root)
        commits = run_git("log", since_arg, "--pretty=%h %ad %s", "--date=short", cwd=root)
    else:
        diffstat = None
        commits = None

    if branch:
        git_info["branch"] = branch
    if last_commit:
        git_info["last_commit"] = last_commit
    if commits:
        git_info["recent_commits"] = commits.splitlines()[:50]
    if diffstat:
        # Sum added/removed
        adds, dels = 0, 0
        for line in diffstat.splitlines():
            parts = line.split()
            if len(parts) >= 2 and parts[0].isdigit() and parts[1].isdigit():
                adds += int(parts[0])
                dels += int(parts[1])
        git_info["diff_summary"] = {"added": adds, "deleted": dels}

    return {
        "label": label,
        "root": str(root),
        "files_total": len(all_files),
        "files_text": len(text_files),
        "ext_counts": dict(ext_counts),
        "ext_lines": dict(ext_lines),
        "total_lines": total_lines,
        "api_routes": api_routes,
        "react_routes": react_routes,
        "todos": todos,
        "recent_files": sorted(recent, key=lambda x: x["modified"], reverse=True)[:200],
        "git": git_info
    }

def make_markdown(front: Optional[Dict], back: Optional[Dict], since_days: int) -> str:
    now = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    def section_title(t): return f"## {t}\n"

    def codeblock(lang, text):
        return f"```{lang}\n{text}\n```\n"

    def summarize_side(side: Dict) -> str:
        lines = []
        lines.append(f"**Path:** `{side['root']}`")
        lines.append(f"**Files (total/text):** {side['files_total']} / {side['files_text']}")
        lines.append(f"**Total Lines:** {side['total_lines']:,}")
        if side.get("git"):
            g = side["git"]
            if "branch" in g:
                lines.append(f"**Git Branch:** {g['branch']}")
            if "last_commit" in g:
                lines.append(f"**Last Commit:** {g['last_commit']}")
        lines.append("\n**By Language/Type (files / lines):**")
        if side["ext_counts"]:
            rows = []
            for k in sorted(side["ext_counts"].keys()):
                rows.append(f"- {k}: {side['ext_counts'][k]} files / {side['ext_lines'].get(k,0):,} lines")
            lines.extend(rows)
        return "\n".join(lines)

    def list_recent(side: Dict) -> str:
        rows = []
        for x in side["recent_files"][:50]:
            rows.append(f"- `{x['file']}` — {x['modified']} ({x['size_kb']} KB)")
        return "\n".join(rows) if rows else "_No recent file changes found_"

    def list_api(side: Dict) -> str:
        # deduplicate by method+path
        seen = set()
        rows = []
        for r in side["api_routes"]:
            key = (r["method"], r["path"])
            if key in seen:
                continue
            seen.add(key)
            rows.append(f"- **{r['method']}** `{r['path']}`  _(in {r['file']})_")
        return "\n".join(rows) if rows else "_No FastAPI routes found_"

    def list_react(side: Dict) -> str:
        # unique paths
        seen = set()
        rows = []
        for r in side["react_routes"]:
            if r["path"] in seen:
                continue
            seen.add(r["path"])
            rows.append(f"- `{r['path']}`  _(in {r['file']})_")
        return "\n".join(rows) if rows else "_No React routes found_"

    def list_todos(side: Dict) -> str:
        rows = []
        for t in side["todos"][:100]:
            rows.append(f"- `{t['file']}`:{t['line']} — {t['text']}")
        return "\n".join(rows) if rows else "_No TODO/FIXME markers found_"

    md = []
    md.append(f"# Weekly Project Report")
    md.append(f"_Generated: {now} (window: last {since_days} days)_\n")

    if front:
        md.append(section_title("Frontend Summary"))
        md.append(summarize_side(front))
        md.append("\n### Frontend Routes (React Router)\n")
        md.append(list_react(front))
        md.append("\n### Frontend Recent Changes\n")
        md.append(list_recent(front))
        md.append("\n### Frontend TODO/FIXME\n")
        md.append(list_todos(front))

    if back:
        md.append(section_title("Backend Summary"))
        md.append(summarize_side(back))
        md.append("\n### API Endpoints (FastAPI)\n")
        md.append(list_api(back))
        md.append("\n### Backend Recent Changes\n")
        md.append(list_recent(back))
        md.append("\n### Backend TODO/FIXME\n")
        md.append(list_todos(back))

    # Combined quick tasks
    md.append("\n## Suggested Next Actions")
    suggestions = []
    if front and len(front["react_routes"]) == 0:
        suggestions.append("- Detect and register routes in `App.jsx` or routing config.")
    if back and len(back["api_routes"]) == 0:
        suggestions.append("- Verify FastAPI routers and ensure decorators `@router.get/post/...` are used.")
    if back and back.get("git", {}).get("diff_summary"):
        ds = back["git"]["diff_summary"]
        suggestions.append(f"- Review backend code churn (added: {ds['added']:,}, deleted: {ds['deleted']:,}) this window.")
    if front and front.get("git", {}).get("diff_summary"):
        ds = front["git"]["diff_summary"]
        suggestions.append(f"- Review frontend code churn (added: {ds['added']:,}, deleted: {ds['deleted']:,}) this window.")
    if back and any("/documents" in r["path"] and r["method"]=="PUT" for r in back["api_routes"]) is False:
        suggestions.append("- Implement `PUT /documents/{id}` for Documents update.")
    if not suggestions:
        suggestions.append("- Keep momentum: tests, RBAC, deployment pipeline.")
    md.extend(suggestions)

    # JSON appendix (machine-readable)
    appendix = {
        "generated_at": now,
        "window_days": since_days,
        "frontend": front or {},
        "backend": back or {},
    }
    md.append("\n---\n## Machine-Readable Appendix (JSON)\n")
    md.append(codeblock("json", json.dumps(appendix, indent=2)[:200000]))  # avoid gigantic size

    return "\n".join(md)

# -------- CLI --------
def main():
    parser = argparse.ArgumentParser(description="Generate a weekly report for frontend & backend codebases.")
    parser.add_argument("--frontend", type=str, default="", help="Path to frontend root")
    parser.add_argument("--backend", type=str, default="", help="Path to backend root")
    parser.add_argument("--since-days", type=int, default=7, help="Lookback window in days (default: 7)")
    parser.add_argument("--out", type=str, default="reports/weekly_report.md", help="Output markdown path")
    args = parser.parse_args()

    if not args.frontend and not args.backend:
        print("Provide at least one of --frontend or --backend", file=sys.stderr)
        sys.exit(2)

    front_res = back_res = None
    if args.frontend:
        fpath = Path(args.frontend).resolve()
        if not fpath.exists():
            print(f"Frontend path not found: {fpath}", file=sys.stderr)
            sys.exit(3)
        front_res = analyze_codebase(fpath, "frontend", args.since_days)

    if args.backend:
        bpath = Path(args.backend).resolve()
        if not bpath.exists():
            print(f"Backend path not found: {bpath}", file=sys.stderr)
            sys.exit(4)
        back_res = analyze_codebase(bpath, "backend", args.since_days)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    md = make_markdown(front_res, back_res, args.since_days)
    out_path.write_text(md, encoding="utf-8")
    print(f"Report written to: {out_path}")

if __name__ == "__main__":
    main()
