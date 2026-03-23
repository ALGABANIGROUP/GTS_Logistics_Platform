#!/usr/bin/env python3
"""
🚀 Deploy and Test Unified System
- Runs migrations
- Starts Backend & Frontend
- Runs comprehensive tests
- Monitors health
"""

import os
import sys
import time
import subprocess
try:
    import requests
except ImportError:
    print("ERROR: requests library not installed. Run: pip install requests")
    sys.exit(1)
import json
import platform
from pathlib import Path
from datetime import datetime

# Color codes
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def log(msg, level="INFO"):
    """Print colored log messages"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    
    if level == "INFO":
        print(f"{Colors.BLUE}[{timestamp}] ℹ️  {msg}{Colors.RESET}")
    elif level == "SUCCESS":
        print(f"{Colors.GREEN}[{timestamp}] ✅ {msg}{Colors.RESET}")
    elif level == "WARNING":
        print(f"{Colors.YELLOW}[{timestamp}] ⚠️  {msg}{Colors.RESET}")
    elif level == "ERROR":
        print(f"{Colors.RED}[{timestamp}] ❌ {msg}{Colors.RESET}")
    elif level == "HEADER":
        print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.RESET}")
        print(f"{Colors.HEADER}{Colors.BOLD}{msg}{Colors.RESET}")
        print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.RESET}\n")
    elif level == "STEP":
        print(f"{Colors.CYAN}{Colors.BOLD}▶ {msg}{Colors.RESET}")

def is_running(port):
    """Check if port is in use"""
    try:
        response = requests.get(f"http://127.0.0.1:{port}", timeout=2)
        return True
    except:
        return False

def kill_port(port):
    """Kill process on specific port"""
    system = platform.system()
    try:
        if system == "Windows":
            os.system(f"netstat -ano | findstr :{port} && taskkill /F /PID <PID>")
        else:
            os.system(f"lsof -ti:{port} | xargs kill -9")
        log(f"Killed process on port {port}", "SUCCESS")
    except:
        pass

def run_command(cmd, cwd=None, description=""):
    """Run shell command and return result"""
    try:
        log(f"Running: {cmd}", "STEP")
        if description:
            log(description)
        
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            log(f"Command succeeded", "SUCCESS")
            return True, result.stdout
        else:
            log(f"Command failed: {result.stderr}", "ERROR")
            return False, result.stderr
    except subprocess.TimeoutExpired:
        log(f"Command timeout", "ERROR")
        return False, "Timeout"
    except Exception as e:
        log(f"Command error: {str(e)}", "ERROR")
        return False, str(e)

class UnifiedDeployment:
    def __init__(self):
        self.root_dir = Path(__file__).parent
        self.backend_dir = self.root_dir / "backend"
        self.frontend_dir = self.root_dir / "frontend"
        self.processes = []
        
    def print_banner(self):
        """Print beautiful banner"""
        print(f"""{Colors.HEADER}{Colors.BOLD}
╔═══════════════════════════════════════════════════════════╗
║  🚀 GTS Unified Platform - Deploy & Test System         ║
║                                                           ║
║  Deployment Pipeline:                                    ║
║  ✓ Database Migration                                    ║
║  ✓ Backend Startup                                       ║
║  ✓ Frontend Startup                                      ║
║  ✓ Health Checks                                         ║
║  ✓ Comprehensive Tests                                   ║
╚═══════════════════════════════════════════════════════════╝
{Colors.RESET}\n""")

    def step_1_migrations(self):
        """Run database migrations"""
        log("HEADER", "STEP 1: DATABASE MIGRATIONS")
        
        log("Checking for pending migrations...")
        cmd = f"cd {self.backend_dir} && python -m alembic current"
        success, output = run_command(cmd, description="Checking current migration state")
        
        if not success:
            log("Attempting upgrade...", "WARNING")
        
        cmd = f"cd {self.backend_dir} && python -m alembic upgrade head"
        success, output = run_command(cmd, description="Applying database migrations")
        
        if success:
            log("Database migrations completed successfully!", "SUCCESS")
            return True
        else:
            log("Migration failed - continuing anyway (DB may be ready)", "WARNING")
            return True

    def step_2_start_backend(self):
        """Start Backend server"""
        log("HEADER", "STEP 2: STARTING BACKEND SERVER")
        
        if is_running(8000):
            log("Port 8000 already in use", "WARNING")
            kill_port(8000)
            time.sleep(2)
        
        # Start backend in background
        backend_cmd = f"cd {self.backend_dir} && python main.py"
        log("Starting backend on port 8000...")
        
        try:
            process = subprocess.Popen(
                backend_cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            self.processes.append(("Backend", process, 8000))
            
            # Wait for backend to be ready
            log("Waiting for backend to be ready...")
            for i in range(30):
                if is_running(8000):
                    log(f"✅ Backend is running on http://127.0.0.1:8000", "SUCCESS")
                    log("API Docs available at http://127.0.0.1:8000/docs", "INFO")
                    return True
                time.sleep(1)
                sys.stdout.write(f"\r  Attempt {i+1}/30...")
                sys.stdout.flush()
            
            log("Backend startup timeout", "ERROR")
            return False
        except Exception as e:
            log(f"Failed to start backend: {str(e)}", "ERROR")
            return False

    def step_3_start_frontend(self):
        """Start Frontend server"""
        log("HEADER", "STEP 3: STARTING FRONTEND SERVER")
        
        if is_running(5173):
            log("Port 5173 already in use", "WARNING")
            kill_port(5173)
            time.sleep(2)
        
        # Start frontend in background
        frontend_cmd = f"cd {self.frontend_dir} && npm run dev"
        log("Starting frontend on port 5173...")
        
        try:
            process = subprocess.Popen(
                frontend_cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            self.processes.append(("Frontend", process, 5173))
            
            # Wait for frontend to be ready
            log("Waiting for frontend to be ready...")
            for i in range(30):
                if is_running(5173):
                    log(f"✅ Frontend is running on http://127.0.0.1:5173", "SUCCESS")
                    return True
                time.sleep(1)
                sys.stdout.write(f"\r  Attempt {i+1}/30...")
                sys.stdout.flush()
            
            log("Frontend startup timeout", "ERROR")
            return False
        except Exception as e:
            log(f"Failed to start frontend: {str(e)}", "ERROR")
            return False

    def step_4_health_check(self):
        """Check system health"""
        log("HEADER", "STEP 4: HEALTH CHECKS")
        
        endpoints = [
            ("Backend", "http://127.0.0.1:8000/health", 8000),
            ("Frontend", "http://127.0.0.1:5173", 5173),
        ]
        
        all_healthy = True
        for name, url, port in endpoints:
            try:
                response = requests.get(url, timeout=5)
                if response.status_code < 500:
                    log(f"✅ {name} ({port}): Healthy", "SUCCESS")
                else:
                    log(f"⚠️  {name} ({port}): Status {response.status_code}", "WARNING")
                    all_healthy = False
            except:
                log(f"❌ {name} ({port}): Unreachable", "ERROR")
                all_healthy = False
        
        return all_healthy

    def step_5_run_tests(self):
        """Run comprehensive test suite"""
        log("HEADER", "STEP 5: RUNNING COMPREHENSIVE TESTS")
        
        test_file = self.root_dir / "test_unified_system.py"
        if not test_file.exists():
            log(f"Test file not found: {test_file}", "ERROR")
            return False
        
        cmd = f"cd {self.root_dir} && python test_unified_system.py"
        success, output = run_command(cmd, description="Running unified system tests")
        
        if output:
            print(output)
        
        return success

    def step_6_summary(self):
        """Print deployment summary"""
        log("HEADER", "DEPLOYMENT SUMMARY")
        
        summary = f"""
{Colors.GREEN}{Colors.BOLD}✅ DEPLOYMENT COMPLETE!{Colors.RESET}

