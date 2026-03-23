#!/usr/bin/env python3
"""
Complete authentication system test
Tests all auth endpoints in sequence
"""
import requests
import json
import time
import sys

BASE_URL = "http://127.0.0.1:8000"

# Color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
END = '\033[0m'

class AuthTester:
    def __init__(self):
        self.access_token = None
        self.user_data = None
        self.test_credentials = {
            "username": "enjoy983@hotmail.com",
            "password": "password123"
        }
    
    def print_header(self, title):
        print(f"\n{BLUE}{'='*60}")
        print(f"  {title}")
        print(f"{'='*60}{END}\n")
    
    def print_success(self, msg):
        print(f"{GREEN}✅ {msg}{END}")
    
    def print_error(self, msg):
        print(f"{RED}❌ {msg}{END}")
    
    def print_info(self, msg):
        print(f"{YELLOW}ℹ️  {msg}{END}")
    
    def test_backend_health(self):
        """Test if backend is running"""
        self.print_header("1. Backend Health Check")
        try:
            response = requests.get(f"{BASE_URL}/", timeout=2)
            if response.status_code == 200:
                self.print_success(f"Backend is running on {BASE_URL}")
                result = response.json()
                print(f"   Name: {result.get('name')}")
                return True
            else:
                self.print_error(f"Backend returned {response.status_code}")
                return False
        except Exception as e:
            self.print_error(f"Cannot connect to backend: {e}")
            return False
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        self.print_header("2. Login Test - Invalid Credentials")
        try:
            response = requests.post(
                f"{BASE_URL}/api/v1/auth/token",
                data=self.test_credentials,
                timeout=5
            )
            print(f"   Status: {response.status_code}")
            result = response.json()
            print(f"   Response: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            if response.status_code == 401:
                self.print_info("401 Unauthorized - credentials not found (expected)")
                return True
            elif response.status_code == 500:
                self.print_error("500 Server Error - endpoint is broken!")
                return False
            else:
                self.print_info(f"Status {response.status_code} - may indicate other issue")
                return True
        except Exception as e:
            self.print_error(f"Error: {e}")
            return False
    
    def test_unauthorized_access(self):
        """Test accessing protected endpoint without token"""
        self.print_header("3. Protected Endpoint Test - No Token")
        try:
            response = requests.get(
                f"{BASE_URL}/api/v1/auth/me",
                timeout=5
            )
            print(f"   Status: {response.status_code}")
            result = response.json()
            print(f"   Response: {json.dumps(result, indent=2)[:200]}...")
            
            if response.status_code == 401:
                self.print_success("Correctly rejected - no token provided")
                return True
            else:
                self.print_error(f"Expected 401, got {response.status_code}")
                return False
        except Exception as e:
            self.print_error(f"Error: {e}")
            return False
    
    def test_quick_auth(self):
        """Test quick auth endpoint (no token needed for structure check)"""
        self.print_header("4. Quick Auth Endpoint - Structure Check")
        try:
            response = requests.get(
                f"{BASE_URL}/api/v1/auth/me/quick",
                timeout=5
            )
            print(f"   Status: {response.status_code}")
            
            if response.status_code in [200, 401]:
                self.print_success(f"Endpoint accessible ({response.status_code})")
                return True
            elif response.status_code == 404:
                self.print_error("Endpoint not found (404)")
                return False
            else:
                self.print_info(f"Status {response.status_code}")
                return True
        except Exception as e:
            self.print_error(f"Error: {e}")
            return False
    
    def test_refresh_endpoint(self):
        """Test refresh token endpoint structure"""
        self.print_header("5. Refresh Token Endpoint - Structure Check")
        try:
            response = requests.post(
                f"{BASE_URL}/api/v1/auth/refresh",
                json={"refresh_token": "test_token"},
                timeout=5
            )
            print(f"   Status: {response.status_code}")
            
            if response.status_code in [200, 400, 401, 422]:
                # Any of these means endpoint exists and is handling requests
                self.print_success(f"Endpoint accessible ({response.status_code})")
                return True
            elif response.status_code == 404:
                self.print_error("Endpoint not found (404)")
                return False
            else:
                self.print_info(f"Status {response.status_code}")
                return True
        except Exception as e:
            self.print_error(f"Error: {e}")
            return False
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        self.print_header("Authentication System Test Suite")
        print(f"Testing against: {BASE_URL}\n")
        
        results = []
        
        # Run tests
        results.append(("Backend Health", self.test_backend_health()))
        results.append(("Login Invalid Creds", self.test_login_invalid_credentials()))
        results.append(("Unauthorized Access", self.test_unauthorized_access()))
        results.append(("Quick Auth Endpoint", self.test_quick_auth()))
        results.append(("Refresh Endpoint", self.test_refresh_endpoint()))
        
        # Summary
        self.print_header("Test Summary")
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for name, result in results:
            status = f"{GREEN}PASS{END}" if result else f"{RED}FAIL{END}"
            print(f"  {name:<30} {status}")
        
        print(f"\nTotal: {passed}/{total} tests passed")
        
        if passed == total:
            self.print_success("All tests passed! ☑️")
            self.print_info("Next: Test with valid credentials from browser login")
            return True
        else:
            self.print_error(f"Some tests failed - {total-passed} issues found")
            return False

if __name__ == "__main__":
    tester = AuthTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
