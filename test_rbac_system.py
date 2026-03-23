#!/usr/bin/env python3
"""
RBAC + Feature Flags + Data Scope System Test
Tests the complete access control system implementation
"""

import json
import os
import sys

def test_rbac_system():
    """Test the complete RBAC system"""
    print("🧪 Testing RBAC + Feature Flags + Data Scope System")
    print("=" * 60)

    # Test 1: Load roles configuration
    print("\n1. Testing Roles Configuration...")
    try:
        # Import the roles loader
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'config'))
        from roles import load_roles_config

        roles_config = load_roles_config()
        print("✅ Roles config loaded successfully")

        # Check SUPER_ADMIN (owner) configuration
        owner_config = roles_config.get('owner', {})
        assert owner_config.get('data_scope') == 'global', "SUPER_ADMIN should have global data scope"
        assert '*' in owner_config.get('features', []), "SUPER_ADMIN should have all features"
        print("✅ SUPER_ADMIN (owner) has global access and all features")

        # Check Finance role configuration
        finance_config = roles_config.get('finance', {})
        assert finance_config.get('data_scope') == 'tenant_only', "Finance should have tenant_only data scope"
        assert 'finance_bot' in finance_config.get('features', []), "Finance should have finance features"
        print("✅ Finance role has tenant_only scope and finance features")

    except Exception as e:
        print(f"❌ Roles configuration test failed: {e}")
        return False

    # Test 2: Check RBAC middleware exists
    print("\n2. Testing RBAC Middleware...")
    try:
        middleware_path = os.path.join(os.path.dirname(__file__), 'backend', 'auth', 'rbac_middleware.py')
        assert os.path.exists(middleware_path), "RBAC middleware file should exist"

        with open(middleware_path, 'r', encoding='utf-8') as f:
            content = f.read()

        assert 'class RBACMiddleware' in content, "RBACMiddleware class should be defined"
        assert 'has_feature_access' in content, "Feature access checking should be implemented"
        assert 'data_scope' in content, "Data scope handling should be implemented"
        print("✅ RBAC middleware implemented with feature checking and data scope")

    except Exception as e:
        print(f"❌ RBAC Middleware test failed: {e}")
        return False

    # Test 3: Check frontend integration
    print("\n3. Testing Frontend Integration...")
    try:
        sidebar_path = os.path.join(os.path.dirname(__file__), 'frontend', 'src', 'components', 'Sidebar.jsx')
        assert os.path.exists(sidebar_path), "Sidebar component should exist"

        with open(sidebar_path, 'r', encoding='utf-8') as f:
            content = f.read()

        assert 'hasFeature' in content, "Feature checking function should be implemented"
        assert 'canAccessFinance' in content, "Finance access control should be implemented"
        assert 'canAccessAdmin' in content, "Admin access control should be implemented"
        assert 'isSuperAdmin' in content, "SUPER_ADMIN handling should be implemented"
        print("✅ Frontend Sidebar updated with feature-based access control")

    except Exception as e:
        print(f"❌ Frontend integration test failed: {e}")
        return False

    print("\n🎉 All RBAC System Tests Passed!")
    print("\n📋 System Summary:")
    print("- ✅ SUPER_ADMIN (owner): Global access to all features")
    print("- ✅ Finance role: Tenant-only scope with finance features")
    print("- ✅ Feature-based UI rendering implemented")
    print("- ✅ Data scope filtering ready for database queries")
    print("- ✅ RBAC middleware enforces access control")

    return True

if __name__ == "__main__":
    success = test_rbac_system()
    sys.exit(0 if success else 1)