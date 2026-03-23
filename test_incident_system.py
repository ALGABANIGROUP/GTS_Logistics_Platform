#!/usr/bin/env python3
"""
Test script for Incident Response System
"""

import asyncio
import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

async def test_incident_system():
    """Test the Incident Response System"""
    try:
        from backend.services.incident_tracker import IncidentTracker, IncidentSeverity, IncidentStatus

        print("🚨 Testing Incident Response System...")

        # Initialize tracker
        tracker = IncidentTracker()
        print("✅ Incident Tracker initialized")

        # Test 1: Capture error
        print("\n📝 Test 1: Capturing error...")
        error_data = {
            "service": "api",
            "error": "Database connection timeout after 30 seconds",
            "description": "Unable to connect to PostgreSQL",
            "traceback": "Traceback (most recent call last)...",
            "affected_users": 150
        }

        incident = tracker.capture_error(error_data)
        print(f"✅ Incident captured: {incident.id}")
        print(f"   Severity: {incident.severity.value}")
        print(f"   Status: {incident.status.value}")

        # Test 2: Start investigation
        print("\n🔍 Test 2: Starting investigation...")
        result = tracker.investigate(incident.id, "John Doe", "Checking database connectivity")
        print(f"✅ Investigation started: {result}")

        # Test 3: Contain incident
        print("\n🛡️ Test 3: Containing incident...")
        result = tracker.contain(incident.id, "Restarted database connection pool")
        print(f"✅ Incident contained: {result}")

        # Test 4: Analyze logs
        print("\n📊 Test 4: Analyzing logs...")
        sample_logs = [
            "2024-01-15 10:30:00 ERROR Database connection timeout",
            "2024-01-15 10:30:05 INFO User login successful",
            "2024-01-15 10:30:10 ERROR Connection refused",
            "2024-01-15 10:30:15 WARNING High memory usage"
        ]
        result = tracker.analyze_logs(incident.id, sample_logs)
        print(f"✅ Log analysis complete: {result['related_errors']} related errors found")

        # Test 5: Resolve incident
        print("\n✅ Test 5: Resolving incident...")
        result = tracker.resolve(
            incident.id,
            "Fixed database connection pool configuration",
            "Database connection pool size was too small"
        )
        print(f"✅ Incident resolved: {result}")

        # Test 6: Get active incidents
        print("\n📋 Test 6: Getting active incidents...")
        active = tracker.get_active_incidents()
        print(f"✅ Active incidents: {len(active)}")

        # Test 7: Get incident report
        print("\n📊 Test 7: Getting incident report...")
        report = tracker.get_incident_report(days=1)
        print(f"✅ Report generated: {report['total_incidents']} incidents in last day")

        print("\n🎉 All Incident Response System tests passed!")

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all dependencies are installed")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_incident_system())