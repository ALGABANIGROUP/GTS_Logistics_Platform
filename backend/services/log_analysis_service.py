import re
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict
import logging
import json

logger = logging.getLogger(__name__)

class LogAnalysisService:
    """
    Security Log Analysis Service - Searches for suspicious activities in real logs
    """

    def __init__(self, log_path: str = "logs/app.log"):
        self.log_path = Path(log_path)

        # Patterns of suspicious activities
        self.suspicious_patterns = [
            (r'(?i)login.*failed', "Failed login attempt"),
            (r'(?i)unauthorized', "Unauthorized access attempt"),
            (r'(?i)error.*500', "Server error (possible exploit)"),
            (r'(?i)sql.*injection', "Potential SQL injection"),
            (r'(?i)xss', "Potential XSS attack"),
            (r'(?i)403', "Forbidden access"),
            (r'(?i)multiple.*failed', "Brute force attempt"),
            (r'(?i)invalid.*token', "Invalid token usage"),
            (r'(?i)api.*key.*invalid', "Invalid API key"),
            (r'(?i)path.*traversal', "Path traversal attempt")
        ]

        logger.info("✅ Log Analysis Service initialized")

    def analyze_logs(self, hours: int = 24) -> Dict:
        """
        Analyze logs to search for suspicious activities
        """
        if not self.log_path.exists():
            return {
                "success": True,
                "message": "No log file found",
                "suspicious_events": [],
                "stats": {"total_events": 0, "unique_ips": []}
            }

        suspicious_events = []
        unique_ips = set()
        events_by_type = {}

        cutoff_time = datetime.now() - timedelta(hours=hours)

        with open(self.log_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                # Extract time (simple simulation)
                # In reality, we use regex to extract real time

                for pattern, description in self.suspicious_patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        # Extract IP (simulation)
                        ip_match = re.search(r'\d+\.\d+\.\d+\.\d+', line)
                        ip = ip_match.group() if ip_match else "unknown"
                        unique_ips.add(ip)

                        event = {
                            "timestamp": datetime.now().isoformat(),
                            "description": description,
                            "ip": ip,
                            "log_line": line[:200]
                        }
                        suspicious_events.append(event)

                        events_by_type[description] = events_by_type.get(description, 0) + 1
                        break

        return {
            "success": True,
            "period_hours": hours,
            "total_suspicious": len(suspicious_events),
            "unique_ips": list(unique_ips),
            "events_by_type": events_by_type,
            "suspicious_events": suspicious_events[-50:],  # Last 50 events
            "recommendation": self._get_recommendation(events_by_type),
            "timestamp": datetime.now().isoformat()
        }

    def _get_recommendation(self, events_by_type: Dict) -> str:
        """Generate recommendation based on analysis"""
        if not events_by_type:
            return "No suspicious activity detected"

        if "Failed login attempt" in events_by_type and events_by_type["Failed login attempt"] > 10:
            return "High number of failed login attempts - consider implementing rate limiting"

        if "Unauthorized access attempt" in events_by_type:
            return "Unauthorized access detected - review access controls"

        if "Server error" in events_by_type:
            return "Server errors detected - review application logs for details"

        return "Monitor suspicious activity"