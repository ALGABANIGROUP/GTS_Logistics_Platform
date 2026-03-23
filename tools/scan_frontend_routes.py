# tools/scan_frontend_routes.py
import re
from pathlib import Path
from typing import List, Tuple

# Configure your frontend source directory here
FRONTEND_SRC = Path(__file__).resolve().parent.parent / "frontend" / "src"

# File extensions to scan
EXTENSIONS = {".ts", ".tsx", ".js", ".jsx"}

# Regex patterns to detect API calls
FETCH_PATTERN = re.compile(
    r"(fetch)\s*\(\s*([\"'])(/[^\"']+)\2", re.MULTILINE
)

AXIOS_PATTERN = re.compile(
    r"(axios\.(get|post|put|delete|patch))\s*\(\s*([\"'])(/[^\"']+)\3",
    re.MULTILINE,
)

CLIENT_PATTERN = re.compile(
    r"(\w+Client\.(get|post|put|delete|patch))\s*\(\s*([\"'])(/[^\"']+)\3",
    re.MULTILINE,
)

RAW_API_STRING_PATTERN = re.compile(
    r"([\"'])(/api/v[0-9]/[^\"']+)\1", re.MULTILINE
)


def find_api_calls_in_text(text: str) -> List[Tuple[str, str]]:
    """
    Returns a list of (method, path) tuples detected in the given text.
    """
    results: List[Tuple[str, str]] = []

    # fetch("/api/...")
    for match in FETCH_PATTERN.finditer(text):
        _, _, path = match.groups()
        results.append(("FETCH", path))

    # axios.get("/api/...")
    for match in AXIOS_PATTERN.finditer(text):
        full, method, _, path = match.groups()
        results.append((method.upper(), path))

    # apiClient.get("/api/...")
    for match in CLIENT_PATTERN.finditer(text):
        full, method, _, path = match.groups()
        results.append((method.upper(), path))

    # Any "/api/v1/..." string
    for match in RAW_API_STRING_PATTERN.finditer(text):
        _, path = match.groups()
        if not any(path == existing[1] for existing in results):
            results.append(("UNKNOWN", path))

    return results


def scan_file(path: Path) -> List[Tuple[int, str, str]]:
    """
    Scan a single file and return list of (line_number, method, path).
    """
    try:
        content = path.read_text(encoding="utf-8")
    except Exception:
        return []

    api_calls = find_api_calls_in_text(content)
    if not api_calls:
        return []

    lines = content.splitlines()
    results: List[Tuple[int, str, str]] = []

    for method, api_path in api_calls:
        for idx, line in enumerate(lines, start=1):
            if api_path in line:
                results.append((idx, method, api_path))
                break

    return results


def scan_frontend():
    if not FRONTEND_SRC.exists():
        print(f"[ERROR] Frontend src directory not found: {FRONTEND_SRC}")
        return

    print(f"[INFO] Scanning frontend directory: {FRONTEND_SRC}")
    print("file, line, method, path")

    for path in FRONTEND_SRC.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() not in EXTENSIONS:
            continue

        findings = scan_file(path)
        for line_no, method, api_path in findings:
            rel = path.relative_to(FRONTEND_SRC.parent)
            print(f"{rel}, {line_no}, {method}, {api_path}")


if __name__ == "__main__":
    scan_frontend()
