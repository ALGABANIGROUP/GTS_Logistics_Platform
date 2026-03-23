from __future__ import annotations

import html
import subprocess
import sys
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORTS_DIR = ROOT / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
REPORT_PATH = REPORTS_DIR / "runtime_smoke_report.html"

TEST_TARGETS = [
    "backend/tests/test_runtime_smoke_suite.py",
    "backend/tests/test_live_shell_smoke.py",
]


def run_pytest() -> subprocess.CompletedProcess[str]:
    command = [sys.executable, "-m", "pytest", *TEST_TARGETS, "-q"]
    return subprocess.run(
        command,
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=300,
    )


def build_report(result: subprocess.CompletedProcess[str]) -> str:
    passed = result.returncode == 0
    status_text = "Passed" if passed else "Failed"
    status_color = "#16a34a" if passed else "#dc2626"
    output = (result.stdout or "").strip()
    errors = (result.stderr or "").strip()
    summary = output.splitlines()[-1] if output else "No pytest summary was captured."

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>GTS Runtime Smoke Report</title>
  <style>
    body {{
      margin: 0;
      font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
      background: #0f172a;
      color: #e2e8f0;
      padding: 32px;
    }}
    .container {{
      max-width: 1100px;
      margin: 0 auto;
    }}
    .hero {{
      border: 1px solid rgba(255,255,255,0.08);
      background: linear-gradient(135deg, rgba(15,23,42,0.95), rgba(30,41,59,0.95));
      border-radius: 20px;
      padding: 28px;
      margin-bottom: 20px;
    }}
    .status {{
      display: inline-block;
      margin-top: 12px;
      padding: 8px 14px;
      border-radius: 999px;
      background: {status_color}22;
      color: {status_color};
      border: 1px solid {status_color}55;
      font-weight: 700;
    }}
    .card {{
      border: 1px solid rgba(255,255,255,0.08);
      background: rgba(15,23,42,0.9);
      border-radius: 20px;
      padding: 24px;
      margin-bottom: 20px;
    }}
    pre {{
      white-space: pre-wrap;
      word-break: break-word;
      background: #020617;
      border-radius: 14px;
      padding: 18px;
      border: 1px solid rgba(255,255,255,0.08);
      overflow: auto;
    }}
    code {{
      font-family: Consolas, "Courier New", monospace;
    }}
  </style>
</head>
<body>
  <div class="container">
    <section class="hero">
      <h1>GTS Runtime Smoke Report</h1>
      <p>Generated at {html.escape(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))}</p>
      <p>Executed targets: <code>{html.escape(", ".join(TEST_TARGETS))}</code></p>
      <div class="status">{status_text}</div>
    </section>
    <section class="card">
      <h2>Pytest Summary</h2>
      <p>{html.escape(summary)}</p>
    </section>
    <section class="card">
      <h2>Standard Output</h2>
      <pre>{html.escape(output or "No stdout captured.")}</pre>
    </section>
    <section class="card">
      <h2>Standard Error</h2>
      <pre>{html.escape(errors or "No stderr captured.")}</pre>
    </section>
  </div>
</body>
</html>
"""


def main() -> int:
    result = run_pytest()
    REPORT_PATH.write_text(build_report(result), encoding="utf-8")

    print(f"Smoke report written to: {REPORT_PATH}")
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)

    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
