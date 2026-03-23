from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List


class AutoDocumentation:
    def _format_changes(self, changes: List[str]) -> str:
        return "\n".join(f"- {c}" for c in (changes or []))

    def _format_tests(self, tests: List[str]) -> str:
        return "\n".join(f"- {t}" for t in (tests or []))

    def _format_metrics(self, metrics: Dict[str, Any]) -> str:
        return "\n".join(f"- {k}: {v}" for k, v in (metrics or {}).items())

    def _format_issues(self, issues: List[str]) -> str:
        return "\n".join(f"- {i}" for i in (issues or []))

    def _format_recommendations(self, recs: List[str]) -> str:
        return "\n".join(f"- {r}" for r in (recs or []))

    def generate_deployment_report(self, deployment_data: Dict[str, Any]) -> str:
        report = f"""
# Deployment Report - {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Deployment Details
- **Version:** {deployment_data.get('version')}
- **Environment:** {deployment_data.get('environment')}
- **Deployer:** {deployment_data.get('deployer')}
- **Duration:** {deployment_data.get('duration')}

## Key Changes
{self._format_changes(deployment_data.get('changes', []))}

## Completed Tests
{self._format_tests(deployment_data.get('tests', []))}

## Post-Deployment Metrics
{self._format_metrics(deployment_data.get('metrics', {}))}

## Discovered Issues
{self._format_issues(deployment_data.get('issues', []))}

## Recommendations
{self._format_recommendations(deployment_data.get('recommendations', []))}
"""
        path = f"./docs/deployments/report-{datetime.now().strftime('%Y%m%d')}.md"
        with open(path, "w", encoding="utf-8") as f:
            f.write(report)
        return report
