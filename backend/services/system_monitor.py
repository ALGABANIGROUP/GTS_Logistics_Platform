import psutil
import platform
from datetime import datetime, timedelta
from typing import Dict
import logging

logger = logging.getLogger(__name__)

class SystemMonitor:
    """
    Simple system monitoring service
    """

    def __init__(self):
        self.start_time = datetime.now()
        logger.info("✅ System Monitor initialized")

    async def get_status(self) -> Dict:
        """Get system status"""
        try:
            return {
                "status": "healthy",
                "uptime": str(datetime.now() - self.start_time),
                "platform": platform.system(),
                "python_version": platform.python_version()
            }
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return {
                "status": "unknown",
                "uptime": "unknown",
                "platform": platform.system(),
                "python_version": platform.python_version()
            }

    async def get_metrics(self) -> Dict:
        """Get system metrics"""
        try:
            return {
                "cpu": psutil.cpu_percent(interval=1),
                "memory": psutil.virtual_memory().percent,
                "disk": psutil.disk_usage('/').percent
            }
        except Exception as e:
            logger.error(f"Error getting system metrics: {e}")
            return {
                "cpu": 0,
                "memory": 0,
                "disk": 0
            }