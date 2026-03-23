# D:\GTS Logistics\backend\tools\system_self_check.py
from __future__ import annotations

import json
import os
from typing import Dict, List, Tuple, Any

import requests

BASE_URL = os.environ.get("SELF_CHECK_BASE_URL", "http://127.0.0.1:8000")
REPORT_PATH = r"D:\GTS Logistics\backend\self_check_report.json"  # fixed path (no duplicate 'backend')


def _env_missing(keys: List[str]) -> List[str]:
    return [k for k in keys if not os.environ.get(k)]


def _token() -> Tuple[bool, str]:
    """
    Prefer an ADMIN token first (role=admin), then fallback to username/password.
    Returns: (ok, access_token)
    """
    headers = {"Content-Type": "application/json", "Accept": "application/json"}

    # 1) Preferred: role-based admin token
    try:
        p_admin = {"username": "yassir", "role": "admin", "expires_minutes": 120}
        r = requests.post(f"{BASE_URL}/auth/token", headers=headers, json=p_admin, timeout=10)
        if r.ok and r.headers.get("content-type", "").startswith("application/json"):
            tok = (r.json() or {}).get("access_token", "")
            if tok:
                return True, tok
    except Exception:
        pass

    # 2) Fallback: username/password (may yield non-admin -> some endpoints will 403)
    try:
        p_user = {"username": "admin", "password": "admin"}
        r = requests.post(f"{BASE_URL}/auth/token", headers=headers, json=p_user, timeout=10)
        if r.ok and r.headers.get("content-type", "").startswith("application/json"):
            tok = (r.json() or {}).get("access_token", "")
            if tok:
                return True, tok
    except Exception:
        pass

    return False, ""


def _get(url: str, headers: Dict[str, str] | None = None) -> requests.Response:
    h = {"Accept": "application/json"}
    if headers:
        h.update(headers)
    return requests.get(url, headers=h, timeout=10)


def _post(url: str, data=None, json_body=None, headers: Dict[str, str] | None = None) -> requests.Response:
    h = {"Accept": "application/json"}
    if headers:
        h.update(headers)
    if json_body is not None:
        return requests.post(url, json=json_body, headers=h, timeout=10)
    return requests.post(url, data=data, headers=h, timeout=10)


