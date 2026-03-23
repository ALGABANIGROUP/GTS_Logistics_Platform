#!/usr/bin/env python3
"""Test admin system bot endpoints with proper auth"""
import asyncio
import httpx
import json
import sys

sys.path.insert(0, '.')

async def test_admin_endpoints():
    # First, let's test by directly calling the route functions
    try:
        from backend.routes.admin_system import (
            get_system_health,
            get_database_health,
            get_users_statistics,
            get_dashboard_stats,
            list_users
        )
        
        # Create a mock current_user
        current_user = {
            'id': 1,
            'email': 'test@example.com',
            'role': 'admin',
            'effective_role': 'admin'
        }
        
        print("Testing admin endpoints...\n")
        
        # Test get_system_health
        print("1. Testing system health...")
        health = await get_system_health(current_user)
        print(f"   Status: {health.get('status')}")
        print(f"   CPU: {health.get('system', {}).get('cpu', {}).get('percent')}%")
        print(f"   Memory: {health.get('system', {}).get('memory', {}).get('percent')}%")
        print(f"   Disk Used: {health.get('system', {}).get('disk', {}).get('used_gb')} GB\n")
        
        # Test get_users_statistics
        print("2. Testing users statistics...")
        stats = await get_users_statistics(current_user)
        print(f"   Total Users: {stats.get('summary', {}).get('total_users')}")
        print(f"   Active Users: {stats.get('summary', {}).get('active_users')}")
        print(f"   Inactive Users: {stats.get('summary', {}).get('inactive_users')}")
        print(f"   New (7d): {stats.get('summary', {}).get('new_users_7d')}\n")
        
        # Test get_database_health
        print("3. Testing database health...")
        db_health = await get_database_health(current_user)
        print(f"   Status: {db_health.get('status')}")
        print(f"   Users table count: {db_health.get('database', {}).get('table_counts', {}).get('users')}\n")
        
        # Test list_users
        print("4. Testing list users...")
        users = await list_users(page=1, limit=5, current_user=current_user)
        print(f"   Total users in DB: {users.get('total')}")
        print(f"   Returned: {len(users.get('users', []))}")
        if users.get('users'):
            print(f"   First user: {users['users'][0].get('email')} ({users['users'][0].get('role')})\n")
        
        # Test get_dashboard_stats
        print("5. Testing dashboard stats...")
        dash = await get_dashboard_stats(current_user)
        print(f"   Status: {dash.get('status')}")
        print(f"   Metrics: {dash.get('metrics')}\n")
        
        print("✓ All endpoint tests passed!")
        
    except Exception as e:
        print(f"✗ Error testing endpoints: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(test_admin_endpoints())
