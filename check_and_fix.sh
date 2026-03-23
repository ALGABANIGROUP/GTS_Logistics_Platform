#!/bin/bash
# File: check_and_fix.sh

echo "Starting Gabani Bots system check..."
echo "=================================="
# Check DB connection
echo "1. Checking database connection..."
if pg_isready -h localhost -p 5432 -U postgres; then
    echo "Database is active"
else
    echo "Database is not active"
    echo "Starting database..."
    docker-compose -f docker-compose-fix.yml up -d postgres
    sleep 10
fi
# Check missing bots
echo ""
echo "2. Checking missing bots..."
python3 -c "
import psycopg2
try:
    conn = psycopg2.connect(
        host='localhost',
        port=5432,
        dbname='gabani_bots',
        user='postgres',
        password='gabani123'
    )
    cursor = conn.cursor()
    cursor.execute('SELECT key, name FROM bots')
    existing = cursor.fetchall()
    required = [
        'general_manager', 'operations_manager', 'finance_bot',
        'freight_broker', 'documents_manager', 'customer_service',
        'system_admin', 'information_coordinator', 'strategy_advisor',
        'maintenance_dev', 'legal_consultant', 'safety_manager',
        'sales', 'security', 'mapleload_canada'
    ]
    existing_keys = [row[0] for row in existing]
    missing = [bot for bot in required if bot not in existing_keys]
    if missing:
        print(f'Missing bots: {len(missing)}')
        print(f'   {missing}')
        response = input('Fix missing bots? (y/n): ')
        if response.lower() == 'y':
            print('Running fixer service...')
            import subprocess
            subprocess.run(['docker-compose', '-f', 'docker-compose-fix.yml', 'up', 'bot_fixer'])
    else:
        print('All bots present')
    cursor.close()
    conn.close()
except Exception as e:
    print(f'Error: {e}')
"
# Check web app
echo ""
echo "3. Checking web app..."
if curl -s http://localhost:3000/health > /dev/null; then
    echo "Web app is running"
else
    echo "Web app is not running"
    echo "Starting web app..."
    docker-compose -f docker-compose-fix.yml up -d bots_app
    sleep 15
fi
# Final status
echo ""
echo "=================================="
echo "System status report:"
if docker ps | grep -q gabani_bots_db; then
    echo "   Database: ACTIVE"
else
    echo "   Database: INACTIVE"
fi
BOT_COUNT=$(docker exec gabani_bots_db psql -U postgres -d gabani_bots -t -c "SELECT COUNT(*) FROM bots WHERE status='active';" 2>/dev/null || echo "0")
echo "   Active bots: $BOT_COUNT/15"
if curl -s http://localhost:3000 > /dev/null; then
    echo "   Web app: ACTIVE"
else
    echo "   Web app: INACTIVE"
fi
echo ""
echo "To start all services: docker-compose -f docker-compose-fix.yml up -d"
echo "To view logs: docker-compose -f docker-compose-fix.yml logs -f"
echo "To stop: docker-compose -f docker-compose-fix.yml down"
