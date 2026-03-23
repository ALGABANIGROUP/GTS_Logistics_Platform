#!/bin/bash

echo "🚀 Starting Database Orchestrator Bot..."

# Check environment variables
if [ -z "$DATABASE_URL" ]; then
    echo "❌ DATABASE_URL environment variable not set"
    exit 1
fi

# Install requirements
pip install -r requirements_orchestrator.txt

# Start Redis
docker run -d --name redis-cache -p 6379:6379 redis:7-alpine

# Start the bot
python database_orchestrator.py

echo "✅ Bot is running on http://localhost:8080"
echo "📊 Dashboard: http://localhost:8080/api/v1/metrics"