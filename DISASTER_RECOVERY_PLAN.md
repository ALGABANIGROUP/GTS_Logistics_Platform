# Backup & Disaster Recovery Plan

## 🎯 Objectives

**Recovery Time Objective (RTO):** < 4 hours  
**Recovery Point Objective (RPO):** < 1 hour  
**Availability Target:** 99.9% uptime (8.76 hours downtime/year)

---

## 📦 Backup Strategy

### 1. Database Backups

#### Daily Automated Backups
```bash
# Backup script: backup_database.sh
#!/bin/bash

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/database"
DB_NAME="gts_production"

# Create backup
pg_dump $DATABASE_URL > $BACKUP_DIR/gts_db_$TIMESTAMP.sql

# Compress
gzip $BACKUP_DIR/gts_db_$TIMESTAMP.sql

# Upload to S3 (or cloud storage)
aws s3 cp $BACKUP_DIR/gts_db_$TIMESTAMP.sql.gz \
  s3://gts-backups/database/ \
  --storage-class STANDARD_IA

# Cleanup local backups older than 7 days
find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete

echo "Backup completed: gts_db_$TIMESTAMP.sql.gz"
```

**Schedule:** Daily at 3:00 AM UTC (low traffic period)  
**Retention Policy:**
- Daily: Keep 7 days
- Weekly: Keep 4 weeks
- Monthly: Keep 12 months

#### Point-in-Time Recovery (PostgreSQL WAL)
```bash
# Enable WAL archiving in postgresql.conf
wal_level = replica
archive_mode = on
archive_command = 'aws s3 cp %p s3://gts-backups/wal/%f'
```

**Benefit:** Restore to any point within last 7 days

### 2. Application Code Backups

**Strategy:** Git repository with multiple remotes

```bash
# Primary: GitHub
git remote add github git@github.com:gts/logistics.git

# Backup: GitLab
git remote add gitlab git@gitlab.com:gts/logistics.git

# Backup: Bitbucket
git remote add bitbucket git@bitbucket.org:gts/logistics.git

# Push to all remotes
git push --all github gitlab bitbucket
```

### 3. Uploaded Files Backup

#### User-Generated Content (PDFs, images, documents)
```bash
# Sync to S3 bucket with versioning enabled
aws s3 sync /var/www/gts/uploads/ \
  s3://gts-uploads/ \
  --storage-class INTELLIGENT_TIERING

# Enable versioning on S3 bucket
aws s3api put-bucket-versioning \
  --bucket gts-uploads \
  --versioning-configuration Status=Enabled
```

**Schedule:** Continuous sync (every 15 minutes)  
**Retention:** Versions kept for 90 days

### 4. Configuration Backups

#### Environment Variables & Secrets
```bash
# Backup script: backup_config.sh
#!/bin/bash

TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Export environment variables (encrypted)
env | grep GTS_ | gpg --encrypt --recipient admin@gts.com \
  > /backups/config/env_$TIMESTAMP.gpg

# Backup Docker/Kubernetes configs
kubectl get configmap gts-config -o yaml \
  > /backups/config/k8s_config_$TIMESTAMP.yaml

# Upload to secure storage
aws s3 cp /backups/config/ s3://gts-backups/config/ --recursive
```

**Schedule:** Daily + after any config change  
**Security:** Encrypted with GPG

---

## 🔄 Disaster Recovery Procedures

### Scenario 1: Database Corruption/Loss

**Symptoms:**
- Database connection failures
- Data inconsistencies
- Query errors

**Recovery Steps:**
```bash
# 1. Stop application to prevent further corruption
systemctl stop gts-backend

# 2. Assess damage
psql $DATABASE_URL -c "SELECT version();"
# If connection fails, proceed to restore

# 3. Create new database (if needed)
createdb gts_production_new

# 4. Restore from latest backup
LATEST_BACKUP=$(aws s3 ls s3://gts-backups/database/ | tail -1 | awk '{print $4}')
aws s3 cp s3://gts-backups/database/$LATEST_BACKUP /tmp/restore.sql.gz
gunzip /tmp/restore.sql.gz
psql gts_production_new < /tmp/restore.sql

# 5. Verify data integrity
psql gts_production_new -c "SELECT COUNT(*) FROM users;"
psql gts_production_new -c "SELECT COUNT(*) FROM loads;"

# 6. Update connection string
export DATABASE_URL=postgresql://...gts_production_new

# 7. Restart application
systemctl start gts-backend

# 8. Verify application health
curl https://api.gts.com/healthz
```

