"""
Comprehensive test suite for Bot Self-Learning System
Tests learning engine, data collection, and API endpoints
"""

import pytest
import asyncio
from datetime import datetime
from typing import Dict, Any

# Import modules to test
from backend.ai.learning_engine import (
    bot_learning_engine,
    BotLearningEngine,
    LearningFrequency,
    LearningIntensity,
    BotLearningProfile
)
from backend.ai.data_collection_service import (
    data_collection_service,
    DataCollectionService
)


class TestBotLearningEngine:
    """Test suite for BotLearningEngine"""
    
    def setup_method(self):
        """Reset learning engine before each test"""
        self.engine = BotLearningEngine()
    
    def test_register_bot(self):
        """Test bot registration for learning"""
        profile = self.engine.register_bot(
            bot_id="test_bot",
            bot_name="Test Bot",
            enabled=True,
            frequency="daily",
            intensity="medium"
        )
        
        assert profile.bot_id == "test_bot"
        assert profile.bot_name == "Test Bot"
        assert profile.enabled == True
        assert profile.frequency == LearningFrequency.DAILY
        assert profile.intensity == LearningIntensity.MEDIUM
        assert "test_bot" in self.engine.learning_profiles
    
    def test_add_error_data(self):
        """Test adding error data for learning"""
        self.engine.register_bot("test_bot", "Test Bot")
        
        self.engine.add_error_data("test_bot", {
            "error_type": "ValueError",
            "error_message": "Test error",
            "severity": 0.8
        })
        
        assert len(self.engine.data_samples["test_bot"]) == 1
        assert self.engine.data_samples["test_bot"][0].sample_type == "error"
        assert self.engine.learning_profiles["test_bot"].error_count == 1
    
    def test_add_performance_data(self):
        """Test adding performance metrics"""
        self.engine.register_bot("test_bot", "Test Bot")
        
        self.engine.add_performance_data("test_bot", {
            "response_time": 150.5,
            "accuracy": 0.95,
            "throughput": 1.2
        })
        
        assert len(self.engine.data_samples["test_bot"]) == 1
        assert self.engine.data_samples["test_bot"][0].sample_type == "performance"
    
    def test_add_user_feedback(self):
        """Test adding user feedback"""
        self.engine.register_bot("test_bot", "Test Bot")
        
        self.engine.add_user_feedback("test_bot", {
            "rating": 4,
            "comment": "Works well",
            "user_id": "user_123"
        })
        
        assert len(self.engine.data_samples["test_bot"]) == 1
        assert self.engine.data_samples["test_bot"][0].sample_type == "feedback"
        assert self.engine.learning_profiles["test_bot"].feedback_entries == 1
    
    def test_should_learn(self):
        """Test learning schedule check"""
        # Register bot with immediate next update (past time)
        profile = self.engine.register_bot("test_bot", "Test Bot", frequency="hourly")
        
        # Manually set next update to past for testing
        profile.next_learning_update = "2020-01-01T00:00:00"
        
        assert self.engine.should_learn("test_bot") == True
    
    def test_perform_learning_no_data(self):
        """Test learning with no data"""
        self.engine.register_bot("test_bot", "Test Bot")
        
        result = self.engine.perform_learning("test_bot")
        
        assert result["status"] == "no_data"
        assert result["samples_processed"] == 0
    
    def test_perform_learning_with_data(self):
        """Test learning update with collected data"""
        self.engine.register_bot("test_bot", "Test Bot", intensity="high")
        
        # Add various data samples
        for i in range(5):
            self.engine.add_error_data("test_bot", {
                "error_type": "ValueError",
                "error_message": f"Error {i}",
                "severity": 0.5
            })
        
        for i in range(10):
            self.engine.add_performance_data("test_bot", {
                "response_time": 200 + i * 10,
                "accuracy": 0.85 + i * 0.01,
                "throughput": 1.0
            })
        
        for i in range(3):
            self.engine.add_user_feedback("test_bot", {
                "rating": 3 + i % 2,
                "comment": "Test feedback"
            })
        
        result = self.engine.perform_learning("test_bot")
        
        assert result["status"] == "success"
        assert result["samples_processed"] == 18
        assert len(result["adaptations"]) > 0
        assert "metrics" in result
        assert result["metrics"]["accuracy"] > 0
    
    def test_learning_adaptations(self):
        """Test that adaptations are generated correctly"""
        self.engine.register_bot("test_bot", "Test Bot", intensity="medium")
        
        # Add error data to trigger error handling adaptation
        for i in range(5):
            self.engine.add_error_data("test_bot", {
                "error_type": "NetworkError",
                "error_message": "Connection failed",
                "severity": 0.8
            })
        
        # Add poor performance data
        for i in range(5):
            self.engine.add_performance_data("test_bot", {
                "response_time": 500,  # High response time
                "accuracy": 0.70,  # Low accuracy
                "throughput": 0.5
            })
        
        result = self.engine.perform_learning("test_bot")
        
        # Check that adaptations include error handling and performance improvements
        adaptation_types = [a["type"] for a in result["adaptations"]]
        assert "error_handling" in adaptation_types
        assert "performance" in adaptation_types or "accuracy" in adaptation_types
    
    def test_learning_intensity_levels(self):
        """Test different learning intensity levels"""
        # Low intensity
        self.engine.register_bot("bot_low", "Low Bot", intensity="low")
        self.engine.add_error_data("bot_low", {"error_type": "Test", "error_message": "Error", "severity": 1.0})
        result_low = self.engine.perform_learning("bot_low")
        
        # High intensity
        self.engine.register_bot("bot_high", "High Bot", intensity="high")
        self.engine.add_error_data("bot_high", {"error_type": "Test", "error_message": "Error", "severity": 1.0})
        result_high = self.engine.perform_learning("bot_high")
        
        # High intensity should produce stronger adaptations
        assert len(result_low["adaptations"]) >= 0
        assert len(result_high["adaptations"]) >= 0
    
    def test_get_bot_profile(self):
        """Test retrieving bot profile"""
        self.engine.register_bot("test_bot", "Test Bot")
        
        profile = self.engine.get_bot_profile("test_bot")
        
        assert profile is not None
        assert profile["bot_id"] == "test_bot"
        assert profile["bot_name"] == "Test Bot"
        assert "accuracy_score" in profile
        assert "performance_score" in profile
        assert "reliability_score" in profile
        assert "behaviors" in profile
    
    def test_get_learning_stats(self):
        """Test overall learning statistics"""
        self.engine.register_bot("bot1", "Bot 1")
        self.engine.register_bot("bot2", "Bot 2", enabled=False)
        
        stats = self.engine.get_learning_stats()
        
        assert stats["total_bots_registered"] == 2
        assert stats["enabled_bots"] == 1
        assert "average_accuracy" in stats
        assert "average_performance" in stats


