# AI Safety Manager Bot - Deployment Guide

## 🚀 Deployment Overview

Complete guide for deploying the AI Safety Manager Bot to production environments.

## 📋 Pre-Deployment Checklist

### Environment Preparation
- [ ] Python 3.9+ installed
- [ ] PostgreSQL database configured
- [ ] Required packages installed (`pip install -r requirements.txt`)
- [ ] Environment variables set (see Configuration section)
- [ ] SSL certificates configured
- [ ] Backup systems operational

### Code Verification
- [ ] All tests passing (`pytest backend/tests/test_safety/ -v`)
- [ ] Code coverage > 80%
- [ ] No security vulnerabilities (bandit scan)
- [ ] No linting errors (pylint)
- [ ] Git repository clean (no uncommitted changes)

### Infrastructure Check
- [ ] Database migrations ready
- [ ] Redis/cache server operational
- [ ] Load balancer configured
- [ ] Monitoring tools installed
- [ ] Logging aggregation ready

## 🔧 Configuration

### Environment Variables

Create `.env` file in project root:

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/gts_safety
ASYNC_DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/gts_safety

# OpenAI API
OPENAI_API_KEY=sk-...
OPENAI_ENABLED=1

# Feature Flags
SAFETY_MANAGER_ENABLED=1
REAL_TIME_MONITORING=1
PREDICTIVE_ANALYTICS=1

# Safety Configuration
INCIDENT_REPORTING_ENABLED=1
COMPLIANCE_CHECK_INTERVAL=3600
INSPECTION_SCHEDULE_INTERVAL=86400
RISK_ASSESSMENT_INTERVAL=7200

# Monitoring
LOG_LEVEL=INFO
SENTRY_DSN=https://...

# Deployment
ENV=production
DEBUG=0
```

### Database Configuration

```python
# backend/database/config.py

SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://user:password@localhost/gts"
)

# Enable connection pooling for production
engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=False,
    pool_size=20,
    max_overflow=0,
    pool_pre_ping=True,
    pool_recycle=3600
)
```

### Logging Configuration

```python
# backend/safety/main.py logging setup

import logging.config

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
        'json': {
            'format': '{"time":"%(asctime)s","level":"%(levelname)s","message":"%(message)s"}'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'standard',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'DEBUG',
            'formatter': 'standard',
            'filename': '/var/log/gts/safety_manager.log',
            'maxBytes': 104857600,  # 100MB
            'backupCount': 10
        },
        'sentry': {
            'class': 'sentry_sdk.integrations.logging.EventHandler',
            'level': 'ERROR'
        }
    },
    'loggers': {
        'backend.safety': {
            'handlers': ['console', 'file', 'sentry'],
            'level': 'INFO',
            'propagate': False
        }
    }
}

logging.config.dictConfig(LOGGING_CONFIG)
```

## 🗄️ Database Setup

### Create Safety Tables

```bash
# Navigate to backend directory
cd backend

# Run migrations
python -m alembic upgrade head

# Verify tables created
python -c "
from backend.database.config import engine
from backend.safety.models import *
import asyncio

async def verify():
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)
    print('Safety tables created successfully')

