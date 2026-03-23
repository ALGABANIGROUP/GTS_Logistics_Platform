#!/usr/bin/env python3
"""
✅ System Status Verification
- Checks all components
- Validates configuration
- Reports readiness
"""

import os
import sys
from pathlib import Path
import json

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def check(condition, name, details=""):
    status = f"{Colors.GREEN}✅{Colors.RESET}" if condition else f"{Colors.RED}❌{Colors.RESET}"
    print(f"  {status} {name:<50} {Colors.CYAN}{details}{Colors.RESET}")
    return condition

def section(title):
    print(f"\n{Colors.BOLD}{Colors.CYAN}{title}{Colors.RESET}")
    print(f"  {Colors.CYAN}{'-' * 70}{Colors.RESET}")

def print_banner():
    print(f"""{Colors.CYAN}{Colors.BOLD}
╔════════════════════════════════════════════════════════════╗
║  ✅ GTS UNIFIED SYSTEM - STATUS VERIFICATION              ║
╚════════════════════════════════════════════════════════════╝
{Colors.RESET}""")

class SystemVerification:
    def __init__(self):
        self.root = Path(__file__).parent
        self.passed = 0
        self.failed = 0
        self.total = 0
    
    def verify_core_files(self):
        """Verify all core files exist"""
        section("📁 CORE FILES")
        
        files = {
            "backend/main.py": "Backend entry point",
            "backend/auth/unified_auth.py": "Unified authentication",
            "backend/models/unified_models.py": "Database models",
            "backend/routes/system_switcher.py": "System switcher API",
            "backend/routes/admin_unified.py": "Admin API",
            "backend/tms/core/tms_core.py": "TMS core",
            "backend/alembic/versions/003_unified_auth_system.py": "Database migration",
            "frontend/src/pages/SystemSelector.jsx": "System selector UI",
            "frontend/src/pages/admin/UnifiedAdminDashboard.jsx": "Admin dashboard",
            "frontend/src/pages/Login.jsx": "Login page",
            "frontend/src/pages/Register.jsx": "Register page",
            "test_unified_system.py": "Test suite",
            "advanced_test_suite.py": "Advanced tests",
            "setup_and_run.py": "Setup automation",
            "deploy_and_test.py": "Deploy pipeline",
        }
        
        for file_path, description in files.items():
            full_path = self.root / file_path
            exists = full_path.exists()
            self.total += 1
            if exists:
                self.passed += 1
            else:
                self.failed += 1
            check(exists, description, file_path)
    
    def verify_backend_structure(self):
        """Verify backend structure"""
        section("🔌 BACKEND STRUCTURE")
        
        backend_items = {
            "backend": "Backend directory",
            "backend/auth": "Auth module",
            "backend/routes": "Routes directory",
            "backend/models": "Models directory",
            "backend/tms": "TMS module",
            "backend/database": "Database module",
            "backend/alembic": "Migrations directory",
        }
        
        for item_path, description in backend_items.items():
            full_path = self.root / item_path
            exists = full_path.exists()
            self.total += 1
            if exists:
                self.passed += 1
            else:
                self.failed += 1
            check(exists, description, item_path)
    
    def verify_frontend_structure(self):
        """Verify frontend structure"""
        section("🎨 FRONTEND STRUCTURE")
        
        frontend_items = {
            "frontend": "Frontend directory",
            "frontend/src": "Source directory",
            "frontend/src/pages": "Pages directory",
            "frontend/src/components": "Components directory",
            "frontend/src/api": "API clients",
            "frontend/src/context": "Context providers",
            "frontend/src/config": "Configuration",
        }
        
        for item_path, description in frontend_items.items():
            full_path = self.root / item_path
            exists = full_path.exists()
            self.total += 1
            if exists:
                self.passed += 1
            else:
                self.failed += 1
            check(exists, description, item_path)
    
    def verify_dependencies(self):
        """Verify key dependencies"""
        section("📦 DEPENDENCIES")
        
        backend_reqs = self.root / "backend" / "requirements.txt"
        frontend_package = self.root / "frontend" / "package.json"
        
        self.total += 2
        if backend_reqs.exists():
            self.passed += 1
            print(f"  {Colors.GREEN}✅{Colors.RESET} Python requirements", end="")
            try:
                with open(backend_reqs) as f:
                    lines = f.readlines()
                print(f" ({len(lines)} packages)")
            except:
                print()
        else:
            self.failed += 1
            print(f"  {Colors.RED}❌{Colors.RESET} Python requirements")
        
        if frontend_package.exists():
            self.passed += 1
            print(f"  {Colors.GREEN}✅{Colors.RESET} NPM dependencies", end="")
            try:
                with open(frontend_package) as f:
                    pkg = json.load(f)
                    deps = len(pkg.get("dependencies", {}))
                print(f" ({deps} packages)")
            except:
                print()
        else:
            self.failed += 1
            print(f"  {Colors.RED}❌{Colors.RESET} NPM dependencies")
    
    def verify_configuration(self):
        """Verify configuration files"""
        section("⚙️  CONFIGURATION")
        
        configs = {
            "frontend/vite.config.js": "Vite config",
            "frontend/.env.example": "Frontend env template",
            "pyrightconfig.json": "Type checking config",
            "eslint.config.mjs": "Linting config",
        }
        
        for config_path, description in configs.items():
            full_path = self.root / config_path
            exists = full_path.exists()
            if exists:
                self.total += 1
                self.passed += 1
                check(True, description, config_path)
    
    def verify_documentation(self):
        """Verify documentation files"""
        section("📚 DOCUMENTATION")
        
        docs = {
            "README.md": "Project README",
            "QUICK_START.md": "Quick start guide",
            "UNIFIED_SYSTEM_GUIDE.md": "System architecture guide",
            "BOS_SYSTEM_INDEX.md": "BOS documentation",
        }
        
        for doc_path, description in docs.items():
            full_path = self.root / doc_path
            exists = full_path.exists()
            if exists:
                self.total += 1
                self.passed += 1
                check(True, description, doc_path)
    
    def verify_environment(self):
        """Verify environment setup"""
        section("🌍 ENVIRONMENT")
        
        # Check Python
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
        self.total += 1
        if sys.version_info.major >= 3 and sys.version_info.minor >= 8:
            self.passed += 1
            check(True, "Python version", f"{python_version}")
        else:
            self.failed += 1
            check(False, "Python version", f"{python_version} (need 3.8+)")
        
        # Check Node.js
        self.total += 1
        node_check = os.system("node --version > nul 2>&1" if sys.platform == "win32" else "node --version > /dev/null 2>&1") == 0
        check(node_check, "Node.js", "Node.js installed" if node_check else "Node.js not found")
        if node_check:
            self.passed += 1
        else:
            self.failed += 1
        
        # Check pip
        self.total += 1
        pip_check = os.system("pip --version > nul 2>&1" if sys.platform == "win32" else "pip --version > /dev/null 2>&1") == 0
        check(pip_check, "pip", "pip installed" if pip_check else "pip not found")
        if pip_check:
            self.passed += 1
        else:
            self.failed += 1
    
    def print_summary(self):
        """Print final summary"""
        section("📊 VERIFICATION SUMMARY")
        
        success_rate = (self.passed / self.total * 100) if self.total > 0 else 0
        
        print(f"\n  {Colors.BOLD}Results:{Colors.RESET}")
        print(f"    ✅ Passed: {Colors.GREEN}{self.passed}{Colors.RESET} / {self.total}")
        print(f"    ❌ Failed: {Colors.RED}{self.failed}{Colors.RESET} / {self.total}")
        print(f"    📊 Rate:   {Colors.CYAN}{success_rate:.1f}%{Colors.RESET}")
        
        print(f"\n  {Colors.BOLD}Status:{Colors.RESET}")
        if success_rate >= 90:
            status = f"{Colors.GREEN}✅ READY FOR DEPLOYMENT{Colors.RESET}"
        elif success_rate >= 70:
            status = f"{Colors.YELLOW}⚠️  PARTIALLY READY (Missing files){Colors.RESET}"
        else:
            status = f"{Colors.RED}❌ NOT READY (Major issues){Colors.RESET}"
        
        print(f"    {status}")
        
        print(f"\n  {Colors.BOLD}Next Steps:{Colors.RESET}")
        print(f"    1. Run: {Colors.CYAN}python deploy_and_test.py{Colors.RESET}")
        print(f"    2. Or:  {Colors.CYAN}python setup_and_run.py{Colors.RESET}")
        print(f"    3. Then: {Colors.CYAN}python advanced_test_suite.py{Colors.RESET}")
        
        return success_rate

    def run(self):
        """Run all verifications"""
        print_banner()
        
        self.verify_core_files()
        self.verify_backend_structure()
        self.verify_frontend_structure()
        self.verify_dependencies()
        self.verify_configuration()
        self.verify_documentation()
        self.verify_environment()
        
        rate = self.print_summary()
        
        return 0 if rate >= 70 else 1

if __name__ == "__main__":
    verifier = SystemVerification()
    exit_code = verifier.run()
    sys.exit(exit_code)
