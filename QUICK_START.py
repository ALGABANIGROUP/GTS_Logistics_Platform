#!/usr/bin/env python3
"""
🚀 GTS Quick Start Guide - Quick Start Guide
Fastest way to get GTS Unified System running
Fastest way to run the GTS Unified System
"""

import subprocess
import sys
import os
from pathlib import Path

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header():
    print(f"{Colors.BOLD}{Colors.BLUE}")
    print("""
╔════════════════════════════════════════════════════════════════════╗
║                                                                    ║
║           🚀 GTS QUICK START GUIDE 🚀                              ║
║                                                                    ║
║        Quick Start Guide - GTS Unified System                      ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
    """)
    print(f"{Colors.END}")

def step(number, title, command=""):
    print(f"{Colors.BOLD}{Colors.CYAN}Step {number}: {title}{Colors.END}")
    if command:
        print(f"{Colors.GREEN}$ {command}{Colors.END}")
    print()

def success(msg):
    print(f"{Colors.GREEN}✅ {msg}{Colors.END}\n")

def info(msg):
    print(f"{Colors.BLUE}ℹ️  {msg}{Colors.END}\n")

def warning(msg):
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.END}\n")

def main():
    print_header()
    
    # Step 1: Check Python
    print(f"{Colors.BOLD}{Colors.CYAN}═══════════════════════════════════════════════════════════{Colors.END}\n")
    step(1, "Verify Python Installation | Verify Python Installation")
    
    version = sys.version_info
    if version.major >= 3 and version.minor >= 10:
        success(f"Python {version.major}.{version.minor}.{version.micro} is installed ✓")
    else:
        warning(f"Python 3.10+ required. You have Python {version.major}.{version.minor}")
        return
    
    # Step 2: Create Virtual Environment
    print(f"{Colors.BOLD}{Colors.CYAN}═══════════════════════════════════════════════════════════{Colors.END}\n")
    step(2, "Create Virtual Environment | Create Virtual Environment", 
         "python -m venv .venv")
    
    venv_path = Path(".venv")
    if venv_path.exists():
        success("Virtual environment already exists")
    else:
        print("Creating virtual environment...")
        try:
            subprocess.run([sys.executable, "-m", "venv", ".venv"], check=True)
            success("Virtual environment created successfully")
        except Exception as e:
            warning(f"Failed to create virtual environment: {e}")
            return
    
    # Step 3: Activate Virtual Environment
    print(f"{Colors.BOLD}{Colors.CYAN}═══════════════════════════════════════════════════════════{Colors.END}\n")
    step(3, "Activate Virtual Environment | Activate Virtual Environment")
    
    if sys.platform == "win32":
        activate_cmd = ".venv\\Scripts\\activate"
        info("Windows detected - Run this command in new terminal:")
        print(f"{Colors.GREEN}$ {activate_cmd}{Colors.END}\n")
    else:
        activate_cmd = "source .venv/bin/activate"
        info("Linux/Mac detected - Run this command in new terminal:")
        print(f"{Colors.GREEN}$ {activate_cmd}{Colors.END}\n")
    
    # Step 4: Install Dependencies
    print(f"{Colors.BOLD}{Colors.CYAN}═══════════════════════════════════════════════════════════{Colors.END}\n")
    step(4, "Install Python Dependencies | Install Requirements",
         "pip install -r requirements.txt")
    
    print("This may take a few minutes... (may take several minutes)\n")
    # Note: We're showing instructions, not actually running
    
    # Step 5: Install Frontend Dependencies
    print(f"{Colors.BOLD}{Colors.CYAN}═══════════════════════════════════════════════════════════{Colors.END}\n")
    step(5, "Install Frontend Dependencies | Install Frontend Requirements",
         "cd frontend && npm install && cd ..")
    
    # Step 6: Environment Configuration
    print(f"{Colors.BOLD}{Colors.CYAN}═══════════════════════════════════════════════════════════{Colors.END}\n")
    step(6, "Configure Environment Variables | Configure Environment Variables")
    
    env_file = Path(".env")
    if env_file.exists():
        success(".env file already exists")
    else:
        info("Create .env file with database connection and API keys")
        print("Required variables | Required Variables:")
        print(f"{Colors.GREEN}")
        print("  • ASYNC_DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/gts")
        print("  • DATABASE_URL=postgresql://user:pass@localhost:5432/gts")
        print("  • BACKEND_PORT=8000")
        print("  • FRONTEND_URL=http://127.0.0.1:5173")
        print("  • SMTP_HOST=smtp.gmail.com")
        print("  • EMAIL_FROM=noreply@gtsdispatcher.com")
        print("  • SECRET_KEY=your-super-secret-key")
        print(f"{Colors.END}\n")
    
    # Step 7: Database Setup
    print(f"{Colors.BOLD}{Colors.CYAN}═══════════════════════════════════════════════════════════{Colors.END}\n")
    step(7, "Setup Database | Setup Database")
    
    info("Run database migrations:")
    print(f"{Colors.GREEN}$ python -m alembic -c backend/alembic.ini upgrade head{Colors.END}\n")
    
    info("Create admin user:")
    print(f"{Colors.GREEN}$ python backend/tools/create_admin_user.py{Colors.END}\n")
    
    # Step 8: Run Tests
    print(f"{Colors.BOLD}{Colors.CYAN}═══════════════════════════════════════════════════════════{Colors.END}\n")
    step(8, "Run Tests | Run Tests")
    
    info("Comprehensive System Test:")
    print(f"{Colors.GREEN}$ python comprehensive_system_test.py{Colors.END}\n")
    
    info("Deployment Verification:")
    print(f"{Colors.GREEN}$ python final_deployment_checklist.py{Colors.END}\n")
    
    # Step 9: Start Backend
    print(f"{Colors.BOLD}{Colors.CYAN}═══════════════════════════════════════════════════════════{Colors.END}\n")
    step(9, "Start Backend Server | Start Backend Server",
         "python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000")
    
    info("Backend will be available at:")
    print(f"{Colors.BLUE}  http://127.0.0.1:8000")
    print(f"{Colors.BLUE}  API Docs: http://127.0.0.1:8000/docs{Colors.END}\n")
    
    # Step 10: Start Frontend
    print(f"{Colors.BOLD}{Colors.CYAN}═══════════════════════════════════════════════════════════{Colors.END}\n")
    step(10, "Start Frontend (New Terminal) | Start Frontend",
          "cd frontend && npm run dev")
    
    info("Frontend will be available at:")
    print(f"{Colors.BLUE}  http://127.0.0.1:5173{Colors.END}\n")
    
    # Final Summary
    print(f"{Colors.BOLD}{Colors.CYAN}═══════════════════════════════════════════════════════════{Colors.END}\n")
    print(f"{Colors.BOLD}{Colors.GREEN}")
    print("""
╔════════════════════════════════════════════════════════════════════╗
║                                                                    ║
║           ✅ QUICK START COMPLETE ✅                               ║
║                                                                    ║
║  Quick start completed successfully - you can now access the system║
║                                                                    ║
║  Next Steps | Next Steps:                                          ║
║  ✓ Open Backend: http://127.0.0.1:8000                            ║
║  ✓ Open Frontend: http://127.0.0.1:5173                           ║
║  ✓ Login with credentials from create_admin_user.py               ║
║  ✓ Explore the system!                                            ║
║                                                                    ║
║  URL Shortcuts | Shortcuts:                                        ║
║  • Backend: http://127.0.0.1:8000                                 ║
║  • Swagger Docs: http://127.0.0.1:8000/docs                       ║
║  • Frontend: http://127.0.0.1:5173                                ║
║  • ReDoc: http://127.0.0.1:8000/redoc                             ║
║                                                                    ║
║  Default Credentials | Default Login Credentials:                 ║
║  • Email: admin@gabanilogistics.com                               ║
║  • Password: AdminPass123! (or from setup)                        ║
║                                                                    ║
║  Helpful Files | Helpful Files:                                    ║
║  • OPERATION_GUIDE.md - Complete operation guide                 ║
║  • LAUNCH_SUMMARY.md - System overview                            ║
║  • README.md - Project documentation                              ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
    """)
    print(f"{Colors.END}")
    
    # Troubleshooting
    print(f"{Colors.BOLD}{Colors.YELLOW}═══════════════════════════════════════════════════════════{Colors.END}\n")
    print(f"{Colors.BOLD}{Colors.YELLOW}Troubleshooting | Troubleshooting:{Colors.END}\n")
    
    troubleshooting = """
1. Port already in use | Port already in use:
   Change port: python -m uvicorn backend.main:app --port 8001

2. Database connection error | Database connection error:
   • Check .env file credentials
   • Ensure PostgreSQL is running
   • Run: python backend/init_db.py

3. CORS error in frontend | CORS error in frontend:
   • Make sure CORS is enabled in backend
   • Check FRONTEND_URL in .env

4. Email not working | Email not working:
   • Update SMTP credentials in .env
   • Use Gmail app password (not regular password)

5. Frontend won't connect to backend | Frontend won't connect to backend:
   • Check backend is running
   • Verify BACKEND_URL in frontend config
   • Check CORS headers
    """
    print(f"{Colors.CYAN}{troubleshooting}{Colors.END}")
    
    print(f"\n{Colors.GREEN}✨ Ready to build amazing things! ✨{Colors.END}")
    print(f"{Colors.GREEN}✨ Ready to build amazing things! ✨{Colors.END}\n")

if __name__ == "__main__":
    main()
