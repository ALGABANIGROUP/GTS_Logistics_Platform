from __future__ import annotations

import os
import subprocess
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

router = APIRouter()

ENVIRONMENT = os.getenv("ENVIRONMENT", "development").lower().strip()
ADMIN_TOOL_SECRET = (os.getenv("ADMIN_TOOL_SECRET") or "").strip()


def _is_production() -> bool:
    return ENVIRONMENT == "production"


def _require_secret(secret: Optional[str]) -> None:
    if not ADMIN_TOOL_SECRET:
        raise HTTPException(status_code=503, detail="Admin tool secret not configured")
    if not secret or secret.strip() != ADMIN_TOOL_SECRET:
        raise HTTPException(status_code=403, detail="Forbidden")


@router.get("/admin/generate_project_structure/", include_in_schema=False)
async def generate_project_structure(secret: Optional[str] = Query(default=None)):
    if _is_production():
        raise HTTPException(status_code=404, detail="Not Found")

    _require_secret(secret)

    try:
        result = subprocess.run(
            ["python", "tools/project_structure_clean.py"],
            capture_output=True,
            text=True,
            cwd=".",
            timeout=60,
            check=False,
        )
        return {
            "status": "success",
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="Command timeout")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
