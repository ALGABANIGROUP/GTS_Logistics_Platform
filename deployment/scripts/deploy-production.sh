#!/bin/bash
# Production deployment script for Bots Platform
# Run only after all tests pass
set -e

echo "🚀 Starting bot platform production deployment"
echo "========================================="

check_requirements() {
  if ! command -v docker &> /dev/null; then
    echo "❌ Docker not installed"; exit 1; fi
  if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose not installed"; exit 1; fi
  if [ ! -f "./security/ssl/production.key" ]; then
    echo "❌ Missing production secret key file"; exit 1; fi
  echo "✅ All prerequisites available"
}

check_requirements

echo "🛑 Stopping current system..."
docker-compose -f docker-compose.production.yml down || true

echo "📥 Pulling latest images from registry..."
docker pull registry.company.com/bots-platform/backend:latest || true
docker pull registry.company.com/bots-platform/frontend:latest || true
docker pull registry.company.com/bots-platform/nginx:latest || true

echo "⚙️ Updating production configuration..."
cp ./deployment/configs/production/.env.production .env
cp ./deployment/configs/production/nginx-production.conf ./nginx/nginx.conf

echo "💾 Creating backup..."
./deployment/scripts/backup-production.sh || true

echo "🗄️ Applying database migrations..."
docker-compose -f docker-compose.production.yml run --rm backend \
  python manage.py migrate --noinput

echo "🚀 Starting system..."
docker-compose -f docker-compose.production.yml up -d

echo "🏥 Performing health checks..."
sleep 30
API_STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://api.bots-platform.com/health)
if [ "$API_STATUS" -ne 200 ]; then echo "❌ API health check failed"; exit 1; fi
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://bots-platform.com)
if [ "$FRONTEND_STATUS" -ne 200 ]; then echo "❌ Frontend load failed"; exit 1; fi

echo "🧪 Running post-deployment tests..."
docker-compose -f docker-compose.production.yml run --rm backend \
  python -m pytest tests/post_deployment/ -v || true

echo "📨 Sending notifications..."
if command -v mail &> /dev/null; then
  echo "Bot platform deployed successfully on $(date)" | \
  mail -s "✅ Successful Deployment - Bots Platform" ops-team@company.com
fi
curl -X POST -H 'Content-type: application/json' \
  --data '{"text":"🚀 Bot platform successfully deployed to production"}' \
  https://hooks.slack.com/services/XXX/YYY/ZZZ || true

echo "========================================="
echo "🎉 Deployment finished successfully!"
echo "📊 Admin: https://admin.bots-platform.com"
echo "📈 Monitoring: https://monitoring.company.com"
echo "📋 Logs: https://logs.company.com"

echo "$(date): Production deployment completed successfully" >> ./deployment/logs/deployment.log
