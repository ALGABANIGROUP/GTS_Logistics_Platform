from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class ReportGenerator:
    """Persist and retrieve machine-readable training reports."""

    def __init__(self, *, reports_dir: Path) -> None:
        self.reports_dir = reports_dir
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def write_report(self, report: dict[str, Any]) -> Path:
        path = self.reports_dir / f"{report['session_id']}.json"
        path.write_text(json.dumps(report, indent=2), encoding="utf-8")
        return path

    def list_reports(self) -> list[dict[str, Any]]:
        reports = []
        for path in sorted(self.reports_dir.glob("*.json")):
            try:
                reports.append(json.loads(path.read_text(encoding="utf-8")))
            except json.JSONDecodeError:
                continue
        reports.sort(key=lambda item: item.get("completed_at", ""), reverse=True)
        return reports

    def get_report(self, session_id: str) -> dict[str, Any] | None:
        path = self.reports_dir / f"{session_id}.json"
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))
