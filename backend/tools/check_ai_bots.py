import sys
import asyncio
import os
from pathlib import Path
backend_path = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(backend_path))
os.environ['PYTHONPATH'] = str(backend_path)

async def check_all_ai_bots():
    """Comprehensive check for all 6 AI bots"""
    print('🤖 Checking all 6 AI bots in the system...')
    print('=' * 50)
    expected_bots = {'general_manager': 'GeneralManagerBot', 'freight_broker': 'FreightBrokerBot', 'operations_manager': 'OperationsManagerBot', 'finance_bot': 'FinanceBot', 'documents_manager': 'DocumentsManagerBot', 'maintenance_dev': 'AIMaintenanceDevBot'}
    try:
        try:
            import importlib.util
            ai_core_path = backend_path / 'core' / 'ai_core.py'
            spec = importlib.util.spec_from_file_location('core.ai_core', str(ai_core_path))
            if spec is None:
                raise ImportError('Could not find the ai_core module')
            ai_core = importlib.util.module_from_spec(spec)
            if getattr(spec, 'loader', None) is None:
                raise ImportError('spec.loader is None for ai_core module')
            spec.loader.exec_module(ai_core)
            AIBotManager = getattr(ai_core, 'AIBotManager')
        except Exception:
            from core.ai_core import AIBotManager
        bot_manager = AIBotManager()
        registered_bots = getattr(bot_manager, 'registered_bots', {})
        print('📊 Expected vs Registered Bots:')
        print('-' * 40)
        working_bots = []
        for (bot_id, bot_class) in expected_bots.items():
            status = '✅' if bot_id in registered_bots else '❌'
            if bot_id in registered_bots:
                working_bots.append(bot_id)
                actual_class = registered_bots[bot_id]
                print(f'{status} {bot_id:20} -> {actual_class}')
            else:
                print(f'{status} {bot_id:20} -> Missing')
        print('-' * 40)
        print(f'🎯 Result: {len(working_bots)}/6 bots are active')
        if len(working_bots) == 6:
            print('🎉 All 6 bots are working successfully!')
            print('\n🧪 Testing bot functionality:')
            print('-' * 30)
            for bot_id in working_bots:
                try:
                    bot_instance = bot_manager.get_bot(bot_id)
                    bot_info = {'name': getattr(bot_instance, 'name', 'Unknown'), 'description': getattr(bot_instance, 'description', 'No description available'), 'version': getattr(bot_instance, 'version', '1.0')}
                    print(f"✅ {bot_id:20} | {bot_info['name']} | v{bot_info['version']}")
                    print(f"   📝 {bot_info['description']}")
                except Exception as e:
                    print(f'⚠️  {bot_id:20} | Error while loading: {e}')
        else:
            missing = set(expected_bots.keys()) - set(working_bots)
            print(f'❌ Missing bots: {list(missing)}')
        return len(working_bots) == 6
    except Exception as e:
        print(f'❌ Bot check failed: {e}')
        return False

async def test_bot_functionality():
    """Test AI bot functionality"""
    print('\n🔧 Testing bot functionality...')
    try:
        from core.ai_core import AIBotManager
        bot_manager = AIBotManager()
        test_message = 'Hello, can you help me?'
        print(f"📝 Test message: '{test_message}'")
        print('-' * 40)
        for bot_id in bot_manager.registered_bots.keys():
            try:
                bot = bot_manager.get_bot(bot_id)
                response = await bot.process_message(test_message)
                print(f'✅ {bot_id:20} | Response: {response[:50]}...')
            except Exception as e:
                print(f'❌ {bot_id:20} | Failed: {e}')
    except Exception as e:
        print(f'❌ Functionality test failed: {e}')

async def check_bot_dependencies():
    """Check bot dependencies"""
    print('\n📦 Checking bot dependencies...')
    dependencies = ['core.ai_core', 'database.config', 'database.session']
    for dep in dependencies:
        try:
            __import__(dep)
            print(f'✅ {dep}')
        except Exception as e:
            print(f'❌ {dep}: {e}')

async def main():
    """Full system AI bot check"""
    print('=' * 60)
    print('🤖 Full AI bot system check (6 bots)')
    print('=' * 60)
    await check_bot_dependencies()
    bots_ok = await check_all_ai_bots()
    if bots_ok:
        await test_bot_functionality()
    print('\n' + '=' * 60)
    if bots_ok:
        print('🎉 The AI bot system is fully operational!')
        print('💡 Ready bots:')
        print('   • GeneralManagerBot - General Manager')
        print('   • FreightBrokerBot - Freight Broker')
        print('   • OperationsManagerBot - Operations Manager')
        print('   • FinanceBot - Finance Assistant')
        print('   • DocumentsManagerBot - Documents Manager')
        print('   • AIMaintenanceDevBot - Maintenance & Dev Assistant')
    else:
        print('⚠️  There are issues in the AI bot system')
    print('=' * 60)
if __name__ == '__main__':
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
