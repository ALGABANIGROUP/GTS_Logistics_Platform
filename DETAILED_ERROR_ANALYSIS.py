#!/usr/bin/env python3
"""
Deep Error & Warning Analysis for GTS SaaS
EN
"""

import json
from pathlib import Path
from typing import Dict, List, Any
import re

# ============================================================================
# CRITICAL ERRORS FOUND
# ============================================================================

CRITICAL_ISSUES = {
    "SQLAlchemy Model Conflicts": {
        "severity": "🔴 CRITICAL",
        "affected_routes": [
            "admin_unified.py",
            "finance_routes.py",
            "finance_reports.py",
            "finance_ai_routes.py"
        ],
        "error": "Table 'tenants' and 'expenses' already defined for this MetaData instance",
        "root_cause": "Multiple imports of same model with different Base instances or circular imports",
        "impact": "Routes fail to mount, endpoints unavailable",
        "solution": [
            "1. Consolidate all model Base definitions to use single Base instance",
            "2. Use extend_existing=True in SQLAlchemy models if necessary",
            "3. Fix circular import dependencies",
            "4. Ensure models/__init__.py correctly exports all models once"
        ],
        "workaround": "Routes already removed/unmounted by _try_import_router"
    },
    
    "Missing Module Imports": {
        "severity": "🔴 CRITICAL",
        "affected_routes": [
            "admin_users.py (file doesn't exist)",
            "bot_os.py (scope_dependency missing)",
            "shipments_pg_api.py (Shipment model missing)"
        ],
        "error": "No module named 'backend.routes.admin_users'",
        "root_cause": "File path mismatch or module not created",
        "impact": "Route not loaded, admin users features unavailable",
        "solution": [
            "1. Check if admin_users.py file exists in backend/routes/",
            "2. If missing, create it or check naming convention",
            "3. Verify bot_os.py imports from correct paths",
            "4. Check if Shipment model is exported from backend.models"
        ]
    },
    
    "users_routes Not Available": {
        "severity": "🟠 HIGH",
        "affected_routes": ["users_routes.py"],
        "error": "users_routes not available after mounting",
        "root_cause": "Unknown - likely import or initialization issue",
        "impact": "User-related endpoints may be affected",
        "solution": [
            "1. Check users_routes.py for syntax errors",
            "2. Verify all imports in users_routes.py",
            "3. Check for circular import dependencies",
            "4. Run pytest on users_routes.py to identify issues"
        ]
    }
}

# ============================================================================
# ROUTES ANALYSIS
# ============================================================================

MOUNTED_ROUTES = {
    "✅ Successfully Mounted": [
        "/api/v1/auth - Authentication",
        "/api/v1/bots/* - Bot Management",
        "/api/transport-laws/* - Transport Laws",
        "/users/* - User endpoints (WARNING: marked not available)",
        "/api/v1/email/* - Email Center",
        "/api/v1/maintenance/* - Maintenance",
        "/api/v1/admin/* - Admin System",
        "/api/v1/admin/data-sources/* - Data Sources",
        "/api/v1/admin/social-media - Social Media",
        "/api/v1/social-media - Social Media Public"
    ],
    
    "❌ Failed to Mount (SQLAlchemy Issues)": [
        "admin_unified.py - tenants table conflict",
        "finance_routes.py - expenses table conflict",
        "finance_reports.py - expenses table conflict",
        "finance_ai_routes.py - expenses table conflict",
        "public_api.py - tenants table conflict"
    ],
    
    "❌ Failed to Mount (Import Issues)": [
        "admin_users.py - No module found",
        "bot_os.py - scope_dependency missing",
        "shipments_pg_api.py - Shipment model missing"
    ]
}

# ============================================================================
# AVAILABLE ENDPOINTS
# ============================================================================

AVAILABLE_ENDPOINTS = {
    "/api/v1/auth": {
        "GET /me": "Get current user",
        "POST /token": "Login",
    },
    "/api/v1/admin": {
        "GET /users/management": "✅ NEW - User management (just added)",
        "GET /users/list": "User list with pagination",
        "GET /users/{user_id}": "Get user details",
        "GET /roles": "✅ NEW - Available roles",
        "GET /org/tree": "✅ NEW - Organization tree",
        "POST /org/units/{user_id}/move": "✅ NEW - Move user to manager",
        "GET /dashboard/stats": "Dashboard statistics"
    },
    "/api/v1/bots": {
        "GET /": "List bots",
        "GET /available": "Available bots",
        "GET /history": "Bot execution history"
    }
}

# ============================================================================
# WORKING VS NOT WORKING
# ============================================================================

