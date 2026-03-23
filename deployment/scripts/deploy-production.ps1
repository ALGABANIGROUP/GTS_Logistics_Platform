Param(
  [string]$ComposeFile = "docker-compose.production.yml"
)

Write-Host "🚀 Starting bot platform production deployment"

function Assert-Cmd($cmd){ if(-not (Get-Command $cmd -ErrorAction SilentlyContinue)){ throw "Missing command: $cmd" } }
Assert-Cmd docker
Assert-Cmd docker-compose

if(-not (Test-Path "./security/ssl/production.key")) { throw "Missing ./security/ssl/production.key" }

Write-Host "🛑 Stopping current system..."
try { docker-compose -f $ComposeFile down } catch {}

Write-Host "📥 Pulling images..."
try { docker pull registry.company.com/bots-platform/backend:latest } catch {}
try { docker pull registry.company.com/bots-platform/frontend:latest } catch {}
try { docker pull registry.company.com/bots-platform/nginx:latest } catch {}

Write-Host "⚙️ Updating production configuration..."
Copy-Item ./deployment/configs/production/.env.production -Destination ./.env -Force
Copy-Item ./deployment/configs/production/nginx-production.conf -Destination ./nginx/nginx.conf -Force

Write-Host "💾 Creating backup..."
if(Test-Path ./deployment/scripts/backup-production.ps1){ ./deployment/scripts/backup-production.ps1 }

Write-Host "🗄️ Applying database migrations..."
docker-compose -f $ComposeFile run --rm backend python manage.py migrate --noinput

Write-Host "🚀 Starting system..."
docker-compose -f $ComposeFile up -d

Write-Host "🏥 Health checks..."
Start-Sleep -Seconds 30
$api = (Invoke-WebRequest https://api.bots-platform.com/health -UseBasicParsing -Method Get -ErrorAction SilentlyContinue).StatusCode
if($api -ne 200){ throw "API health check failed: $api" }
$fe = (Invoke-WebRequest https://bots-platform.com -UseBasicParsing -Method Get -ErrorAction SilentlyContinue).StatusCode
if($fe -ne 200){ throw "Frontend health check failed: $fe" }

Write-Host "🧪 Post-deploy tests..."
try { docker-compose -f $ComposeFile run --rm backend python -m pytest tests/post_deployment/ -v } catch {}

Write-Host "📨 Notifications..."
try { Send-MailMessage -To 'ops-team@company.com' -From 'deploy@company.com' -SmtpServer 'smtp.company.com' -Subject 'Deployment Success' -Body ("Bot platform deployed at " + (Get-Date)) } catch {}
try { Invoke-RestMethod -Method Post -Uri 'https://hooks.slack.com/services/XXX/YYY/ZZZ' -ContentType 'application/json' -Body '{"text":"🚀 Bot platform successfully deployed to production"}' } catch {}

"$(Get-Date): Production deployment completed successfully" | Out-File -FilePath ./deployment/logs/deployment.log -Append -Encoding utf8
Write-Host "🎉 Deployment finished successfully!"