**RTO:** 2-3 hours  
**RPO:** < 24 hours (daily backup)

### Scenario 2: Complete Server Failure

**Symptoms:**
- Server unreachable
- All services down
- SSH connection timeout

**Recovery Steps:**
```bash
# 1. Provision new server (AWS EC2, Render, etc.)
# Use infrastructure-as-code (Terraform/CloudFormation)

# 2. Install dependencies
sudo apt-get update
sudo apt-get install -y python3.11 postgresql-client nginx

# 3. Clone repository
git clone https://github.com/gts/logistics.git /opt/gts
cd /opt/gts

# 4. Restore environment variables
aws s3 cp s3://gts-backups/config/env_latest.gpg /tmp/
gpg --decrypt /tmp/env_latest.gpg > /opt/gts/.env

# 5. Restore database (see Scenario 1)

# 6. Restore uploaded files
aws s3 sync s3://gts-uploads/ /var/www/gts/uploads/

# 7. Install application
cd /opt/gts/backend
pip install -r requirements.txt

# 8. Start services
systemctl start gts-backend
systemctl start gts-frontend
systemctl start nginx

# 9. Update DNS (if IP changed)
# Update A/AAAA records to point to new server

# 10. Verify recovery
curl https://api.gts.com/healthz
curl https://gts.com
```

**RTO:** 4-6 hours  
**RPO:** < 24 hours

### Scenario 3: Data Center / Region Failure

**Symptoms:**
- Entire AWS region down
- All services in region unavailable

**Recovery Steps:**
```bash
# Prerequisites: Multi-region setup
# - Database replica in secondary region
# - Application deployed in secondary region
# - DNS configured for automatic failover

# 1. Verify secondary region operational
curl https://api-backup.gts.com/healthz

# 2. Promote database replica to primary
# PostgreSQL:
pg_ctl promote -D /var/lib/postgresql/data

# 3. Update DNS to point to secondary region
# CloudFlare, Route53, or DNS provider:
# Change A record from primary IP to secondary IP

# 4. Verify failover
dig api.gts.com +short
# Should show new IP

curl https://api.gts.com/healthz
# Should return 200 OK from secondary region

# 5. Monitor for 24 hours
# Watch for any issues with secondary region

# 6. When primary region recovers
# Replicate data back to primary
# Restore as primary when stable
```

**RTO:** 1-2 hours (automated failover)  
**RPO:** < 5 minutes (streaming replication)

### Scenario 4: Ransomware / Security Breach

**Symptoms:**
- Encrypted files
- Unusual database modifications
- Unauthorized access detected

**Recovery Steps:**
```bash
# 1. IMMEDIATELY isolate affected systems
# Disconnect from network, revoke all access tokens

# 2. Assess scope of breach
# Check logs for entry point and affected data

# 3. Restore from clean backup BEFORE breach
# Identify last known-good backup timestamp
CLEAN_BACKUP="gts_db_20260201_030000.sql.gz"  # Before breach
aws s3 cp s3://gts-backups/database/$CLEAN_BACKUP /tmp/
gunzip /tmp/$CLEAN_BACKUP

# 4. Create new clean environment
# New server, new database, new credentials

# 5. Restore data to new environment
psql $NEW_DATABASE_URL < /tmp/gts_db_20260201_030000.sql

# 6. Rotate ALL credentials
# Database passwords, JWT secrets, API keys, SSH keys

# 7. Apply security patches
# Update all packages, fix vulnerabilities

# 8. Implement additional security measures
# WAF rules, enhanced monitoring, 2FA enforcement

# 9. Gradual service restoration
# Start with read-only mode, then full service

# 10. Post-incident analysis
# Document breach, improve security posture
```

**RTO:** 6-24 hours (security investigation required)  
**RPO:** Depends on breach timing (potentially days)

---

## 🧪 Disaster Recovery Testing

### Quarterly DR Drill Schedule