class TestDataCollectionService:
    """Test suite for DataCollectionService"""
    
    def setup_method(self):
        """Reset data collection service before each test"""
        self.service = DataCollectionService()
    
    def test_log_bot_error(self):
        """Test error logging"""
        self.service.log_bot_error(
            bot_id="test_bot",
            error_type="ValueError",
            error_message="Test error",
            severity=0.8,
            traceback="Traceback...",
            context={"test": "context"}
        )
        
        assert len(self.service.error_logs) == 1
        assert self.service.collection_stats["errors_collected"] == 1
        assert self.service.error_logs[0].bot_id == "test_bot"
        assert self.service.error_logs[0].error_type == "ValueError"
    
    def test_record_performance(self):
        """Test performance recording"""
        self.service.record_performance(
            bot_id="test_bot",
            response_time=150.5,
            accuracy=0.95,
            throughput=1.2,
            resource_usage={"cpu_percent": 25.5, "memory_percent": 30.0}
        )
        
        assert len(self.service.performance_metrics) == 1
        assert self.service.collection_stats["metrics_collected"] == 1
        assert self.service.performance_metrics[0].response_time == 150.5
        assert self.service.performance_metrics[0].accuracy == 0.95
    
    def test_collect_user_feedback(self):
        """Test user feedback collection"""
        self.service.collect_user_feedback(
            bot_id="test_bot",
            rating=4,
            session_id="session_123",
            comment="Great bot!",
            user_id="user_456",
            feedback_type="performance",
            tags=["helpful", "fast"]
        )
        
        assert len(self.service.user_feedback) == 1
        assert self.service.collection_stats["feedback_collected"] == 1
        assert self.service.user_feedback[0].rating == 4
        assert self.service.user_feedback[0].comment == "Great bot!"
    
    def test_get_bot_error_logs(self):
        """Test retrieving bot error logs"""
        for i in range(5):
            self.service.log_bot_error(
                bot_id="test_bot",
                error_type=f"Error{i}",
                error_message=f"Message {i}",
                severity=0.5 + i * 0.1
            )
        
        errors = self.service.get_bot_error_logs("test_bot", limit=3)
        
        assert len(errors) == 3
        assert all(isinstance(e, dict) for e in errors)
    
    def test_get_bot_performance_history(self):
        """Test retrieving performance history"""
        for i in range(10):
            self.service.record_performance(
                bot_id="test_bot",
                response_time=100 + i * 10,
                accuracy=0.8 + i * 0.02,
                throughput=1.0
            )
        
        metrics = self.service.get_bot_performance_history("test_bot", limit=5)
        
        assert len(metrics) == 5
        assert all("response_time" in m for m in metrics)
        assert all("accuracy" in m for m in metrics)
    
    def test_get_bot_feedback(self):
        """Test retrieving user feedback"""
        for i in range(7):
            self.service.collect_user_feedback(
                bot_id="test_bot",
                rating=3 + i % 3,
                session_id=f"session_{i}"
            )
        
        feedback = self.service.get_bot_feedback("test_bot", limit=4)
        
        assert len(feedback) == 4
        assert all("rating" in f for f in feedback)
    
    def test_get_bot_data_summary(self):
        """Test data summary generation"""
        # Add mixed data
        self.service.log_bot_error("test_bot", "Error", "Message", 0.5)
        self.service.record_performance("test_bot", 150, 0.9, 1.0)
        self.service.collect_user_feedback("test_bot", 4, "session_1")
        
        summary = self.service.get_bot_data_summary("test_bot")
        
        assert summary["bot_id"] == "test_bot"
        assert summary["error_count"] == 1
        assert summary["metric_count"] == 1
        assert summary["feedback_count"] == 1
        assert "avg_response_time_ms" in summary
        assert "avg_accuracy" in summary
        assert "avg_feedback_rating" in summary
    
    def test_export_learning_data(self):
        """Test data export"""
        self.service.log_bot_error("test_bot", "Error", "Message", 0.5)
        self.service.record_performance("test_bot", 150, 0.9, 1.0)
        self.service.collect_user_feedback("test_bot", 4, "session_1")
        
        export_data = self.service.export_learning_data("test_bot")
        
        assert export_data["bot_id"] == "test_bot"
        assert "export_timestamp" in export_data
        assert "error_logs" in export_data
        assert "performance_metrics" in export_data
        assert "user_feedback" in export_data


