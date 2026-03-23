#!/usr/bin/env python3
"""
Comprehensive Unified System Test
Tests all core operations: login, system selection, switching, administration
"""

try:
    import requests
except ImportError:
    print("ERROR: requests library not installed. Run: pip install requests")
    sys.exit(1)
import json
import sys
import time
from typing import Dict, Optional

# Print colors
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class UnifiedSystemTester:
    """Unified system test class"""
    
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url
        self.token = None
        self.user_email = None
        self.tests_passed = 0
        self.tests_failed = 0
    
    def print_header(self, text: str):
        """Print section header"""
        print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 70}")
        print(f"  {text}")
        print(f"{'=' * 70}{Colors.ENDC}\n")
    
    def print_test(self, name: str, status: bool, message: str = ""):
        """Print test result"""
        icon = "✅" if status else "❌"
        color = Colors.OKGREEN if status else Colors.FAIL
        
        if status:
            self.tests_passed += 1
        else:
            self.tests_failed += 1
        
        print(f"{icon} {color}{name}{Colors.ENDC}")
        if message:
            print(f"   {Colors.OKCYAN}→ {message}{Colors.ENDC}")
    
    def test_login(self, email: str = "enjoy983@hotmail.com", password: str = "password123"):
        """✅ Login test"""
        self.print_header("1️⃣ Login Test")
        
        try:
            response = requests.post(
                f"{self.base_url}/auth/token",
                data={"email": email, "password": password},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token") or data.get("token")
                self.user_email = email
                
                self.print_test(
                    "Login",
                    True,
                    f"Token: {self.token[:20]}..."
                )
                return True
            else:
                self.print_test(
                    "Login",
                    False,
                    f"Status: {response.status_code}, Message: {response.text[:100]}"
                )
                return False
                
        except Exception as e:
            self.print_test("Login", False, str(e))
            return False
    
    def test_available_systems(self):
        """✅ Test fetching available systems"""
        self.print_header("2️⃣ Available Systems Test")
        
        if not self.token:
            self.print_test("Fetch Systems", False, "No token available")
            return False
        
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/systems/available",
                headers={"Authorization": f"Bearer {self.token}"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                systems = data.get("systems", [])
                
                self.print_test(
                    "Fetch Systems",
                    True,
                    f"Number of systems: {len(systems)}"
                )
                
                for system in systems:
                    print(f"   • {system.get('name', 'Unknown')} ({system.get('type')})")
                
                return True
            else:
                self.print_test(
                    "Fetch Systems",
                    False,
                    f"Status: {response.status_code}"
                )
                return False
                
        except Exception as e:
            self.print_test("Fetch Systems", False, str(e))
            return False
    
    def test_system_selector(self):
        """✅ Test system selector interface"""
        self.print_header("3️⃣ System Selector Data Test")
        
        if not self.token:
            self.print_test("Selector Data", False, "No token available")
            return False
        
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/systems/selector",
                headers={"Authorization": f"Bearer {self.token}"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                systems = data.get("systems", [])
                
                self.print_test(
                    "Selector Interface Data",
                    True,
                    f"Number of systems: {len(systems)}"
                )
                
                for system in systems:
                    print(f"   • {system.get('title')} - Available: {system.get('available')}")
                
                return True
            else:
                self.print_test(
                    "Selector Data",
                    False,
                    f"Status: {response.status_code}"
                )
                return False
                
        except Exception as e:
            self.print_test("Selector Data", False, str(e))
            return False
    
    def test_system_switch(self, target_system: str = "tms"):
        """✅ Test system switching"""
        self.print_header(f"4️⃣ System Switch Test to {target_system}")
        
        if not self.token:
            self.print_test("System Switch", False, "No token available")
            return False
        
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/systems/switch",
                json={"new_system": target_system},
                headers={"Authorization": f"Bearer {self.token}"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                new_token = data.get("token")
                
                if new_token:
                    self.token = new_token  # Update token
                    self.print_test(
                        f"Switch to {target_system}",
                        True,
                        f"New token: {new_token[:20]}..."
                    )
                    return True
                else:
                    self.print_test(
                        f"Switch to {target_system}",
                        False,
                        "No new token in response"
                    )
                    return False
            else:
                self.print_test(
                    f"Switch to {target_system}",
                    False,
                    f"Status: {response.status_code}"
                )
                return False
                
        except Exception as e:
            self.print_test(f"Switch to {target_system}", False, str(e))
            return False
    
    def test_admin_overview(self):
        """✅ Test admin dashboard - overview"""
        self.print_header("5️⃣ Admin Dashboard Test - Overview")
        
        if not self.token:
            self.print_test("Admin Overview", False, "No token available")
            return False
        
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/admin/overview",
                headers={"Authorization": f"Bearer {self.token}"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                overview = data.get("overview", {})
                
                self.print_test(
                    "Admin Overview",
                    True,
                    "Data retrieved successfully"
                )
                
                # Print statistics
                gts = overview.get("gts_platform", {})
                tms = overview.get("tms_system", {})
                overall = overview.get("overall", {})
                
                print(f"\n   {Colors.OKBLUE}📊 GTS Platform Statistics:{Colors.ENDC}")
                print(f"      Users: {gts.get('users', 'N/A')}")
                print(f"      Companies: {gts.get('companies', 'N/A')}")
                print(f"      Revenue: ${gts.get('revenue_this_month', 'N/A')}")
                
                print(f"\n   {Colors.OKBLUE}🚚 TMS Statistics:{Colors.ENDC}")
                print(f"      Users: {tms.get('users', 'N/A')}")
                print(f"      Active Shipments: {tms.get('active_shipments', 'N/A')}")
                print(f"      Revenue: ${tms.get('revenue_this_month', 'N/A')}")
                
                print(f"\n   {Colors.OKBLUE}📈 Overall:{Colors.ENDC}")
                print(f"      Total Users: {overall.get('total_users', 'N/A')}")
                print(f"      Total Revenue: ${overall.get('total_revenue_this_month', 'N/A')}")
                
                return True
            elif response.status_code == 403:
                self.print_test(
                    "Admin Overview",
                    False,
                    "You don't have admin permissions (normal for regular users)"
                )
                return True  # Ignore this error for regular users
            else:
                self.print_test(
                    "Admin Overview",
                    False,
                    f"Status: {response.status_code}"
                )
                return False
                
        except Exception as e:
            self.print_test("Admin Overview", False, str(e))
            return False
    
    def test_admin_subscriptions(self):
        """✅ Test subscription analytics"""
        self.print_header("6️⃣ Subscription Analytics Test")
        
        if not self.token:
            self.print_test("Subscription Analytics", False, "No token available")
            return False
        
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/admin/subscriptions/analytics",
                headers={"Authorization": f"Bearer {self.token}"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.print_test(
                    "Subscription Analytics",
                    True,
                    "Data retrieved successfully"
                )
                
                subscriptions = data.get("subscriptions", {})
                by_tier = subscriptions.get("by_tier", {})
                
                print(f"\n   {Colors.OKBLUE}💳 Subscription Distribution:{Colors.ENDC}")
                for tier, info in by_tier.items():
                    print(f"      {tier}: {info.get('count')} - ${info.get('monthly_revenue')}")
                
                return True
            elif response.status_code == 403:
                self.print_test(
                    "Subscription Analytics",
                    False,
                    "You don't have admin permissions"
                )
                return True
            else:
                self.print_test(
                    "Subscription Analytics",
                    False,
                    f"Status: {response.status_code}"
                )
                return False
                
        except Exception as e:
            self.print_test("Subscription Analytics", False, str(e))
            return False
    
    def test_system_health(self):
        """✅ Test system health"""
        self.print_header("7️⃣ System Health Test")
        
        if not self.token:
            self.print_test("System Health", False, "No token available")
            return False
        
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/admin/system-health",
                headers={"Authorization": f"Bearer {self.token}"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                health = data.get("health", {})
                
                self.print_test(
                    "System Health",
                    True,
                    f"Status: {health.get('overall_status', 'Unknown')}"
                )
                
                print(f"\n   {Colors.OKBLUE}🔧 Health Details:{Colors.ENDC}")
                print(f"      API Servers: {health.get('api_servers', {}).get('status')}")
                print(f"      Database: {health.get('database', {}).get('status')}")
                print(f"      WebSocket: {health.get('websocket_hub', {}).get('status')}")
                
                return True
            elif response.status_code == 403:
                self.print_test(
                    "System Health",
                    False,
                    "You don't have admin permissions"
                )
                return True
            else:
                self.print_test(
                    "System Health",
                    False,
                    f"Status: {response.status_code}"
                )
                return False
                
        except Exception as e:
            self.print_test("System Health", False, str(e))
            return False
    
    def print_summary(self):
        """Print test results summary"""
        self.print_header("📋 Test Results Summary")
        
        total = self.tests_passed + self.tests_failed
        percentage = (self.tests_passed / total * 100) if total > 0 else 0
        
        print(f"{Colors.OKGREEN}✅ Passed: {self.tests_passed}{Colors.ENDC}")
        print(f"{Colors.FAIL}❌ Failed: {self.tests_failed}{Colors.ENDC}")
        print(f"{Colors.BOLD}Overall Percentage: {percentage:.1f}%{Colors.ENDC}\n")
        
        if self.tests_failed == 0:
            print(f"{Colors.OKGREEN}{Colors.BOLD}🎉 All tests passed!{Colors.ENDC}\n")
            return 0
        else:
            print(f"{Colors.FAIL}{Colors.BOLD}⚠️ Some tests failed{Colors.ENDC}\n")
            return 1
    
    def run_all_tests(self):
        """Run all tests"""
        print(f"{Colors.HEADER}{Colors.BOLD}")
        print("""
╔════════════════════════════════════════════════════════════════════╗
║                                                                    ║
║            🌐 GTS Logistics Unified System Test                   ║
║                                                                    ║
║           Gabani Transport Solutions (GTS) Unified System Test           ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
        """)
        print(Colors.ENDC)
        
        # Test list
        tests = [
            ("Login", self.test_login),
            ("Fetch Available Systems", self.test_available_systems),
            ("System Selector Interface", self.test_system_selector),
            ("System Switch", self.test_system_switch),
            ("Admin Dashboard - Overview", self.test_admin_overview),
            ("Subscription Analytics", self.test_admin_subscriptions),
            ("System Health", self.test_system_health),
        ]
        
        for test_name, test_func in tests:
            try:
                test_func()
            except Exception as e:
                print(f"{Colors.FAIL}Unexpected error in {test_name}: {str(e)}{Colors.ENDC}\n")
        
        # Results summary
        return self.print_summary()


if __name__ == "__main__":
    tester = UnifiedSystemTester()
    exit_code = tester.run_all_tests()
    sys.exit(exit_code)
