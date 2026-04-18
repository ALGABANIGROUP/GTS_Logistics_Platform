#!/usr/bin/env python
"""Repository guard against introducing mock/demo/placeholder production code."""

from __future__ import annotations

import argparse
import fnmatch
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]


@dataclass
class Finding:
    category: str
    file: str
    line: int
    text: str


BANNED_BACKEND = re.compile(r"\b(mock|demo|stub|fake|dummy)\b|coming\s+soon|placeholder", re.IGNORECASE)
BANNED_FRONTEND = re.compile(r"\b(mock|demo|stub|fake|dummy)\b|coming\s+soon|placeholder", re.IGNORECASE)
BANNED_ENV = re.compile(r"enable_mock|demo_mode|mock_mode", re.IGNORECASE)
BANNED_IMPORTS = re.compile(r"mockDataApi|mock.*Api|mock.*Service", re.IGNORECASE)
BANNED_RANDOM = re.compile(r"Math\.random\(\)")

EXCLUDED_DIR_TOKENS = {
    ".venv",
    "venv",
    "site-packages",
    "node_modules",
    "__pycache__",
    ".git",
    "alembic",
    "migrations",
    "storybook",
    "dist",
    "build",
    "GTS_Logistics_Platform",
    "no_mock_check",
    "no_mock_allowlist",
}

ALLOWED_LINE_PATTERNS = [
    re.compile(r"placeholders?\s*=", re.IGNORECASE),
    re.compile(r"placeholders?:", re.IGNORECASE),
    re.compile(r"demographics", re.IGNORECASE),
    re.compile(r"mock\s+mode\s+is\s+disabled", re.IGNORECASE),
    # CSS / Tailwind placeholder styling is legitimate UI, not mock code.
    re.compile(r"placeholder-\w+"),
    re.compile(r"::placeholder"),
    re.compile(r"-placeholder\b"),
    re.compile(r"'\s*placeholder\s*'", re.IGNORECASE),
    re.compile(r'"\s*placeholder\s*"', re.IGNORECASE),
    re.compile(r"PLACEHOLDER\b"),
    re.compile(r"placeholders?\s*[,()]"),
    re.compile(r"\+\s*placeholder\b"),
    re.compile(r"\{placeholders\}"),
]

# Files that deal with legitimate product concepts (subscription tier names, mock
# integration modes, etc.) that intentionally use the reserved words.  The check
# would otherwise produce false positives for code that merely references these
# existing business entities.
EXCLUDED_FILES = {
    # The "demo" subscription tier is a real product tier and is stored in the
    # database.  Renaming it would break existing subscribers.
    "backend/ai/bot_subscription_manager.py",
    "backend/security/access_context.py",
    "backend/security/entitlements.py",
    "backend/routes/bots_subscription.py",
    "backend/routes/bots_available_enhanced.py",
    "frontend/src/utils/tierUtils.js",
    "frontend/src/pages/BotFeatures.jsx",
    # TruckerPath offline/stub integration intentionally exposes a mock source as
    # a last-resort fallback when API credentials are missing.
    "backend/routes/bots_mock_api.py",
    "backend/integrations/loadboards/truckerpath_api.py",
    "backend/integrations/loadboards/truckerpath_provider.py",
    "backend/integrations/truckerpath/create_company.py",
    "backend/services/truckerpath_service.py",
    # Fixture adapter dedicated to the "demo acme" learning source.
    "backend/tools/open_web_leads/adapters/demo_acme.py",
    # User model defaults new users to the "demo" subscription tier — that
    # string value is a real tier and cannot be renamed without a DB migration.
    "backend/models/user.py",
}


def should_skip_file(path: Path, include_globs: Iterable[str], exclude_name_tokens: Iterable[str]) -> bool:
    rel = path.relative_to(ROOT).as_posix()
    if rel in EXCLUDED_FILES:
        return True
    if not any(fnmatch.fnmatch(rel, g) for g in include_globs):
        return True
    if any(tok in rel for tok in EXCLUDED_DIR_TOKENS):
        return True
    name = path.name.lower()
    if any(tok in name for tok in exclude_name_tokens):
        return True
    return False


def line_allowed(text: str) -> bool:
    return any(p.search(text) for p in ALLOWED_LINE_PATTERNS)


def scan(include_globs: list[str], exclude_name_tokens: list[str], pattern: re.Pattern[str], category: str) -> list[Finding]:
    findings: list[Finding] = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if should_skip_file(path, include_globs, exclude_name_tokens):
            continue
        try:
            content = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        except OSError:
            continue

        for idx, line in enumerate(content, start=1):
            if pattern.search(line) and not line_allowed(line):
                findings.append(Finding(category, path.relative_to(ROOT).as_posix(), idx, line.strip()))
    return findings


def summarize(findings: list[Finding]) -> dict:
    by_category: dict[str, int] = {}
    for f in findings:
        by_category[f.category] = by_category.get(f.category, 0) + 1
    return {
        "total_findings": len(findings),
        "by_category": by_category,
        "findings": [
            {
                "category": f.category,
                "file": f.file,
                "line": f.line,
                "text": f.text[:220],
            }
            for f in findings
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", help="Write JSON report to this path")
    args = parser.parse_args()

    findings: list[Finding] = []
    findings.extend(
        scan(
            include_globs=["backend/**/*.py"],
            exclude_name_tokens=["test"],
            pattern=BANNED_BACKEND,
            category="backend_patterns",
        )
    )
    findings.extend(
        scan(
            include_globs=["frontend/src/**/*.js", "frontend/src/**/*.jsx"],
            exclude_name_tokens=["test"],
            pattern=BANNED_FRONTEND,
            category="frontend_patterns",
        )
    )
    findings.extend(
        scan(
            include_globs=["**/*.yml", "**/*.yaml", "**/*.env", "**/*.env.*", "**/*.py"],
            exclude_name_tokens=[],
            pattern=BANNED_ENV,
            category="mock_mode_env",
        )
    )
    findings.extend(
        scan(
            include_globs=["frontend/src/**/*.js", "frontend/src/**/*.jsx"],
            exclude_name_tokens=["test"],
            pattern=BANNED_IMPORTS,
            category="mock_api_imports",
        )
    )
    findings.extend(
        scan(
            include_globs=["frontend/src/**/*.js", "frontend/src/**/*.jsx"],
            exclude_name_tokens=["test"],
            pattern=BANNED_RANDOM,
            category="math_random",
        )
    )

    report = summarize(findings)
    if args.report:
        out = ROOT / args.report
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    if report["total_findings"]:
        print("Found blocked mock/demo patterns:", report["total_findings"])
        for item in report["findings"][:30]:
            print(f"- [{item['category']}] {item['file']}:{item['line']} :: {item['text']}")
        return 1

    print("No blocked mock/demo patterns found.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