**Q1 (January):** Database restore test
```bash
# 1. Restore latest backup to staging environment
# 2. Verify data integrity
# 3. Run application against restored database
# 4. Document time taken and issues
```

**Q2 (April):** Full system recovery test
```bash
# 1. Simulate complete server failure
# 2. Provision new infrastructure
# 3. Restore all components
# 4. Measure RTO/RPO achieved
```

**Q3 (July):** Multi-region failover test
```bash
# 1. Simulate primary region failure
# 2. Trigger automatic failover
# 3. Verify secondary region takes over
# 4. Restore service to primary
```

**Q4 (October):** Security breach simulation
```bash
# 1. Simulate ransomware attack
# 2. Practice isolation and recovery
# 3. Test backup restoration
# 4. Verify security measures
```

---

## 📊 Backup Verification

### Automated Backup Health Checks

```python
# backup_verification.py
import boto3
import psycopg2
from datetime import datetime, timedelta

def verify_backups():
    s3 = boto3.client('s3')
    
    # Check latest database backup exists
    response = s3.list_objects_v2(
        Bucket='gts-backups',
        Prefix='database/'
    )
    
    latest_backup = max(response['Contents'], key=lambda x: x['LastModified'])
    backup_age = datetime.now() - latest_backup['LastModified']
    
    if backup_age > timedelta(hours=25):
        alert("Database backup is too old!")
        return False
    
    # Check backup file size (should be > 1MB)
    if latest_backup['Size'] < 1024 * 1024:
        alert("Database backup file is suspiciously small!")
        return False
    
    # Test restore to temporary database
    # ... restore logic ...
    
    return True

if __name__ == "__main__":
    verify_backups()
```

**Schedule:** Daily after backup completion  
**Alerts:** Slack/Email if verification fails

---

## 🔔 Alerting & Monitoring

### Critical Alerts

**Backup Failure:**
- Trigger: Backup job fails or times out
- Notification: Email + SMS to on-call engineer
- Response: Manual investigation required

**Backup Too Old:**
- Trigger: No successful backup in 25 hours
- Notification: Email + Slack
- Response: Check backup script and database

**Disk Space Low:**
- Trigger: < 20% free space on backup volume
- Notification: Email
- Response: Cleanup old backups or increase storage

**Database Replication Lag:**
- Trigger: Replica > 5 minutes behind primary
- Notification: Email + Slack
- Response: Check network and replica health

---

## 📋 Backup Inventory

| Data Type | Location | Frequency | Retention | Encryption |
|-----------|----------|-----------|-----------|------------|
| PostgreSQL DB | S3 (us-east-1) | Daily | 7D/4W/12M | AES-256 |
| Uploaded Files | S3 (us-west-2) | 15 minutes | 90 days | AES-256 |
| Application Code | GitHub/GitLab | Continuous | Forever | No |
| Environment Config | S3 (us-east-1) | Daily | 30 days | GPG |
| WAL Logs | S3 (us-east-1) | Continuous | 7 days | AES-256 |
| Server Configs | S3 (us-east-1) | Weekly | 12 months | GPG |

**Total Backup Storage:** ~50 GB  
**Monthly Cost:** ~$5-10 (S3 Standard-IA)

---

## ✅ Recovery Validation Checklist

After any disaster recovery:

- [ ] Database accessible and queries working
- [ ] All tables and data present (row counts match)
- [ ] Application starts without errors
- [ ] Frontend loads and functions correctly
- [ ] Users can log in successfully
- [ ] Bots executing normally
- [ ] WebSocket connections working
- [ ] File uploads/downloads functional
- [ ] API endpoints responding correctly
- [ ] Monitoring and alerts operational
- [ ] Backups resumed on new system
- [ ] Performance metrics within normal range

---

## 📞 Emergency Contacts

**Database Admin:** [Name] - [Phone] - [Email]  
**Infrastructure Lead:** [Name] - [Phone] - [Email]  
**Security Team:** security@gts.com  
**AWS Support:** [Support Case Portal]  
**On-Call Rotation:** [PagerDuty/Opsgenie Link]

---

**Last Tested:** [Date]  
**Next DR Drill:** [Date]  
**Document Owner:** [Name]  
**Last Updated:** February 3, 2026
