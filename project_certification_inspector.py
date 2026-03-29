#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import os
import re
from collections import Counter, defaultdict
from pathlib import Path

TEXT_EXTENSIONS = {
    ".py", ".js", ".jsx", ".ts", ".tsx", ".json", ".md", ".html", ".css",
    ".scss", ".sql", ".yml", ".yaml", ".toml", ".ini",
}

SKIP_DIRS = {
    ".git", ".github", ".venv", "venv", "node_modules", "__pycache__", "dist",
    "build", "coverage", "logs", "pgdata", "_archive", "_trash_TMS_20260116",
    "GTS_Logistics_Platform",
}

FASTAPI_ROUTE_RE = re.compile(
    r"@(?P<router>[A-Za-z_][A-Za-z0-9_]*)\.(?P<method>get|post|put|patch|delete|options|head)\(\s*[\"'](?P<path>[^\"']+)[\"']",
    re.MULTILINE,
)
FASTAPI_PREFIX_RE = re.compile(
    r"(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*=\s*APIRouter\((?P<args>.*?)\)",
    re.DOTALL,
)
PREFIX_VALUE_RE = re.compile(r"prefix\s*=\s*[\"']([^\"']+)[\"']")
EXPRESS_ROUTE_RE = re.compile(
    r"(?P<router>router|app)\.(?P<method>get|post|put|patch|delete|use)\(\s*[\"'](?P<path>[^\"']+)[\"']",
    re.MULTILINE,
)
SQLALCHEMY_MODEL_RE = re.compile(
    r"class\s+(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*\(.*?\):(?P<body>.*?)(?=\nclass\s+[A-Za-z_]|$)",
    re.DOTALL,
)
TABLENAME_RE = re.compile(r"__tablename__\s*=\s*[\"']([^\"']+)[\"']")


def utc_now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def safe_read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def rel(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root)).replace("\\", "/")
    except Exception:
        return str(path).replace("\\", "/")


