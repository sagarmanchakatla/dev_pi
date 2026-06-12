#!/bin/bash
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR=/opt/platform-api/backups
mkdir -p $BACKUP_DIR
echo "[$TIMESTAMP] Backup started" >> /var/log/platform-backup.log
cp /opt/platform-api/server.py $BACKUP_DIR/server.py.$TIMESTAMP
echo "[$TIMESTAMP] Backup completed" >> /var/log/platform-backup.log
