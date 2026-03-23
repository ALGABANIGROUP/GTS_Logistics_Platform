#!/usr/bin/env python3
"""
🎯 GTS Unified System - Deployment Roadmap
Complete step-by-step guide to get started
"""

def print_section(title, emoji=""):
    print(f"\n{'='*70}")
    print(f"{emoji} {title}")
    print(f"{'='*70}\n")

def main():
    print("""
    ╔═══════════════════════════════════════════════════════════════╗
    ║  🚀 GTS UNIFIED SYSTEM - DEPLOYMENT ROADMAP                  ║
    ║                                                               ║
    ║  Your guide to starting the complete GTS system               ║
    ║  Your guide to starting GTS complete system                 ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)
    
    print_section("PHASE 1: PRE-DEPLOYMENT CHECKS", "✅")
    print("""
    Step 1: Verify System Readiness
    ────────────────────────────────────
    
    Command:
    $ python verify_system.py
    
    What it checks:
    ✓ All required files exist
    ✓ Backend structure is correct
    ✓ Frontend structure is correct
    ✓ Dependencies are installed
    ✓ Configuration files are present
    ✓ Environment is configured
    
    Expected output: 90%+ verification rate
    """)
    
    print_section("PHASE 2: DATABASE SETUP", "🗄️")
    print("""
    Step 1: Navigate to Backend Directory
    ──────────────────────────────────────
    Command:
    $ cd backend
    
    Step 2: Run Database Migrations
    ────────────────────────────────
    Command:
    $ python -m alembic upgrade head
    
    What it does:
    ✓ Creates unified_users table
    ✓ Creates user_systems_access table
    ✓ Creates auth_audit_log table
    ✓ Creates tms_subscriptions table
    ✓ Sets up all relationships
    
    Step 3: Verify Migration Success
    ─────────────────────────────────
    Command:
    $ python -m alembic current
    
    Expected: Shows latest revision number
    
    Step 4: Go Back to Root
    ──────────────────────
    Command:
    $ cd ..
    """)
    
    print_section("PHASE 3: BACKEND STARTUP", "🔌")
    print("""
    Step 1: Open Terminal for Backend
    ──────────────────────────────────
    (Keep this terminal open)
    
    Step 2: Start Backend Server
    ─────────────────────────────
    Command:
    $ cd backend
    $ python main.py
    
    Expected Output:
    ────────────────
    [startup] Backend server started
    [startup] Connected to database
    [startup] Bot OS initialized
    [main] system_switcher router mounted at /api/v1/systems
    [main] admin_unified router mounted at /api/v1/admin
    
    Backend is READY when you see:
    Uvicorn running on http://127.0.0.1:8000
    
    ✨ API Documentation: http://127.0.0.1:8000/docs
    """)
    
    print_section("PHASE 4: FRONTEND STARTUP", "🎨")
    print("""
    Step 1: Open NEW Terminal for Frontend
    ──────────────────────────────────────
    (Keep this terminal open)
    
    Step 2: Navigate to Frontend
    ─────────────────────────────
    Command:
    $ cd frontend
    
    Step 3: Install Dependencies (first time only)
    ───────────────────────────────────────────────
    Command:
    $ npm install
    
    Step 4: Start Development Server
    ─────────────────────────────────
    Command:
    $ npm run dev
    
    Expected Output:
    ────────────────
    ✓ 1234 modules transformed
    ready in 1234 ms
    
    Frontend is READY when you see:
    ➜ Local: http://127.0.0.1:5173
    ➜ Press h to show help
    
    🌐 UI is now accessible: http://127.0.0.1:5173
    """)
    
    print_section("PHASE 5: SYSTEM VERIFICATION", "🧪")
    print("""
    Step 1: Open NEW Terminal for Testing
    ──────────────────────────────────────
    
    Step 2: Run Advanced Test Suite
    ────────────────────────────────
    Command:
    $ python advanced_test_suite.py
    
    What it tests:
    ✓ Backend connectivity
    ✓ Authentication (login)
    ✓ System APIs
    ✓ System switching
    ✓ Admin endpoints
    ✓ WebSocket support
    ✓ Performance metrics
    
    Expected Output:
    ────────────────
    ✅ PASSED: Backend Health Check
    ✅ PASSED: Token Generation
    ✅ PASSED: Available Systems (2 systems)
    ✅ PASSED: System Selector UI Data
    ✅ PASSED: Switch to TMS
    ✅ PASSED: Admin Overview
    ...
    
    Success Rate: 85%+
    """)
    
    print_section("PHASE 6: MANUAL UI TESTING", "👨💻")
    print("""
    Step 1: Open Browser
    ────────────────────
    URL: http://127.0.0.1:5173
    
    Step 2: Test Landing Page
    ──────────────────────────
    ✓ Beautiful truck background image
    ✓ "Get Started" button is clickable
    ✓ Navigation menu works
    
    Step 3: Test Login
    ──────────────────
    Click "Sign In" or navigate to /login
    
    Enter Credentials:
    Email:    enjoy983@hotmail.com
    Password: password123
    
    Expected:
    ✓ Page with glass morphism design
    ✓ Matching background to landing page
    ✓ Login button redirects after success
    
    Step 4: Test System Selector
    ─────────────────────────────
    After login, you should see:
    ✓ Two system cards (GTS + TMS)
    ✓ "Admin" badge on TMS (if admin user)
    ✓ Click any card to select system
    
    Step 5: Test System Switching
    ──────────────────────────────
    From dashboard:
    ✓ Look for system switcher menu
    ✓ Click to open list of systems
    ✓ Select different system
    ✓ Should redirect to new dashboard
    
    Step 6: Test Admin Dashboard (admin users only)
    ────────────────────────────────────────────────
    Navigate to: /admin/unified-dashboard
    
    You should see:
    ✓ Tab 1: Overview (GTS + TMS stats)
    ✓ Tab 2: Users Management
    ✓ Tab 3: Subscriptions Analytics
    ✓ Tab 4: Bots Status
    ✓ Tab 5: System Health
    """)
    
    print_section("PHASE 7: TROUBLESHOOTING", "🔧")
    print("""
    Issue 1: Port 8000 Already in Use
    ──────────────────────────────────
    
    Windows:
    $ netstat -ano | findstr :8000
    $ taskkill /PID <PID> /F
    
    macOS/Linux:
    $ lsof -i :8000
    $ kill -9 <PID>
    
    Then restart backend.
    
    Issue 2: Port 5173 Already in Use
    ──────────────────────────────────
    
    Windows:
    $ netstat -ano | findstr :5173
    $ taskkill /PID <PID> /F
    
    macOS/Linux:
    $ lsof -i :5173
    $ kill -9 <PID>
    
    Then restart frontend.
    
    Issue 3: Database Connection Failed
    ─────────────────────────────────────
    
    Check database URL in environment:
    $ echo $DATABASE_URL
    
    Make sure PostgreSQL is running and accessible
    Check credentials in .env file
    
    Issue 4: NPM Packages Not Found
    ────────────────────────────────
    
    Clear and reinstall:
    $ cd frontend
    $ rm -rf node_modules package-lock.json
    $ npm install
    $ npm run dev
    
    Issue 5: Python Packages Not Found
    ───────────────────────────────────
    
    Reinstall requirements:
    $ pip install -r backend/requirements.txt
    
    Issue 6: Tests Failing
    ──────────────────────
    
    Make sure:
    1. Backend is running on http://127.0.0.1:8000
    2. Database migrations are complete
    3. Test credentials exist in database
    
    Then run tests again:
    $ python advanced_test_suite.py
    """)
    
    print_section("PHASE 8: QUICK ROUTES", "🗺️")
    print("""
    Frontend Routes:
    ─────────────────
    http://127.0.0.1:5173/              → Portal Landing
    http://127.0.0.1:5173/login         → Login Page
    http://127.0.0.1:5173/register      → Register Page
    http://127.0.0.1:5173/system-selector → System Selection
    http://127.0.0.1:5173/dashboard     → Main Dashboard
    http://127.0.0.1:5173/tms/dashboard → TMS Dashboard
    http://127.0.0.1:5173/admin/unified-dashboard → Admin Panel
    
    Backend Routes:
    ────────────────
    POST   http://127.0.0.1:8000/auth/token               → Login
    GET    http://127.0.0.1:8000/api/v1/systems/available → List Systems
    POST   http://127.0.0.1:8000/api/v1/systems/switch    → Switch System
    GET    http://127.0.0.1:8000/api/v1/admin/overview    → Admin Overview
    GET    http://127.0.0.1:8000/docs                     → API Documentation
    """)
    
    print_section("PHASE 9: QUICK COMMANDS REFERENCE", "⚡")
    print("""
    One-Command Deployment (Recommended):
    ──────────────────────────────────────
    $ python deploy_and_test.py
    
    (This runs everything automatically)
    
    Manual Step-by-Step:
    ────────────────────
    $ python verify_system.py           # Check readiness
    $ cd backend && alembic upgrade head  # Database
    $ python main.py                    # Backend (Terminal 1)
    $ cd frontend && npm run dev        # Frontend (Terminal 2)
    $ python advanced_test_suite.py     # Tests (Terminal 3)
    
    Auto Setup (without running):
    ──────────────────────────────
    $ python setup_and_run.py
    """)
    
    print_section("NEXT STEPS CHECKLIST", "✅")
    print("""
    Choose ONE approach:
    
    [ ] Approach 1: AUTOMATIC (Easiest)
        - Run: python deploy_and_test.py
        - Everything runs automatically
        - Perfect for first-time setup
    
    [ ] Approach 2: SEMI-AUTOMATIC (Balanced)
        - Run: python verify_system.py
        - Run: python setup_and_run.py
        - Then: Run tests manually
        - Good control while still automated
    
    [ ] Approach 3: MANUAL (Full Control)
        - Run all commands step by step
        - Open 3 terminals
        - Full visibility into each component
        - Best for debugging
    
    Once running, open browser:
    ──────────────────────────
    [ ] Visit: http://127.0.0.1:5173
    [ ] Login with test credentials
    [ ] Test system switching
    [ ] Access admin dashboard
    [ ] Check API docs at /docs
    """)
    
    print_section("SUPPORT & DOCUMENTATION", "📚")
    print("""
    Quick References:
    ──────────────────
    📖 QUICK_START.md                 → Quick start guide
    🔧 IMPLEMENTATION_COMPLETE_GUIDE.md → Complete guide
    🏗️ UNIFIED_SYSTEM_GUIDE.md         → Architecture guide
    📚 API_REFERENCE_COMPLETE.md       → API documentation
    ✅ DEPLOYMENT_COMPLETE_SUMMARY.md  → Summary
    
    When Things Go Wrong:
    ──────────────────────
    1. Check terminal output for error messages
    2. Run: python verify_system.py
    3. Run: python advanced_test_suite.py -v
    4. Check database with: alembic current
    5. Inspect logs in both terminals
    
    API Documentation:
    ───────────────────
    After backend starts:
    → http://127.0.0.1:8000/docs
    
    This shows all endpoints with examples!
    """)
    
    print("""
    
    ╔═══════════════════════════════════════════════════════════════╗
    ║  🎉 YOU'RE READY TO START!                                   ║
    ║                                                               ║
    ║  Run this command to begin:                                  ║
    ║                                                               ║
    ║  $ python deploy_and_test.py                                 ║
    ║                                                               ║
    ║  Or follow PHASE 1 - PHASE 9 above for manual setup          ║
    ║                                                               ║
    ║  Questions? Check the documentation files!                   ║
    ╚═══════════════════════════════════════════════════════════════╝
    
    """)

if __name__ == "__main__":
    main()
