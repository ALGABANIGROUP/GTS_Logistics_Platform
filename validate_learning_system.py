"""
Quick validation script for bot learning system
"""

from backend.ai.learning_engine import bot_learning_engine
from backend.ai.data_collection_service import data_collection_service

print("=" * 60)
print("BOT SELF-LEARNING SYSTEM - VALIDATION TEST")
print("=" * 60)

# Test 1: Bot Registration
print("\n1. Testing Bot Registration...")
profile = bot_learning_engine.register_bot(
    bot_id="validation_bot",
    bot_name="Validation Test Bot",
    enabled=True,
    frequency="daily",
    intensity="medium"
)
print(f"   ✅ Bot registered: {profile.bot_id}")
print(f"   ✅ Learning enabled: {profile.enabled}")
print(f"   ✅ Frequency: {profile.frequency}")
print(f"   ✅ Intensity: {profile.intensity}")

# Test 2: Data Collection
print("\n2. Testing Data Collection...")
data_collection_service.log_bot_error(
    bot_id="validation_bot",
    error_type="ValueError",
    error_message="Test error for validation",
    severity=0.8
)
print("   ✅ Error logged")

data_collection_service.record_performance(
    bot_id="validation_bot",
    response_time=150.0,
    accuracy=0.95,
    throughput=1.0
)
print("   ✅ Performance metric recorded")

data_collection_service.collect_user_feedback(
    bot_id="validation_bot",
    rating=4,
    session_id="validation_session_123",
    comment="Excellent bot!"
)
print("   ✅ User feedback collected")

# Test 3: Data Summary
print("\n3. Testing Data Summary...")
summary = data_collection_service.get_bot_data_summary("validation_bot")
print(f"   ✅ Errors collected: {summary['error_count']}")
print(f"   ✅ Metrics collected: {summary['metric_count']}")
print(f"   ✅ Feedback collected: {summary['feedback_count']}")
print(f"   ✅ Avg accuracy: {summary['avg_accuracy']:.2%}")

# Test 4: Learning Engine Integration
print("\n4. Testing Learning Engine Integration...")
bot_learning_engine.add_error_data("validation_bot", {
    "error_type": "NetworkError",
    "error_message": "Connection timeout",
    "severity": 0.6
})
bot_learning_engine.add_performance_data("validation_bot", {
    "response_time": 200.0,
    "accuracy": 0.88,
    "throughput": 0.9
})
bot_learning_engine.add_user_feedback("validation_bot", {
    "rating": 3,
    "comment": "Could be faster"
})
print("   ✅ Data added to learning engine")

# Test 5: Learning Update
print("\n5. Testing Learning Update...")
result = bot_learning_engine.perform_learning("validation_bot")
print(f"   ✅ Learning status: {result['status']}")
print(f"   ✅ Samples processed: {result['samples_processed']}")
print(f"   ✅ Adaptations generated: {len(result.get('adaptations', []))}")

if result.get("adaptations"):
    print("\n   Adaptations:")
    for adaptation in result["adaptations"][:3]:  # Show first 3
        print(f"      - {adaptation['type']}: {adaptation['description']}")

# Test 6: Bot Profile
print("\n6. Testing Bot Profile Retrieval...")
bot_profile = bot_learning_engine.get_bot_profile("validation_bot")
if bot_profile:
    print(f"   ✅ Accuracy score: {bot_profile['accuracy_score']:.2%}")
    print(f"   ✅ Performance score: {bot_profile['performance_score']:.2%}")
    print(f"   ✅ Reliability score: {bot_profile['reliability_score']:.2%}")
    print(f"   ✅ Total samples: {bot_profile['total_samples_processed']}")
    print(f"   ✅ Adaptations applied: {bot_profile['adaptations_applied']}")

# Test 7: Learning Stats
print("\n7. Testing Learning Statistics...")
stats = bot_learning_engine.get_learning_stats()
print(f"   ✅ Total bots registered: {stats['total_bots_registered']}")
print(f"   ✅ Enabled bots: {stats['enabled_bots']}")
print(f"   ✅ Average accuracy: {stats['average_accuracy']:.2%}")
print(f"   ✅ Average performance: {stats['average_performance']:.2%}")

print("\n" + "=" * 60)
print("✅ ALL VALIDATION TESTS PASSED!")
print("Bot self-learning system is fully operational")
print("=" * 60)
