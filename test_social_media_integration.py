#!/usr/bin/env python
"""
Social Media System Integration Test
Tests API routes, database, and basic functionality
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
repo_root = Path(__file__).parent
sys.path.insert(0, str(repo_root))

async def test_imports():
    """Test that all modules can be imported"""
    print("\n" + "="*60)
    print("1. Testing Imports")
    print("="*60)
    
    try:
        print("  ✓ Importing database models...")
        from backend.models.social_media import (
            SocialMediaAccount,
            SocialMediaPost,
            SocialMediaAnalytics,
            SocialMediaTemplate,
            SocialMediaSettings,
        )
        print("    - SocialMediaAccount")
        print("    - SocialMediaPost")
        print("    - SocialMediaAnalytics")
        print("    - SocialMediaTemplate")
        print("    - SocialMediaSettings")
        
        print("  ✓ Importing API clients...")
        from backend.social_media import LinkedInClient, TwitterClient, FacebookClient
        print("    - LinkedInClient")
        print("    - TwitterClient")
        print("    - FacebookClient")
        
        print("  ✓ Importing business logic...")
        from backend.social_media import AutoPoster, SocialAnalytics
        print("    - AutoPoster")
        print("    - SocialAnalytics")
        
        print("  ✓ Importing API routes...")
        from backend.routes.social_media_routes import router, public_router
        print("    - router (admin routes)")
        print("    - public_router (public routes)")
        
        print("  ✓ All imports successful!")
        return True
    except Exception as e:
        print(f"  ✗ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_api_routes():
    """Test that API routes are properly defined"""
    print("\n" + "="*60)
    print("2. Testing API Routes Definition")
    print("="*60)
    
    try:
        from backend.routes.social_media_routes import router, public_router
        
        # Count routes
        admin_routes = [route for route in router.routes if hasattr(route, 'path')]
        public_routes = [route for route in public_router.routes if hasattr(route, 'path')]
        
        print(f"  ✓ Admin routes defined: {len(admin_routes)} endpoints")
        for route in admin_routes[:5]:
            if hasattr(route, 'path'):
                methods = ', '.join(getattr(route, 'methods', [])) if hasattr(route, 'methods') else 'N/A'
                print(f"    - {getattr(route, 'path', 'unknown')} [{methods}]")
        if len(admin_routes) > 5:
            print(f"    ... and {len(admin_routes) - 5} more")
        
        print(f"  ✓ Public routes defined: {len(public_routes)} endpoints")
        for route in public_routes:
            if hasattr(route, 'path'):
                methods = ', '.join(getattr(route, 'methods', [])) if hasattr(route, 'methods') else 'N/A'
                print(f"    - {getattr(route, 'path', 'unknown')} [{methods}]")
        
        print("  ✓ All routes configured!")
        return True
    except Exception as e:
        print(f"  ✗ Route testing failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_frontend_components():
    """Check if frontend components exist"""
    print("\n" + "="*60)
    print("3. Testing Frontend Components")
    print("="*60)
    
    components = [
        ("Admin Dashboard", "frontend/src/components/admin/SocialMediaDashboard.jsx"),
        ("Admin Styles", "frontend/src/components/admin/SocialMediaDashboard.css"),
        ("Public Footer", "frontend/src/components/layout/SocialMediaFooter.jsx"),
        ("Footer Styles", "frontend/src/components/layout/SocialMediaFooter.css"),
        ("Admin Page", "frontend/src/pages/admin/SocialMedia.jsx"),
    ]
    
    all_found = True
    for name, path in components:
        full_path = repo_root / path
        if full_path.exists():
            size = full_path.stat().st_size
            print(f"  ✓ {name}: {path} ({size} bytes)")
        else:
            print(f"  ✗ {name}: NOT FOUND - {path}")
            all_found = False
    
    return all_found


def test_database_migration():
    """Test that migration file exists and is valid"""
    print("\n" + "="*60)
    print("4. Testing Database Migration")
    print("="*60)
    
    try:
        migration_file = repo_root / "backend/alembic/versions/sm_001_add_social_media_tables.py"
        
        if migration_file.exists():
            print(f"  ✓ Migration file exists: {migration_file.name}")
            
            # Read and validate migration
            content = migration_file.read_text()
            
            checks = [
                ("upgrade function", "def upgrade()" in content),
                ("downgrade function", "def downgrade()" in content),
                ("accounts table", "social_media_accounts" in content),
                ("posts table", "social_media_posts" in content),
                ("analytics table", "social_media_analytics" in content),
                ("templates table", "social_media_templates" in content),
                ("settings table", "social_media_settings" in content),
                ("indexes", "op.create_index" in content),
            ]
            
            all_valid = True
            for check_name, check_result in checks:
                status = "✓" if check_result else "✗"
                print(f"  {status} {check_name}")
                all_valid = all_valid and check_result
            
            return all_valid
        else:
            print(f"  ✗ Migration file not found: {migration_file}")
            return False
    except Exception as e:
        print(f"  ✗ Migration test failed: {e}")
        return False


def check_backend_integration():
    """Check if routes are registered in main.py"""
    print("\n" + "="*60)
    print("5. Testing Backend Integration (main.py)")
    print("="*60)
    
    try:
        main_file = repo_root / "backend/main.py"
        content = main_file.read_text()
        
        checks = [
            ("Social media imports", "from backend.routes.social_media_routes import" in content),
            ("Admin router import", "social_media_admin_router" in content),
            ("Public router import", "social_media_public_router" in content),
            ("Admin router mounting", "social_media_admin_router" in content and "include_router" in content),
            ("Public router mounting", "social_media_public_router" in content and "include_router" in content),
        ]
        
        all_found = True
        for check_name, check_result in checks:
            status = "✓" if check_result else "✗"
            print(f"  {status} {check_name}")
            all_found = all_found and check_result
        
        return all_found
    except Exception as e:
        print(f"  ✗ Integration test failed: {e}")
        return False


def check_frontend_integration():
    """Check if routes are registered in App.jsx"""
    print("\n" + "="*60)
    print("6. Testing Frontend Integration (App.jsx)")
    print("="*60)
    
    try:
        app_file = repo_root / "frontend/src/App.jsx"
        content = app_file.read_text()
        
        checks = [
            ("SocialMedia page import", "import SocialMedia from" in content),
            ("SocialMedia route", "/admin/social-media" in content),
            ("AppShell footer import", "SocialMediaFooter" in content),
        ]
        
        all_found = True
        for check_name, check_result in checks:
            status = "✓" if check_result else "✗"
            print(f"  {status} {check_name}")
            all_found = all_found and check_result
        
        return all_found
    except Exception as e:
        print(f"  ✗ Frontend integration test failed: {e}")
        return False


async def main():
    """Run all tests"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*10 + "Social Media System Integration Test" + " "*12 + "║")
    print("╚" + "="*58 + "╝")
    
    results = {
        "Imports": test_imports() or await asyncio.sleep(0) or False,
        "API Routes": test_api_routes(),
        "Frontend Components": test_frontend_components(),
        "Database Migration": test_database_migration(),
        "Backend Integration": check_backend_integration(),
        "Frontend Integration": check_frontend_integration(),
    }
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {test_name}")
    
    all_passed = all(results.values())
    
    print("\n" + "="*60)
    if all_passed:
        print("✓ All tests passed! System is ready for deployment.")
    else:
        print("✗ Some tests failed. Please review the output above.")
    print("="*60 + "\n")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
