"""
Data Collection Pipeline for Bot Learning
Collects errors, performance metrics, and user feedback
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass
import asyncio

logger = logging.getLogger(__name__)


@dataclass
class ErrorLog:
    """Error log entry for learning"""
    bot_id: str
    error_type: str
    error_message: str
    severity: float  # 0-1
    timestamp: str
    traceback: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


@dataclass
class PerformanceMetric:
    """Performance metric for learning"""
    bot_id: str
    response_time: float  # milliseconds
    accuracy: float  # 0-1
    throughput: float  # requests/second
    resource_usage: Dict[str, float]  # CPU%, memory%
    timestamp: str
    context: Optional[Dict[str, Any]] = None


@dataclass
class UserFeedback:
    """User feedback entry for learning"""
    bot_id: str
    rating: int  # 1-5
    comment: Optional[str]
    user_id: Optional[str]
    session_id: str
    timestamp: str
    feedback_type: str = "general"  # general, performance, accuracy, ux
    tags: Optional[List[str]] = None


class DataCollectionService:
    """Service for collecting learning data from multiple sources"""
    
    def __init__(self):
        self.error_logs: List[ErrorLog] = []
        self.performance_metrics: List[PerformanceMetric] = []
        self.user_feedback: List[UserFeedback] = []
        self.collection_stats = {
            "errors_collected": 0,
            "metrics_collected": 0,
            "feedback_collected": 0,
            "last_collection_time": None
        }
    
    def log_bot_error(
        self,
        bot_id: str,
        error_type: str,
        error_message: str,
        severity: float = 1.0,
        traceback: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log an error from a bot"""
        error_log = ErrorLog(
            bot_id=bot_id,
            error_type=error_type,
            error_message=error_message,
            severity=min(1.0, max(0.0, severity)),
            timestamp=datetime.utcnow().isoformat(),
            traceback=traceback,
            context=context or {}
        )
        
        self.error_logs.append(error_log)
        self.collection_stats["errors_collected"] += 1
        
        logger.debug(f"Error logged for bot {bot_id}: {error_type}")

    def record_error(
        self,
        bot_id: str,
        error_type: str,
        error_message: str,
        context: Optional[Dict[str, Any]] = None,
        severity: float = 1.0,
        traceback: Optional[str] = None,
    ) -> None:
        """Compatibility alias for logging bot errors."""
        self.log_bot_error(
            bot_id=bot_id,
            error_type=error_type,
            error_message=error_message,
            severity=severity,
            traceback=traceback,
            context=context,
        )
    
    def record_performance(
        self,
        bot_id: str,
        response_time: float,
        accuracy: float,
        throughput: float = 1.0,
        resource_usage: Optional[Dict[str, float]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Record performance metrics for a bot"""
        metric = PerformanceMetric(
            bot_id=bot_id,
            response_time=response_time,
            accuracy=min(1.0, max(0.0, accuracy)),
            throughput=throughput,
            resource_usage=resource_usage or {"cpu_percent": 0, "memory_percent": 0},
            timestamp=datetime.utcnow().isoformat(),
            context=context or {}
        )
        
        self.performance_metrics.append(metric)
        self.collection_stats["metrics_collected"] += 1
        
        logger.debug(f"Performance metric recorded for bot {bot_id}")
    
    def collect_user_feedback(
        self,
        bot_id: str,
        rating: int,
        session_id: str,
        comment: Optional[str] = None,
        user_id: Optional[str] = None,
        feedback_type: str = "general",
        tags: Optional[List[str]] = None
    ) -> None:
        """Collect user feedback for a bot"""
        feedback = UserFeedback(
            bot_id=bot_id,
            rating=min(5, max(1, rating)),
            comment=comment,
            user_id=user_id,
            session_id=session_id,
            timestamp=datetime.utcnow().isoformat(),
            feedback_type=feedback_type,
            tags=tags or []
        )
        
        self.user_feedback.append(feedback)
        self.collection_stats["feedback_collected"] += 1
        
        logger.debug(f"User feedback recorded for bot {bot_id}: rating {rating}/5")

    def record_feedback(
        self,
        bot_id: str,
        rating: int,
        feedback_text: Optional[str] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        feedback_type: str = "general",
        tags: Optional[List[str]] = None,
    ) -> None:
        """Compatibility alias for collecting user feedback."""
        resolved_session_id = session_id or f"{bot_id}-{datetime.utcnow().timestamp():.0f}"
        self.collect_user_feedback(
            bot_id=bot_id,
            rating=rating,
            session_id=resolved_session_id,
            comment=feedback_text,
            user_id=user_id,
            feedback_type=feedback_type,
            tags=tags,
        )
    
    def get_bot_error_logs(
        self,
        bot_id: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get error logs for a specific bot"""
        bot_errors = [e for e in self.error_logs if e.bot_id == bot_id]
        
        # Sort by timestamp (most recent first)
        bot_errors.sort(key=lambda x: x.timestamp, reverse=True)
        
        return [
            {
                "error_type": e.error_type,
                "error_message": e.error_message,
                "severity": e.severity,
                "timestamp": e.timestamp,
                "traceback": e.traceback,
                "context": e.context
            }
            for e in bot_errors[:limit]
        ]
    
    def get_bot_performance_history(
        self,
        bot_id: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get performance history for a specific bot"""
        bot_metrics = [m for m in self.performance_metrics if m.bot_id == bot_id]
        
        # Sort by timestamp (most recent first)
        bot_metrics.sort(key=lambda x: x.timestamp, reverse=True)
        
        return [
            {
                "response_time": m.response_time,
                "accuracy": m.accuracy,
                "throughput": m.throughput,
                "resource_usage": m.resource_usage,
                "timestamp": m.timestamp,
                "context": m.context
            }
            for m in bot_metrics[:limit]
        ]
    
    def get_bot_feedback(
        self,
        bot_id: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get user feedback for a specific bot"""
        bot_feedback = [f for f in self.user_feedback if f.bot_id == bot_id]
        
        # Sort by timestamp (most recent first)
        bot_feedback.sort(key=lambda x: x.timestamp, reverse=True)
        
        return [
            {
                "rating": f.rating,
                "comment": f.comment,
                "user_id": f.user_id,
                "session_id": f.session_id,
                "timestamp": f.timestamp,
                "feedback_type": f.feedback_type,
                "tags": f.tags
            }
            for f in bot_feedback[:limit]
        ]
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get data collection statistics"""
        return {
            **self.collection_stats,
            "last_collection_time": datetime.utcnow().isoformat()
        }
    
    def get_bot_data_summary(self, bot_id: str) -> Dict[str, Any]:
        """Get summary of all collected data for a bot"""
        errors = [e for e in self.error_logs if e.bot_id == bot_id]
        metrics = [m for m in self.performance_metrics if m.bot_id == bot_id]
        feedback = [f for f in self.user_feedback if f.bot_id == bot_id]
        
        # Calculate averages
        avg_response_time = sum(m.response_time for m in metrics) / len(metrics) if metrics else 0
        avg_accuracy = sum(m.accuracy for m in metrics) / len(metrics) if metrics else 0
        avg_feedback_rating = sum(f.rating for f in feedback) / len(feedback) if feedback else 0
        
        error_types = {}
        for e in errors:
            error_types[e.error_type] = error_types.get(e.error_type, 0) + 1
        
        return {
            "bot_id": bot_id,
            "error_count": len(errors),
            "error_types": error_types,
            "avg_error_severity": sum(e.severity for e in errors) / len(errors) if errors else 0,
            "metric_count": len(metrics),
            "avg_response_time_ms": avg_response_time,
            "avg_accuracy": avg_accuracy,
            "feedback_count": len(feedback),
            "avg_feedback_rating": avg_feedback_rating,
            "data_collection_period": {
                "earliest": min([e.timestamp for e in errors + metrics + feedback], default=None),
                "latest": max([e.timestamp for e in errors + metrics + feedback], default=None)
            }
        }
    
    def export_learning_data(self, bot_id: str) -> Dict[str, Any]:
        """Export all learning data for a bot"""
        return {
            "bot_id": bot_id,
            "export_timestamp": datetime.utcnow().isoformat(),
            "error_logs": self.get_bot_error_logs(bot_id),
            "performance_metrics": self.get_bot_performance_history(bot_id),
            "user_feedback": self.get_bot_feedback(bot_id)
        }
    
    def cleanup_old_data(self, days_to_keep: int = 90) -> None:
        """Remove data older than specified days"""
        from datetime import timedelta
        
        cutoff_date = (datetime.utcnow() - timedelta(days=days_to_keep)).isoformat()
        
        initial_count = len(self.error_logs) + len(self.performance_metrics) + len(self.user_feedback)
        
        self.error_logs = [e for e in self.error_logs if e.timestamp > cutoff_date]
        self.performance_metrics = [m for m in self.performance_metrics if m.timestamp > cutoff_date]
        self.user_feedback = [f for f in self.user_feedback if f.timestamp > cutoff_date]
        
        final_count = len(self.error_logs) + len(self.performance_metrics) + len(self.user_feedback)
        removed = initial_count - final_count
        
        logger.info(f"Data cleanup completed: removed {removed} old records")


# Global data collection service instance
data_collection_service = DataCollectionService()
