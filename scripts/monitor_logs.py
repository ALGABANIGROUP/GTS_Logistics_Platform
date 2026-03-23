#!/usr/bin/env python3
"""
Log monitoring script for incident detection
"""

import asyncio
import sys
import os
from pathlib import Path
import re
from datetime import datetime
import requests

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.services.incident_tracker import IncidentTracker

async def monitor_logs():
    """
    Monitor logs for errors
    """
    tracker = IncidentTracker()

    # Get log path from environment or use default
    log_path_str = os.getenv('LOG_PATH', 'logs/app.log')
    log_path = Path(log_path_str)

    # Create directory if it doesn't exist
    log_path.parent.mkdir(parents=True, exist_ok=True)

    if not log_path.exists():
        print(f"⚠️  Log file not found: {log_path}")
        print("   Creating empty log file for monitoring...")
        log_path.touch()
        print("   ✅ Log file created. Monitoring will start now.")

    print(f"📡 Monitoring logs for errors: {log_path} (Press Ctrl+C to stop)")

    try:
        with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
            # Go to end of file
            f.seek(0, 2)

            while True:
                line = f.readline()
                if not line:
                    await asyncio.sleep(1)
                    continue

                # Search for errors
                if re.search(r'ERROR|CRITICAL|Exception', line, re.IGNORECASE):
                    print(f"\n🚨 Error detected at {datetime.now().isoformat()}")
                    print(f"   {line[:200]}")

                    # Extract error information
                    error_data = {
                        "service": "application",
                        "error": line[:500],
                        "description": "Error detected in logs",
                        "traceback": line,
                        "affected_users": 0
                    }

                    # Record incident
                    incident = tracker.capture_error(error_data)
                    print(f"   📋 Incident created: {incident.id}")

                    # Send notification (optional)
                    # requests.post("http://localhost:8000/api/v1/incidents/capture", json=error_data)

    except KeyboardInterrupt:
        print("\n👋 Monitoring stopped")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(monitor_logs())