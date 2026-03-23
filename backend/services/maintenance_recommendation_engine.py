from typing import List, Dict, Any

# Simple recommendation rules: each rule returns a recommendation if its condition is met

def recommend_if_issue_type(issue: Dict[str, Any]) -> List[str]:
    if issue.get("type") == "overdue_maintenance":
        return ["Schedule immediate maintenance run"]
    if issue.get("type") == "missing_documentation":
        return ["Upload required maintenance documents"]
    return []

def recommend_if_run_failed(run: Dict[str, Any]) -> List[str]:
    if run.get("status") == "failed":
        return ["Investigate failure cause and retry run"]
    return []

# Main recommendation engine

def generate_recommendations(runs: List[Dict[str, Any]], issues: List[Dict[str, Any]]) -> List[str]:
    recs = []
    for issue in issues:
        recs.extend(recommend_if_issue_type(issue))
    for run in runs:
        recs.extend(recommend_if_run_failed(run))
    return list(set(recs))  # deduplicate recommendations
