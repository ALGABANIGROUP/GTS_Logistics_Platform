#!/bin/bash
# Roll back to previous stable version
set -e

echo "🔄 Starting rollback..."

docker-compose -f docker-compose.production.yml down || true
./deployment/scripts/restore-backup.sh latest_stable_backup || true

git checkout tags/v1.2.3-stable

docker-compose -f docker-compose.production.yml build
DockerComposeStatus=$?
if [ $DockerComposeStatus -ne 0 ]; then echo "❌ Build failed"; exit 1; fi

docker-compose -f docker-compose.production.yml up -d

echo "✅ Rolled back to stable version"