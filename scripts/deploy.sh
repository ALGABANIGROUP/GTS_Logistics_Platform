#!/bin/bash
# Phase 5: Production Deployment Script
# Usage: ./scripts/deploy.sh [environment] [action]

set -e

ENVIRONMENT=${1:-production}
ACTION=${2:-deploy}
LOG_DIR="/var/log/gts"
LOG_FILE="${LOG_DIR}/deploy-${ENVIRONMENT}-$(date +%Y%m%d-%H%M%S).log"
APP_DIR="/app"
BACKUP_DIR="/backups/gts"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Ensure log directory exists
mkdir -p $LOG_DIR
mkdir -p $BACKUP_DIR

# Logging function
log() {
    local level=$1
    shift
    local message="$@"
    local timestamp=$(date +'%Y-%m-%d %H:%M:%S')
    local log_message="[$timestamp] [$level] $message"
    
    case $level in
        "ERROR")
            echo -e "${RED}$log_message${NC}" | tee -a $LOG_FILE
            ;;
        "SUCCESS")
            echo -e "${GREEN}$log_message${NC}" | tee -a $LOG_FILE
            ;;
        "WARNING")
            echo -e "${YELLOW}$log_message${NC}" | tee -a $LOG_FILE
            ;;
        "INFO")
            echo -e "${BLUE}$log_message${NC}" | tee -a $LOG_FILE
            ;;
        *)
            echo "$log_message" | tee -a $LOG_FILE
            ;;
    esac
}

# Error handler
error_exit() {
    local message=$1
    local code=${2:-1}
    log "ERROR" "$message"
    exit $code
}

# ============================================================================
# DEPLOYMENT FUNCTIONS
# ============================================================================

deploy() {
    log "INFO" "🚀 Starting $ENVIRONMENT deployment..."
    
    # 1. Pre-deployment checks
    log "INFO" "1️⃣  Running pre-deployment checks..."
    pre_deployment_checks || error_exit "Pre-deployment checks failed"
    
    # 2. Pull latest code
    log "INFO" "2️⃣  Pulling latest code from repository..."
    pull_code || error_exit "Failed to pull code"
    
    # 3. Backup database
    log "INFO" "3️⃣  Creating database backup..."
    backup_database || error_exit "Failed to backup database"
    
    # 4. Install dependencies
    log "INFO" "4️⃣  Installing dependencies..."
    install_dependencies || error_exit "Failed to install dependencies"
    
    # 5. Run migrations
    log "INFO" "5️⃣  Running database migrations..."
    run_migrations || error_exit "Failed to run migrations"
    
    # 6. Run tests
    log "INFO" "6️⃣  Running tests..."
    run_tests || error_exit "Tests failed"
    
    # 7. Build Docker image
    log "INFO" "7️⃣  Building Docker image..."
    build_docker_image || error_exit "Failed to build Docker image"
    
    # 8. Stop old container
    log "INFO" "8️⃣  Stopping old container..."
    stop_container || true  # Don't fail if container doesn't exist
    
    # 9. Start new container
    log "INFO" "9️⃣  Starting new container..."
    start_container || error_exit "Failed to start container"
    
    # 10. Health check
    log "INFO" "🔟 Running health checks..."
    health_check || error_exit "Health check failed"
    
    log "SUCCESS" "✅ Deployment completed successfully!"
    notify_slack "success"
}

# ============================================================================
# PRE-DEPLOYMENT CHECKS
# ============================================================================

pre_deployment_checks() {
    log "INFO" "Checking Docker installation..."
    command -v docker &> /dev/null || error_exit "Docker not installed"
    
    log "INFO" "Checking Docker daemon..."
    docker info &> /dev/null || error_exit "Docker daemon not running"
    
    log "INFO" "Checking environment configuration..."
    [ -f "$APP_DIR/.env.$ENVIRONMENT" ] || error_exit ".env.$ENVIRONMENT not found"
    
    log "SUCCESS" "Pre-deployment checks passed ✅"
    return 0
}

# ============================================================================
# PULL CODE
# ============================================================================

pull_code() {
    cd $APP_DIR
    
    # Determine branch
    local branch="main"
    if [ "$ENVIRONMENT" = "production" ]; then
        branch="production"
    fi
    
    log "INFO" "Pulling branch: $branch"
    git fetch origin $branch || return 1
    git checkout $branch || return 1
    git pull origin $branch || return 1
    
    log "SUCCESS" "Code pulled successfully ✅"
    return 0
}

