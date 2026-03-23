"""
Bot Learning API Routes
Endpoints for managing bot self-learning and feedback
"""

from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any, Optional, List
import logging

from backend.ai.learning_engine import bot_learning_engine, LearningFrequency, LearningIntensity
from backend.ai.data_collection_service import data_collection_service
from backend.services.learning_bootstrap import register_default_learning_bots

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai/learning", tags=["bot-learning"])


# Bot Learning Registration and Configuration
@router.post("/register")
async def register_bot_for_learning(
    bot_id: str,
    bot_name: str,
    enabled: bool = True,
    frequency: str = "daily",
    intensity: str = "medium",
    data_sources: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Register a bot for self-learning"""
    try:
        if frequency not in [f.value for f in LearningFrequency]:
            raise HTTPException(status_code=400, detail=f"Invalid frequency: {frequency}")
        
        if intensity not in [i.value for i in LearningIntensity]:
            raise HTTPException(status_code=400, detail=f"Invalid intensity: {intensity}")
        
        profile = bot_learning_engine.register_bot(
            bot_id=bot_id,
            bot_name=bot_name,
            enabled=enabled,
            frequency=frequency,
            intensity=intensity,
            data_sources=data_sources or ["error_logs", "performance_metrics", "user_feedback"]
        )
        
        return {
            "status": "success",
            "message": f"Bot {bot_name} registered for self-learning",
            "profile": bot_learning_engine.get_bot_profile(bot_id)
        }
    except Exception as e:
        logger.error(f"Bot registration failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/register-defaults")
async def register_default_bots_for_learning() -> Dict[str, Any]:
    """Register the default 16 bots for self-learning."""
    try:
        result = register_default_learning_bots()
        return {
            "status": "success",
            "message": "Default learning bots registered",
            **result,
        }
    except Exception as e:
        logger.error(f"Default bot registration failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/profile/{bot_id}")
async def get_bot_learning_profile(bot_id: str) -> Dict[str, Any]:
    """Get learning profile for a specific bot"""
    profile = bot_learning_engine.get_bot_profile(bot_id)
    if not profile:
        raise HTTPException(status_code=404, detail=f"Bot {bot_id} not found")
    
    return {
        "status": "success",
        "profile": profile
    }


@router.put("/profile/{bot_id}")
async def update_bot_learning_profile(
    bot_id: str,
    enabled: Optional[bool] = None,
    frequency: Optional[str] = None,
    intensity: Optional[str] = None,
    data_sources: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Update learning profile for a bot"""
    try:
        profile = bot_learning_engine.learning_profiles.get(bot_id)
        if not profile:
            raise HTTPException(status_code=404, detail=f"Bot {bot_id} not found")
        
        if enabled is not None:
            profile.enabled = enabled
        if frequency is not None:
            profile.frequency = LearningFrequency(frequency)
        if intensity is not None:
            profile.intensity = LearningIntensity(intensity)
        if data_sources is not None:
            profile.data_sources = data_sources
        
        logger.info(f"Updated learning profile for bot {bot_id}")
        
        return {
            "status": "success",
            "message": "Learning profile updated",
            "profile": bot_learning_engine.get_bot_profile(bot_id)
        }
    except Exception as e:
        logger.error(f"Profile update failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Data Collection Endpoints
@router.post("/data/error")
async def log_bot_error(
    bot_id: str,
    error_type: str = Body(...),
    error_message: str = Body(...),
    severity: float = Body(1.0),
    traceback: Optional[str] = Body(None),
    context: Optional[Dict[str, Any]] = Body(None)
) -> Dict[str, Any]:
    """Log an error from a bot"""
    try:
        data_collection_service.log_bot_error(
            bot_id=bot_id,
            error_type=error_type,
            error_message=error_message,
            severity=severity,
            traceback=traceback,
            context=context
        )
        
        # Add to learning engine
        bot_learning_engine.add_error_data(bot_id, {
            "error_type": error_type,
            "error_message": error_message,
            "severity": severity,
            "traceback": traceback,
            "context": context
        })
        
        return {
            "status": "success",
            "message": "Error logged and added to learning data"
        }
    except Exception as e:
        logger.error(f"Error logging failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/data/performance")
async def record_performance(
    bot_id: str,
    response_time: float = Body(...),
    accuracy: float = Body(...),
    throughput: float = Body(1.0),
    resource_usage: Optional[Dict[str, float]] = Body(None),
    context: Optional[Dict[str, Any]] = Body(None)
) -> Dict[str, Any]:
    """Record performance metrics for a bot"""
    try:
        data_collection_service.record_performance(
            bot_id=bot_id,
            response_time=response_time,
            accuracy=accuracy,
            throughput=throughput,
            resource_usage=resource_usage,
            context=context
        )
        
        # Add to learning engine
        bot_learning_engine.add_performance_data(bot_id, {
            "response_time": response_time,
            "accuracy": accuracy,
            "throughput": throughput,
            "resource_usage": resource_usage or {}
        })
        
        return {
            "status": "success",
            "message": "Performance metric recorded and added to learning data"
        }
    except Exception as e:
        logger.error(f"Performance recording failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/data/feedback")
async def collect_feedback(
    bot_id: str,
    rating: int = Body(...),
    session_id: str = Body(...),
    comment: Optional[str] = Body(None),
    user_id: Optional[str] = Body(None),
    feedback_type: str = Body("general"),
    tags: Optional[List[str]] = Body(None)
) -> Dict[str, Any]:
    """Collect user feedback for a bot"""
    try:
        if not 1 <= rating <= 5:
            raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
        
        data_collection_service.collect_user_feedback(
            bot_id=bot_id,
            rating=rating,
            session_id=session_id,
            comment=comment,
            user_id=user_id,
            feedback_type=feedback_type,
            tags=tags
        )
        
        # Add to learning engine
        bot_learning_engine.add_user_feedback(bot_id, {
            "rating": rating,
            "comment": comment,
            "user_id": user_id,
            "feedback_type": feedback_type,
            "tags": tags or []
        })
        
        return {
            "status": "success",
            "message": "User feedback recorded and added to learning data"
        }
    except Exception as e:
        logger.error(f"Feedback collection failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Learning Execution
@router.post("/trigger/{bot_id}")
async def trigger_learning(bot_id: str) -> Dict[str, Any]:
    """Manually trigger learning update for a bot"""
    try:
        profile = bot_learning_engine.learning_profiles.get(bot_id)
        if not profile:
            raise HTTPException(status_code=404, detail=f"Bot {bot_id} not found")
        
        if not profile.enabled:
            raise HTTPException(status_code=400, detail="Bot learning is disabled")
        
        result = bot_learning_engine.perform_learning(bot_id)
        
        return {
            "status": "success",
            "learning_result": result,
            "profile": bot_learning_engine.get_bot_profile(bot_id)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Learning trigger failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/check-and-update")
async def check_and_update_all_bots() -> Dict[str, Any]:
    """Check all bots and perform learning if needed"""
    try:
        results = {}
        
        for bot_id in bot_learning_engine.learning_profiles.keys():
            if bot_learning_engine.should_learn(bot_id):
                result = bot_learning_engine.perform_learning(bot_id)
                results[bot_id] = result
        
        return {
            "status": "success",
            "bots_updated": len(results),
            "learning_results": results,
            "stats": bot_learning_engine.get_learning_stats()
        }
    except Exception as e:
        logger.error(f"Batch learning update failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Statistics and Monitoring
@router.get("/stats")
async def get_learning_stats() -> Dict[str, Any]:
    """Get overall learning system statistics"""
    learning_stats = bot_learning_engine.get_learning_stats()
    collection_stats = data_collection_service.get_collection_stats()
    return {
        "status": "success",
        **learning_stats,
        "learning_stats": learning_stats,
        "collection_stats": collection_stats,
    }


@router.get("/data/summary/{bot_id}")
async def get_bot_data_summary(bot_id: str) -> Dict[str, Any]:
    """Get summary of collected data for a bot"""
    summary = data_collection_service.get_bot_data_summary(bot_id)
    
    if summary["error_count"] == 0 and summary["metric_count"] == 0 and summary["feedback_count"] == 0:
        return {
            "status": "warning",
            "message": "No data collected yet for this bot",
            "summary": summary
        }
    
    return {
        "status": "success",
        "summary": summary
    }


@router.get("/data/errors/{bot_id}")
async def get_bot_errors(bot_id: str, limit: int = 100) -> Dict[str, Any]:
    """Get error logs for a bot"""
    errors = data_collection_service.get_bot_error_logs(bot_id, limit)
    
    return {
        "status": "success",
        "bot_id": bot_id,
        "error_count": len(errors),
        "errors": errors
    }


@router.get("/data/performance/{bot_id}")
async def get_bot_performance(bot_id: str, limit: int = 100) -> Dict[str, Any]:
    """Get performance history for a bot"""
    metrics = data_collection_service.get_bot_performance_history(bot_id, limit)
    
    return {
        "status": "success",
        "bot_id": bot_id,
        "metric_count": len(metrics),
        "metrics": metrics
    }


@router.get("/data/feedback/{bot_id}")
async def get_bot_feedback(bot_id: str, limit: int = 100) -> Dict[str, Any]:
    """Get user feedback for a bot"""
    feedback = data_collection_service.get_bot_feedback(bot_id, limit)
    
    return {
        "status": "success",
        "bot_id": bot_id,
        "feedback_count": len(feedback),
        "feedback": feedback
    }


@router.get("/export/{bot_id}")
async def export_learning_data(bot_id: str) -> Dict[str, Any]:
    """Export all learning data for a bot"""
    data = data_collection_service.export_learning_data(bot_id)
    
    return {
        "status": "success",
        "export_data": data
    }


# Cleanup
@router.post("/cleanup")
async def cleanup_old_data(days_to_keep: int = 90) -> Dict[str, Any]:
    """Remove data older than specified days"""
    try:
        data_collection_service.cleanup_old_data(days_to_keep)
        
        return {
            "status": "success",
            "message": f"Data cleanup completed (kept last {days_to_keep} days)"
        }
    except Exception as e:
        logger.error(f"Cleanup failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
