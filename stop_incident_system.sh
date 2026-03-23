#!/bin/bash
# Incident Response System - Stop Script

echo "🛑 Stopping GTS Incident Response System..."

# Function to stop service
stop_service() {
    local service_name=$1
    local pid_file="/var/run/${service_name}.pid"

    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if kill -0 "$pid" 2>/dev/null; then
            echo "Stopping $service_name (PID: $pid)..."
            kill "$pid"
            # Wait for process to stop
            for i in {1..10}; do
                if ! kill -0 "$pid" 2>/dev/null; then
                    break
                fi
                sleep 1
            done
            # Force kill if still running
            if kill -0 "$pid" 2>/dev/null; then
                echo "Force stopping $service_name..."
                kill -9 "$pid"
            fi
        else
            echo "$service_name is not running"
        fi
        rm -f "$pid_file"
        echo "✅ $service_name stopped"
    else
        echo "$service_name PID file not found"
    fi
}

# Stop services in reverse order
stop_service "alert_processor"
stop_service "incident_monitor"
stop_service "gts_backend"

echo ""
echo "🎯 All Incident Response System services stopped"