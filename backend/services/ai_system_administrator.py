from __future__ import annotations

try:
    import psutil
except Exception:
    psutil = None


def system_health_check() -> dict:
    """Monitor system health and analyze performance."""
    if psutil is None:
        return {
            "CPU Usage": "unavailable",
            "Memory Usage": "unavailable",
            "error": "psutil_not_installed",
        }

    cpu_usage = psutil.cpu_percent(interval=1)
    memory_usage = psutil.virtual_memory().percent

    return {
        "CPU Usage": f"{cpu_usage}%",
        "Memory Usage": f"{memory_usage}%",
    }
