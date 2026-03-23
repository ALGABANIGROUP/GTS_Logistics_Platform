from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def main() -> int:
    repo_root = _repo_root()
    env_candidates = [
        Path(__file__).resolve().parent / ".env",
        repo_root / "backend" / ".env",
        repo_root / ".env",
    ]
    for env_path in env_candidates:
        if env_path.exists():
            load_dotenv(env_path, override=True)
    print("Starting GTS Logistics Backend Server...")

    cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "backend.main:app",
        "--reload",
        "--app-dir",
        str(repo_root),
    ]
    return subprocess.call(cmd)


if __name__ == "__main__":
    raise SystemExit(main())
