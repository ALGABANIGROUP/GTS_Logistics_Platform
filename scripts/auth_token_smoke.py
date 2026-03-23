import argparse
import json
import os
import sys
import urllib.error
import urllib.request


def _request(method: str, url: str, headers: dict[str, str] | None = None, body: str | None = None):
    data = body.encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, method=method, data=data, headers=headers or {})
    try:
        with urllib.request.urlopen(req) as resp:
            raw = resp.read().decode("utf-8")
            return resp.status, raw
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8") if exc.fp else ""
        return exc.code, raw


def _json_or_text(raw: str):
    try:
        return json.loads(raw)
    except Exception:
        return raw


def _print_result(label: str, status_code: int, raw: str):
    payload = _json_or_text(raw)
    print(f"[{label}] status={status_code} body={payload}")


def _expect_ai_result(label: str, status_code: int, raw: str, failures: list[str]):
    _print_result(label, status_code, raw)
    if status_code == 200:
        return
    if status_code == 403:
        payload = _json_or_text(raw)
        detail = payload.get("detail") if isinstance(payload, dict) else ""
        if "Forbidden: role=" not in str(detail):
            failures.append(f"{label} returned 403 without role detail")
        return
    failures.append(f"{label} unexpected status {status_code}")


def main() -> int:
    parser = argparse.ArgumentParser(description="GTS auth smoke checks")
    parser.add_argument("--base-url", default=os.getenv("GTS_BASE_URL", "http://localhost:8000"))
    parser.add_argument("--mode", choices=("dev", "prod"), default=os.getenv("GTS_MODE", "dev"))
    parser.add_argument("--email", default=os.getenv("GTS_TEST_EMAIL"))
    parser.add_argument("--password", default=os.getenv("GTS_TEST_PASSWORD"))
    parser.add_argument("--token", default=os.getenv("GTS_TEST_TOKEN"))
    args = parser.parse_args()

    base_url = args.base_url.rstrip("/")
    failures: list[str] = []

    status_code, raw = _request("GET", f"{base_url}/auth/me")
    _print_result("auth_me_no_token", status_code, raw)
    if status_code not in (401, 403):
        failures.append("expected /auth/me to require auth")

    if args.mode == "prod":
        bad_payload = json.dumps({"email": "x@example.com", "password": "bad"})
        status_code, raw = _request(
            "POST",
            f"{base_url}/auth/token",
            headers={"Content-Type": "application/json"},
            body=bad_payload,
        )
        _print_result("auth_token_prod", status_code, raw)
        if status_code != 503:
            failures.append("expected /auth/token blocked in prod (503)")
    else:
        bad_payload = json.dumps({"email": "invalid@example.com", "password": "wrong"})
        status_code, raw = _request(
            "POST",
            f"{base_url}/auth/token",
            headers={"Content-Type": "application/json"},
            body=bad_payload,
        )
        _print_result("auth_token_bad_creds", status_code, raw)
        if status_code not in (400, 401):
            failures.append("expected /auth/token to reject bad credentials in dev")

        if not (args.email and args.password):
            failures.append("set GTS_TEST_EMAIL/GTS_TEST_PASSWORD for dev login checks")
        else:
            good_payload = json.dumps({"email": args.email, "password": args.password})
            status_code, raw = _request(
                "POST",
                f"{base_url}/auth/token",
                headers={"Content-Type": "application/json"},
                body=good_payload,
            )
            _print_result("auth_token_good_creds", status_code, raw)
            access_token = None
            refresh_token = None
            if status_code == 200:
                payload = _json_or_text(raw)
                if isinstance(payload, dict):
                    access_token = payload.get("access_token")
                    refresh_token = payload.get("refresh_token")
            if status_code != 200 or not access_token or not refresh_token:
                failures.append("expected /auth/token to return access_token and refresh_token")
            else:
                status_code, raw = _request(
                    "GET",
                    f"{base_url}/auth/me",
                    headers={"Authorization": f"Bearer {access_token}"},
                )
                _print_result("auth_me_with_token", status_code, raw)
                if status_code != 200:
                    failures.append("expected /auth/me success with access token")

                status_code, raw = _request(
                    "GET",
                    f"{base_url}/ai/bots",
                    headers={"Authorization": f"Bearer {access_token}"},
                )
                _expect_ai_result("ai_bots", status_code, raw, failures)

                ask_payload = json.dumps({"query": "system status", "context": {}})
                status_code, raw = _request(
                    "POST",
                    f"{base_url}/ai/ask",
                    headers={"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"},
                    body=ask_payload,
                )
                _expect_ai_result("ai_ask", status_code, raw, failures)

                refresh_payload = json.dumps({"refresh_token": refresh_token})
                status_code, raw = _request(
                    "POST",
                    f"{base_url}/auth/refresh",
                    headers={"Content-Type": "application/json"},
                    body=refresh_payload,
                )
                _print_result("auth_refresh", status_code, raw)
                new_refresh = None
                if status_code == 200:
                    payload = _json_or_text(raw)
                    if isinstance(payload, dict):
                        new_refresh = payload.get("refresh_token")
                if status_code != 200 or not new_refresh:
                    failures.append("expected /auth/refresh to return new refresh_token")
                else:
                    status_code, raw = _request(
                        "POST",
                        f"{base_url}/auth/refresh",
                        headers={"Content-Type": "application/json"},
                        body=refresh_payload,
                    )
                    _print_result("auth_refresh_reuse", status_code, raw)
                    if status_code != 401:
                        failures.append("expected /auth/refresh reuse to return 401")

                    logout_payload = json.dumps({"refresh_token": new_refresh})
                    status_code, raw = _request(
                        "POST",
                        f"{base_url}/auth/logout",
                        headers={"Content-Type": "application/json"},
                        body=logout_payload,
                    )
                    _print_result("auth_logout", status_code, raw)
                    if status_code != 200:
                        failures.append("expected /auth/logout to return 200")

    if failures:
        print("FAILED:")
        for item in failures:
            print(f"- {item}")
        return 1

    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