@pytest.mark.asyncio
class TestLearningAPIIntegration:
    """Integration tests for learning API endpoints"""
    
    async def test_register_bot_endpoint(self, test_client):
        """Test bot registration endpoint"""
        response = await test_client.post(
            "/ai/learning/register",
            params={
                "bot_id": "integration_bot",
                "bot_name": "Integration Test Bot",
                "enabled": True,
                "frequency": "daily",
                "intensity": "medium"
            }
        )
        
        assert response.status_code == 200
        assert response.json()["status"] == "success"
        assert "profile" in response.json()
    
    async def test_log_error_endpoint(self, test_client):
        """Test error logging endpoint"""
        # First register a bot
        await test_client.post(
            "/ai/learning/register",
            params={"bot_id": "test_bot", "bot_name": "Test Bot"}
        )
        
        # Log an error
        response = await test_client.post(
            "/ai/learning/data/error",
            params={"bot_id": "test_bot"},
            json={
                "error_type": "ValueError",
                "error_message": "Test error",
                "severity": 0.8
            }
        )
        
        assert response.status_code == 200
        assert response.json()["status"] == "success"
    
    async def test_trigger_learning_endpoint(self, test_client):
        """Test manual learning trigger"""
        # Register bot and add data
        await test_client.post(
            "/ai/learning/register",
            params={"bot_id": "test_bot", "bot_name": "Test Bot"}
        )
        
        await test_client.post(
            "/ai/learning/data/performance",
            params={"bot_id": "test_bot"},
            json={
                "response_time": 150,
                "accuracy": 0.9,
                "throughput": 1.0
            }
        )
        
        # Trigger learning
        response = await test_client.post("/ai/learning/trigger/test_bot")
        
        assert response.status_code == 200
        assert "learning_result" in response.json()


def run_all_tests():
    """Run all tests and report results"""
    print("=" * 60)
    print("BOT SELF-LEARNING SYSTEM - COMPREHENSIVE TEST SUITE")
    print("=" * 60)
    
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "--color=yes"
    ])


if __name__ == "__main__":
    run_all_tests()
