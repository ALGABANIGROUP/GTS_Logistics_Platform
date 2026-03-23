# Incident Response System - Production Deployment Guide

## 🚀 Production Setup

### Prerequisites
- Linux server (Ubuntu 20.04+ recommended)
- Python 3.8+
- PostgreSQL database
- Redis (optional, for caching)
- Email service for alerts

### 1. Environment Setup

#### Install Dependencies
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install python3 python3-pip python3-venv -y

# Install PostgreSQL client (if using external DB)
sudo apt install postgresql-client -y

# Install Redis (optional)
sudo apt install redis-server -y
```

#### Create Application Directory
```bash
sudo mkdir -p /opt/gts
sudo chown $USER:$USER /opt/gts
cd /opt/gts
```

#### Clone/Deploy Code
```bash
# Copy your GTS codebase to /opt/gts
# Make sure all files are present including:
# - backend/
# - scripts/
# - .env (configured)
```

#### Set Up Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configuration

#### Environment Variables
Update `.env` file with production values:

```bash
# Database (use production connection)
DATABASE_URL=postgresql+asyncpg://user:pass@prod-host:5432/dbname
INCIDENT_DB_URL=postgresql://user:pass@prod-host:5432/dbname

# Logging
LOG_PATH=/var/log/gts/app.log
API_LOG_PATH=/var/log/gts/api.log

# Alerts
ALERT_EMAIL=oncall@gts.com
SMTP_USERNAME=alerts@gabanilogistics.com
SMTP_PASSWORD=your-production-password

# External integrations
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK
PAGERDUTY_INTEGRATION_KEY=your-pagerduty-key
```

#### Create Log Directories
```bash
sudo mkdir -p /var/log/gts
sudo chown $USER:$USER /var/log/gts
```

### 3. Database Setup

#### Create Incident Tables
```bash
# Run database migrations if needed
# The incident tracker will create tables automatically on first use
```

### 4. Service Deployment

#### Make Scripts Executable
```bash
chmod +x start_incident_system.sh
chmod +x stop_incident_system.sh
```

#### Start Services
```bash
./start_incident_system.sh
```

#### Verify Services
```bash
# Check running processes
ps aux | grep -E "(monitor_logs|uvicorn|incident)"

# Check logs
tail -f /var/log/gts/monitor.log
tail -f /var/log/gts/backend.log
```

### 5. Systemd Service (Optional)

#### Create Systemd Service File
```bash
sudo tee /etc/systemd/system/gts-incident.service > /dev/null <<EOF
[Unit]
Description=GTS Incident Response System
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=/opt/gts
ExecStart=/opt/gts/start_incident_system.sh
ExecStop=/opt/gts/stop_incident_system.sh
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
```

#### Enable and Start Service
```bash
sudo systemctl daemon-reload
sudo systemctl enable gts-incident
sudo systemctl start gts-incident
sudo systemctl status gts-incident
```

### 6. Monitoring & Alerts

#### Log Rotation
```bash
# Create logrotate config
sudo tee /etc/logrotate.d/gts-incident > /dev/null <<EOF
/var/log/gts/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 644 $USER $USER
    postrotate
        systemctl reload gts-incident 2>/dev/null || true
    endscript
}
EOF
```

#### Health Checks
```bash
# Test API endpoint
curl http://localhost:8000/api/v1/incidents/active

# Test log monitoring
echo "2026-03-22 12:00:00 ERROR Test error" >> /var/log/gts/app.log
# Check if incident is created
curl http://localhost:8000/api/v1/incidents/active
```

### 7. Backup & Recovery

#### Database Backup
```bash
# Add to crontab for daily backups
0 2 * * * pg_dump $DATABASE_URL > /opt/gts/backups/incident_$(date +\%Y\%m\%d).sql
```

#### Configuration Backup
```bash
# Backup configs weekly
0 3 * * 0 tar -czf /opt/gts/backups/config_$(date +\%Y\%m\%d).tar.gz /opt/gts/.env /opt/gts/scripts/
```

### 8. Security Considerations

#### File Permissions
```bash
# Secure sensitive files
chmod 600 /opt/gts/.env
chmod 644 /opt/gts/scripts/*.sh
```

#### Firewall
```bash
# Allow only necessary ports
sudo ufw allow 8000/tcp  # API port
sudo ufw allow 22/tcp    # SSH
sudo ufw --force enable
```

#### SSL/TLS
```bash
# Use reverse proxy (nginx) for SSL termination
sudo apt install nginx -y
# Configure nginx with SSL certificates
```

### 9. Troubleshooting

#### Common Issues

**Services not starting:**
```bash
# Check logs
tail -f /var/log/gts/*.log

# Check environment
source venv/bin/activate && python -c "import os; print(os.environ.get('DATABASE_URL'))"
```

**Database connection errors:**
```bash
# Test connection
psql $DATABASE_URL -c "SELECT 1"
```

**Permission errors:**
```bash
# Fix permissions
sudo chown -R $USER:$USER /opt/gts
sudo chown -R $USER:$USER /var/log/gts
```

#### Performance Tuning
```bash
# Monitor resource usage
top -p $(cat /var/run/incident_monitor.pid)

# Adjust Python settings in .env
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=30
```

### 10. Maintenance

#### Update Procedure
```bash
# Stop services
./stop_incident_system.sh

# Update code
git pull  # or redeploy

# Install new dependencies
source venv/bin/activate
pip install -r requirements.txt

# Run tests
python test_incident_system.py

# Start services
./start_incident_system.sh
```

#### Monitoring Dashboard
- Use Grafana/Prometheus for metrics
- Set up alerts for service downtime
- Monitor incident creation rates

---

## 📞 Support

For production issues:
- Check logs: `tail -f /var/log/gts/*.log`
- Restart services: `./stop_incident_system.sh && ./start_incident_system.sh`
- Contact: operations@gabanilogistics.com

## ✅ Deployment Checklist

- [ ] Server provisioned with required specs
- [ ] Dependencies installed
- [ ] Code deployed to `/opt/gts`
- [ ] Environment configured
- [ ] Database accessible
- [ ] Services started successfully
- [ ] Health checks passing
- [ ] Monitoring configured
- [ ] Backups scheduled
- [ ] Security hardened
- [ ] Team notified of deployment