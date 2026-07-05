#!/bin/bash
set -euo pipefail

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR=/opt/platform-api/backups
LOG_FILE=/var/log/platform-backup.log
DB_NAME=platform_api
DB_USER=platform
RETENTION_DAYS=7

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "Starting backup: $TIMESTAMP"

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Run backup
BACKUP_FILE="$BACKUP_DIR/${DB_NAME}_${TIMESTAMP}.dump"

if pg_dump -U "$DB_USER" -h localhost -Fc "$DB_NAME" > "$BACKUP_FILE"; then
    SIZE=$(du -sh "$BACKUP_FILE" | cut -f1)
    log "Backup completed: $BACKUP_FILE ($SIZE)"
else
    log "ERROR: Backup failed"
    exit 1
fi

# Remove backups older than retention period
find "$BACKUP_DIR" -name "*.dump" -mtime +$RETENTION_DAYS -delete
log "Cleaned up backups older than $RETENTION_DAYS days"

# List current backups
log "Current backups:"
ls -lh "$BACKUP_DIR"/*.dump 2>/dev/null | tee -a "$LOG_FILE"

log "Backup complete"
