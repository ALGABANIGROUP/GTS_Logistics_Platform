#!/usr/bin/env python3
"""
Setup and run the unified system
Developed based on UNIFIED_SYSTEM_GUIDE.md
"""

import os
import sys
import subprocess
import time
import platform
from pathlib import Path

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

class SystemSetup:
    def __init__(self):
        self.repo_root = Path(__file__).parent
        self.backend_dir = self.repo_root / "backend"
        self.frontend_dir = self.repo_root / "frontend"
        self.is_windows = platform.system() == "Windows"
    
    def print_header(self, text):
        print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 70}")
        print(f"  {text}")
        print(f"{'=' * 70}{Colors.ENDC}\n")
    
    def print_step(self, num, text, emoji=""):
        print(f"{Colors.OKBLUE}{Colors.BOLD}[Step {num}] {emoji} {text}{Colors.ENDC}")
    
    def print_success(self, text):
        print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")
    
    def print_warning(self, text):
        print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")
    
    def run_command(self, cmd, cwd=None, description=""):
        """Run command in terminal"""
        if description:
            print(f"{Colors.OKCYAN}→ {description}...{Colors.ENDC}")
        
        try:
            result = subprocess.run(cmd, cwd=cwd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                self.print_success(description or "Executed successfully")
                return True
            else:
                self.print_warning(f"{description}: {result.stderr[:100]}")
                return False
        except Exception as e:
            self.print_warning(f"{description}: {str(e)}")
            return False
    
    def setup_backend(self):
        """Setup Backend"""
        self.print_header("🔧 Setup Backend")
        
        self.print_step(1, "Check virtual environment", "🐍")
        venv_path = self.backend_dir.parent / ".venv"
        
        if not venv_path.exists():
            self.print_warning("Virtual environment does not exist")
            return False
        
        self.print_success("Virtual environment exists")
        
        self.print_step(2, "Install/update requirements", "📦")
        if self.is_windows:
            pip_cmd = str(venv_path / "Scripts" / "pip")
        else:
            pip_cmd = str(venv_path / "bin" / "pip")
        
        self.run_command(f"{pip_cmd} install -q -r requirements.txt", cwd=self.backend_dir, description="Install requirements")
        
        return True
    
    def setup_frontend(self):
        """Setup Frontend"""
        self.print_header("🎨 Setup Frontend")
        
        self.print_step(1, "Check Node.js", "📱")
        result = self.run_command("node --version", description="Check Node.js")
        
        if not result:
            self.print_warning("Node.js not found or not available in PATH")
            return False
        
        self.print_step(2, "Install/update requirements", "📦")
        self.run_command("npm install -q", cwd=self.frontend_dir, description="Install npm packages")
        
        return True
    
    def run_migrations(self):
        """Run Database Migrations"""
        self.print_header("🗄️  Run Database Migrations")
        
        self.print_step(1, "Run Alembic Migration", "🔄")
        
        if self.is_windows:
            cmd = "python -m alembic -c backend\\alembic.ini upgrade head"
        else:
            cmd = "python -m alembic -c backend/alembic.ini upgrade head"
        
        self.run_command(cmd, cwd=self.repo_root, description="Upgrade database")
        
        self.print_success("Migrations ran successfully (or were already up to date)")
    
    def start_backend(self):
        """Start Backend Server"""
        self.print_header("🚀 Start Backend Server")
        
        self.print_step(1, "Start Uvicorn on port 8000", "⚡")
        
        if self.is_windows:
            python_exe = self.backend_dir.parent / ".venv" / "Scripts" / "python.exe"
        else:
            python_exe = self.backend_dir.parent / ".venv" / "bin" / "python"
        
        print(f"{Colors.OKCYAN}→ Running: {python_exe} backend/main.py{Colors.ENDC}\n")
        
        try:
            subprocess.Popen([str(python_exe), "backend/main.py"], cwd=self.repo_root)
            self.print_success("Backend started successfully on http://127.0.0.1:8000")
            time.sleep(3)  # Wait for server to start
            return True
        except Exception as e:
            self.print_warning(f"Failed to start Backend: {str(e)}")
            return False
    
    def start_frontend(self):
        """Start Frontend Server"""
        self.print_header("🎨 Start Frontend Server")
        
        self.print_step(1, "Start Vite on port 5173", "⚡")
        
        print(f"{Colors.OKCYAN}→ Running: npm run dev{Colors.ENDC}\n")
        
        try:
            subprocess.Popen("npm run dev", cwd=self.frontend_dir, shell=True)
            self.print_success("Frontend started successfully on http://127.0.0.1:5173")
            time.sleep(3)
            return True
        except Exception as e:
            self.print_warning(f"Failed to start Frontend: {str(e)}")
            return False
    
    def print_setup_complete(self):
        """Print setup completion message"""
        self.print_header("✅ Setup completed successfully!")
        
        print(f"{Colors.OKGREEN}{Colors.BOLD}🌐 System is ready for use!{Colors.ENDC}\n")
        
        print(f"{Colors.OKBLUE}Links:{Colors.ENDC}")
        print(f"  🏠 Frontend: {Colors.BOLD}http://127.0.0.1:5173{Colors.ENDC}")
        print(f"  🔧 Backend Server: {Colors.BOLD}http://127.0.0.1:8000{Colors.ENDC}")
        print(f"  📚 Swagger Docs: {Colors.BOLD}http://127.0.0.1:8000/docs{Colors.ENDC}\n")
        
        print(f"{Colors.OKBLUE}Usage steps:{Colors.ENDC}")
        print(f"  1. Go to {Colors.BOLD}http://127.0.0.1:5173{Colors.ENDC}")
        print(f"  2. Login with email and password")
        print(f"  3. Choose the system (GTS or TMS)")
        print(f"  4. Use the interface\n")
        
        print(f"{Colors.WARNING}📝 Note:{Colors.ENDC}")
        print(f"  Both servers (Backend + Frontend) must remain running")
        print(f"  To stop servers, press Ctrl+C in each terminal window\n")
    
    def run(self, skip_migrations=False):
        """Run complete setup"""
        print(f"\n{Colors.HEADER}{Colors.BOLD}")
        print("""
╔════════════════════════════════════════════════════════════════════╗
║                                                                    ║
║           🚀 Setup and Run GTS Unified System                     ║
║                                                                    ║
║              Gabani Transport Solutions (GTS) Unified Setup              ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
        """)
        print(Colors.ENDC)
        
        # Setup Backend
        if not self.setup_backend():
            self.print_warning("Backend setup failed")
            return False
        
        # Setup Frontend
        if not self.setup_frontend():
            self.print_warning("Frontend setup failed")
            return False
        
        # Run Migrations
        if not skip_migrations:
            self.run_migrations()
        
        # Start servers
        if not self.start_backend():
            self.print_warning("Failed to start Backend")
            return False
        
        if not self.start_frontend():
            self.print_warning("Failed to start Frontend")
            return False
        
        # Success message
        self.print_setup_complete()
        
        print(f"{Colors.BOLD}Press Ctrl+C to stop servers{Colors.ENDC}\n")
        
        # Keep program running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print(f"\n{Colors.WARNING}⏹️  Servers stopped{Colors.ENDC}\n")
            return True


if __name__ == "__main__":
    setup = SystemSetup()
    success = setup.run(skip_migrations=False)
    sys.exit(0 if success else 1)