asyncio.run(verify())
"
```

### Sample Migration File

**File**: `backend/alembic/versions/add_safety_tables.py`

```python
"""add safety tables

Revision ID: abc123def456
Revises: 
Create Date: 2026-01-07 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = 'abc123def456'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'safety_incidents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('incident_id', sa.String(), nullable=False),
        sa.Column('incident_type', sa.String(), nullable=False),
        sa.Column('severity', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('location', sa.String(), nullable=True),
        sa.Column('reporter', sa.String(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('investigation_initiated', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('incident_id')
    )
    
    op.create_table(
        'safety_compliance_records',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('framework', sa.String(), nullable=False),
        sa.Column('compliance_rate', sa.Float(), nullable=False),
        sa.Column('compliant_count', sa.Integer(), nullable=False),
        sa.Column('non_compliant_count', sa.Integer(), nullable=False),
        sa.Column('check_date', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table(
        'safety_inspections',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('inspection_id', sa.String(), nullable=False),
        sa.Column('inspection_type', sa.String(), nullable=False),
        sa.Column('scheduled_date', sa.DateTime(), nullable=False),
        sa.Column('completed_date', sa.DateTime(), nullable=True),
        sa.Column('score', sa.Float(), nullable=True),
        sa.Column('findings', sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('inspection_id')
    )

def downgrade():
    op.drop_table('safety_inspections')
    op.drop_table('safety_compliance_records')
    op.drop_table('safety_incidents')
```

## 🚀 Deployment Process

### Step 1: Pre-Deployment Testing

```bash
# Run all tests
pytest backend/tests/test_safety/ -v

# Check code quality
pylint backend/safety/
bandit -r backend/safety/

# Check security vulnerabilities
safety check

# Run code coverage
pytest backend/tests/test_safety/ --cov=backend.safety --cov-report=term-missing
```

### Step 2: Database Migrations

```bash
# Create backup
pg_dump gts_logistics > backup_$(date +%Y%m%d_%H%M%S).sql

# Run migrations
python -m alembic -c backend/alembic.ini upgrade head

# Verify migrations
python -c "
import asyncio
from backend.database.config import engine

async def verify():
    async with engine.connect() as conn:
        result = await conn.execute(
            'SELECT table_name FROM information_schema.tables WHERE table_schema = \"public\"'
        )
        tables = [row[0] for row in result.fetchall()]
        print(f'Tables created: {len(tables)}')
        for table in tables:
            print(f'  - {table}')

asyncio.run(verify())
"
```

### Step 3: Deploy to Staging

```bash
# Pull latest code
git pull origin main

# Install dependencies
pip install -r requirements.txt --upgrade

# Run tests
pytest backend/tests/test_safety/ -v

# Start safety manager in staging
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Step 4: Smoke Tests

```bash
# Test health endpoint
curl http://staging.gts.local:8000/api/v1/safety/status

# Test authentication
TOKEN=$(curl -X POST http://staging.gts.local:8000/auth/token \
  -d "email=test@test.com&password=password" | jq -r .access_token)

# Test dashboard
curl -H "Authorization: Bearer $TOKEN" \
  http://staging.gts.local:8000/api/v1/safety/dashboard

# Test incident reporting
curl -X POST http://staging.gts.local:8000/api/v1/safety/incidents/report \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "incident_type": "slip_trip_fall",
    "severity": "moderate",
    "description": "Test incident",
    "location": "Test Location",
    "reporter": "Test User"
  }'
```

### Step 5: Deploy to Production

```bash
# Stop existing service
systemctl stop gts-safety-manager

# Pull latest code
git pull origin main

# Install dependencies
pip install -r requirements.txt --upgrade

# Run migrations
python -m alembic -c backend/alembic.ini upgrade head

# Start service
systemctl start gts-safety-manager

# Verify service health
curl http://localhost:8000/api/v1/safety/status

# Monitor logs
journalctl -u gts-safety-manager -f
```

## 🐳 Docker Deployment

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create logs directory
RUN mkdir -p /var/log/gts

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV ENV=production

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/safety/status || exit 1

# Run application
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose

```yaml
version: '3.9'

services:
  safety_manager:
    build: .
    container_name: gts-safety-manager
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://user:password@postgres:5432/gts
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ENV=production
    depends_on:
      - postgres
    volumes:
      - /var/log/gts:/var/log/gts
    restart: unless-stopped

  postgres:
    image: postgres:15
    container_name: gts-postgres
    environment:
      - POSTGRES_USER=gts
      - POSTGRES_PASSWORD=secure_password
      - POSTGRES_DB=gts_logistics
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  postgres_data:
```

### Deploy with Docker Compose

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# Check logs
docker-compose logs -f safety_manager

# Run migrations
docker-compose exec safety_manager python -m alembic upgrade head

# Stop services
docker-compose down
```

## 🔍 Monitoring & Health Checks

### Health Check Endpoint

```python
# Add to backend/routes/health.py
from fastapi import APIRouter, Depends
from backend.security.auth import get_current_user

router = APIRouter(tags=["health"])

@router.get("/api/v1/health/safety")
async def safety_health_check(current_user = Depends(get_current_user)):
    """Health check for safety manager"""
    return {
        "status": "healthy",
        "service": "safety_manager",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }
```

### Monitoring Metrics

```bash
# Monitor response times
curl -w "Response time: %{time_total}s\n" \
  http://localhost:8000/api/v1/safety/dashboard

# Monitor memory usage
ps aux | grep "uvicorn backend.main"

# Monitor database connections
psql -c "SELECT count(*) FROM pg_stat_activity WHERE datname = 'gts_logistics'"
```

### Logging Best Practices

```python
import logging
import json

logger = logging.getLogger(__name__)

# Log incidents
logger.info(json.dumps({
    "event": "incident_reported",
    "incident_id": incident_id,
    "severity": severity,
    "timestamp": datetime.utcnow().isoformat()
}))

# Log errors
logger.error(
    "Incident processing failed",
    extra={
        "incident_id": incident_id,
        "error": str(e),
        "traceback": traceback.format_exc()
    }
)

# Log performance
logger.info(
    "Compliance check completed",
    extra={
        "duration_ms": elapsed_time * 1000,
        "compliance_rate": compliance_rate
    }
)
```

## 🔐 Security Deployment

### SSL/TLS Configuration

```python
# backend/main.py
from fastapi.middleware import HTTPSMiddleware

app.add_middleware(HTTPSMiddleware, enforce_https_redirect=True)
```

### CORS Configuration

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://gts.example.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Rate Limiting

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@router.get("/api/v1/safety/dashboard")
@limiter.limit("100/minute")
async def get_dashboard(request: Request):
    ...
```

## 🚨 Rollback Procedure

### Quick Rollback

```bash
# Stop service
systemctl stop gts-safety-manager

# Rollback code
git revert HEAD

# Rollback database
python -m alembic -c backend/alembic.ini downgrade -1

# Start service
systemctl start gts-safety-manager

# Verify health
curl http://localhost:8000/api/v1/safety/status
```

## ✅ Post-Deployment Verification

- [ ] All API endpoints responding
- [ ] Database connectivity verified
- [ ] Incident reporting working
- [ ] Compliance checks running
- [ ] Background tasks active
- [ ] Logs being collected
- [ ] Monitoring alerts configured
- [ ] Performance baseline established

## 📞 Support

For deployment issues:

1. Check logs: `journalctl -u gts-safety-manager -n 100`
2. Verify database: `psql -c "SELECT COUNT(*) FROM safety_incidents"`
3. Test endpoints: Use provided curl examples
4. Check system resources: `top`, `free -h`, `df -h`

---

**Last Updated**: January 7, 2026
**Deployment Guide v1.0**