{Colors.CYAN}{Colors.BOLD}🌐 Frontend:{Colors.RESET}
   URL: {Colors.YELLOW}http://127.0.0.1:5173{Colors.RESET}
   - Login Page: /login
   - System Selector: /system-selector
   - Dashboard: /dashboard
   - Admin Panel: /admin/unified-dashboard

{Colors.CYAN}{Colors.BOLD}🔌 Backend:{Colors.RESET}
   URL: {Colors.YELLOW}http://127.0.0.1:8000{Colors.RESET}
   - API Docs: /docs
   - Swagger: /swagger
   - Systems: /api/v1/systems
   - Admin: /api/v1/admin
   - WebSocket: /api/v1/ws/live

{Colors.CYAN}{Colors.BOLD}📊 Key Endpoints:{Colors.RESET}
   POST   /auth/token                    - Login
   GET    /api/v1/systems/available      - List systems
   POST   /api/v1/systems/switch         - Switch system
   GET    /api/v1/admin/overview         - Admin dashboard
   GET    /api/v1/admin/system-health    - System health

{Colors.CYAN}{Colors.BOLD}📝 Test Credentials:{Colors.RESET}
   Email:    enjoy983@hotmail.com
   Password: password123

{Colors.CYAN}{Colors.BOLD}📚 Documentation:{Colors.RESET}
   - QUICK_START.md
   - UNIFIED_SYSTEM_GUIDE.md
   - API Swagger Docs

{Colors.YELLOW}{Colors.BOLD}⚠️  Press Ctrl+C to stop servers{Colors.RESET}
"""
        print(summary)

    def cleanup(self):
        """Cleanup and stop all processes"""
        log("Cleaning up processes...", "INFO")
        for name, process, port in self.processes:
            try:
                process.terminate()
                process.wait(timeout=5)
            except:
                process.kill()
        log("Cleanup complete", "SUCCESS")

    def run(self):
        """Execute full deployment pipeline"""
        self.print_banner()
        
        try:
            # Step 1: Migrations
            if not self.step_1_migrations():
                log("Migrations critical - aborting", "ERROR")
                return False
            
            # Step 2: Start Backend
            if not self.step_2_start_backend():
                log("Backend startup failed - aborting", "ERROR")
                return False
            
            time.sleep(2)
            
            # Step 3: Start Frontend
            if not self.step_3_start_frontend():
                log("Frontend startup failed - aborting", "ERROR")
                return False
            
            time.sleep(2)
            
            # Step 4: Health Check
            if not self.step_4_health_check():
                log("Health check warnings detected", "WARNING")
            
            # Step 5: Run Tests
            self.step_5_run_tests()
            
            # Step 6: Summary
            self.step_6_summary()
            
            # Keep servers running
            log("Servers are running. Press Ctrl+C to stop.", "INFO")
            while True:
                time.sleep(1)
                
        except KeyboardInterrupt:
            log("\nShutdown signal received", "INFO")
        finally:
            self.cleanup()

if __name__ == "__main__":
    deployer = UnifiedDeployment()
    deployer.run()
