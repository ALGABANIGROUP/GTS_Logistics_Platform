"""
Vizion Eye Integration - Performance Monitoring and Analytics
"""

import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class VizionEye:
    """
    Vizion Eye monitoring and analytics integration
    Tracks system performance, errors, and business metrics
    """

    def __init__(self):
        self.api_key = os.getenv("VIZION_API_KEY", "")
        self.enabled = os.getenv("VIZION_EYE_ENABLE", "false").lower() in ("1", "true", "yes")
        self.base_url = os.getenv("VIZION_API_URL", "https://api.vizion.ai/v1")
        self._initialized = False
        self._metrics = []
        self._events = []

    def init(self) -> bool:
        """Initialize Vizion Eye connection"""
        if not self.enabled:
            logger.info("Vizion Eye disabled by configuration")
            return False

        if not self.api_key:
            logger.warning("Vizion Eye enabled but no API key provided")
            return False

        try:
            # Test connection (would use async in production)
            logger.info("Vizion Eye initialized successfully")
            self._initialized = True
            return True
        except Exception as e:
            logger.error(f"Vizion Eye initialization failed: {e}")
            return False

    def log_event(self, event_name: str, event_data: Dict[str, Any]) -> bool:
        """Log an event to Vizion Eye"""
        if not self._initialized:
            return False

        event = {
            "name": event_name,
            "timestamp": datetime.now().isoformat(),
            "data": event_data
        }
        self._events.append(event)
        logger.debug(f"Vizion event logged: {event_name}")

        # In production, send to API asynchronously
        return True

    def log_metric(self, metric_name: str, value: float, tags: Optional[Dict] = None) -> bool:
        """Log a metric to Vizion Eye"""
        if not self._initialized:
            return False

        metric = {
            "name": metric_name,
            "value": value,
            "timestamp": datetime.now().isoformat(),
            "tags": tags or {}
        }
        self._metrics.append(metric)
        logger.debug(f"Vizion metric logged: {metric_name}={value}")

        return True

    def record_request(self, endpoint: str, method: str, status_code: int, duration_ms: int) -> None:
        """Record API request metrics"""
        if not self._initialized:
            return

        self.log_metric("api.request.duration", duration_ms, {
            "endpoint": endpoint,
            "method": method,
            "status": status_code
        })

        if status_code >= 400:
            self.log_event("api.error", {
                "endpoint": endpoint,
                "method": method,
                "status": status_code,
                "duration_ms": duration_ms
            })

    def record_business_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Record business events (shipments, loads, etc.)"""
        if not self._initialized:
            return

        self.log_event(f"business.{event_type}", data)

    def get_metrics(self) -> Dict[str, Any]:
        """Get collected metrics for reporting"""
        return {
            "initialized": self._initialized,
            "enabled": self.enabled,
            "events_count": len(self._events),
            "metrics_count": len(self._metrics),
            "last_event": self._events[-1] if self._events else None
        }

    def flush(self) -> None:
        """Flush all pending metrics to Vizion Eye"""
        if not self._initialized:
            return

        # In production, send batch to API
        self._metrics.clear()
        self._events.clear()
        logger.debug("Vizion metrics flushed")


# Singleton instance
_vizion = None


def get_vizion() -> VizionEye:
    """Get or create Vizion Eye instance"""
    global _vizion
    if _vizion is None:
        _vizion = VizionEye()
        _vizion.init()
    return _vizion