def main() -> int:
    report: Dict[str, Any] = {
        "base_url": BASE_URL,
        "checks": [],
        "summary": {},
    }

    # 0) ENV check
    required_env = ["HOST", "PORT", "DATABASE_URL", "ASYNC_DATABASE_URL"]
    miss = _env_missing(required_env)
    env_ok = len(miss) == 0
    report["checks"].append({"name": "env", "ok": env_ok, "missing": miss})

    # 1) server /health/ping
    try:
        r = _get(f"{BASE_URL}/health/ping")
        ping_ok = r.ok
    except Exception:
        ping_ok = False
    report["checks"].append({"name": "health_ping", "ok": ping_ok})

    # 2) auth (admin-first)
    tok_ok, tok = _token()
    headers = {"Authorization": f"Bearer {tok}"} if tok_ok else {}
    report["checks"].append({"name": "auth_token", "ok": tok_ok})

    # 3) routes
    try:
        r = _get(f"{BASE_URL}/_debug/routes", headers=headers or None)
        routes_ok = r.ok
        routes = r.json() if routes_ok else {}
    except Exception:
        routes_ok = False
        routes = {}
    report["checks"].append({
        "name": "routes",
        "ok": routes_ok,
        "count": (routes.get("count") if isinstance(routes, dict) else None)
    })

    # Helper to check if a path exists in current app
    def exists(path: str) -> bool:
        if not routes_ok:
            return False
        rs = routes.get("routes", [])
        return any(isinstance(item, dict) and item.get("path") == path for item in rs)

    # 4) Documents
    docs_results = {"ok": [], "fail": [], "skipped": []}
    # debug db + list
    for path in ["/documents/_debug/db", "/documents/"]:
        if exists(path):
            try:
                r = _get(f"{BASE_URL}{path}", headers=headers or None)
                (docs_results["ok"] if r.ok else docs_results["fail"]).append(path)
            except Exception:
                docs_results["fail"].append(path)
        else:
            docs_results["skipped"].append(path)

    # expiring/notify (might not be present in all builds)
    for path in ["/documents/expiring-soon/", "/documents/notify-expiring/"]:
        if exists(path):
            try:
                if path.endswith("/notify-expiring/"):
                    r = _post(f"{BASE_URL}{path}", headers=headers or None, json_body={})
                else:
                    r = _get(f"{BASE_URL}{path}", headers=headers or None)
                (docs_results["ok"] if r.ok else docs_results["fail"]).append(path)
            except Exception:
                docs_results["fail"].append(path)
        else:
            docs_results["skipped"].append(path)

    report["checks"].append({"name": "documents", **docs_results})

    # 5) Finance
    finance_paths = [
        ("/finance/health", "GET"),
        ("/finance/expenses", "GET"),
        ("/finance/summary", "GET"),
        ("/finance/reports/summary", "GET"),
        ("/ai/finance-analysis", "GET"),
    ]
    fin_ok, fin_fail, fin_skip = [], [], []
    for p, m in finance_paths:
        if exists(p):
            try:
                if m == "GET":
                    r = _get(f"{BASE_URL}{p}", headers=headers or None)
                else:
                    r = _post(f"{BASE_URL}{p}", headers=headers or None, json_body={})
                (fin_ok if r.ok else fin_fail).append(p)
            except Exception:
                fin_fail.append(p)
        else:
            fin_skip.append(p)
    report["checks"].append({"name": "finance", "ok": fin_ok, "fail": fin_fail, "skipped": fin_skip})

    # 6) Bots (status only; 5xx recorded as warnings)
    bots_warn: List[str] = []
    for b in ["operations_manager", "finance_bot"]:
        path = f"/ai/{b}/status"
        if exists(path):
            try:
                r = _get(f"{BASE_URL}{path}", headers=headers or None)
                if not r.ok:
                    bots_warn.append(f"{b}: status {r.status_code}")
            except Exception as e:
                bots_warn.append(f"{b}: {e!s}")

    # Summary
    overall_ok = env_ok and ping_ok and tok_ok and routes_ok and len(docs_results["fail"]) == 0 and len(fin_fail) == 0
    report["summary"] = {
        "overall_ok": overall_ok,
        "env_ok": env_ok,
        "ping_ok": ping_ok,
        "auth_ok": tok_ok,
        "routes_ok": routes_ok,
        "bots_warnings": bots_warn,
    }

    # Save
    try:
        with open(REPORT_PATH, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
    except Exception:
        pass

    # Console output
    print("=" * 60)
    print("🔎 GTS Self-Check — Phase 1")
    print("=" * 60)
    if not env_ok:
        print(f"[FAIL] Missing ENV keys: {miss}")
    else:
        print("[OK]  ENV present")

    print(f"[{'OK' if ping_ok else 'FAIL'}] /health/ping")
    print(f"[{'OK' if tok_ok else 'FAIL'}] auth token")
    print(f"[{'OK' if routes_ok else 'FAIL'}] routes")

    print(f"[..]  Documents OK: {docs_results['ok']}")
    if docs_results["fail"]:
        print(f"[FAIL] Documents FAIL: {docs_results['fail']}")
    if docs_results["skipped"]:
        print(f"[..]  Documents SKIPPED (not present): {docs_results['skipped']}")

    if fin_fail:
        print(f"[FAIL] Finance FAIL: {fin_fail}")
    else:
        print(f"[OK]  Finance OK: {fin_ok or []}")

    print("-" * 60)
    print(f"{'✅ OVERALL: READY' if overall_ok else '❌ OVERALL: NOT READY'}")
    print(f"📝 Report saved: {REPORT_PATH}")
    return 0 if overall_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
