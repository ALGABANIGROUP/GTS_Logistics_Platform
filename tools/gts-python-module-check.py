#!/usr/bin/env python3
"""
GTS Python Module Checker
Checks all required Python modules and dependencies
"""

import sys
import importlib
import pkg_resources
from datetime import datetime

REQUIRED_PACKAGES = [
    "fastapi",
    "uvicorn",
    "sqlalchemy",
    "asyncpg", 
    "alembic",
    "pydantic",
    "python-dotenv",
    "python-jose",
    "passlib",
    "bcrypt",
    "httpx",
    "aiofiles",
    "redis",
    "celery",
    "pandas",
    "openpyxl",
    "python-dateutil",
    "stripe",
    "twilio",
    "sendgrid",
    "websockets",
    "aioredis"
]

OPTIONAL_PACKAGES = {
    "jupyter": "For data analysis notebooks",
    "matplotlib": "For reporting charts",
    "seaborn": "For advanced visualizations",
    "scikit-learn": "For AI/ML features",
    "torch": "For advanced AI models"
}

def check_package(package_name):
    """Check if a package is installed and get its version"""
    try:
        dist = pkg_resources.get_distribution(package_name)
        return True, dist.version
    except pkg_resources.DistributionNotFound:
        return False, None

def main():
    print("🔍 GTS Python Module Diagnostic")
    print("=" * 50)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"Python: {sys.version}")
    print()
    
    # Check required packages
    print("📦 REQUIRED PACKAGES:")
    print("-" * 30)
    
    all_required_ok = True
    for package in REQUIRED_PACKAGES:
        installed, version = check_package(package)
        status = "✅ OK" if installed else "❌ MISSING"
        version_info = f" (v{version})" if installed else ""
        print(f"{status} {package}{version_info}")
        
        if not installed:
            all_required_ok = False
    
    print()
    
    # Check optional packages
    print("🎯 OPTIONAL PACKAGES:")
    print("-" * 30)
    
    for package, description in OPTIONAL_PACKAGES.items():
        installed, version = check_package(package)
        status = "✅ INSTALLED" if installed else "⚠️  OPTIONAL"
        version_info = f" (v{version})" if installed else ""
        print(f"{status} {package}{version_info}")
        if installed:
            print(f"       📝 {description}")
    
    print()
    
    # Check app-specific modules
    print("🏗️  APPLICATION MODULES:")
    print("-" * 30)
    
    app_modules = [
        "app.main",
        "app.core.config",
        "app.core.database",
        "app.models",
        "app.schemas",
        "app.api.endpoints.shipments",
        "app.services.shipment_service",
        "app.bots.tracking_bot",
        "app.bots.notification_bot",
        "alembic.env"
    ]
    
    for module in app_modules:
        try:
            importlib.import_module(module)
            print(f"✅ OK {module}")
        except ImportError as e:
            print(f"❌ FAIL {module}")
            print(f"       Error: {e}")
    
    print()
    print("=" * 50)
    
    if all_required_ok:
        print("🎉 ALL REQUIRED PACKAGES ARE INSTALLED!")
        sys.exit(0)
    else:
        print("❌ SOME REQUIRED PACKAGES ARE MISSING!")
        print("\nTo install missing packages, run:")
        print("pip install -r requirements.txt")
        sys.exit(1)

if __name__ == "__main__":
    main()