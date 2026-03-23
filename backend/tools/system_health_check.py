import asyncio
import sys
import os
import importlib
import inspect
from pathlib import Path
from typing import Dict, List, Any, Optional
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))
print(f'🔧 System path: {backend_path}')

class SystemHealthChecker:

    def __init__(self):
        self.results = {'database': {}, 'ai_bots': {}, 'api_routes': {}, 'config': {}, 'module_imports': {}, 'overall_status': 'healthy'}

    async def check_system_structure(self):
        """Check folder and file structure"""
        print('📁 Checking system structure...')
        required_dirs = [backend_path / 'database', backend_path / 'core', backend_path / 'routes', backend_path / 'tools']
        required_files = [backend_path / 'database' / 'config.py', backend_path / 'database' / 'session.py', backend_path / 'database' / 'base.py', backend_path / 'main.py']
        existing_dirs = []
        missing_dirs = []
        for dir_path in required_dirs:
            if dir_path.exists():
                existing_dirs.append(str(dir_path))
                print(f'✅ Folder: {dir_path.name}')
            else:
                missing_dirs.append(str(dir_path))
                print(f'❌ Missing folder: {dir_path.name}')
        existing_files = []
        missing_files = []
        for file_path in required_files:
            if file_path.exists():
                existing_files.append(str(file_path))
                print(f'✅ File: {file_path.name}')
            else:
                missing_files.append(str(file_path))
                print(f'❌ Missing file: {file_path.name}')
        self.results['structure'] = {'existing_dirs': existing_dirs, 'missing_dirs': missing_dirs, 'existing_files': existing_files, 'missing_files': missing_files}
        return len(missing_dirs) == 0 and len(missing_files) == 0

    async def check_database_connection(self):
        """Check database connection"""
        print('\n🔍 Checking database connection...')
        try:
            config_path = backend_path / 'database' / 'config.py'
            if not config_path.exists():
                print('❌ config.py file not found')
                return False
            with open(config_path, 'r', encoding='utf-8') as f:
                config_content = f.read()
                print(f'📄 config.py content length: {len(config_content)} chars')
            import database.config
            required_vars = ['DATABASE_URL', 'ASYNC_DATABASE_URL', 'async_engine']
            available_vars = []
            missing_vars = []
            for var in required_vars:
                if hasattr(database.config, var):
                    available_vars.append(var)
                    value = getattr(database.config, var)
                    if 'password' in var.lower():
                        print(f'✅ {var}: [protected]')
                    else:
                        print(f'✅ {var}: {value}')
                else:
                    missing_vars.append(var)
                    print(f'❌ {var}: not found')
            self.results['database']['available_vars'] = available_vars
            self.results['database']['missing_vars'] = missing_vars
            if missing_vars:
                return False
            try:
                from sqlalchemy import text
                engine = database.config.async_engine
                async with engine.connect() as conn:
                    result = await conn.execute(text('SELECT version()'))
                    version = result.scalar()
                    print(f'✅ Database connection successful: {version}')
                    self.results['database']['connection'] = 'success'
                    return True
            except Exception as e:
                print(f'❌ Connection test failed: {e}')
                self.results['database']['connection_error'] = str(e)
                return False
        except Exception as e:
            print(f'❌ Database check failed: {e}')
            self.results['database']['error'] = str(e)
            return False

    async def check_module_imports(self):
        """Check module imports"""
        print('\n📦 Checking module imports...')
        modules_to_check = ['database.config', 'database.session', 'main']
        core_path = backend_path / 'core'
        if core_path.exists():
            modules_to_check.extend(['core.config', 'core.ai_core'])
        routes_path = backend_path / 'routes'
        if routes_path.exists():
            modules_to_check.extend(['routes.finance_routes', 'routes.documents_routes'])
        imported_modules = []
        failed_modules = []
        for module_path in modules_to_check:
            try:
                module = importlib.import_module(module_path)
                imported_modules.append(module_path)
                print(f'✅ {module_path}')
            except Exception as e:
                failed_modules.append(f'{module_path}: {e}')
                print(f'❌ {module_path}: {e}')
        self.results['module_imports'] = {'successful': imported_modules, 'failed': failed_modules}
        return len(failed_modules) == 0

    async def check_ai_bots(self):
        """Check AI bots"""
        print('\n🤖 Checking AI bots...')
        try:
            ai_core_path = backend_path / 'core' / 'ai_core.py'
            if not ai_core_path.exists():
                print('❌ ai_core.py not found')
                self.results['ai_bots']['error'] = 'ai_core.py not found'
                return False
            import core.ai_core
            bot_manager = core.ai_core.AIBotManager()
            registered_bots = getattr(bot_manager, 'registered_bots', {})
            expected_bots = {'general_manager': 'GeneralManagerBot', 'freight_broker': 'FreightBrokerBot', 'operations_manager': 'OperationsManagerBot', 'finance_bot': 'FinanceBot', 'documents_manager': 'DocumentsManagerBot', 'maintenance_dev': 'AIMaintenanceDevBot'}
            working_bots = []
            missing_bots = []
            for (bot_id, bot_class) in expected_bots.items():
                if bot_id in registered_bots:
                    working_bots.append(bot_id)
                    print(f'✅ {bot_id} ({bot_class})')
                else:
                    missing_bots.append(bot_id)
                    print(f'❌ {bot_id} ({bot_class})')
            self.results['ai_bots'] = {'expected': expected_bots, 'registered': registered_bots, 'working': working_bots, 'missing': missing_bots, 'total_working': len(working_bots)}
            print(f'📊 Working bots: {len(working_bots)}/6')
            return len(working_bots) == 6
        except Exception as e:
            print(f'❌ AI bot check failed: {e}')
            self.results['ai_bots']['error'] = str(e)
            return False

    async def check_fastapi_app(self):
        """Check FastAPI application"""
        print('\n🌐 Checking FastAPI application...')
        try:
            import main
            app = main.app
            routes = []
            for route in app.routes:
                route_info = {'path': getattr(route, 'path', ''), 'methods': getattr(route, 'methods', []), 'name': getattr(route, 'name', '')}
                routes.append(route_info)
            self.results['api_routes'] = {'total_routes': len(routes), 'routes': [r['path'] for r in routes[:10]]}
            print(f'✅ Total routes: {len(routes)}')
            for route in routes[:5]:
                print(f"   📍 {route['path']} {route['methods']}")
            if len(routes) > 5:
                print(f'   ... and {len(routes) - 5} more routes')
            return len(routes) > 0
        except Exception as e:
            print(f'❌ FastAPI check failed: {e}')
            self.results['api_routes']['error'] = str(e)
            return False

    async def run_comprehensive_check(self):
        """Run full system health check"""
        print('=' * 60)
        print('🔧 Starting full system health check (fixed version)')
        print('=' * 60)
        structure_ok = await self.check_system_structure()
        if not structure_ok:
            print('\n💥 System structure incomplete. Cannot proceed.')
            return self.results
        checks = [self.check_module_imports(), self.check_database_connection(), self.check_fastapi_app(), self.check_ai_bots()]
        results = await asyncio.gather(*checks, return_exceptions=True)
        successful_checks = sum((1 for r in results if r is True))
        total_checks = len(checks)
        print('\n' + '=' * 60)
        print('📊 Full Health Check Report')
        print('=' * 60)
        print(f'✅ Successful checks: {successful_checks}/{total_checks}')
        if successful_checks == total_checks:
            print('🎉 System is fully operational!')
            self.results['overall_status'] = 'healthy'
        elif successful_checks >= total_checks - 1:
            print('⚠️ System operational with minor issues')
            self.results['overall_status'] = 'warning'
        else:
            print('❌ System has critical issues')
            self.results['overall_status'] = 'unhealthy'
        self.generate_recommendations()
        return self.results

    def generate_recommendations(self):
        """Generate recommendations based on results"""
        print('\n💡 Recommendations:')
        if self.results['structure'].get('missing_dirs'):
            print('  • Create the missing folders')
        if self.results['database'].get('missing_vars'):
            print('  • Fix config.py and add missing variables')
        ai_bots_count = self.results['ai_bots'].get('total_working', 0)
        if ai_bots_count < 6:
            print(f'  • Fix missing bots ({ai_bots_count}/6 working)')

async def main():
    """Main function"""
    checker = SystemHealthChecker()
    try:
        results = await checker.run_comprehensive_check()
        report_path = backend_path / 'system_health_report_fixed.txt'
        with open(report_path, 'w', encoding='utf-8') as f:
            import json
            f.write(json.dumps(results, indent=2, ensure_ascii=False))
        print(f'\n📄 Report saved to: {report_path}')
        return results['overall_status'] == 'healthy'
    except Exception as e:
        print(f'❌ Full check failed: {e}')
        return False
if __name__ == '__main__':
    success = asyncio.run(main())
    if success:
        print('\n🎉 Check completed successfully! System is ready to use.')
    else:
        print('\n💥 System requires maintenance. See report above.')


