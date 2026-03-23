import asyncio
import sys
from pathlib import Path

backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))


async def quick_test():
    print("Quick system test after repairs...")
    tests_passed = 0
    total_tests = 4

    try:
        print("1. Checking database config...")
        import backend.database.config

        print("   OK: backend.database.config")
        tests_passed += 1

        print("2. Checking session module...")
        import backend.database.session

        print("   OK: backend.database.session")
        tests_passed += 1

        print("3. Checking main application...")
        import backend.main

        print("   OK: backend.main")
        tests_passed += 1

        print("4. Testing database connectivity...")
        from backend.database.config import async_ping

        if await async_ping():
            print("   OK: database connection")
            tests_passed += 1
        else:
            print("   FAILED: database connection")
    except Exception as exc:
        print(f"   FAILED: {exc}")

    print(f"\nResults: {tests_passed}/{total_tests} tests passed")
    if tests_passed == total_tests:
        print("System is ready to run")
        return True

    print("System needs further fixes")
    return False


if __name__ == "__main__":
    success = asyncio.run(quick_test())
    sys.exit(0 if success else 1)
