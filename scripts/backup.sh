#!/bin/bash
# Database Backup Script
# Creates daily backups and maintains retention policy

set -e

BACKUP_DIR="${1:-.}"
RETENTION_DAYS="${2:-30}"
DATABASE_URL="${DATABASE_URL:-}"
LOG_FILE="${BACKUP_DIR}/backup_$(date +%Y%m%d).log"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}" | tee -a "$LOG_FILE"
    exit 1
}

success() {
    echo -e "${GREEN}[SUCCESS] $1${NC}" | tee -a "$LOG_FILE"
}

# Validate inputs
if [ -z "$DATABASE_URL" ]; then
    error "DATABASE_URL environment variable not set"
fi

if [ ! -d "$BACKUP_DIR" ]; then
    error "Backup directory does not exist: $BACKUP_DIR"
fi

# Create backup
BACKUP_FILE="$BACKUP_DIR/gts_backup_$(date +%Y%m%d_%H%M%S).sql"

log "Starting database backup..."
log "Database URL: ${DATABASE_URL:0:50}..."
log "Backup file: $BACKUP_FILE"

if pg_dump "$DATABASE_URL" > "$BACKUP_FILE"; then
    log "Backup created successfully"
    
    # Compress backup
    gzip "$BACKUP_FILE"
    BACKUP_FILE="${BACKUP_FILE}.gz"
    
    FILE_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    log "Compressed backup size: $FILE_SIZE"
    success "✅ Backup completed: $BACKUP_FILE"
else
    error "Failed to create backup"
fi

# Cleanup old backups
log ""
log "Cleaning up backups older than $RETENTION_DAYS days..."

DELETED_COUNT=0
while IFS= read -r -d '' file; do
    rm "$file"
    DELETED_COUNT=$((DELETED_COUNT + 1))
    log "Deleted: $file"
done < <(find "$BACKUP_DIR" -name "gts_backup_*.sql.gz" -mtime +$RETENTION_DAYS -print0)

log "Deleted $DELETED_COUNT old backup files"

# Backup statistics
log ""
log "📊 Backup Statistics:"
log "Total backups: $(ls -1 "$BACKUP_DIR"/gts_backup_*.sql.gz 2>/dev/null | wc -l)"
log "Total size: $(du -sh "$BACKUP_DIR" | cut -f1)"
log "Retention period: $RETENTION_DAYS days"

success "✅ Backup process completed successfully"
