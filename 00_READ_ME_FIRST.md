# GTS Logistics Platform - Development Setup

## 🚀 Quick Start (Local Development)

### 1. Setting up the virtual environment
```bash
# Create the virtual environment
cd backend
python -m venv .venv

# Activate the environment
.venv\Scripts\activate # Windows
# or
source .venv/bin/activate # Linux/Mac

# Install dependencies
pip install -r ../requirements-simple.txt
```

### 2. Starting the server
```bash
# From the main folder
./start_dev_server.bat # Windows
# or
python backend/main_simple.py # directly
```

### 3. Verifying operation
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Root Endpoint**: http://localhost:8000/

## 📁 Created Files

- `backend/main_simple.py` - Simple Development Server
- `.env` - Environment Variables for Development
- `requirements-simple.txt` - Basic Dependencies
- `start_dev_server.bat` - Server Launcher

## 🔧 Available Features

### Basic Endpoints
- `GET /` - Server Information
- `GET /health` - Health Check
- `GET /docs` - API Documentation
- `GET /ai-bots/status` - AI Status
- `GET /api/v1/reports/summary` - Report Summary

### Database
- **SQLite** for Rapid Development
- No PostgreSQL or Redis Required
- Data stored in `gts_logistics.db`

## 🐳 Docker (if you want to use it later)

### Simple Docker Compose Setup
```yaml
# docker-compose.dev.yml
version: '3.8'
services:

app:

build: .

ports:

- "8000:8000"

env_file:

- .env

volumes:

- ./backend:/app/backend

- ./uploads:/app/uploads

command: uvicorn main_simple:app --host 0.0.0.0 --port 8000 --reload

### Running Docker
```bash
docker-compose -f docker-compose.dev.yml up --build

```

## 🔍 Troubleshooting

### If the server is not working
1. Make sure the virtual environment is enabled
2. Make sure dependencies are installed
3. Check port 8000 (it may be busy)

### If import errors occur
- Some routers may not be available
- This is normal in Simple Development mode
# GTS Logistics Platform - Environment Variables
# Environment Variables File for Local Development

# Database Configuration
DB_PASSWORD=dev_password_123
POSTGRES_PASSWORD=dev_password_123
POSTGRES_USER=gts_user
POSTGRES_DB=gts_logistics

# JWT Security
JWT_SECRET_KEY=dev-jwt-secret-key-change-in-production-32-chars-minimum
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API Keys (Optional - can be left blank for local operation)
OPENAI_API_KEY=
OPENPHONE_API_KEY=
SENTRY_DSN=

# Application Settings
ENVIRONMENT=development
DEBUG=true
APP_VERSION=2.0.0
MAINTENANCE_MODE=false

# CORS Origins (For Local Development)
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000

# Redis Configuration (Optional for Development)
REDIS_URL=redis://localhost:6379
REDIS_HOST=localhost
REDIS_PORT=6379

# Database URL (SQLite for Rapid Development)
DATABASE_URL=sqlite+aiosqlite:///./gts_logistics.db
ASYNC_DATABASE_URL=sqlite+aiosqlite:///./gts_logistics.db

# Upload Settings
MAX_UPLOAD_SIZE=52428800
UPLOAD_DIR=./uploads

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_DEFAULT=100
RATE_LIMIT_AUTH=10
RATE_LIMIT_API=1000
# Logging
LOG_LEVEL=INFO
GTS_LOG_LEVEL=INFO
# OpenAPI Documentation
ENABLE_OPENAPI=true
# Development Settings
VIZION_EYE_ENABLE=false
ENABLE_MEM_SNAPSHOT=false
OPS_MONITOR_ENABLED=false
DISABLE_SCHEDULER=true - The server will work with the base points.

## 📊 Monitoring and Testing

### Health Check
```bash
curl http://localhost:8000/health
```

### API Test
```bash
curl http://localhost:8000/ai-bots/status


## 🔄 Upgrade to Production

When you want to go to production:
1. Change `DATABASE_URL` to PostgreSQL
2. Add Redis for caching
3. Enable real environment variables
4. Use the full `main.py` instead of `main_simple.py`

## 📞 Support

- **Full Documentation**: See `USER_GUIDE.md`

- **Support Training**: See `SUPPORT_TEAM_TRAINING.md`

- **Performance Improvements**: See `PERFORMANCE_SECURITY_IMPROVEMENTS.md`