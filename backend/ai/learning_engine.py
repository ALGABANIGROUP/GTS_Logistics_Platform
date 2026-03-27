"""
Self-Learning Engine for AI Bots
Implements continuous learning from data sources and feedback
"""

import logging
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    np = None  # type: ignore[assignment]
    NUMPY_AVAILABLE = False

logger = logging.getLogger(__name__)


def _mean(values: List[float], default: float = 0.0) -> float:
    if not values:
        return default
    if NUMPY_AVAILABLE and np is not None:
        return float(np.mean(values))
    return float(sum(values) / len(values))


class LearningIntensity(str, Enum):
    """Learning intensity levels"""
    LOW = "low"          # Conservative adjustments
    MEDIUM = "medium"    # Balanced learning
    HIGH = "high"        # Aggressive optimization


class LearningFrequency(str, Enum):
    """Learning update frequency"""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"


@dataclass
class BotLearningProfile:
    """Bot learning profile and history"""
    bot_id: str
    bot_name: str
    enabled: bool
    frequency: LearningFrequency
    intensity: LearningIntensity
    data_sources: List[str]  # ["error_logs", "performance_metrics", "user_feedback"]
    
    # Learning metrics
    total_samples_processed: int = 0
    accuracy_score: float = 0.0
    performance_score: float = 0.0
    reliability_score: float = 0.0
    
    # Adaptation history
    adaptations_applied: int = 0
    last_learning_update: Optional[str] = None
    next_learning_update: Optional[str] = None
    
    # Data collection
    error_count: int = 0
    success_count: int = 0
    feedback_entries: int = 0


@dataclass
class DataSample:
    """A single data sample for learning"""
    timestamp: str
    bot_id: str
    sample_type: str  # "error", "performance", "feedback"
    data: Dict[str, Any]
    priority: float = 1.0  # Weight for learning


