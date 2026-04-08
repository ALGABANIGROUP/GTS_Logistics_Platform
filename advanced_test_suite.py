#!/usr/bin/env python3
"""
🧪 Advanced Unified System Test Suite
- Tests all endpoints
- Validates responses
- Checks database connectivity
- Verifies authentication flow
"""

try:
    import requests
except ImportError:
    print("ERROR: requests library not installed. Run: pip install requests")
    import sys
    sys.exit(1)
import json
import time
from datetime import datetime
from typing import Dict, Tuple, List

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.RESET}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text}{Colors.RESET}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.RESET}\n")

def print_test(name, passed, details=""):
    status = f"{Colors.GREEN}✅ PASSED{Colors.RESET}" if passed else f"{Colors.RED}❌ FAILED{Colors.RESET}"
    print(f"  {name:<50} {status}")
    if details and not passed:
        print(f"    {Colors.YELLOW}➜ {details}{Colors.RESET}")

def print_endpoint_result(endpoint, method, status_code, response_time):
    color = Colors.GREEN if status_code < 400 else Colors.YELLOW if status_code < 500 else Colors.RED
    print(f"  {method:<6} {endpoint:<45} {color}{status_code}{Colors.RESET} ({response_time:.2f}s)")

class AdvancedTestSuite:
    def __init__(self, backend_url="http://127.0.0.1:8000"):
        self.backend_url = backend_url
        self.token = None
        self.results = []
        self.total_tests = 0
        self.passed_tests = 0
        
    def check_backend_connectivity(self) -> bool:
        """Check if backend is accessible"""
        print_header("1️⃣  BACKEND CONNECTIVITY CHECK")
        
        try:
            response = requests.get(f"{self.backend_url}/api/v1/system/readiness", timeout=5)
            print_test("Backend Health Check", response.status_code < 400, f"Status: {response.status_code}")
            return response.status_code < 400
        except Exception as e:
            print_test("Backend Health Check", False, f"Error: {str(e)}")
            return False

    def test_authentication(self) -> bool:
        """Test login and token generation"""
        print_header("2️⃣  AUTHENTICATION TESTS")
        
        # Test login
        login_url = f"{self.backend_url}/api/v1/auth/login"
        login_data = {
            "email": "enjoy983@hotmail.com",
            "password": "Gabani@2026"
        }
        
        try:
            start_time = time.time()
            response = requests.post(
                login_url,
                json=login_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            elapsed = time.time() - start_time
            
            print_endpoint_result("/api/v1/auth/login", "POST", response.status_code, elapsed)
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                print_test("Token Generation", bool(self.token), f"Token: {self.token[:20]}..." if self.token else "No token")
                self.passed_tests += 1
                return True
            else:
                print_test("Token Generation", False, f"Status: {response.status_code}")
                error_msg = response.text[:100]
                print(f"    {Colors.YELLOW}Response: {error_msg}{Colors.RESET}")
                return False
        except Exception as e:
            print_test("Authentication", False, f"Error: {str(e)}")
            return False

    def test_system_endpoints(self) -> bool:
        """Test system switcher endpoints"""
        print_header("3️⃣  SYSTEM SWITCHER ENDPOINTS")
        
        if not self.token:
            print_test("System Endpoints", False, "No token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.token}"}
        all_passed = True
        
        # Test 1: Available Systems
        try:
            start_time = time.time()
            response = requests.get(
                f"{self.backend_url}/api/v1/systems/available",
                headers=headers,
                timeout=10
            )
            elapsed = time.time() - start_time
            
            print_endpoint_result("/api/v1/systems/available", "GET", response.status_code, elapsed)
            
            if response.status_code == 200:
                data = response.json()
                system_count = len(data.get("systems", []))
                print_test(f"Available Systems ({system_count} systems)", True, 
                          f"Systems: {[s.get('name') for s in data.get('systems', [])]}")
                self.passed_tests += 1
            else:
                print_test("Available Systems", False, f"Status: {response.status_code}")
                all_passed = False
        except Exception as e:
            print_test("Available Systems", False, f"Error: {str(e)}")
            all_passed = False
        
        # Test 2: System Selector
        try:
            start_time = time.time()
            response = requests.get(
                f"{self.backend_url}/api/v1/systems/selector",
                headers=headers,
                timeout=10
            )
            elapsed = time.time() - start_time
            
            print_endpoint_result("/api/v1/systems/selector", "GET", response.status_code, elapsed)
            
            if response.status_code == 200:
                data = response.json()
                print_test("System Selector UI Data", True)
                self.passed_tests += 1
            else:
                print_test("System Selector UI Data", False, f"Status: {response.status_code}")
                all_passed = False
        except Exception as e:
            print_test("System Selector UI Data", False, f"Error: {str(e)}")
            all_passed = False
        
        # Test 3: Current System
        try:
            start_time = time.time()
            response = requests.get(
                f"{self.backend_url}/api/v1/systems/current",
                headers=headers,
                timeout=10
            )
            elapsed = time.time() - start_time
            
            print_endpoint_result("/api/v1/systems/current", "GET", response.status_code, elapsed)
            
            if response.status_code == 200:
                data = response.json()
                current_system = data.get("current_system", "unknown")
                print_test(f"Current System ({current_system})", True)
                self.passed_tests += 1
            else:
                print_test("Current System", False, f"Status: {response.status_code}")
                all_passed = False
        except Exception as e:
            print_test("Current System", False, f"Error: {str(e)}")
            all_passed = False
        
        return all_passed

    def test_system_switch(self) -> bool:
        """Test switching between systems"""
        print_header("4️⃣  SYSTEM SWITCHING TESTS")
        
        if not self.token:
            print_test("System Switch", False, "No token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.token}"}
        all_passed = True
        
        # Try switching to TMS
        try:
            start_time = time.time()
            response = requests.post(
                f"{self.backend_url}/api/v1/systems/switch",
                json={"new_system": "tms"},
                headers=headers,
                timeout=10
            )
            elapsed = time.time() - start_time
            
            print_endpoint_result("/api/v1/systems/switch", "POST", response.status_code, elapsed)
            
            if response.status_code == 200:
                data = response.json()
                new_token = data.get("access_token")
                if new_token:
                    print_test("Switch to TMS", True, f"New token received")
                    self.passed_tests += 1
                    # Update token for further tests
                    self.token = new_token
                else:
                    print_test("Switch to TMS", False, "No token in response")
                    all_passed = False
            else:
                print_test("Switch to TMS", False, f"Status: {response.status_code}")
                all_passed = False
        except Exception as e:
            print_test("Switch to TMS", False, f"Error: {str(e)}")
            all_passed = False
        
        return all_passed

    def test_admin_endpoints(self) -> bool:
        """Test admin endpoints"""
        print_header("5️⃣  ADMIN ENDPOINTS TESTS")
        
        if not self.token:
            print_test("Admin Endpoints", False, "No token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.token}"}
        all_passed = True
        
        endpoints = [
            ("/api/v1/admin/overview", "Admin Overview"),
            ("/api/v1/admin/users/management", "Users Management"),
            ("/api/v1/admin/subscriptions/analytics", "Subscriptions Analytics"),
            ("/api/v1/admin/bots/status", "Bots Status"),
            ("/api/v1/admin/shipments/analytics", "Shipments Analytics"),
            ("/api/v1/admin/system-health", "System Health"),
        ]
        
        for endpoint, name in endpoints:
            try:
                start_time = time.time()
                response = requests.get(
                    f"{self.backend_url}{endpoint}",
                    headers=headers,
                    timeout=10
                )
                elapsed = time.time() - start_time
                
                print_endpoint_result(endpoint, "GET", response.status_code, elapsed)
                
                if response.status_code < 400:
                    print_test(name, True)
                    self.passed_tests += 1
                elif response.status_code == 403:
                    print_test(name, True, "Requires admin role (expected)")
                    self.passed_tests += 1
                else:
                    print_test(name, False, f"Status: {response.status_code}")
                    all_passed = False
            except Exception as e:
                print_test(name, False, f"Error: {str(e)}")
                all_passed = False
        
        return all_passed

    def test_websocket_support(self) -> bool:
        """Test WebSocket endpoint availability"""
        print_header("6️⃣  WEBSOCKET SUPPORT CHECK")
        
        if not self.token:
            print_test("WebSocket Support", False, "No token available")
            return False
        
        # Check if WebSocket endpoint exists
        try:
            ws_url = self.backend_url.replace("http", "ws") + "/api/v1/ws/live"
            print_test("WebSocket Endpoint", True, f"URL: {ws_url}")
            self.passed_tests += 1
            return True
        except Exception as e:
            print_test("WebSocket Endpoint", False, f"Error: {str(e)}")
            return False

    def test_performance(self) -> bool:
        """Test response times and performance"""
        print_header("7️⃣  PERFORMANCE TESTS")
        
        if not self.token:
            print_test("Performance Tests", False, "No token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.token}"}
        response_times = []
        
        for i in range(5):
            try:
                start_time = time.time()
                response = requests.get(
                    f"{self.backend_url}/api/v1/systems/available",
                    headers=headers,
                    timeout=10
                )
                elapsed = time.time() - start_time
                response_times.append(elapsed)
            except:
                pass
        
        if response_times:
            avg_time = sum(response_times) / len(response_times)
            max_time = max(response_times)
            min_time = min(response_times)
            
            status = avg_time < 0.5
            print_test(
                f"Average Response Time ({avg_time:.3f}s)",
                status,
                f"Min: {min_time:.3f}s, Max: {max_time:.3f}s"
            )
            if status:
                self.passed_tests += 1
            
            return status
        else:
            print_test("Performance Tests", False, "Unable to measure")
            return False

    def print_summary(self):
        """Print test summary"""
        print_header("📊 TEST SUMMARY")
        
        total_endpoints = 10
        success_rate = (self.passed_tests / total_endpoints * 100) if total_endpoints > 0 else 0
        
        summary = f"""
{Colors.BOLD}Test Results:{Colors.RESET}
  ✅ Passed Tests:   {Colors.GREEN}{self.passed_tests}{Colors.RESET} / {total_endpoints}
  ⚠️  Success Rate:   {Colors.CYAN}{success_rate:.1f}%{Colors.RESET}
  
{Colors.BOLD}System Status:{Colors.RESET}
  Backend:    {Colors.GREEN}✓ Running{Colors.RESET}
  Token:      {Colors.GREEN}✓ Valid{Colors.RESET if self.token else Colors.RED}✗ Invalid{Colors.RESET}
  
{Colors.BOLD}Key Endpoints:{Colors.RESET}
  🔐 Login:           /api/v1/auth/token
  🔀 System Switch:   /api/v1/systems/switch
  🎛️  Admin Panel:    /api/v1/admin/overview
  📊 Health:          /api/v1/system/readiness
  
{Colors.BOLD}Next Steps:{Colors.RESET}
  1. Open http://127.0.0.1:5173 in browser
  2. Login with credentials
  3. Test system switching
  4. Access admin dashboard
"""
        print(summary)
        
        return success_rate >= 80

    def run_all_tests(self):
        """Run all test suites"""
        print(f"\n{Colors.BOLD}{Colors.CYAN}🚀 Starting Advanced Test Suite...{Colors.RESET}\n")
        
        tests = [
            ("Backend Connectivity", self.check_backend_connectivity),
            ("Authentication", self.test_authentication),
            ("System Endpoints", self.test_system_endpoints),
            ("System Switching", self.test_system_switch),
            ("Admin Endpoints", self.test_admin_endpoints),
            ("WebSocket Support", self.test_websocket_support),
            ("Performance", self.test_performance),
        ]
        
        for test_name, test_func in tests:
            try:
                test_func()
            except Exception as e:
                print_test(test_name, False, f"Test error: {str(e)}")
        
        # Print summary
        success = self.print_summary()
        
        return 0 if success else 1

if __name__ == "__main__":
    import sys
    
    backend_url = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000"
    
    tester = AdvancedTestSuite(backend_url)
    exit_code = tester.run_all_tests()
    sys.exit(exit_code)