FUNCTIONALITY_STATUS = {
    "✅ Working": {
        "Authentication": [
            "Login (/api/v1/auth/token)",
            "Get current user (/api/v1/auth/me)",
            "Token validation",
            "Role extraction"
        ],
        "Admin Dashboard": [
            "/admin/users page loads",
            "User listing",
            "User management",
            "Organization tree",
            "Role display"
        ],
        "Database": [
            "PostgreSQL connection",
            "User queries",
            "Role-based queries",
            "User count, filtering, pagination"
        ],
        "Email System": [
            "Registration emails",
            "Password reset emails",
            "Forgot password flow"
        ]
    },
    
    "⚠️  Partially Working": {
        "Finance Module": [
            "Finance routes fail to load (SQLAlchemy conflict)",
            "Finance reports unavailable",
            "Finance AI routes unavailable"
        ],
        "Bot OS": [
            "Bot management partially available",
            "Some endpoints unavailable due to import errors"
        ]
    },
    
    "❌ Not Working": {
        "Shipments API": [
            "shipments_pg_api routes failed to mount",
            "Shipment model not available"
        ],
        "Admin Users": [
            "admin_users.py routes not found",
            "Some admin user features unavailable"
        ]
    }
}

# ============================================================================
# RECOMMENDATIONS
# ============================================================================

RECOMMENDATIONS = {
    "IMMEDIATE (Priority: 🔴 CRITICAL)": [
        {
            "task": "Fix SQLAlchemy Model Metadata Conflicts",
            "description": "Consolidate all Base instances and fix circular imports",
            "estimated_time": "2-3 hours",
            "impact": "Enables Finance, Admin Unified, and Public API routes"
        },
        {
            "task": "Locate/Create missing admin_users.py",
            "description": "Check if file exists or needs to be created",
            "estimated_time": "30 minutes",
            "impact": "Enables admin user management features"
        }
    ],
    
    "SHORT TERM (Priority: 🟠 HIGH)": [
        {
            "task": "Fix bot_os scope_dependency import",
            "description": "Resolve missing scope_dependency in bot_os.py",
            "estimated_time": "1 hour",
            "impact": "Enables Bot OS management endpoints"
        },
        {
            "task": "Implement Shipment model",
            "description": "Create or restore Shipment model in backend/models",
            "estimated_time": "1-2 hours",
            "impact": "Enables shipments tracking APIs"
        },
        {
            "task": "Debug users_routes not available",
            "description": "Investigate why users_routes marked as unavailable",
            "estimated_time": "1 hour",
            "impact": "Ensures all user endpoints are accessible"
        }
    ],
    
    "MEDIUM TERM (Priority: 🟡 MEDIUM)": [
        {
            "task": "Complete /admin/users page features",
            "description": "Test and ensure all user management operations work",
            "estimated_time": "2-3 hours",
            "impact": "Full admin user management UI"
        },
        {
            "task": "Add docker-compose.yml",
            "description": "Create Docker setup for development/production",
            "estimated_time": "2-3 hours",
            "impact": "Easier deployment and development setup"
        },
        {
            "task": "Implement comprehensive logging",
            "description": "Add structured logging throughout the app",
            "estimated_time": "3-4 hours",
            "impact": "Better debugging and monitoring"
        }
    ],
    
    "LONG TERM (Priority: 🟢 LOW)": [
        {
            "task": "Implement automated testing",
            "description": "Add unit tests, integration tests, and e2e tests",
            "estimated_time": "8-10 hours",
            "impact": "Code quality, reliability, CI/CD"
        },
        {
            "task": "Add API documentation",
            "description": "Generate OpenAPI/Swagger docs for all endpoints",
            "estimated_time": "3-4 hours",
            "impact": "Better developer experience"
        },
        {
            "task": "Performance optimization",
            "description": "Profile and optimize database queries",
            "estimated_time": "4-6 hours",
            "impact": "Better application performance"
        }
    ]
}

# ============================================================================
# SECURITY ASSESSMENT
# ============================================================================

SECURITY_ASSESSMENT = {
    "✅ Secure": [
        "JWT token-based authentication",
        "Role-based access control (RBAC)",
        "Password hashing",
        "Token expiration",
        "Email verification"
    ],
    
    "⚠️  Needs Review": [
        "Rate limiting configuration",
        "CORS policy",
        "SQL injection prevention (using ORM - good)",
        "XSS protection in frontend",
        "CSRF token implementation"
    ],
    
    "❌ Not Implemented": [
        "API key authentication",
        "OAuth2 integration",
        "Two-factor authentication (2FA)",
        "Audit logging (partial)",
        "API versioning strategy"
    ]
}

# ============================================================================
# PERFORMANCE ASSESSMENT
# ============================================================================

PERFORMANCE_ASSESSMENT = {
    "Database": {
        "status": "✅ Good",
        "details": [
            "Using async SQLAlchemy - good for concurrent requests",
            "PostgreSQL with asyncpg - high performance",
            "Pagination implemented for list endpoints"
        ],
        "improvements": [
            "Add database indexes for frequent queries",
            "Implement query caching",
            "Consider read replicas for reporting"
        ]
    },
    
    "API": {
        "status": "✅ Good",
        "details": [
            "171 endpoints available",
            "Proper pagination support",
            "Async/await pattern used"
        ],
        "improvements": [
            "Add response caching",
            "Implement rate limiting",
            "Add request timeouts"
        ]
    },
    
    "Frontend": {
        "status": "✅ Good",
        "details": [
            "Using Vite for fast builds",
            "React with hooks",
            "Zustand for state management"
        ],
        "improvements": [
            "Code splitting for large bundles",
            "Lazy loading for components",
            "Image optimization"
        ]
    }
}


