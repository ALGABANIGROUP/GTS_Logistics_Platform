# System Architect Bot - Direct Python Test
Write-Host "`n=== System Architect Bot Test ===" -ForegroundColor Cyan

# Test 1: Router Import
Write-Host "[1/5] Router Import..." -ForegroundColor White
.\.venv\Scripts\python.exe -c "from backend.routes.system_architect_routes import router; print('✅ Router: {} routes'.format(len(router.routes)))"
if ($LASTEXITCODE -ne 0) { Write-Host "❌ FAILED" -ForegroundColor Red; exit 1 }

# Test 2: Bot Instance
Write-Host "[2/5] Bot Instance..." -ForegroundColor White
.\.venv\Scripts\python.exe -c "from backend.bots.system_architect import SystemArchitectBot; bot = SystemArchitectBot(); print('✅ Bot: {} v{}'.format(bot.name, bot.version))"
if ($LASTEXITCODE -ne 0) { Write-Host "❌ FAILED" -ForegroundColor Red; exit 1 }

# Test 3: Status Method
Write-Host "[3/5] Status Method..." -ForegroundColor White
.\.venv\Scripts\python.exe -c "import asyncio; from backend.bots.system_architect import SystemArchitectBot; bot = SystemArchitectBot(); result = asyncio.run(bot.status()); print('✅ Status: {} capabilities'.format(len(result['capabilities'])))"
if ($LASTEXITCODE -ne 0) { Write-Host "❌ FAILED" -ForegroundColor Red; exit 1 }

# Test 4: System Diagnostics
Write-Host "[4/5] System Diagnostics..." -ForegroundColor White
.\.venv\Scripts\python.exe -c "import asyncio; from backend.bots.system_architect import SystemArchitectBot; bot = SystemArchitectBot(); result = asyncio.run(bot.run_system_diagnostics({'diagnostic_type': 'full', 'components': ['api', 'database'], 'include_performance': True, 'include_security': True})); print('✅ Diagnostics: Health Score {}'.format(result['overall_health']['score']))"
if ($LASTEXITCODE -ne 0) { Write-Host "❌ FAILED" -ForegroundColor Red; exit 1 }

# Test 5: Performance Optimization
Write-Host "[5/5] Performance Optimization..." -ForegroundColor White
.\.venv\Scripts\python.exe -c "import asyncio; from backend.bots.system_architect import SystemArchitectBot; bot = SystemArchitectBot(); result = asyncio.run(bot.optimize_performance({'target_component': 'database', 'optimization_type': 'query_optimization', 'dry_run': True})); print('✅ Optimization: {} changes proposed'.format(len(result['proposed_changes'])))"
if ($LASTEXITCODE -ne 0) { Write-Host "❌ FAILED" -ForegroundColor Red; exit 1 }

Write-Host "`n✅ ALL TESTS PASSED!" -ForegroundColor Green
Write-Host "Opening API docs..." -ForegroundColor Cyan
Start-Process "http://127.0.0.1:8000/docs#/System%20Architect%20Bot"
