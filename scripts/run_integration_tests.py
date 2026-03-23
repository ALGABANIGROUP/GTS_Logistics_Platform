#!/usr/bin/env python3
"""
Integration Tests Runner for GTS Platform

This script runs all integration tests for Email, Payment (Stripe), and ERP systems.
"""

import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple


class Color:
    """ANSI color codes"""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'


class IntegrationTestRunner:
    """Run all integration tests"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.test_results = {}
        self.start_time = None
        self.end_time = None
    
    def print_header(self, text: str):
        """Print section header"""
        print(f"\n{Color.BOLD}{Color.CYAN}{'=' * 80}{Color.END}")
        print(f"{Color.BOLD}{Color.CYAN}{text:^80}{Color.END}")
        print(f"{Color.BOLD}{Color.CYAN}{'=' * 80}{Color.END}\n")
    
    def print_success(self, text: str):
        """Print success message"""
        print(f"{Color.GREEN}✅ {text}{Color.END}")
    
    def print_error(self, text: str):
        """Print error message"""
        print(f"{Color.RED}❌ {text}{Color.END}")
    
    def print_info(self, text: str):
        """Print info message"""
        print(f"{Color.BLUE}ℹ️  {text}{Color.END}")
    
    def print_warning(self, text: str):
        """Print warning message"""
        print(f"{Color.YELLOW}⚠️  {text}{Color.END}")
    
    def run_test_file(
        self,
        test_file: str,
        test_name: str,
        description: str
    ) -> Tuple[bool, int, int, float]:
        """Run a single test file"""
        
        print(f"\n{Color.BOLD}{Color.MAGENTA}{'─' * 80}{Color.END}")
        print(f"{Color.BOLD}{Color.MAGENTA}Running: {test_name}{Color.END}")
        print(f"{Color.WHITE}Description: {description}{Color.END}")
        print(f"{Color.MAGENTA}{'─' * 80}{Color.END}\n")
        
        test_path = self.project_root / "tests" / test_file
        
        if not test_path.exists():
            self.print_error(f"Test file not found: {test_path}")
            return False, 0, 0, 0.0
        
        # Run pytest
        start = time.time()
        result = subprocess.run(
            [
                sys.executable, "-m", "pytest",
                str(test_path),
                "-v",
                "--tb=short",
                "--color=yes"
            ],
            capture_output=True,
            text=True
        )
        duration = time.time() - start
        
        # Parse results
        passed = 0
        failed = 0
        
        for line in result.stdout.split('\n'):
            if 'passed' in line.lower():
                try:
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if 'passed' in part.lower() and i > 0:
                            passed = int(parts[i-1])
                            break
                except:
                    pass
            
            if 'failed' in line.lower():
                try:
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if 'failed' in part.lower() and i > 0:
                            failed = int(parts[i-1])
                            break
                except:
                    pass
        
        # Print results
        success = result.returncode == 0
        
        if success:
            self.print_success(
                f"{test_name} completed: {passed} tests passed in {duration:.2f}s"
            )
        else:
            self.print_error(
                f"{test_name} failed: {failed} tests failed, {passed} passed"
            )
            
            # Print failure details
            if failed > 0:
                print(f"\n{Color.RED}Failure Details:{Color.END}")
                print(result.stdout)
        
        return success, passed, failed, duration
    
    def run_all_tests(self):
        """Run all integration tests"""
        
        self.start_time = time.time()
        
        # Print banner
        self.print_header("GTS PLATFORM - INTEGRATION TESTS")
        
        print(f"{Color.WHITE}Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Color.END}")
        
        # Define test suites
        test_suites = [
            {
                "file": "test_email_integration.py",
                "name": "Email Integration Tests",
                "description": "Tests for SMTP, templates, and email sending",
                "expected_tests": 13
            },
            {
                "file": "test_payment_integration.py",
                "name": "Payment Integration Tests (Stripe)",
                "description": "Tests for payment processing, refunds, and webhooks",
                "expected_tests": 18
            },
            {
                "file": "test_erp_integration.py",
                "name": "ERP Integration Tests",
                "description": "Tests for order sync, inventory, and data exchange",
                "expected_tests": 20
            }
        ]
        
        # Run each test suite
        total_passed = 0
        total_failed = 0
        total_duration = 0.0
        all_success = True
        
        for suite in test_suites:
            success, passed, failed, duration = self.run_test_file(
                suite["file"],
                suite["name"],
                suite["description"]
            )
            
            self.test_results[suite["name"]] = {
                "success": success,
                "passed": passed,
                "failed": failed,
                "expected": suite["expected_tests"],
                "duration": duration
            }
            
            total_passed += passed
            total_failed += failed
            total_duration += duration
            
            if not success:
                all_success = False
            
            # Check if all expected tests ran
            if passed + failed != suite["expected_tests"]:
                self.print_warning(
                    f"Expected {suite['expected_tests']} tests, "
                    f"but ran {passed + failed}"
                )
        
        self.end_time = time.time()
        
        # Print summary
        self.print_summary(
            all_success,
            total_passed,
            total_failed,
            total_duration
        )
        
        return all_success
    
    def print_summary(
        self,
        all_success: bool,
        total_passed: int,
        total_failed: int,
        total_duration: float
    ):
        """Print test summary"""
        
        self.print_header("TEST SUMMARY")
        
        # Individual test suite results
        print(f"{Color.BOLD}Individual Results:{Color.END}\n")
        
        for name, results in self.test_results.items():
            status_icon = "✅" if results["success"] else "❌"
            status_color = Color.GREEN if results["success"] else Color.RED
            
            print(f"{status_icon} {Color.BOLD}{name}{Color.END}")
            print(f"   {status_color}Passed: {results['passed']}/{results['expected']}{Color.END}")
            
            if results["failed"] > 0:
                print(f"   {Color.RED}Failed: {results['failed']}{Color.END}")
            
            print(f"   Duration: {results['duration']:.2f}s\n")
        
        # Overall statistics
        print(f"\n{Color.BOLD}Overall Statistics:{Color.END}\n")
        
        total_tests = total_passed + total_failed
        pass_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📊 Total Tests:    {total_tests}")
        print(f"{Color.GREEN}✅ Passed:         {total_passed}{Color.END}")
        
        if total_failed > 0:
            print(f"{Color.RED}❌ Failed:         {total_failed}{Color.END}")
        
        print(f"📈 Pass Rate:      {pass_rate:.1f}%")
        print(f"⏱️  Total Duration: {total_duration:.2f}s")
        
        if self.start_time and self.end_time:
            total_time = self.end_time - self.start_time
            print(f"🕐 Total Time:     {total_time:.2f}s")
        
        # Final verdict
        print(f"\n{Color.BOLD}Final Verdict:{Color.END}\n")
        
        if all_success and pass_rate >= 95:
            self.print_success("ALL TESTS PASSED! ✨")
            print(f"{Color.GREEN}Integration tests are ready for production! 🚀{Color.END}")
        elif pass_rate >= 80:
            self.print_warning("TESTS MOSTLY PASSED")
            print(f"{Color.YELLOW}Some tests failed. Review failures before deploying.{Color.END}")
        else:
            self.print_error("TESTS FAILED")
            print(f"{Color.RED}Critical failures detected. Fix issues before proceeding.{Color.END}")
        
        # Recommendations
        print(f"\n{Color.BOLD}Recommendations:{Color.END}\n")
        
        if pass_rate == 100:
            print("✅ All systems operational")
            print("✅ Integration tests passing")
            print("✅ Ready for production deployment")
        else:
            print("⚠️  Review failed tests")
            print("⚠️  Check external service configurations")
            print("⚠️  Verify network connectivity")
            print("⚠️  Check API credentials")
        
        # Next steps
        print(f"\n{Color.BOLD}Next Steps:{Color.END}\n")
        print("1. Review test results above")
        print("2. Fix any failing tests")
        print("3. Verify external service configurations")
        print("4. Run tests again to confirm fixes")
        print("5. Proceed to production deployment")
        
        print(f"\n{Color.CYAN}{'=' * 80}{Color.END}\n")


def main():
    """Main entry point"""
    
    print("""
    ╔═══════════════════════════════════════════════════════════════════╗
    ║                                                                   ║
    ║          GTS PLATFORM - INTEGRATION TEST RUNNER                  ║
    ║                                                                   ║
    ║          Testing: Email, Payment (Stripe), ERP Systems           ║
    ║                                                                   ║
    ╚═══════════════════════════════════════════════════════════════════╝
    """)
    
    runner = IntegrationTestRunner()
    
    try:
        success = runner.run_all_tests()
        sys.exit(0 if success else 1)
    
    except KeyboardInterrupt:
        print(f"\n\n{Color.YELLOW}Test run interrupted by user.{Color.END}")
        sys.exit(130)
    
    except Exception as e:
        print(f"\n\n{Color.RED}Error running tests: {e}{Color.END}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
