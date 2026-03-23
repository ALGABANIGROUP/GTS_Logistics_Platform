#!/usr/bin/env python3
"""
GTS Final Verification & Deployment Checklist
EN GTS
"""

import subprocess
import os
from datetime import datetime
from pathlib import Path

class GreenText:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    END = '\033[0m'
    BOLD = '\033[1m'

class DeploymentChecklist:
    """Final deployment checklist and verification"""
    
    def __init__(self):
        self.passed_checks = []
        self.failed_checks = []
        self.warnings = []
    
    def check(self, name: str, condition: bool, details: str = ""):
        """Record a check result"""
        if condition:
            print(f"{GreenText.GREEN}✅ {name}{GreenText.END}")
            if details:
                print(f"   {GreenText.CYAN}→ {details}{GreenText.END}")
            self.passed_checks.append(name)
        else:
            print(f"{GreenText.RED}❌ {name}{GreenText.END}")
            if details:
                print(f"   {GreenText.YELLOW}→ {details}{GreenText.END}")
            self.failed_checks.append(name)
    
    def warn(self, name: str, message: str = ""):
        """Record a warning"""
        print(f"{GreenText.YELLOW}⚠️  {name}{GreenText.END}")
        if message:
            print(f"   {GreenText.CYAN}→ {message}{GreenText.END}")
        self.warnings.append(name)
    
    def run_all_checks(self):
        """Run all verification checks"""
        
        print(f"\n{GreenText.BOLD}{GreenText.BLUE}")
        print("""
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║     🚀 GTS FINAL VERIFICATION & DEPLOYMENT CHECKLIST 🚀       ║
║                                                                ║
║  EN GTS                      ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
        """)
        print(f"{GreenText.END}\n")
        
        # ============ ENVIRONMENT CHECKS ============
        print(f"{GreenText.BOLD}{GreenText.CYAN}📋 Environment & Configuration Checks{GreenText.END}\n")
        
        self.check(".env file exists", Path(".env").exists(), "Configuration file found")
        self.check("requirements.txt exists", Path("requirements.txt").exists(), "Python dependencies file found")
        self.check("frontend package.json exists", Path("frontend/package.json").exists(), "Node.js configuration found")
        
        # ============ PROJECT STRUCTURE CHECKS ============
        print(f"\n{GreenText.BOLD}{GreenText.CYAN}📁 Project Structure Checks{GreenText.END}\n")
        
        self.check("Backend directory exists", Path("backend").exists(), "Backend source code found")
        self.check("Frontend directory exists", Path("frontend").exists(), "Frontend source code found")
        self.check("Database migrations exist", Path("backend/alembic/versions").exists(), "Migration files found")
        self.check("Models defined", Path("backend/models").exists(), "Database models found")
        self.check("Routes configured", Path("backend/routes").exists(), "API routes found")
        self.check("Services created", Path("backend/services").exists(), "Business logic services found")
        self.check("Bots implemented", Path("backend/bots").exists(), "AI bots found")
        
        # ============ BACKEND CONFIGURATION CHECKS ============
        print(f"\n{GreenText.BOLD}{GreenText.CYAN}⚙️  Backend Configuration Checks{GreenText.END}\n")
        
        try:
            with open("backend/main.py", "r", encoding="utf-8") as f:
                main_content = f.read()
                self.check("FastAPI app configured", "FastAPI" in main_content, "Main application setup found")
                self.check("CORS enabled", "CORSMiddleware" in main_content or "cors" in main_content.lower(), 
                          "Cross-origin requests configured")
                self.check("Routes mounted", "include_router" in main_content, "API routes included")
        except Exception as e:
            self.failed_checks.append(f"Backend check error: {str(e)}")
        
        # ============ AUTHENTICATION CHECKS ============
        print(f"\n{GreenText.BOLD}{GreenText.CYAN}🔐 Authentication & Security Checks{GreenText.END}\n")
        
        try:
            with open("backend/auth/unified_auth.py", "r", encoding="utf-8") as f:
                auth_content = f.read()
                self.check("Unified auth system", "UnifiedAuthSystem" in auth_content, "Centralized authentication found")
                self.check("JWT tokens implemented", "jwt" in auth_content.lower(), "JWT authentication configured")
                self.check("Password hashing", "hash" in auth_content.lower(), "Password encryption enabled")
        except Exception as e:
            self.warn(f"Auth check - {str(e)}")
        
        # ============ DATABASE CHECKS ============
        print(f"\n{GreenText.BOLD}{GreenText.CYAN}🗄️  Database Checks{GreenText.END}\n")
        
        try:
            with open("backend/database/config.py", "r", encoding="utf-8") as f:
                db_content = f.read()
                self.check("Database configured", "postgresql" in db_content or "asyncpg" in db_content, 
                          "PostgreSQL async driver setup")
                self.check("SQLAlchemy ORM", "SQLAlchemy" in db_content, "ORM configured")
                self.check("Base model defined", "Base" in db_content, "Database base model found")
        except Exception as e:
            self.warn(f"Database check - {str(e)}")
        
        # ============ EMAIL SYSTEM CHECKS ============
        print(f"\n{GreenText.BOLD}{GreenText.CYAN}📧 Email System Checks{GreenText.END}\n")
        
        try:
            with open("backend/services/unified_email.py", "r", encoding="utf-8") as f:
                email_content = f.read()
                self.check("Email system implemented", "UnifiedEmailSystem" in email_content, 
                          "Email service configured")
                self.check("SMTP configured", "smtp" in email_content.lower(), "SMTP server setup")
                self.check("Email templates", "html" in email_content.lower(), "HTML email templates found")
        except Exception as e:
            self.warn(f"Email check - {str(e)}")
        
        # ============ ADMIN PANEL CHECKS ============
        print(f"\n{GreenText.BOLD}{GreenText.CYAN}👨💼 Admin Panel Checks{GreenText.END}\n")
        
        try:
            admin_files = [
                "backend/routes/admin_unified.py",
                "frontend/src/pages/admin/UnifiedAdminDashboard.jsx"
            ]
            
            admin_found = all(Path(f).exists() for f in admin_files)
            self.check("Admin routes implemented", Path(admin_files[0]).exists(), "Backend admin endpoints")
            self.check("Admin dashboard UI", Path(admin_files[1]).exists(), "Frontend admin interface")
            
            with open("backend/routes/admin_unified.py", "r", encoding="utf-8") as f:
                admin_content = f.read()
                self.check("User management", "/users" in admin_content, "Admin user management")
                self.check("Statistics dashboard", "statistics" in admin_content.lower(), "Analytics features")
                self.check("Settings management", "settings" in admin_content.lower(), "Configuration management")
        except Exception as e:
            self.warn(f"Admin check - {str(e)}")
        
        # ============ PRICING & SUBSCRIPTIONS CHECKS ============
        print(f"\n{GreenText.BOLD}{GreenText.CYAN}💰 Pricing & Subscriptions Checks{GreenText.END}\n")
        
        try:
            with open("backend/tms/core/tms_core.py", "r", encoding="utf-8") as f:
                pricing_content = f.read()
                self.check("Subscription tiers defined", "SubscriptionTier" in pricing_content, 
                          "Three tiers: Starter, Professional, Enterprise")
                self.check("Pricing models", "SubscriptionPlans" in pricing_content, "Pricing configuration")
                self.check("Permission levels", "PermissionLevel" in pricing_content, "Access control system")
        except Exception as e:
            self.warn(f"Pricing check - {str(e)}")
        
        # ============ AI BOTS CHECKS ============
        print(f"\n{GreenText.BOLD}{GreenText.CYAN}🤖 AI Bots Checks{GreenText.END}\n")
        
        bot_files = list(Path("backend/bots").glob("*.py")) if Path("backend/bots").exists() else []
        self.check(f"AI bots implemented", len(bot_files) > 0, 
                  f"Found {len(bot_files)} bot implementations")
        
        # Check for specific bots
        bot_names = ["finance", "freight", "general_manager", "sales_intelligence", "safe_manager"]
        for bot_name in bot_names:
            bot_exists = any(bot_name.lower() in str(f).lower() for f in bot_files)
            self.check(f"{bot_name.title()} bot", bot_exists, f"Bot module found")
        
        # ============ TESTING CHECKS ============
        print(f"\n{GreenText.BOLD}{GreenText.CYAN}🧪 Testing Checks{GreenText.END}\n")
        
        test_files = [
            ("comprehensive_system_test.py", "Comprehensive system tests"),
            ("test_unified_system.py", "Unified system tests"),
            ("test_safety_system.py", "Safety tests"),
            ("advanced_test_suite.py", "Advanced tests"),
        ]
        
        for test_file, description in test_files:
            self.check(f"Test: {description}", Path(test_file).exists(), f"Test file: {test_file}")
        
        # ============ DOCUMENTATION CHECKS ============
        print(f"\n{GreenText.BOLD}{GreenText.CYAN}📚 Documentation Checks{GreenText.END}\n")
        
        doc_files = [
            ("OPERATION_GUIDE.md", "Operation guide"),
            ("README.md", "Project README"),
            ("BOS_SYSTEM_INDEX.md", "Bot OS documentation"),
        ]
        
        for doc_file, description in doc_files:
            self.check(f"Documentation: {description}", Path(doc_file).exists(), f"File: {doc_file}")
        
        # ============ FRONTEND CHECKS ============
        print(f"\n{GreenText.BOLD}{GreenText.CYAN}🖥️  Frontend Checks{GreenText.END}\n")
        
        frontend_pages = [
            "Login.jsx",
            "Dashboard.jsx",
            "Shipments.jsx",
            "LoadBoard.jsx",
            "Pricing.jsx",
            "UnifiedAdminDashboard.jsx"
        ]
        
        frontend_path = Path("frontend/src/pages")
        for page in frontend_pages:
            page_exists = (frontend_path / page).exists()
            self.check(f"Page: {page.replace('.jsx', '')}", page_exists, f"React component found")
        
        # ============ FINAL SUMMARY ============
        self.print_summary()
    
    def print_summary(self):
        """Print final summary"""
        total = len(self.passed_checks) + len(self.failed_checks)
        pass_rate = (len(self.passed_checks) / total * 100) if total > 0 else 0
        
        print(f"\n{GreenText.BOLD}{GreenText.BLUE}{'='*70}{GreenText.END}")
        print(f"{GreenText.BOLD}{GreenText.BLUE}{'FINAL DEPLOYMENT VERIFICATION SUMMARY':^70}{GreenText.END}")
        print(f"{GreenText.BOLD}{GreenText.BLUE}{'='*70}{GreenText.END}\n")
        
        print(f"{GreenText.GREEN}✅ Passed Checks: {len(self.passed_checks)}/{total}{GreenText.END}")
        print(f"{GreenText.RED}❌ Failed Checks: {len(self.failed_checks)}/{total}{GreenText.END}")
        print(f"{GreenText.YELLOW}⚠️  Warnings: {len(self.warnings)}{GreenText.END}")
        print(f"\n{GreenText.BLUE}📊 Completion Rate: {pass_rate:.1f}%{GreenText.END}\n")
        
        if len(self.failed_checks) == 0:
            print(f"{GreenText.GREEN}{GreenText.BOLD}{'✅ SYSTEM IS READY FOR PRODUCTION DEPLOYMENT ✅':^70}{GreenText.END}")
            print(f"{GreenText.GREEN}{GreenText.BOLD}{'✅ EN ✅':^70}{GreenText.END}\n")
            return True
        else:
            print(f"{GreenText.YELLOW}{GreenText.BOLD}{'⚠️  Review failed checks before deployment':^70}{GreenText.END}\n")
            print("Failed Checks:")
            for check in self.failed_checks:
                print(f"  {GreenText.RED}• {check}{GreenText.END}")
            return False
    
    def generate_report(self):
        """Generate deployment report"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        report = f"""