# ============================================================================
# BACKUP DATABASE
# ============================================================================

backup_database() {
    local db_url=$(grep DATABASE_URL $APP_DIR/.env.$ENVIRONMENT | cut -d '=' -f 2-)
    local backup_file="$BACKUP_DIR/gts_$(date +%Y%m%d_%H%M%S).sql"
    
    log "INFO" "Creating backup at $backup_file..."
    
    # Extract connection info from DATABASE_URL
    # Format: postgresql+asyncpg://user:password@host:port/database?ssl=require
    if pg_dump "$db_url" > "$backup_file" 2>/dev/null; then
        gzip "$backup_file"
        log "SUCCESS" "Backup created: ${backup_file}.gz ✅"
        
        # Clean old backups (keep last 30 days)
        find $BACKUP_DIR -name "gts_*.sql.gz" -mtime +30 -delete
        log "INFO" "Old backups cleaned (retention: 30 days)"
        
        return 0
    else
        log "ERROR" "Failed to create backup"
        return 1
    fi
}

# ============================================================================
# INSTALL DEPENDENCIES
# ============================================================================

install_dependencies() {
    cd $APP_DIR
    
    log "INFO" "Installing Python dependencies..."
    python -m pip install --upgrade pip || return 1
    pip install -r backend/requirements.txt || return 1
    
    log "INFO" "Installing Node dependencies..."
    npm install --prefix frontend || return 1
    
    log "SUCCESS" "Dependencies installed ✅"
    return 0
}

# ============================================================================
# RUN DATABASE MIGRATIONS
# ============================================================================

run_migrations() {
    cd $APP_DIR
    
    log "INFO" "Running Alembic migrations..."
    python -m alembic -c backend/alembic.ini upgrade head || return 1
    
    log "SUCCESS" "Migrations completed ✅"
    return 0
}

# ============================================================================
# RUN TESTS
# ============================================================================

run_tests() {
    cd $APP_DIR
    
    log "INFO" "Running security tests..."
    python -m pytest tests/test_security.py -v --tb=short || return 1
    
    log "INFO" "Running functional tests..."
    python -m pytest backend/tests/ -v --tb=short || return 1
    
    log "SUCCESS" "Tests passed ✅"
    return 0
}

# ============================================================================
# BUILD DOCKER IMAGE
# ============================================================================

build_docker_image() {
    cd $APP_DIR
    
    local build_date=$(date -u +'%Y-%m-%dT%H:%M:%SZ')
    local git_ref=$(git rev-parse --short HEAD)
    local tag="gts:${ENVIRONMENT}-$(date +%Y%m%d-%H%M%S)"
    local latest_tag="gts:${ENVIRONMENT}-latest"
    
    log "INFO" "Building Docker image: $tag"
    
    docker build \
        -f Dockerfile.production \
        -t "$tag" \
        -t "$latest_tag" \
        --build-arg ENVIRONMENT=$ENVIRONMENT \
        --build-arg BUILD_DATE=$build_date \
        --build-arg VCS_REF=$git_ref \
        . || return 1
    
    log "SUCCESS" "Docker image built: $tag ✅"
    return 0
}

# ============================================================================
# STOP CONTAINER
# ============================================================================

stop_container() {
    local container_name="gts-${ENVIRONMENT}"
    
    if docker ps -a --format '{{.Names}}' | grep -q "^${container_name}$"; then
        log "INFO" "Stopping container: $container_name"
        docker stop "$container_name" || return 1
        docker rm "$container_name" || return 1
        log "SUCCESS" "Container stopped ✅"
    else
        log "INFO" "No running container found"
    fi
    
    return 0
}

# ============================================================================
# START CONTAINER
# ============================================================================

start_container() {
    local container_name="gts-${ENVIRONMENT}"
    local port=$([ "$ENVIRONMENT" = "production" ] && echo "8000" || echo "8001")
    local env_file="$APP_DIR/.env.$ENVIRONMENT"
    
    log "INFO" "Starting container: $container_name on port $port"
    
    docker run -d \
        --name "$container_name" \
        --env-file "$env_file" \
        --volume /data/gts:/data \
        --volume $LOG_DIR:/app/logs \
        --network prod-network \
        -p "$port":8000 \
        --restart=unless-stopped \
        --log-driver=json-file \
        --log-opt max-size=10m \
        --log-opt max-file=3 \
        "gts:${ENVIRONMENT}-latest" || return 1
    
    log "SUCCESS" "Container started ✅"
    return 0
}

# ============================================================================
# HEALTH CHECK
# ============================================================================