class GTSProjectCertificationInspector:
    def __init__(self, project_path: str = "."):
        self.project_path = Path(project_path).resolve()
        self.scanned_files = []
        self.results = {
            "project_name": "GTS Logistics",
            "project_root": str(self.project_path),
            "inspection_date": utc_now_iso(),
            "statistics": {},
            "architecture": {},
            "modules": [],
            "api_endpoints": [],
            "ai_bots": [],
            "ai_bots_classification": {},
            "database_models": [],
            "security_features": [],
            "unique_features": [],
            "patent_claims": [],
            "certification_readiness": {},
        }

    def walk_files(self):
        for root, dirs, files in os.walk(self.project_path):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith(".pytest")]
            root_path = Path(root)
            for name in files:
                path = root_path / name
                if path.suffix.lower() in TEXT_EXTENSIONS:
                    yield path

    def run_full_inspection(self):
        print("Starting GTS Logistics certification inspection...")
        self.scanned_files = list(self.walk_files())
        self.collect_statistics()
        self.analyze_architecture()
        self.analyze_modules()
        self.analyze_api_endpoints()
        self.analyze_ai_bots()
        self.analyze_database()
        self.analyze_security()
        self.identify_unique_features()
        self.generate_patent_claims()
        self.assess_certification_readiness()
        print("Inspection complete.")
        return self.results

    def collect_statistics(self):
        print("Collecting project statistics...")
        stats = {
            "total_files": 0,
            "total_lines": 0,
            "total_directories": 0,
            "python_files": 0,
            "python_lines": 0,
            "javascript_files": 0,
            "typescript_files": 0,
            "html_files": 0,
            "css_files": 0,
            "json_files": 0,
            "markdown_files": 0,
            "sql_files": 0,
            "top_directories": [],
        }
        dir_counter = Counter()
        directories = set()
        for path in self.scanned_files:
            stats["total_files"] += 1
            directories.add(str(path.parent))
            dir_counter[rel(path.parent, self.project_path).split("/", 1)[0]] += 1
            text = safe_read_text(path)
            line_count = len(text.splitlines())
            stats["total_lines"] += line_count
            ext = path.suffix.lower()
            if ext == ".py":
                stats["python_files"] += 1
                stats["python_lines"] += line_count
            elif ext in {".js", ".jsx"}:
                stats["javascript_files"] += 1
            elif ext in {".ts", ".tsx"}:
                stats["typescript_files"] += 1
            elif ext == ".html":
                stats["html_files"] += 1
            elif ext in {".css", ".scss"}:
                stats["css_files"] += 1
            elif ext == ".json":
                stats["json_files"] += 1
            elif ext == ".md":
                stats["markdown_files"] += 1
            elif ext == ".sql":
                stats["sql_files"] += 1
        stats["total_directories"] = len(directories)
        stats["top_directories"] = [{"name": name or ".", "files": count} for name, count in dir_counter.most_common(10)]
        self.results["statistics"] = stats

    def analyze_architecture(self):
        print("Analyzing architecture...")
        layers, technologies, patterns = [], [], []
        if (self.project_path / "backend").exists():
            layers.append("Backend API Layer")
        if (self.project_path / "frontend").exists():
            layers.append("Frontend Client Layer")
        if (self.project_path / "database").exists() or (self.project_path / "models").exists():
            layers.append("Database Layer")
        if (self.project_path / "backend" / "bots").exists() or (self.project_path / "trainer_bot_advanced").exists():
            layers.append("AI and Automation Layer")
        has_fastapi = has_react = has_sqlalchemy = has_websocket = has_alembic = False
        for path in self.scanned_files:
            text = safe_read_text(path)
            if not has_fastapi and ("from fastapi import" in text or "APIRouter(" in text):
                has_fastapi = True
            if not has_react and ("react-router-dom" in text or "React.lazy" in text or "useState(" in text):
                has_react = True
            if not has_sqlalchemy and ("sqlalchemy" in text or "__tablename__" in text):
                has_sqlalchemy = True
            if not has_websocket and ("WebSocket" in text or "websocket" in path.name.lower()):
                has_websocket = True
            if not has_alembic and "alembic" in rel(path, self.project_path).lower():
                has_alembic = True
        if has_fastapi:
            technologies.append("FastAPI")
            patterns.append("REST API routing")
        if has_react:
            technologies.append("React")
            patterns.append("Single-page application")
        if has_sqlalchemy:
            technologies.append("SQLAlchemy ORM")
            patterns.append("Repository/data-access abstraction")
        if has_alembic:
            technologies.append("Alembic migrations")
        if has_websocket:
            technologies.append("WebSocket transport")
            patterns.append("Real-time event delivery")
        if (self.project_path / "docker-compose.orchestrator.yml").exists() or (self.project_path / "Dockerfile.production").exists():
            technologies.append("Containerized deployment")
        self.results["architecture"] = {
            "type": "Layered web platform with backend services and frontend SPA",
            "layers": layers,
            "patterns": sorted(set(patterns)),
            "technologies": sorted(set(technologies)),
        }

    def analyze_modules(self):
        print("Analyzing modules...")
        modules = []
        candidate_dirs = {
            "backend/routes": "API routes",
            "backend/bots": "AI bots",
            "backend/models": "ORM models",
            "backend/services": "Backend services",
            "frontend/src/pages": "Frontend pages",
            "frontend/src/components": "Frontend components",
            "trainer_bot_advanced": "Training subsystem",
        }
        for raw_path, module_type in candidate_dirs.items():
            path = self.project_path / raw_path.replace("/", os.sep)
            if path.exists():
                modules.append({"name": path.name, "path": rel(path, self.project_path), "type": module_type})
        self.results["modules"] = modules

    def analyze_api_endpoints(self):
        print("Analyzing API endpoints...")
        api_endpoints = []
        for path in self.scanned_files:
            if path.suffix.lower() not in {".py", ".js", ".ts"}:
                continue
            text = safe_read_text(path)
            path_rel = rel(path, self.project_path)
            if path.suffix.lower() == ".py" and ("APIRouter(" in text or "@router." in text):
                prefixes = self._extract_fastapi_prefixes(text)
                for match in FASTAPI_ROUTE_RE.finditer(text):
                    route_prefix = prefixes.get(match.group("router"), "")
                    api_endpoints.append({
                        "framework": "FastAPI",
                        "method": match.group("method").upper(),
                        "path": self._join_paths(route_prefix, match.group("path")),
                        "file": path_rel,
                    })
            elif path.suffix.lower() in {".js", ".ts"} and (
                "require('express')" in text
                or 'require("express")' in text
                or "from 'express'" in text
                or 'from "express"' in text
                or "express.Router(" in text
            ):
                for match in EXPRESS_ROUTE_RE.finditer(text):
                    api_endpoints.append({
                        "framework": "Express",
                        "method": match.group("method").upper(),
                        "path": match.group("path"),
                        "file": path_rel,
                    })
        self.results["api_endpoints"] = sorted(api_endpoints, key=lambda x: (x["framework"], x["path"], x["method"], x["file"]))

    def _extract_fastapi_prefixes(self, text: str):
        prefixes = {}
        for match in FASTAPI_PREFIX_RE.finditer(text):
            value = PREFIX_VALUE_RE.search(match.group("args"))
            prefixes[match.group("name")] = value.group(1) if value else ""
        return prefixes

    def _join_paths(self, prefix: str, route: str):
        if not prefix:
            return route
        return f"{prefix.rstrip('/')}/{route.lstrip('/')}"

    def analyze_ai_bots(self):
        print("Analyzing AI bot and automation assets...")
        bots = []
        classes = defaultdict(list)
        patterns = {
            "chatbots": ["chat", "customer_service", "support"],
            "automation_bots": ["dispatcher", "automation", "orchestrator", "maintenance"],
            "analysis_bots": ["analytics", "intelligence", "advisor", "report"],
            "assistant_bots": ["assistant", "manager", "broker", "bot"],
        }
        for path in self.scanned_files:
            lower = path.name.lower()
            if path.suffix.lower() not in {".py", ".js", ".jsx", ".ts", ".tsx"}:
                continue
            if "bot" not in lower and "assistant" not in lower and "trainer" not in lower and "dispatcher" not in lower:
                continue
            bots.append({"name": path.stem, "file": rel(path, self.project_path), "language": path.suffix.lower().lstrip(".")})
            for bucket, words in patterns.items():
                if any(word in lower for word in words):
                    classes[bucket].append(path.stem)
        self.results["ai_bots"] = sorted(bots, key=lambda x: x["file"])
        self.results["ai_bots_classification"] = {key: sorted(set(value)) for key, value in classes.items()}

    def analyze_database(self):
        print("Analyzing database models...")
        db_models = []
        for path in self.scanned_files:
            text = safe_read_text(path)
            path_rel = rel(path, self.project_path)
            if path.suffix.lower() == ".py":
                for match in SQLALCHEMY_MODEL_RE.finditer(text):
                    body = match.group("body")
                    table_match = TABLENAME_RE.search(body)
                    if "__tablename__" in body or "mapped_column(" in body or "Column(" in body:
                        db_models.append({
                            "name": match.group("name"),
                            "table": table_match.group(1) if table_match else "",
                            "file": path_rel,
                            "type": "ORM model",
                        })
            elif path.suffix.lower() == ".sql" and ("create table" in text.lower() or "alter table" in text.lower()):
                db_models.append({"name": path.stem, "table": "", "file": path_rel, "type": "SQL migration/script"})
        self.results["database_models"] = sorted(db_models, key=lambda x: (x["type"], x["file"], x["name"]))

    def analyze_security(self):
        print("Analyzing security features...")
        security_keywords = ["auth", "jwt", "token", "security", "session", "webhook", "audit", "password", "permission", "role", "rbac"]
        features = []
        for path in self.scanned_files:
            path_rel = rel(path, self.project_path)
            lower_path = path_rel.lower()
            if any(keyword in lower_path for keyword in security_keywords):
                features.append({"name": path.name, "path": path_rel, "reason": "Matched security-related file naming"})
        self.results["security_features"] = sorted(features, key=lambda x: x["path"])

    def identify_unique_features(self):
        print("Identifying feature candidates...")
        candidates = []

        def add_feature(name: str, description: str, evidence, confidence: str):
            if evidence:
                candidates.append({"name": name, "description": description, "evidence": sorted(set(evidence)), "confidence": confidence})

        all_files = [rel(path, self.project_path) for path in self.scanned_files]
        add_feature("AI bot operations layer", "The repository contains multiple AI-oriented bot and control surfaces across backend and frontend.", [p for p in all_files if "/bots/" in p or "/ai-bots/" in p][:12], "High")
        add_feature("Payment workflow platform", "The repository includes payment pages, gateway integrations, and webhook handlers.", [p for p in all_files if "payment" in p.lower() or "webhook" in p.lower()][:12], "High")
        add_feature("Partner portal capability", "Partner-facing portal pages and partner API routes are present.", [p for p in all_files if "partner" in p.lower()][:12], "High")
        add_feature("Training center subsystem", "A dedicated training-center and trainer-bot subsystem exists for structured training workflows.", [p for p in all_files if "training" in p.lower() or "trainer" in p.lower()][:12], "Medium")
        add_feature("Real-time transport monitoring", "WebSocket and transport tracking modules indicate real-time monitoring features.", [p for p in all_files if "ws_" in p.lower() or "tracking" in p.lower() or "monitor" in p.lower()][:12], "Medium")
        add_feature("Document intelligence workflow", "Document upload, OCR, and document dashboard code paths are present.", [p for p in all_files if "document" in p.lower() or "ocr" in p.lower()][:12], "High")
        self.results["unique_features"] = candidates

    def generate_patent_claims(self):
        print("Generating claim candidates...")
        claims = []
        templates = {
            "AI bot operations layer": ("Multi-agent logistics operations orchestration", "A system that coordinates specialized software agents across logistics workflows, including evidence of bot control surfaces and backend execution paths."),
            "Payment workflow platform": ("Integrated freight-payment workflow platform", "A payment workflow combining customer-facing payment pages, gateway integrations, and asynchronous webhook processing for logistics operations."),
            "Partner portal capability": ("Partner logistics portal with role-aware data access", "A partner portal architecture that exposes partner-specific views, data retrieval paths, and settings management within a shared logistics platform."),
            "Training center subsystem": ("AI or operator training workflow subsystem", "A training-center subsystem that plans, tracks, and evaluates structured scenarios or learning paths within the platform."),
            "Real-time transport monitoring": ("Real-time transport visibility and alert delivery", "A transport monitoring architecture using tracking and live communication modules to surface operational state changes in real time."),
            "Document intelligence workflow": ("Automated logistics document processing pipeline", "A document-processing flow with upload, parsing, OCR, and dashboard presentation layers for operational documents."),
        }
        for index, feature in enumerate(self.results.get("unique_features", []), start=1):
            title, description = templates.get(feature["name"], (feature["name"], feature["description"]))
            claims.append({
                "claim_number": index,
                "title": title,
                "description": description,
                "basis": feature["name"],
                "evidence": feature["evidence"][:6],
                "confidence": feature["confidence"],
            })
        self.results["patent_claims"] = claims

    def assess_certification_readiness(self):
        print("Assessing certification readiness...")
        stats = self.results["statistics"]
        api_count = len(self.results["api_endpoints"])
        bot_count = len(self.results["ai_bots"])
        model_count = len(self.results["database_models"])
        security_count = len(self.results["security_features"])
        feature_count = len(self.results["unique_features"])
        criteria = [
            {"name": "Repository scale", "score": min(100, 40 + stats["total_files"] // 20), "weight": 0.15, "basis": f"{stats['total_files']} scanned text files"},
            {"name": "API surface", "score": min(100, 25 + api_count), "weight": 0.20, "basis": f"{api_count} detected API endpoints"},
            {"name": "Data model maturity", "score": min(100, 30 + model_count // 2), "weight": 0.15, "basis": f"{model_count} model or migration artifacts"},
            {"name": "AI and automation depth", "score": min(100, 30 + bot_count), "weight": 0.20, "basis": f"{bot_count} bot-related files"},
            {"name": "Security footprint", "score": min(100, 35 + security_count // 3), "weight": 0.15, "basis": f"{security_count} security-related files"},
            {"name": "Differentiated capabilities", "score": min(100, 40 + feature_count * 8), "weight": 0.15, "basis": f"{feature_count} evidence-based feature candidates"},
        ]
        overall = round(sum(item["score"] * item["weight"] for item in criteria), 2)
        self.results["certification_readiness"] = {
            "overall_score": overall,
            "status": "Ready for review" if overall >= 80 else "Needs improvement",
            "criteria": criteria,
            "recommendations": [
                "Add an evidence map linking each claim candidate to exact code references and screenshots.",
                "Document runtime architecture, deployment topology, and environment boundaries.",
                "Add automated tests for the most material API and payment workflows.",
                "Prepare a concise patentability memo distinguishing implementation evidence from aspirational roadmap items.",
                "Create a public-facing product capability summary that matches the codebase reality.",
            ],
            "disclaimer": "This score is evidence-based but heuristic. It is not a formal legal, patent, or certification opinion.",
        }

    def generate_report(self):
        print("Writing reports...")
        json_path = self.project_path / "certification_report.json"
        md_path = self.project_path / "certification_report.md"
        html_path = self.project_path / "certification_report.html"
        json_path.write_text(json.dumps(self.results, indent=2, ensure_ascii=False), encoding="utf-8")
        md_path.write_text(self._build_markdown_report(), encoding="utf-8")
        html_path.write_text(self._build_html_report(), encoding="utf-8")
        return {"json": str(json_path), "markdown": str(md_path), "html": str(html_path)}

    def _build_markdown_report(self):
        stats = self.results["statistics"]
        arch = self.results["architecture"]
        readiness = self.results["certification_readiness"]
        lines = [
            "# GTS Logistics Certification Report",
            "",
            f"- Inspection date: `{self.results['inspection_date']}`",
            f"- Project root: `{self.results['project_root']}`",
            "",
            "## Statistics",
            "",
            f"- Total files scanned: {stats['total_files']}",
            f"- Total lines scanned: {stats['total_lines']}",
            f"- Python files: {stats['python_files']}",
            f"- JavaScript files: {stats['javascript_files']}",
            f"- TypeScript files: {stats['typescript_files']}",
            f"- HTML files: {stats['html_files']}",
            f"- CSS files: {stats['css_files']}",
            "",
            "## Architecture",
            "",
            f"- Type: {arch['type']}",
            "- Layers:",
        ]
        for item in arch["layers"]:
            lines.append(f"  - {item}")
        lines.append("- Technologies:")
        for item in arch["technologies"]:
            lines.append(f"  - {item}")
        lines.extend(["", "## API Surface", "", f"- Detected endpoints: {len(self.results['api_endpoints'])}"])
        for endpoint in self.results["api_endpoints"][:30]:
            lines.append(f"  - `{endpoint['method']}` `{endpoint['path']}` ({endpoint['framework']}) in `{endpoint['file']}`")
        if len(self.results["api_endpoints"]) > 30:
            lines.append(f"  - ... and {len(self.results['api_endpoints']) - 30} more")
        lines.extend(["", "## AI and Automation Assets", "", f"- Bot-related files: {len(self.results['ai_bots'])}"])
        for item in self.results["ai_bots"][:30]:
            lines.append(f"  - `{item['name']}` in `{item['file']}`")
        if len(self.results["ai_bots"]) > 30:
            lines.append(f"  - ... and {len(self.results['ai_bots']) - 30} more")
        lines.extend(["", "## Database Models", "", f"- Model or migration artifacts: {len(self.results['database_models'])}"])
        for item in self.results["database_models"][:30]:
            label = item["table"] or item["name"]
            lines.append(f"  - `{label}` in `{item['file']}`")
        if len(self.results["database_models"]) > 30:
            lines.append(f"  - ... and {len(self.results['database_models']) - 30} more")
        lines.extend(["", "## Differentiated Feature Candidates", ""])
        for feature in self.results["unique_features"]:
            lines.extend([f"### {feature['name']}", "", feature["description"], "", f"- Confidence: {feature['confidence']}", "- Evidence:"])
            for evidence in feature["evidence"]:
                lines.append(f"  - `{evidence}`")
            lines.append("")
        lines.extend(["## Claim Candidates", ""])
        for claim in self.results["patent_claims"]:
            lines.extend([f"### Claim {claim['claim_number']}: {claim['title']}", "", claim["description"], "", f"- Confidence: {claim['confidence']}", "- Evidence:"])
            for evidence in claim["evidence"]:
                lines.append(f"  - `{evidence}`")
            lines.append("")
        lines.extend([
            "## Certification Readiness",
            "",
            f"- Overall score: {readiness['overall_score']}/100",
            f"- Status: {readiness['status']}",
            f"- Note: {readiness['disclaimer']}",
            "",
            "| Criterion | Score | Weight | Basis |",
            "|---|---:|---:|---|",
        ])
        for item in readiness["criteria"]:
            lines.append(f"| {item['name']} | {item['score']} | {int(item['weight'] * 100)}% | {item['basis']} |")
        lines.extend(["", "### Recommendations", ""])
        for item in readiness["recommendations"]:
            lines.append(f"- {item}")
        lines.append("")
        return "\n".join(lines)

    def _build_html_report(self):
        readiness = self.results["certification_readiness"]
        stats = self.results["statistics"]
        feature_cards = "\n".join(
            f"""
            <div class="feature-card">
              <h3>{html.escape(feature['name'])}</h3>
              <p>{html.escape(feature['description'])}</p>
              <p><strong>Confidence:</strong> {html.escape(feature['confidence'])}</p>
              <ul>{''.join(f'<li><code>{html.escape(e)}</code></li>' for e in feature['evidence'][:6])}</ul>
            </div>
            """
            for feature in self.results["unique_features"]
        )
        criteria_rows = "\n".join(
            f"<tr><td>{html.escape(item['name'])}</td><td>{item['score']}</td><td>{int(item['weight']*100)}%</td><td>{html.escape(item['basis'])}</td></tr>"
            for item in readiness["criteria"]
        )
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>GTS Logistics Certification Report</title>
  <style>
    body {{ font-family: Segoe UI, Arial, sans-serif; background: #f4f7fb; color: #1f2937; margin: 0; }}
    .wrap {{ max-width: 1100px; margin: 0 auto; padding: 24px; }}
    .hero {{ background: linear-gradient(135deg, #0f172a, #1d4ed8); color: white; padding: 28px; border-radius: 16px; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 16px; margin-top: 20px; }}
    .card, .feature-card {{ background: white; border-radius: 14px; padding: 18px; box-shadow: 0 8px 30px rgba(15, 23, 42, 0.08); }}
    .section {{ margin-top: 24px; }}
    h1, h2, h3 {{ margin-top: 0; }}
    table {{ width: 100%; border-collapse: collapse; background: white; border-radius: 14px; overflow: hidden; }}
    th, td {{ padding: 12px; border-bottom: 1px solid #e5e7eb; text-align: left; }}
    th {{ background: #eff6ff; }}
    code {{ background: #eff6ff; padding: 2px 6px; border-radius: 6px; }}
    .score {{ font-size: 36px; font-weight: 700; }}
  </style>
</head>
<body>
  <div class="wrap">
    <div class="hero">
      <h1>GTS Logistics Certification Report</h1>
      <p>Inspection date: {html.escape(self.results['inspection_date'])}</p>
      <p>Status: <strong>{html.escape(readiness['status'])}</strong></p>
      <div class="score">{readiness['overall_score']}/100</div>
    </div>
    <div class="section grid">
      <div class="card"><h3>Files scanned</h3><div class="score">{stats['total_files']}</div></div>
      <div class="card"><h3>Lines scanned</h3><div class="score">{stats['total_lines']}</div></div>
      <div class="card"><h3>API endpoints</h3><div class="score">{len(self.results['api_endpoints'])}</div></div>
      <div class="card"><h3>Bot-related files</h3><div class="score">{len(self.results['ai_bots'])}</div></div>
      <div class="card"><h3>Data models</h3><div class="score">{len(self.results['database_models'])}</div></div>
      <div class="card"><h3>Security files</h3><div class="score">{len(self.results['security_features'])}</div></div>
    </div>
    <div class="section">
      <h2>Readiness Criteria</h2>
      <table>
        <thead><tr><th>Criterion</th><th>Score</th><th>Weight</th><th>Basis</th></tr></thead>
        <tbody>{criteria_rows}</tbody>
      </table>
    </div>
    <div class="section">
      <h2>Differentiated Feature Candidates</h2>
      {feature_cards or '<div class="card">No feature candidates detected.</div>'}
    </div>
  </div>
</body>
</html>
"""


def parse_args():
    parser = argparse.ArgumentParser(description="Inspect the GTS Logistics repository and generate certification reports.")
    parser.add_argument("project_path", nargs="?", default=".", help="Project root path")
    return parser.parse_args()


def main():
    args = parse_args()
    inspector = GTSProjectCertificationInspector(args.project_path)
    inspector.run_full_inspection()
    report_files = inspector.generate_report()
    print("Reports generated:")
    for name, path in report_files.items():
        print(f"- {name}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
