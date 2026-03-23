#!/usr/bin/env python3
"""
🔍 GTS System Diagnostics & Debugging Guide
Diagnostics and Debugging Guide - Unified GTS System

Complete troubleshooting and verification tool for production deployment
Comprehensive tool for troubleshooting and readiness verification
"""

import subprocess
import sys
import os
from pathlib import Path
import asyncio
import json
from datetime import datetime

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    BOLD = '\033[1m'
    END = '\033[0m'

class SystemDiagnostics:
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "sections": {}
        }
        self.total_checks = 0
        self.passed_checks = 0
        self.failed_checks = 0
        self.warnings = 0

    def print_header(self):
        print(f"{Colors.BOLD}{Colors.MAGENTA}")
        print("""
╔════════════════════════════════════════════════════════════════════╗
║                                                                    ║
║          🔍 GTS SYSTEM DIAGNOSTICS & DEBUGGING 🔍                  ║
║                                                                    ║
║        Diagnostics and Debugging Guide - Unified GTS System       ║
║                                                                    ║
║           Complete System Health Check & Troubleshooting           ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
        """)
        print(f"{Colors.END}")

    def section(self, title):
        print(f"\n{Colors.BOLD}{Colors.CYAN}{'═' * 70}")
        print(f"📋 {title}")
        print(f"{'═' * 70}{Colors.END}\n")

    def check(self, item, condition, details=""):
        self.total_checks += 1
        status = "✅ PASS" if condition else "❌ FAIL"
        color = Colors.GREEN if condition else Colors.RED
        
        print(f"{color}{status}{Colors.END} - {item}")
        if details:
            print(f"    {Colors.BLUE}→ {details}{Colors.END}")
        
        if condition:
            self.passed_checks += 1
        else:
            self.failed_checks += 1
        
        print()

    def warning(self, item, details=""):
        self.total_checks += 1
        self.warnings += 1
        print(f"{Colors.YELLOW}⚠️  WARNING{Colors.END} - {item}")
        if details:
            print(f"    {Colors.BLUE}→ {details}{Colors.END}")
        print()

    def print_summary(self):
        print(f"\n{Colors.BOLD}{Colors.CYAN}{'═' * 70}")
        print(f"📊 DIAGNOSTIC SUMMARY")
        print(f"{'═' * 70}{Colors.END}\n")
        
        passed_pct = (self.passed_checks / self.total_checks * 100) if self.total_checks > 0 else 0
        
        print(f"{Colors.GREEN}✅ Passed: {self.passed_checks}/{self.total_checks}{Colors.END}")
        print(f"{Colors.RED}❌ Failed: {self.failed_checks}/{self.total_checks}{Colors.END}")
        print(f"{Colors.YELLOW}⚠️  Warnings: {self.warnings}{Colors.END}")
        print(f"{Colors.BOLD}Overall Health: {passed_pct:.1f}%{Colors.END}\n")
        
        if self.failed_checks == 0 and self.warnings == 0:
            print(f"{Colors.BOLD}{Colors.GREEN}✨ SYSTEM IS PRODUCTION READY! ✨{Colors.END}\n")
        elif self.failed_checks == 0:
            print(f"{Colors.BOLD}{Colors.YELLOW}⚠️  System operational with minor warnings{Colors.END}\n")
        else:
            print(f"{Colors.BOLD}{Colors.RED}❌ System has critical issues that need attention{Colors.END}\n")

    def diagnostic_test(self):
        self.print_header()
        
        # Section 1: System Requirements
        self.section("1️⃣  SYSTEM REQUIREMENTS | System requirements")
        
        py_version = sys.version_info
        self.check("Python Version", 
                  py_version.major >= 3 and py_version.minor >= 10,
                  f"Python {py_version.major}.{py_version.minor}.{py_version.micro}")
        
        self.check("OS Platform",
                  sys.platform in ["win32", "linux", "darwin"],
                  f"Detected: {sys.platform}")
        
        # Section 2: Project Structure
        self.section("2️⃣  PROJECT STRUCTURE | Project structure")
        
        dirs_to_check = [
            ("backend", "Backend source code"),
            ("frontend", "Frontend source code"),
            ("backend/routes", "API routes"),
            ("backend/models", "Database models"),
            ("backend/bots", "AI Bots system"),
            ("frontend/src", "React source"),
            ("frontend/src/pages", "React pages"),
            ("frontend/src/components", "React components"),
        ]
        
        for dir_path, desc in dirs_to_check:
            exists = Path(dir_path).is_dir()
            self.check(f"Directory: {dir_path}", exists, desc)
        
        # Section 3: Critical Files
        self.section("3️⃣  CRITICAL FILES | Critical files")
        
        files_to_check = [
            ("backend/main.py", "FastAPI application entry point"),
            (".env", "Environment configuration"),
            ("requirements.txt", "Python dependencies"),
            ("frontend/package.json", "Node.js dependencies"),
            ("frontend/vite.config.js", "Vite configuration"),
            ("backend/alembic.ini", "Database migration config"),
            ("backend/database/config.py", "Database configuration"),
        ]
        
        for file_path, desc in files_to_check:
            exists = Path(file_path).is_file()
            self.check(f"File: {file_path}", exists, desc)
        
        # Section 4: Environment Variables
        self.section("4️⃣  ENVIRONMENT VARIABLES | Environment variables")
        
        env_file = Path(".env")
        if env_file.exists():
            self.check(".env file exists", True, "Configuration file found")
            try:
                with open(env_file) as f:
                    env_vars = [line.split("=")[0] for line in f if "=" in line and not line.startswith("#")]
                
                required_vars = ["ASYNC_DATABASE_URL", "DATABASE_URL", "BACKEND_PORT"]
                for var in required_vars:
                    self.check(f"  Variable: {var}", var in env_vars, "Required configuration")
            except Exception as e:
                self.check(".env parsing", False, str(e))
        else:
            self.warning(".env file not found", "Create .env from .env.example or follow OPERATION_GUIDE.md")
        
        # Section 5: Dependencies
        self.section("5️⃣  DEPENDENCIES | Requirements")
        
        reqs_file = Path("requirements.txt")
        if reqs_file.exists():
            with open(reqs_file) as f:
                requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]
            
            critical_packages = {
                "fastapi": "Web framework",
                "sqlalchemy": "ORM",
                "asyncpg": "Async PostgreSQL driver",
                "pydantic": "Data validation",
                "python-multipart": "Form handling",
            }
            
            for pkg, desc in critical_packages.items():
                found = any(pkg.lower() in req.lower() for req in requirements)
                self.check(f"Package: {pkg}", found, desc)
        
        # Section 6: Backend Validation
        self.section("6️⃣  BACKEND VALIDATION | Backend validation")
        
        try:
            main_file = Path("backend/main.py")
            if main_file.exists():
                with open(main_file) as f:
                    content = f.read()
                
                self.check("FastAPI app initialization", "app = FastAPI()" in content, "FastAPI instance created")
                self.check("CORS configuration", "CORSMiddleware" in content, "CORS is configured")
                self.check("Router mounting", "include_router" in content, "Routes are mounted")
                self.check("Startup event", "@app.on_event" in content or "@app.event_handler", "Startup hook exists")
        except Exception as e:
            self.check("Backend validation", False, str(e))
        
        # Section 7: Frontend Validation
        self.section("7️⃣  FRONTEND VALIDATION | Frontend validation")
        
        try:
            vite_config = Path("frontend/vite.config.js")
            if vite_config.exists():
                self.check("Vite config exists", True, "Frontend build tool configured")
            
            main_jsx = Path("frontend/src/main.jsx")
            if main_jsx.exists():
                self.check("React entry point", True, "main.jsx found")
            
            app_jsx = Path("frontend/src/App.jsx")
            if app_jsx.exists():
                self.check("React App component", True, "App.jsx found")
        except Exception as e:
            self.check("Frontend validation", False, str(e))
        
        # Section 8: Database Setup
        self.section("8️⃣  DATABASE SETUP | Database setup")
        
        try:
            config_file = Path("backend/database/config.py")
            if config_file.exists():
                with open(config_file) as f:
                    content = f.read()
                
                self.check("Async engine creation", "create_async_engine" in content, "PostgreSQL async configured")
                self.check("Session factory", "sessionmaker" in content, "Session factory defined")
                self.check("Base model", "Base" in content, "Declarative base exists")
        except Exception as e:
            self.check("Database config", False, str(e))
        
        # Section 9: Authentication System
        self.section("9️⃣  AUTHENTICATION SYSTEM | Authentication system")
        
        try:
            auth_file = Path("backend/auth/unified_auth.py")
            if auth_file.exists():
                with open(auth_file) as f:
                    content = f.read()
                
                self.check("JWT implementation", "jwt" in content.lower(), "JWT tokens supported")
                self.check("Password hashing", "bcrypt" in content.lower() or "hash" in content.lower(), "Password encryption")
                self.check("User authentication", "authenticate_user" in content, "User auth function exists")
        except Exception as e:
            self.check("Auth system", False, str(e))
        
        # Section 10: API Routes
        self.section("🔟 API ROUTES | API routes")
        
        try:
            routes_dir = Path("backend/routes")
            if routes_dir.exists():
                route_files = list(routes_dir.glob("*.py"))
                self.check(f"Route files ({len(route_files)})", len(route_files) > 0, 
                          f"Found {len(route_files)} route modules")
                
                # Check specific routes
                critical_routes = [
                    "auth_routes.py",
                    "bot_os.py",
                    "ws_routes.py",
                ]
                
                for route_file in critical_routes:
                    exists = (routes_dir / route_file).exists()
                    self.check(f"  Route: {route_file}", exists, "Critical API endpoint module")
        except Exception as e:
            self.check("Routes validation", False, str(e))
        
        # Section 11: AI Bots System
        self.section("1️⃣1️⃣  AI BOTS SYSTEM | AI bots system")
        
        try:
            bots_dir = Path("backend/bots")
            if bots_dir.exists():
                bot_files = list(bots_dir.glob("*.py"))
                self.check(f"Bot modules ({len(bot_files)})", len(bot_files) > 5, 
                          f"Found {len(bot_files)} bot modules")
                
                critical_bots = [
                    "os.py",
                    "command_parser.py",
                    "rate_limit.py",
                ]
                
                for bot_file in critical_bots:
                    exists = (bots_dir / bot_file).exists()
                    self.check(f"  Bot module: {bot_file}", exists, "BOS system component")
        except Exception as e:
            self.check("Bots system", False, str(e))
        
        # Section 12: Configuration & Documentation
        self.section("1️⃣2️⃣  CONFIGURATION & DOCUMENTATION")
        
        config_files = [
            ("OPERATION_GUIDE.md", "Complete operation manual"),
            ("LAUNCH_SUMMARY.md", "Project status summary"),
            ("README.md", "Project documentation"),
            ("API_REFERENCE_COMPLETE.md", "API documentation"),
        ]
        
        for file_path, desc in config_files:
            exists = Path(file_path).is_file()
            self.check(f"Doc: {file_path}", exists, desc)
        
        # Summary
        self.print_summary()
        
        # Common Issues Guide
        self.print_issues_guide()

    def print_issues_guide(self):
        print(f"\n{Colors.BOLD}{Colors.YELLOW}{'═' * 70}")
        print(f"🛠️  COMMON ISSUES & SOLUTIONS | Common issues and solutions")
        print(f"{'═' * 70}{Colors.END}\n")
        
        issues = {
            "Port 8000 already in use": {
                "symptoms": "Address already in use",
                "solution": "python -m uvicorn backend.main:app --port 8001",
                "details": "Change port in command or .env"
            },
            "Database connection failed": {
                "symptoms": "Cannot connect to PostgreSQL",
                "solution": "python backend/init_db.py",
                "details": "Check DATABASE_URL in .env and PostgreSQL service"
            },
            "CORS error in browser": {
                "symptoms": "No 'Access-Control-Allow-Origin' header",
                "solution": "Check FRONTEND_URL in backend/main.py CORS config",
                "details": "Ensure frontend and backend URLs match"
            },
            "Frontend can't reach backend": {
                "symptoms": "Network error, connection refused",
                "solution": "Verify backend is running on correct port",
                "details": "Check VITE_API_BASE_URL in frontend config"
            },
            "Email not sending": {
                "symptoms": "SMTP connection error",
                "solution": "Update SMTP credentials in .env",
                "details": "Use Gmail app password, not regular password"
            },
            "Python import errors": {
                "symptoms": "ModuleNotFoundError",
                "solution": "pip install -r requirements.txt",
                "details": "Make sure virtual environment is activated"
            },
        }
        
        for issue, info in issues.items():
            print(f"{Colors.BOLD}{Colors.RED}❌ {issue}{Colors.END}")
            print(f"   {Colors.YELLOW}Symptoms:{Colors.END} {info['symptoms']}")
            print(f"   {Colors.GREEN}Solution:{Colors.END} {info['solution']}")
            print(f"   {Colors.BLUE}Details:{Colors.END} {info['details']}")
            print()

    def print_quick_commands(self):
        print(f"\n{Colors.BOLD}{Colors.CYAN}{'═' * 70}")
        print(f"⚡ QUICK COMMAND REFERENCE | Quick command reference")
        print(f"{'═' * 70}{Colors.END}\n")
        
        commands = {
            "Start Backend": "python -m uvicorn backend.main:app --reload",
            "Start Frontend": "cd frontend && npm run dev",
            "Run Tests": "python comprehensive_system_test.py",
            "Database Migrate": "python -m alembic -c backend/alembic.ini upgrade head",
            "Check System": "python final_deployment_checklist.py",
            "Create Admin": "python backend/tools/create_admin_user.py",
            "Backend Docs": "http://127.0.0.1:8000/docs",
            "Frontend App": "http://127.0.0.1:5173",
        }
        
        for task, cmd in commands.items():
            print(f"{Colors.BOLD}{task}{Colors.END}")
            print(f"  {Colors.GREEN}$ {cmd}{Colors.END}\n")

    def run(self):
        """Run complete diagnostic suite"""
        self.diagnostic_test()
        self.print_quick_commands()

def main():
    diagnostics = SystemDiagnostics()
    diagnostics.run()

if __name__ == "__main__":
    main()
