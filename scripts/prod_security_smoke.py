# scripts/prod_security_smoke.py
import os
import sys
import json
import urllib.request
import urllib.error

DEFAULT_BASE = "http://127.0.0.1:8000"


def _base_url() -> str:
    base = (os.getenv("BASE_URL") or DEFAULT_BASE).strip().rstrip("/")
    return base


def _read_body(resp) -> str:
    try:
        data = resp.read()
        return data.decode("utf-8", errors="replace") if data else ""
    except Exception:
        return ""


def run_check(method: str, path: str, expected: int, payload=None, headers=None, timeout=10):
    url = _base_url() + path
    headers = headers or {}

    data = None
    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
        data = body
        headers.setdefault("Content-Type", "application/json")

    req = urllib.request.Request(url, data=data, method=method.upper())
    for k, v in headers.items():
        req.add_header(k, v)

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            code = getattr(resp, "status", resp.getcode())
            body = _read_body(resp)
            return (code == expected), code, body
    except urllib.error.HTTPError as he:
        # Important: in urllib, 401/404/503 are considered Exceptions but have code
        body = ""
        try:
            body = he.read().decode("utf-8", errors="replace")
        except Exception:
            pass
        return (he.code == expected), he.code, body
    except urllib.error.URLError as ue:
        # Connection failure/server down
        return False, 0, f"URLError: {ue}"
    except Exception as e:
        return False, 0, f"Exception: {e}"


def main() -> int:
    checks = [
        ("GET",  "/openapi.json", 404, None),
        ("GET",  "/docs",         404, None),
        ("POST", "/auth/token",   503, {"username": "x", "password": "y"}),
        ("GET",  "/auth/me",      401, None),
        ("GET",  "/users/me",     401, None),
        ("GET",  "/ai/bots",      401, None),
        ("POST", "/documents/notify-expiring/", 401, {}),
    ]

    all_ok = True
    for method, path, expected, payload in checks:
        ok, code, body = run_check(method, path, expected, payload=payload)
        if ok:
            print(f"OK:   {method} {path} -> {code}")
        else:
            all_ok = False
            # Print small snippet only
            snippet = (body or "").strip().replace("\n", " ")
            if len(snippet) > 180:
                snippet = snippet[:180] + "..."
            print(f"FAIL: {method} {path} -> expected {expected}, got {code} | {snippet}")

    print("SMOKE: PASS" if all_ok else "SMOKE: FAIL")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