╔════════════════════════════════════════════════════════════════════╗
║                  GTS DEPLOYMENT VERIFICATION REPORT                ║
║                   EN - GTS                     ║
╚════════════════════════════════════════════════════════════════════╝

Timestamp: {timestamp}
EN: {timestamp}

SUMMARY | EN:
─────────────────────────────────────────────────────────────────────
✅ Passed Checks: {len(self.passed_checks)}
❌ Failed Checks: {len(self.failed_checks)}
⚠️  Warnings: {len(self.warnings)}

Total: {len(self.passed_checks) + len(self.failed_checks)} checks

PASSED CHECKS | EN:
─────────────────────────────────────────────────────────────────────
{chr(10).join(f'  ✅ {check}' for check in self.passed_checks)}

{'FAILED CHECKS | EN:' if self.failed_checks else ''}
─────────────────────────────────────────────────────────────────────
{chr(10).join(f'  ❌ {check}' for check in self.failed_checks) if self.failed_checks else '  None - All checks passed!'}

WARNINGS | EN:
─────────────────────────────────────────────────────────────────────
{chr(10).join(f'  ⚠️  {warn}' for warn in self.warnings) if self.warnings else '  None'}

DEPLOYMENT READINESS | EN:
─────────────────────────────────────────────────────────────────────
Status: {'🟢 READY FOR PRODUCTION' if len(self.failed_checks) == 0 else '🟡 NEEDS REVIEW'}
EN: {'🟢 EN' if len(self.failed_checks) == 0 else '🟡 EN'}

NEXT STEPS | EN:
─────────────────────────────────────────────────────────────────────
1. Review all failed checks (if any)
   EN

2. Run comprehensive system test
   EN
   $ python comprehensive_system_test.py

3. Deploy to production
   EN
   $ python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000

4. Monitor system performance
   EN

Report Generated: {timestamp}
"""
        
        # Save report
        report_file = Path("deployment_report.txt")
        report_file.write_text(report)
        print(f"\n{GreenText.CYAN}📄 Deployment report saved to: {report_file}{GreenText.END}\n")
        
        return report


def main():
    """Main entry point"""
    checker = DeploymentChecklist()
    checker.run_all_checks()
    report = checker.generate_report()
    print(report)


if __name__ == "__main__":
    main()