def print_analysis():
    """EN"""
    
    print("\n" + "=" * 80)
    print("🔍 EN - Deep Error & Warning Analysis")
    print("=" * 80)
    
    # Critical Issues
    print("\n🔴 EN (CRITICAL ISSUES):\n")
    for issue_name, details in CRITICAL_ISSUES.items():
        print(f"{details['severity']} {issue_name}")
        print(f"   EN: {details['error']}")
        print(f"   EN: {details['root_cause']}")
        print(f"   EN: {details['impact']}")
        print(f"   EN:")
        for solution in details['solution']:
            print(f"      • {solution}")
        print()
    
    # Routes Status
    print("\n" + "=" * 80)
    print("🛣️  EN (ROUTES STATUS):\n")
    
    for category, routes in MOUNTED_ROUTES.items():
        print(f"{category}:")
        for route in routes:
            print(f"   • {route}")
        print()
    
    # Functionality Status
    print("\n" + "=" * 80)
    print("📊 EN (FUNCTIONALITY STATUS):\n")
    
    for status, features in FUNCTIONALITY_STATUS.items():
        print(f"{status}")
        for category, items in features.items():
            print(f"   {category}:")
            for item in items:
                print(f"      • {item}")
        print()
    
    # Security Assessment
    print("\n" + "=" * 80)
    print("🔐 EN (SECURITY ASSESSMENT):\n")
    
    print("✅ EN (Secure):")
    for item in SECURITY_ASSESSMENT["✅ Secure"]:
        print(f"   • {item}")
    
    print("\n⚠️  EN (Needs Review):")
    for item in SECURITY_ASSESSMENT["⚠️  Needs Review"]:
        print(f"   • {item}")
    
    print("\n❌ EN (Not Implemented):")
    for item in SECURITY_ASSESSMENT["❌ Not Implemented"]:
        print(f"   • {item}")
    
    # Performance Assessment
    print("\n" + "=" * 80)
    print("⚡ EN (PERFORMANCE ASSESSMENT):\n")
    
    for component, assessment in PERFORMANCE_ASSESSMENT.items():
        print(f"{component} {assessment['status']}")
        print(f"   EN:")
        for detail in assessment['details']:
            print(f"      • {detail}")
        print(f"   EN:")
        for improvement in assessment['improvements']:
            print(f"      • {improvement}")
        print()
    
    # Recommendations
    print("\n" + "=" * 80)
    print("📋 EN (RECOMMENDATIONS):\n")
    
    for priority, tasks in RECOMMENDATIONS.items():
        print(f"\n{priority}")
        print("-" * 80)
        for idx, task in enumerate(tasks, 1):
            print(f"\n{idx}. {task['task']}")
            print(f"   EN: {task['description']}")
            print(f"   EN: {task['estimated_time']}")
            print(f"   EN: {task['impact']}")
    
    # Summary
    print("\n" + "=" * 80)
    print("📈 EN (SUMMARY):\n")
    
    summary = {
        "EN": "100% (EN) / 75% (EN)",
        "EN": "3 (SQLAlchemy, Missing modules)",
        "EN": "2 (bot_os, users_routes)",
        "EN": "75%+",
        "EN": "Finance, Shipments, Some Admin",
        "EN": "⚠️  EN | Nearly Production Ready"
    }
    
    for key, value in summary.items():
        print(f"• {key}: {value}")
    
    print("\n" + "=" * 80)
    print("✅ EN (NEXT STEPS):\n")
    
    next_steps = [
        "1. EN SQLAlchemy EN (CRITICAL)",
        "2. EN admin_users.py EN",
        "3. EN bot_os scope_dependency",
        "4. EN Shipment model",
        "5. EN",
        "6. EN"
    ]
    
    for step in next_steps:
        print(f"   {step}")
    
    print("\n" + "=" * 80)


def save_analysis():
    """EN JSON"""
    
    analysis_data = {
        "timestamp": str(Path("READINESS_REPORT.json").stat().st_mtime),
        "critical_issues": CRITICAL_ISSUES,
        "mounted_routes": MOUNTED_ROUTES,
        "available_endpoints": AVAILABLE_ENDPOINTS,
        "functionality_status": FUNCTIONALITY_STATUS,
        "security_assessment": SECURITY_ASSESSMENT,
        "performance_assessment": PERFORMANCE_ASSESSMENT,
        "recommendations": RECOMMENDATIONS,
        "summary": {
            "readiness_percentage": "100% (automated) / 75% (realistic)",
            "critical_problems": 3,
            "high_priority_problems": 2,
            "working_features": "75%+",
            "missing_features": ["Finance", "Shipments", "Some Admin"],
            "overall_status": "⚠️  Nearly Production Ready"
        }
    }
    
    report_file = Path("DETAILED_ERROR_ANALYSIS.json")
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(analysis_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 EN: {report_file}")


if __name__ == "__main__":
    print_analysis()
    save_analysis()
