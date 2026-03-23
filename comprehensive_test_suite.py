"""
Comprehensive System Test Suite
Tests all core features after SQLAlchemy unification
"""

import asyncio
import logging
from typing import Dict, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_comprehensive")


class TestResult:
    def __init__(self, name: str):
        self.name = name
        self.passed = False
        self.error: Optional[str] = None
        self.details: Dict[str, Any] = {}
    
    def mark_passed(self, details: Dict[str, Any] = None):
        self.passed = True
        if details:
            self.details.update(details)
    
    def mark_failed(self, error: str, details: Dict[str, Any] = None):
        self.passed = False
        self.error = error
        if details:
            self.details.update(details)
    
    def __str__(self):
        status = "✅ PASS" if self.passed else "❌ FAIL"
        msg = f"{status} - {self.name}"
        if self.error:
            msg += f"\n  Error: {self.error}"
        if self.details:
            for k, v in self.details.items():
                msg += f"\n  {k}: {v}"
        return msg


class ComprehensiveTests:
    def __init__(self):
        self.results: list[TestResult] = []
    
    async def run_all(self):
        """Run all tests"""
        logger.info("=" * 80)
        logger.info("COMPREHENSIVE SYSTEM TEST SUITE")
        logger.info("=" * 80)
        
        # 1. SQLAlchemy Models Test
        await self.test_sqlalchemy_models()
        
        # 2. Database Connection Test
        await self.test_database_connection()
        
        # 3. Core Models Test
        await self.test_core_models()
        
        # 4. Admin Routes Test
        await self.test_admin_routes()
        
        # 5. Finance Routes Test
        await self.test_finance_routes()
        
        # 6. Shipments Routes Test
        await self.test_shipments_routes()
        
        # 7. Bot OS Routes Test
        await self.test_bot_os_routes()
        
        # 8. Users Routes Test
        await self.test_users_routes()
        
        # 9. Scope Dependency Test
        await self.test_scope_dependency()
        
        # 10. Import Dependencies Test
        await self.test_import_dependencies()
        
        # Print results
        self.print_results()
    
    async def test_sqlalchemy_models(self):
        """Test SQLAlchemy model consolidation"""
        result = TestResult("SQLAlchemy Models Consolidation")
        try:
            from backend.database.base import Base
            from backend.models.user import User
            from backend.models.tenant import Tenant
            from backend.models.financial import Expense
            from backend.billing.models import Plan, Subscription
            from backend.models.subscription import BotRun, Role
            
            # Check single Base instance
            models = [User, Tenant, Expense, Plan, Subscription, BotRun, Role]
            all_same = all(m.__table__.metadata is Base.metadata for m in models)
            
            if not all_same:
                result.mark_failed("Not all models use same Base instance")
            else:
                result.mark_passed({
                    "Base instances": 1,
                    "Models checked": len(models),
                    "Tables registered": len(Base.metadata.tables),
                })
        except Exception as e:
            result.mark_failed(str(e))
        
        self.results.append(result)
    
    async def test_database_connection(self):
        """Test database connection"""
        result = TestResult("Database Connection")
        try:
            from backend.database.session import wrap_session_factory
            
            async with wrap_session_factory() as session:
                # Try a simple query
                from sqlalchemy import text
                await session.execute(text("SELECT 1"))
            
            result.mark_passed({"status": "Connected"})
        except Exception as e:
            result.mark_failed(f"Database connection failed: {str(e)}")
        
        self.results.append(result)
    
    async def test_core_models(self):
        """Test core model imports"""
        result = TestResult("Core Models Import")
        try:
            from backend.models.user import User
            from backend.models.tenant import Tenant
            from backend.models.financial import Expense
            from backend.models.subscription import Role, BotRun, Bot
            from backend.billing.models import Plan, Subscription
            
            models_imported = {
                'User': User,
                'Tenant': Tenant,
                'Expense': Expense,
                'Role': Role,
                'BotRun': BotRun,
                'Bot': Bot,
                'Plan': Plan,
                'Subscription': Subscription,
            }
            
            result.mark_passed({
                "Models imported": len(models_imported),
                "Models": ", ".join(models_imported.keys()),
            })
        except Exception as e:
            result.mark_failed(f"Core models import failed: {str(e)}")
        
        self.results.append(result)
    
    async def test_admin_routes(self):
        """Test admin routes import"""
        result = TestResult("Admin Routes (admin_users.py)")
        try:
            from backend.routes.admin_users import router
            from backend.routes.admin_system import router as admin_system_router
            
            # Check that routers are APIRouter instances
            from fastapi import APIRouter
            
            if not isinstance(router, APIRouter):
                result.mark_failed("admin_users router is not APIRouter instance")
            else:
                result.mark_passed({
                    "admin_users routes": len(router.routes),
                    "admin_system routes": len(admin_system_router.routes),
                })
        except Exception as e:
            result.mark_failed(f"Admin routes import failed: {str(e)}")
        
        self.results.append(result)
    
    async def test_finance_routes(self):
        """Test finance routes"""
        result = TestResult("Finance Routes")
        try:
            from backend.routes.finance_routes import router as finance_router
            from backend.routes.finance_reports import router as reports_router
            from backend.routes.finance_ai_routes import router as ai_router
            
            from fastapi import APIRouter
            
            if not all(isinstance(r, APIRouter) for r in [finance_router, reports_router, ai_router]):
                result.mark_failed("Finance routers not properly initialized")
            else:
                result.mark_passed({
                    "finance_routes endpoints": len(finance_router.routes),
                    "finance_reports endpoints": len(reports_router.routes),
                    "finance_ai_routes endpoints": len(ai_router.routes),
                })
        except Exception as e:
            result.mark_failed(f"Finance routes import failed: {str(e)}")
        
        self.results.append(result)
    
    async def test_shipments_routes(self):
        """Test shipments routes"""
        result = TestResult("Shipments Routes")
        try:
            from backend.routes.shipments_pg_api import router as shipments_router
            from backend.routes.shipments_import_routes import router as import_router
            
            from fastapi import APIRouter
            
            if not all(isinstance(r, APIRouter) for r in [shipments_router, import_router]):
                result.mark_failed("Shipments routers not properly initialized")
            else:
                result.mark_passed({
                    "shipments_pg_api endpoints": len(shipments_router.routes),
                    "shipments_import_routes endpoints": len(import_router.routes),
                })
        except Exception as e:
            result.mark_failed(f"Shipments routes import failed: {str(e)}")
        
        self.results.append(result)
    
    async def test_bot_os_routes(self):
        """Test bot OS routes"""
        result = TestResult("Bot OS Routes")
        try:
            from backend.routes.bot_os import router as bot_os_router
            from fastapi import APIRouter
            
            if not isinstance(bot_os_router, APIRouter):
                result.mark_failed("bot_os router not properly initialized")
            else:
                result.mark_passed({
                    "bot_os endpoints": len(bot_os_router.routes),
                })
        except Exception as e:
            result.mark_failed(f"Bot OS routes import failed: {str(e)}")
        
        self.results.append(result)
    
    async def test_users_routes(self):
        """Test users routes"""
        result = TestResult("Users Routes")
        try:
            from backend.routes.users_routes import router as users_router
            from fastapi import APIRouter
            
            if not isinstance(users_router, APIRouter):
                result.mark_failed("users_routes router not properly initialized")
            else:
                result.mark_passed({
                    "users_routes endpoints": len(users_router.routes),
                })
        except Exception as e:
            result.mark_failed(f"Users routes import failed: {str(e)}")
        
        self.results.append(result)
    
    async def test_scope_dependency(self):
        """Test scope dependency"""
        result = TestResult("Scope Dependency (scope_dependency.py)")
        try:
            from backend.security.scope_dependency import require_scope, require_scopes
            
            # Check that functions are callable
            if not callable(require_scope) or not callable(require_scopes):
                result.mark_failed("Scope dependency functions not callable")
            else:
                result.mark_passed({
                    "require_scope": "available",
                    "require_scopes": "available",
                })
        except Exception as e:
            result.mark_failed(f"Scope dependency import failed: {str(e)}")
        
        self.results.append(result)
    
    async def test_import_dependencies(self):
        """Test all critical import dependencies"""
        result = TestResult("Import Dependencies Check")
        failed_imports = []
        
        import_paths = [
            ("backend.database.base", "Base"),
            ("backend.database.session", "wrap_session_factory"),
            ("backend.models.user", "User"),
            ("backend.models.tenant", "Tenant"),
            ("backend.models.financial", "Expense"),
            ("backend.models.subscription", "Role"),
            ("backend.billing.models", "Plan"),
            ("backend.security.auth", "get_current_user"),
            ("backend.security.scope_dependency", "require_scope"),
        ]
        
        for module_path, item_name in import_paths:
            try:
                module = __import__(module_path, fromlist=[item_name])
                getattr(module, item_name)
            except Exception as e:
                failed_imports.append(f"{module_path}.{item_name}: {str(e)}")
        
        if failed_imports:
            result.mark_failed(
                f"Failed to import {len(failed_imports)} items",
                {"failed": failed_imports}
            )
        else:
            result.mark_passed({
                "total imports checked": len(import_paths),
                "successful imports": len(import_paths),
            })
        
        self.results.append(result)
    
    def print_results(self):
        """Print test results summary"""
        logger.info("\n" + "=" * 80)
        logger.info("TEST RESULTS SUMMARY")
        logger.info("=" * 80)
        
        passed = sum(1 for r in self.results if r.passed)
        failed = sum(1 for r in self.results if not r.passed)
        
        for result in self.results:
            logger.info(str(result))
        
        logger.info("\n" + "=" * 80)
        logger.info(f"TOTAL: {len(self.results)} | PASSED: ✅ {passed} | FAILED: ❌ {failed}")
        logger.info("=" * 80 + "\n")
        
        return passed, failed


async def main():
    """Run comprehensive tests"""
    tests = ComprehensiveTests()
    await tests.run_all()


if __name__ == "__main__":
    asyncio.run(main())
