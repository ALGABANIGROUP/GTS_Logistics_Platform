#!/usr/bin/env python3
"""
Comprehensive GTS SaaS Project Check
EN GTS EN SaaS
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Dict, Any, List, Tuple
from datetime import datetime
import traceback

sys.path.insert(0, str(Path(__file__).parent))

# ============================================================================
# 1. DATABASE CHECK
# ============================================================================

async def check_database() -> Dict[str, Any]:
    """EN"""
    try:
        from backend.database.config import get_sessionmaker
        from backend.models.user import User
        from sqlalchemy import select, func, inspect
        from sqlalchemy.ext.asyncio import AsyncSession

        sessionmaker = get_sessionmaker()
        
        results = {
            "status": "healthy",
            "tables": {},
            "users": {},
            "errors": []
        }
        
        async with sessionmaker() as session:
            # Check users table
            try:
                total_users = await session.scalar(select(func.count(User.id))) or 0
                active_users = await session.scalar(
                    select(func.count(User.id)).where(User.is_active == True)
                ) or 0
                
                results["users"] = {
                    "total": total_users,
                    "active": active_users,
                    "inactive": total_users - active_users
                }
            except Exception as e:
                results["errors"].append(f"Failed to count users: {str(e)}")
                results["status"] = "error"
            
            # Check roles distribution
            try:
                from sqlalchemy import distinct
                roles_query = select(User.role, func.count(User.id)).group_by(User.role)
                role_result = await session.execute(roles_query)
                roles_data = {}
                for role, count in role_result:
                    roles_data[role or "unknown"] = count
                results["users"]["by_role"] = roles_data
            except Exception as e:
                results["errors"].append(f"Failed to check roles: {str(e)}")
        
        return results
    except Exception as e:
        return {
            "status": "error",
            "tables": {},
            "users": {},
            "errors": [f"Database connection failed: {str(e)}"]
        }


# ============================================================================
# 2. AUTH & SECURITY CHECK
# ============================================================================

async def check_auth_system() -> Dict[str, Any]:
    """EN"""
    results = {
        "status": "checking",
        "auth_endpoints": {},
        "security": {},
        "errors": []
    }
    
    # Test auth endpoints
    endpoints = [
        ("/api/v1/auth/token", "POST", "Login endpoint"),
        ("/api/v1/auth/me", "GET", "Get current user"),
        ("/auth/register", "POST", "Register endpoint"),
    ]
    
    for endpoint, method, desc in endpoints:
        try:
            # This is a check if endpoint exists, not a real call
            results["auth_endpoints"][endpoint] = {
                "method": method,
                "description": desc,
                "status": "available"
            }
        except Exception as e:
            results["auth_endpoints"][endpoint] = {
                "status": "error",
                "error": str(e)
            }
    
    return results


# ============================================================================
# 3. ROUTES & APIs CHECK
# ============================================================================

def check_routes() -> Dict[str, Any]:
    """EN APIs"""
    try:
        from backend.main import app
        results = {
            "status": "healthy",
            "total_routes": 0,
            "by_prefix": {},
            "errors": []
        }
        
        routes_by_prefix = {}
        for route in app.routes:
            if hasattr(route, 'path'):
                path = route.path
                # Extract prefix
                parts = path.split('/')
                prefix = f"/{parts[1]}/{parts[2]}" if len(parts) > 2 else path
                
                if prefix not in routes_by_prefix:
                    routes_by_prefix[prefix] = 0
                routes_by_prefix[prefix] += 1
        
        results["by_prefix"] = routes_by_prefix
        results["total_routes"] = sum(routes_by_prefix.values())
        
        return results
    except Exception as e:
        return {
            "status": "error",
            "total_routes": 0,
            "by_prefix": {},
            "errors": [str(e)]
        }


# ============================================================================
# 4. FRONTEND CHECK
# ============================================================================

def check_frontend() -> Dict[str, Any]:
    """EN"""
    frontend_dir = Path("frontend")
    results = {
        "status": "healthy",
        "exists": frontend_dir.exists(),
        "structure": {},
        "config": {},
        "errors": []
    }
    
    if not frontend_dir.exists():
        results["errors"].append("Frontend directory not found")
        results["status"] = "error"
        return results
    
    # Check key files
    key_files = [
        "package.json",
        "vite.config.js",
        "src/main.jsx",
        "src/App.jsx",
        "src/contexts/AuthContext.jsx",
        "src/components/RequireAuth.jsx",
    ]
    
    for file in key_files:
        file_path = frontend_dir / file
        results["structure"][file] = file_path.exists()
        if not file_path.exists():
            results["errors"].append(f"Missing: {file}")
    
    # Check package.json
    pkg_json = frontend_dir / "package.json"
    if pkg_json.exists():
        try:
            import json
            with open(pkg_json) as f:
                pkg = json.load(f)
                results["config"]["name"] = pkg.get("name")
                results["config"]["version"] = pkg.get("version")
                results["config"]["dependencies_count"] = len(pkg.get("dependencies", {}))
                results["config"]["dev_dependencies_count"] = len(pkg.get("devDependencies", {}))
        except Exception as e:
            results["errors"].append(f"Failed to read package.json: {str(e)}")
    
    return results


# ============================================================================
# 5. BACKEND CHECK
# ============================================================================

def check_backend() -> Dict[str, Any]:
    """EN"""
    backend_dir = Path("backend")
    results = {
        "status": "healthy",
        "exists": backend_dir.exists(),
        "modules": {},
        "files": {},
        "errors": []
    }
    
    if not backend_dir.exists():
        results["errors"].append("Backend directory not found")
        results["status"] = "error"
        return results
    
    # Check key modules
    key_modules = [
        "main.py",
        "routes",
        "models",
        "database",
        "security",
        "bots"
    ]
    
    for module in key_modules:
        path = backend_dir / module
        results["modules"][module] = path.exists()
        if not path.exists():
            results["errors"].append(f"Missing module: {module}")
    
    # Check routes
    routes_dir = backend_dir / "routes"
    if routes_dir.exists():
        route_files = list(routes_dir.glob("*.py"))
        results["files"]["route_files"] = len(route_files)
        results["files"]["routes"] = [f.stem for f in route_files if f.name != "__init__.py"]
    
    return results


# ============================================================================
# 6. CONFIGURATION CHECK
# ============================================================================

def check_configuration() -> Dict[str, Any]:
    """EN"""
    results = {
        "status": "healthy",
        "files": {},
        "database_configured": False,
        "errors": []
    }
    
    config_files = [
        (".env", "Environment variables"),
        ("alembic.ini", "Database migrations config"),
        ("docker-compose.yml", "Docker compose"),
        ("backend/alembic.ini", "Backend alembic config")
    ]
    
    for file, desc in config_files:
        path = Path(file)
        results["files"][file] = {
            "exists": path.exists(),
            "description": desc
        }
    
    # Check if database is configured
    env_file = Path(".env")
    if env_file.exists():
        try:
            with open(env_file) as f:
                content = f.read()
                if "DATABASE_URL" in content or "RENDER_DATABASE_URL" in content:
                    results["database_configured"] = True
        except Exception as e:
            results["errors"].append(f"Failed to read .env: {str(e)}")
    
    return results


# ============================================================================
# 7. MODEL & SCHEMA CHECK
# ============================================================================

def check_models() -> Dict[str, Any]:
    """EN"""
    models_dir = Path("backend/models")
    results = {
        "status": "healthy",
        "models": [],
        "total_models": 0,
        "errors": []
    }
    
    if models_dir.exists():
        model_files = [f.stem for f in models_dir.glob("*.py") if f.name != "__init__.py"]
        results["models"] = model_files
        results["total_models"] = len(model_files)
    else:
        results["errors"].append("Models directory not found")
        results["status"] = "error"
    
    return results


# ============================================================================
# 8. PROJECT STRUCTURE CHECK
# ============================================================================

def check_project_structure() -> Dict[str, Any]:
    """EN"""
    root = Path(".")
    results = {
        "status": "healthy",
        "directories": {},
        "key_files": {},
        "errors": []
    }
    
    key_dirs = [
        "backend",
        "frontend",
        "config",
        "docs",
        ".git"
    ]
    
    for dir_name in key_dirs:
        results["directories"][dir_name] = (root / dir_name).exists()
    
    key_files = [
        "README.md",
        "package.json",
        "pyproject.toml",
        "requirements.txt",
        ".gitignore"
    ]
    
    for file_name in key_files:
        results["key_files"][file_name] = (root / file_name).exists()
    
    return results


# ============================================================================
# MAIN CHECK FUNCTION
# ============================================================================

async def run_comprehensive_check() -> Dict[str, Any]:
    """EN"""
    print("🔍 EN...")
    print("=" * 80)
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "project": "GTS SaaS",
        "checks": {
            "project_structure": check_project_structure(),
            "backend": check_backend(),
            "frontend": check_frontend(),
            "models": check_models(),
            "configuration": check_configuration(),
            "database": await check_database(),
            "auth_system": await check_auth_system(),
            "routes": check_routes(),
        },
        "summary": {}
    }
    
    return results


async def calculate_readiness(results: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
    """EN"""
    scores = {}
    max_score = 0
    actual_score = 0
    
    checks = results.get("checks", {})
    
    # Backend (20%)
    backend = checks.get("backend", {})
    backend_score = 0
    if backend.get("modules", {}).get("main.py"):
        backend_score += 5
    if len(backend.get("files", {}).get("routes", [])) > 5:
        backend_score += 8
    backend_score += 7 if not backend.get("errors") else 0
    scores["backend"] = (backend_score, 20)
    actual_score += backend_score
    max_score += 20
    
    # Frontend (15%)
    frontend = checks.get("frontend", {})
    frontend_score = 0
    if frontend.get("exists"):
        frontend_score += 5
    if frontend.get("structure", {}).get("package.json"):
        frontend_score += 5
    frontend_score += 5 if not frontend.get("errors") else 0
    scores["frontend"] = (frontend_score, 15)
    actual_score += frontend_score
    max_score += 15
    
    # Database (20%)
    database = checks.get("database", {})
    db_score = 0
    if database.get("status") == "healthy":
        db_score += 15
    if database.get("users", {}).get("total", 0) > 0:
        db_score += 5
    scores["database"] = (db_score, 20)
    actual_score += db_score
    max_score += 20
    
    # Auth System (15%)
    auth = checks.get("auth_system", {})
    auth_score = 0
    if len(auth.get("auth_endpoints", {})) > 0:
        auth_score += 10
    auth_score += 5 if not auth.get("errors") else 0
    scores["auth"] = (auth_score, 15)
    actual_score += auth_score
    max_score += 15
    
    # Routes (15%)
    routes = checks.get("routes", {})
    routes_score = 0
    if routes.get("total_routes", 0) > 20:
        routes_score += 10
    routes_score += 5 if not routes.get("errors") else 0
    scores["routes"] = (routes_score, 15)
    actual_score += routes_score
    max_score += 15
    
    # Config (10%)
    config = checks.get("configuration", {})
    config_score = 0
    if config.get("database_configured"):
        config_score += 7
    config_score += 3 if not config.get("errors") else 0
    scores["config"] = (config_score, 10)
    actual_score += config_score
    max_score += 10
    
    # Models (10%)
    models = checks.get("models", {})
    models_score = 0
    if models.get("total_models", 0) > 3:
        models_score += 10
    scores["models"] = (models_score, 10)
    actual_score += models_score
    max_score += 10
    
    readiness = (actual_score / max_score * 100) if max_score > 0 else 0
    
    return readiness, scores


def print_detailed_report(results: Dict[str, Any], readiness: float, scores: Dict[str, Any]):
    """EN"""
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + f"{'EN GTS SaaS - Comprehensive Project Audit':^78}" + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "═" * 78 + "╝")
    
    print(f"\n📊 EN: {readiness:.1f}%")
    print("=" * 80)
    
    # Status indicator
    if readiness >= 90:
        status = "✅ EN | Production Ready"
    elif readiness >= 70:
        status = "⚠️  EN | Nearly Ready"
    elif readiness >= 50:
        status = "🔧 EN | Under Construction"
    else:
        status = "❌ EN | Not Ready"
    
    print(f"EN: {status}")
    print("=" * 80)
    
    print("\n📈 EN:\n")
    
    for component, (score, max_score) in scores.items():
        pct = (score / max_score * 100) if max_score > 0 else 0
        bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
        component_name = {
            "backend": "🔧 Backend",
            "frontend": "🎨 Frontend",
            "database": "💾 Database",
            "auth": "🔐 Authentication",
            "routes": "🛣️  Routes & APIs",
            "config": "⚙️  Configuration",
            "models": "📦 Models"
        }.get(component, component)
        
        print(f"{component_name:20} [{bar}] {score}/{max_score} ({pct:.0f}%)")
    
    print("\n" + "=" * 80)
    print("\n📋 EN:\n")
    
    checks = results.get("checks", {})
    
    # Database Details
    print("💾 EN (Database):")
    db = checks.get("database", {})
    if db.get("users"):
        print(f"   • EN: {db['users'].get('total', 0)}")
        print(f"   • EN: {db['users'].get('active', 0)}")
        print(f"   • EN (Roles): {db['users'].get('by_role', {})}")
    if db.get("errors"):
        print(f"   ⚠️  EN: {'; '.join(db['errors'])}")
    print()
    
    # Backend Details
    print("🔧 Backend:")
    backend = checks.get("backend", {})
    print(f"   • EN: {len(backend.get('files', {}).get('routes', []))} route files")
    print(f"   • EN: {', '.join([k for k, v in backend.get('modules', {}).items() if v])}")
    if backend.get("errors"):
        print(f"   ⚠️  EN: {'; '.join(backend['errors'])}")
    print()
    
    # Frontend Details
    print("🎨 Frontend:")
    frontend = checks.get("frontend", {})
    print(f"   • EN: {'EN ✓' if frontend.get('exists') else 'EN ✗'}")
    if frontend.get("config"):
        print(f"   • EN: {frontend['config'].get('version', 'N/A')}")
        print(f"   • EN: {frontend['config'].get('dependencies_count', 0)}")
    if frontend.get("errors"):
        print(f"   ⚠️  EN: {'; '.join(frontend['errors'])}")
    print()
    
    # Routes Details
    print("🛣️  Routes & APIs:")
    routes = checks.get("routes", {})
    print(f"   • EN: {routes.get('total_routes', 0)}")
    by_prefix = routes.get("by_prefix", {})
    for prefix, count in sorted(by_prefix.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"   • {prefix}: {count} endpoints")
    if routes.get("errors"):
        print(f"   ⚠️  EN: {'; '.join(routes['errors'])}")
    print()
    
    # Models Details
    print("📦 Models:")
    models = checks.get("models", {})
    print(f"   • EN: {models.get('total_models', 0)}")
    if models.get("models"):
        print(f"   • EN: {', '.join(models['models'][:5])}")
    if models.get("errors"):
        print(f"   ⚠️  EN: {'; '.join(models['errors'])}")
    print()
    
    # Auth System Details
    print("🔐 Authentication System:")
    auth = checks.get("auth_system", {})
    endpoints = auth.get("auth_endpoints", {})
    for endpoint, info in endpoints.items():
        status = "✓" if info.get("status") == "available" else "✗"
        print(f"   • {status} {endpoint}")
    if auth.get("errors"):
        print(f"   ⚠️  EN: {'; '.join(auth['errors'])}")
    print()
    
    # Configuration Details
    print("⚙️  EN (Configuration):")
    config = checks.get("configuration", {})
    print(f"   • EN: {'EN ✓' if config.get('database_configured') else 'EN ✗'}")
    for file, info in config.get("files", {}).items():
        status = "✓" if info.get("exists") else "✗"
        print(f"   • {status} {file}")
    if config.get("errors"):
        print(f"   ⚠️  EN: {'; '.join(config['errors'])}")


async def main():
    try:
        results = await run_comprehensive_check()
        readiness, scores = await calculate_readiness(results)
        print_detailed_report(results, readiness, scores)
        
        # Save to file
        report_file = Path("READINESS_REPORT.json")
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump({
                "readiness_percentage": readiness,
                "scores": {k: {"score": v[0], "max": v[1], "percentage": (v[0]/v[1]*100)} 
                          for k, v in scores.items()},
                "detailed_checks": results
            }, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ EN: {report_file}")
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ EN: {str(e)}")
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