health_check() {
    local port=$([ "$ENVIRONMENT" = "production" ] && echo "8000" || echo "8001")
    local max_attempts=30
    local attempt=0
    
    log "INFO" "Running health checks on port $port..."
    
    while [ $attempt -lt $max_attempts ]; do
        if curl -sf "http://localhost:$port/health" > /dev/null 2>&1; then
            log "SUCCESS" "✅ Health check passed!"
            return 0
        fi
        
        attempt=$((attempt + 1))
        log "INFO" "Health check attempt $attempt/$max_attempts..."
        sleep 2
    done
    
    log "ERROR" "Health check failed after $max_attempts attempts"
    return 1
}

# ============================================================================
# ROLLBACK
# ============================================================================

rollback() {
    log "WARNING" "🔄 Rolling back to previous version..."
    
    local container_name="gts-${ENVIRONMENT}"
    
    # Get previous image
    local previous_image=$(docker image ls "gts:${ENVIRONMENT}-*" --format "{{.Repository}}:{{.Tag}}" | tail -2 | head -1)
    
    if [ -z "$previous_image" ]; then
        error_exit "No previous image found for rollback"
    fi
    
    log "INFO" "Stopping current container..."
    docker stop "$container_name" || true
    docker rm "$container_name" || true
    
    log "INFO" "Starting previous version: $previous_image"
    docker run -d \
        --name "$container_name" \
        --env-file "$APP_DIR/.env.$ENVIRONMENT" \
        --volume /data/gts:/data \
        --volume $LOG_DIR:/app/logs \
        --network prod-network \
        -p $([ "$ENVIRONMENT" = "production" ] && echo "8000" || echo "8001"):8000 \
        --restart=unless-stopped \
        "$previous_image" || error_exit "Failed to start previous image"
    
    log "SUCCESS" "Rollback completed ✅"
    health_check || error_exit "Health check failed after rollback"
}

# ============================================================================
# LOGS
# ============================================================================

show_logs() {
    local container_name="gts-${ENVIRONMENT}"
    
    log "INFO" "Showing logs for: $container_name"
    docker logs -f "$container_name"
}

# ============================================================================
# STATUS
# ============================================================================

status() {
    local container_name="gts-${ENVIRONMENT}"
    
    log "INFO" "Container Status:"
    docker ps -a --filter "name=$container_name" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    
    log "INFO" "Recent Logs:"
    docker logs --tail 20 "$container_name" 2>/dev/null || log "WARNING" "No logs available"
}

# ============================================================================
# SLACK NOTIFICATION
# ============================================================================

notify_slack() {
    local status=$1
    local webhook_url=$(grep SLACK_WEBHOOK_URL $APP_DIR/.env.$ENVIRONMENT | cut -d '=' -f 2-)
    
    if [ -z "$webhook_url" ]; then
        return 0  # Skip if webhook not configured
    fi
    
    local emoji=$([ "$status" = "success" ] && echo "✅" || echo "❌")
    local color=$([ "$status" = "success" ] && echo "good" || echo "danger")
    
    curl -X POST -H 'Content-type: application/json' \
        --data "{
            \"text\": \"$emoji GTS $ENVIRONMENT Deployment\",
            \"attachments\": [{
                \"color\": \"$color\",
                \"fields\": [
                    {\"title\": \"Environment\", \"value\": \"$ENVIRONMENT\", \"short\": true},
                    {\"title\": \"Status\", \"value\": \"$status\", \"short\": true},
                    {\"title\": \"Time\", \"value\": \"$(date)\", \"short\": false}
                ]
            }]
        }" \
        $webhook_url 2>/dev/null || true
}

# ============================================================================
# MAIN
# ============================================================================

case $ACTION in
    deploy)
        deploy
        ;;
    rollback)
        rollback
        ;;
    logs)
        show_logs
        ;;
    status)
        status
        ;;
    *)
        echo "Usage: $0 [environment] [action]"
        echo ""
        echo "Environments:"
        echo "  staging       - Staging environment (default port 8001)"
        echo "  production    - Production environment (default port 8000)"
        echo ""
        echo "Actions:"
        echo "  deploy        - Deploy application (default)"
        echo "  rollback      - Rollback to previous version"
        echo "  logs          - Show container logs"
        echo "  status        - Show deployment status"
        echo ""
        echo "Examples:"
        echo "  $0 production deploy"
        echo "  $0 staging logs"
        echo "  $0 production rollback"
        exit 1
        ;;
esac
