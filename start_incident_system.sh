#!/bin/bash
# Incident Response System - Production Startup Script
# This script starts all incident response components

echo "🚀 Starting GTS Incident Response System..."

# Set environment
export PYTHONPATH="/opt/gts/backend:$PYTHONPATH"
cd /opt/gts

# Load environment variables
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Function to start service in background
start_service() {
    local service_name=$1
    local command=$2
    local log_file=$3

    echo "📡 Starting $service_name..."
    nohup $command > $log_file 2>&1 &
    echo $! > /var/run/${service_name}.pid
    echo "✅ $service_name started (PID: $(cat /var/run/${service_name}.pid))"
}

# Create log directories
mkdir -p /var/log/gts
mkdir -p /var/run

# Start log monitoring
start_service "incident_monitor" "python scripts/monitor_logs.py" "/var/log/gts/monitor.log"

# Start backend server (if not already running)
if ! pgrep -f "uvicorn.*main:app" > /dev/null; then
    start_service "gts_backend" "python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload" "/var/log/gts/backend.log"
fi

# Start alert processor (if configured)
if [ ! -z "$SLACK_WEBHOOK_URL" ] || [ ! -z "$PAGERDUTY_INTEGRATION_KEY" ]; then
    start_service "alert_processor" "python scripts/process_alerts.py" "/var/log/gts/alerts.log"
fi

echo ""
echo "🎉 Incident Response System started successfully!"
echo ""
echo "Active Services:"
echo "  📊 Log Monitor: $(cat /var/run/incident_monitor.pid 2>/dev/null || echo 'N/A')"
echo "  🚀 Backend API: $(cat /var/run/gts_backend.pid 2>/dev/null || echo 'N/A')"
echo "  📢 Alert Processor: $(cat /var/run/alert_processor.pid 2>/dev/null || echo 'N/A')"
echo ""
echo "Monitor logs:"
echo "  tail -f /var/log/gts/monitor.log"
echo "  tail -f /var/log/gts/backend.log"
echo ""
echo "Stop services: ./stop_incident_system.sh"