class BotLearningEngine:
    """Core self-learning engine for bots"""
    
    def __init__(self):
        self.learning_profiles: Dict[str, BotLearningProfile] = {}
        self.data_samples: Dict[str, List[DataSample]] = defaultdict(list)
        self.bot_behaviors: Dict[str, Dict[str, Any]] = {}  # Adaptive behaviors
        self.learning_history: Dict[str, List[Dict]] = defaultdict(list)
        
    def register_bot(
        self,
        bot_id: str,
        bot_name: str,
        enabled: bool = True,
        frequency: str = "daily",
        intensity: str = "medium",
        data_sources: Optional[List[str]] = None
    ) -> BotLearningProfile:
        """Register a bot for self-learning"""
        if data_sources is None:
            data_sources = ["error_logs", "performance_metrics", "user_feedback"]
            
        profile = BotLearningProfile(
            bot_id=bot_id,
            bot_name=bot_name,
            enabled=enabled,
            frequency=LearningFrequency(frequency),
            intensity=LearningIntensity(intensity),
            data_sources=data_sources,
            next_learning_update=self._calculate_next_update(frequency)
        )
        
        self.learning_profiles[bot_id] = profile
        self.bot_behaviors[bot_id] = self._initialize_behaviors(intensity)
        logger.info(f"Bot {bot_name} registered for self-learning")
        
        return profile
    
    def add_error_data(self, bot_id: str, error_info: Dict[str, Any]) -> None:
        """Add error sample to learning data"""
        if bot_id not in self.learning_profiles:
            logger.warning(f"Bot {bot_id} not registered")
            return
            
        if not self.learning_profiles[bot_id].enabled:
            return
            
        sample = DataSample(
            timestamp=datetime.utcnow().isoformat(),
            bot_id=bot_id,
            sample_type="error",
            data=error_info,
            priority=2.0  # Errors have higher priority
        )
        
        self.data_samples[bot_id].append(sample)
        self.learning_profiles[bot_id].error_count += 1
        logger.debug(f"Error data added for {bot_id}")
    
    def add_performance_data(self, bot_id: str, metrics: Dict[str, Any]) -> None:
        """Add performance metric sample to learning data"""
        if bot_id not in self.learning_profiles:
            logger.warning(f"Bot {bot_id} not registered")
            return
            
        if not self.learning_profiles[bot_id].enabled:
            return
            
        sample = DataSample(
            timestamp=datetime.utcnow().isoformat(),
            bot_id=bot_id,
            sample_type="performance",
            data=metrics,
            priority=1.5
        )
        
        self.data_samples[bot_id].append(sample)
        logger.debug(f"Performance data added for {bot_id}")
    
    def add_user_feedback(self, bot_id: str, feedback: Dict[str, Any]) -> None:
        """Add user feedback sample"""
        if bot_id not in self.learning_profiles:
            logger.warning(f"Bot {bot_id} not registered")
            return
            
        if not self.learning_profiles[bot_id].enabled:
            return
            
        sample = DataSample(
            timestamp=datetime.utcnow().isoformat(),
            bot_id=bot_id,
            sample_type="feedback",
            data=feedback,
            priority=1.0
        )
        
        self.data_samples[bot_id].append(sample)
        self.learning_profiles[bot_id].feedback_entries += 1
        logger.debug(f"User feedback added for {bot_id}")
    
    def should_learn(self, bot_id: str) -> bool:
        """Check if bot should perform learning update"""
        if bot_id not in self.learning_profiles:
            return False
            
        profile = self.learning_profiles[bot_id]
        if not profile.enabled:
            return False
            
        if not profile.next_learning_update:
            return False
            
        next_update = datetime.fromisoformat(profile.next_learning_update)
        return datetime.utcnow() >= next_update
    
    def perform_learning(self, bot_id: str) -> Dict[str, Any]:
        """Execute learning update for a bot"""
        if bot_id not in self.learning_profiles:
            return {"error": f"Bot {bot_id} not found"}
            
        profile = self.learning_profiles[bot_id]
        samples = self.data_samples[bot_id]
        
        if not samples:
            logger.info(f"No samples to learn from for {bot_id}")
            return {
                "bot_id": bot_id,
                "samples_processed": 0,
                "status": "no_data",
                "adaptations": []
            }
        
        # Analyze data samples
        analysis = self._analyze_samples(samples, profile)
        
        # Generate adaptations based on learning intensity
        adaptations = self._generate_adaptations(analysis, profile)
        
        # Apply adaptations to bot behavior
        self._apply_adaptations(bot_id, adaptations)
        
        # Update scores
        self._update_learning_scores(profile, analysis, adaptations)
        
        # Record learning history
        self._record_learning_history(bot_id, analysis, adaptations)
        
        # Schedule next learning update
        profile.next_learning_update = self._calculate_next_update(profile.frequency.value)
        profile.last_learning_update = datetime.utcnow().isoformat()
        profile.total_samples_processed += len(samples)
        profile.adaptations_applied += len(adaptations)
        
        # Clear old samples (keep last 1000)
        self.data_samples[bot_id] = samples[-1000:]
        
        logger.info(f"Learning update completed for {bot_id}: {len(adaptations)} adaptations")
        
        return {
            "bot_id": bot_id,
            "samples_processed": len(samples),
            "status": "success",
            "adaptations": adaptations,
            "metrics": {
                "accuracy": profile.accuracy_score,
                "performance": profile.performance_score,
                "reliability": profile.reliability_score
            }
        }
    
    def _analyze_samples(
        self,
        samples: List[DataSample],
        profile: BotLearningProfile
    ) -> Dict[str, Any]:
        """Analyze collected data samples"""
        error_samples = [s for s in samples if s.sample_type == "error"]
        performance_samples = [s for s in samples if s.sample_type == "performance"]
        feedback_samples = [s for s in samples if s.sample_type == "feedback"]
        
        # Calculate error patterns
        error_types = defaultdict(int)
        error_severity = []
        for sample in error_samples:
            error_type = sample.data.get("error_type", "unknown")
            error_types[error_type] += 1
            severity = sample.data.get("severity", 1.0)
            error_severity.append(severity)
        
        # Calculate performance metrics
        response_times = []
        accuracies = []
        for sample in performance_samples:
            rt = sample.data.get("response_time", 0)
            response_times.append(rt)
            acc = sample.data.get("accuracy", 0.5)
            accuracies.append(acc)
        
        # Calculate feedback scores
        feedback_scores = []
        for sample in feedback_samples:
            score = sample.data.get("rating", 3) / 5.0  # Normalize to 0-1
            feedback_scores.append(score)
        
        return {
            "error_count": len(error_samples),
            "error_types": dict(error_types),
            "avg_error_severity": _mean(error_severity, 0),
            "performance_count": len(performance_samples),
            "avg_response_time": _mean(response_times, 0),
            "avg_accuracy": _mean(accuracies, 0.5),
            "feedback_count": len(feedback_samples),
            "avg_feedback_score": _mean(feedback_scores, 0.5),
        }
    
    def _generate_adaptations(
        self,
        analysis: Dict[str, Any],
        profile: BotLearningProfile
    ) -> List[Dict[str, Any]]:
        """Generate behavior adaptations based on analysis"""
        adaptations = []
        intensity_multiplier = {
            LearningIntensity.LOW: 0.5,
            LearningIntensity.MEDIUM: 1.0,
            LearningIntensity.HIGH: 1.5
        }.get(profile.intensity, 1.0)
        
        # Adaptation 1: Improve error handling
        if analysis["error_count"] > 0:
            error_reduction = min(0.1 * intensity_multiplier, 0.3)
            adaptations.append({
                "type": "error_handling",
                "description": f"Reduce errors by {error_reduction*100:.1f}%",
                "adjustment": -error_reduction,
                "target_metric": "error_rate"
            })
        
        # Adaptation 2: Optimize response time
        if analysis["avg_response_time"] > 100:  # ms
            time_reduction = min(0.05 * intensity_multiplier, 0.2)
            adaptations.append({
                "type": "performance",
                "description": f"Reduce response time by {time_reduction*100:.1f}%",
                "adjustment": -time_reduction,
                "target_metric": "response_time"
            })
        
        # Adaptation 3: Improve accuracy
        if analysis["avg_accuracy"] < 0.9:
            accuracy_gain = min(0.05 * intensity_multiplier, 0.15)
            adaptations.append({
                "type": "accuracy",
                "description": f"Increase accuracy by {accuracy_gain*100:.1f}%",
                "adjustment": accuracy_gain,
                "target_metric": "accuracy"
            })
        
        # Adaptation 4: Handle specific error types
        for error_type, count in analysis["error_types"].items():
            if count > 2:
                adaptations.append({
                    "type": "error_specific",
                    "error_type": error_type,
                    "description": f"Handle {error_type} errors with improved logic",
                    "action": "implement_handler"
                })
        
        # Adaptation 5: Respond to feedback
        if analysis["avg_feedback_score"] < 3.5 / 5.0:
            adaptations.append({
                "type": "user_experience",
                "description": "Improve user-facing interactions based on feedback",
                "adjustment": 0.1 * intensity_multiplier,
                "target_metric": "user_satisfaction"
            })
        
        return adaptations
    
    def _apply_adaptations(self, bot_id: str, adaptations: List[Dict[str, Any]]) -> None:
        """Apply generated adaptations to bot behavior"""
        if bot_id not in self.bot_behaviors:
            self.bot_behaviors[bot_id] = {}
            
        for adaptation in adaptations:
            if adaptation["type"] == "error_handling":
                self.bot_behaviors[bot_id]["error_threshold"] = \
                    self.bot_behaviors[bot_id].get("error_threshold", 1.0) + adaptation["adjustment"]
            
            elif adaptation["type"] == "performance":
                self.bot_behaviors[bot_id]["response_time_target"] = \
                    max(50, (self.bot_behaviors[bot_id].get("response_time_target", 200) or 200) * (1 + adaptation["adjustment"]))
            
            elif adaptation["type"] == "accuracy":
                self.bot_behaviors[bot_id]["accuracy_threshold"] = \
                    min(1.0, (self.bot_behaviors[bot_id].get("accuracy_threshold", 0.8) or 0.8) + adaptation["adjustment"])
            
            elif adaptation["type"] == "error_specific":
                handlers = self.bot_behaviors[bot_id].get("error_handlers", {})
                handlers[adaptation["error_type"]] = "improved_handler_v1"
                self.bot_behaviors[bot_id]["error_handlers"] = handlers
    
    def _update_learning_scores(
        self,
        profile: BotLearningProfile,
        analysis: Dict[str, Any],
        adaptations: List[Dict[str, Any]]
    ) -> None:
        """Update bot learning and performance scores"""
        # Accuracy score: based on observed accuracy with adaptation bonus
        base_accuracy = analysis["avg_accuracy"]
        adaptation_bonus = min(len(adaptations) * 0.02, 0.1)
        profile.accuracy_score = min(1.0, base_accuracy + adaptation_bonus)
        
        # Performance score: based on response time
        # Optimal response time is 100ms
        response_time = analysis["avg_response_time"]
        if response_time <= 100:
            perf_score = 1.0
        elif response_time <= 200:
            perf_score = 1.0 - (response_time - 100) / 100 * 0.5
        else:
            perf_score = max(0.3, 0.5 - (response_time - 200) / 1000)
        profile.performance_score = perf_score
        
        # Reliability score: based on error rate
        error_rate = analysis["error_count"] / max(1, analysis["error_count"] + analysis["performance_count"])
        profile.reliability_score = 1.0 - error_rate
    
    def _record_learning_history(
        self,
        bot_id: str,
        analysis: Dict[str, Any],
        adaptations: List[Dict[str, Any]]
    ) -> None:
        """Record learning event in history"""
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "analysis": analysis,
            "adaptations_count": len(adaptations),
            "adaptations": adaptations
        }
        self.learning_history[bot_id].append(event)
        
        # Keep last 100 learning events
        self.learning_history[bot_id] = self.learning_history[bot_id][-100:]
    
    def _calculate_next_update(self, frequency: str) -> str:
        """Calculate next learning update time"""
        now = datetime.utcnow()
        
        if frequency == "hourly":
            next_time = now + timedelta(hours=1)
        elif frequency == "daily":
            next_time = now + timedelta(days=1)
        elif frequency == "weekly":
            next_time = now + timedelta(weeks=1)
        else:
            next_time = now + timedelta(days=1)
        
        return next_time.isoformat()
    
    def _initialize_behaviors(self, intensity: str) -> Dict[str, Any]:
        """Initialize bot behavior parameters based on learning intensity"""
        return {
            "error_threshold": 1.0,
            "response_time_target": 200,
            "accuracy_threshold": 0.8,
            "error_handlers": {},
            "learning_intensity": intensity,
            "adaptation_history": []
        }
    
    def get_bot_profile(self, bot_id: str) -> Optional[Dict[str, Any]]:
        """Get learning profile for a bot"""
        if bot_id not in self.learning_profiles:
            return None
            
        profile = self.learning_profiles[bot_id]
        return {
            "bot_id": profile.bot_id,
            "bot_name": profile.bot_name,
            "enabled": profile.enabled,
            "frequency": profile.frequency.value,
            "intensity": profile.intensity.value,
            "data_sources": profile.data_sources,
            "total_samples_processed": profile.total_samples_processed,
            "accuracy_score": profile.accuracy_score,
            "performance_score": profile.performance_score,
            "reliability_score": profile.reliability_score,
            "adaptations_applied": profile.adaptations_applied,
            "last_learning_update": profile.last_learning_update,
            "next_learning_update": profile.next_learning_update,
            "error_count": profile.error_count,
            "success_count": profile.success_count,
            "feedback_entries": profile.feedback_entries,
            "behaviors": self.bot_behaviors.get(bot_id, {}),
            "learning_history": self.learning_history.get(bot_id, [])[-10:]  # Last 10 events
        }
    
    def get_learning_stats(self) -> Dict[str, Any]:
        """Get overall learning system statistics"""
        per_bot_stats = {}
        for bot_id, profile in self.learning_profiles.items():
            sample_count = len(self.data_samples.get(bot_id, []))
            per_bot_stats[bot_id] = {
                "enabled": profile.enabled,
                "samples": sample_count,
                "adaptations": profile.adaptations_applied,
                "accuracy_score": profile.accuracy_score,
                "performance_score": profile.performance_score,
                "reliability_score": profile.reliability_score,
                "last_learning_update": profile.last_learning_update,
                "next_learning_update": profile.next_learning_update,
            }
        return {
            "total_bots_registered": len(self.learning_profiles),
            "enabled_bots": sum(1 for p in self.learning_profiles.values() if p.enabled),
            "total_samples_collected": sum(len(s) for s in self.data_samples.values()),
            "total_adaptations": sum(p.adaptations_applied for p in self.learning_profiles.values()),
            "average_accuracy": _mean([p.accuracy_score for p in self.learning_profiles.values()], 0),
            "average_performance": _mean([p.performance_score for p in self.learning_profiles.values()], 0),
            "average_reliability": _mean([p.reliability_score for p in self.learning_profiles.values()], 0),
            "per_bot": per_bot_stats,
        }


# Global learning engine instance
bot_learning_engine = BotLearningEngine()
