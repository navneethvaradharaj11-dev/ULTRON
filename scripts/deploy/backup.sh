#!/usr/bin/env bash
# ==============================================================================
# PROJECT ULTRON — AUTOMATED DATABASE BACKUP SCRIPT
# ==============================================================================

set -euo pipefail

BACKUP_DIR="/opt/ultron/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/ultron_backup_$TIMESTAMP.sql.gz"

mkdir -p "$BACKUP_DIR"

echo "💾 Starting MySQL Database Backup..."
docker compose exec -T mysql mysqldump -u ultron_user -p"$MYSQL_PASSWORD" ultron_prod | gzip > "$BACKUP_FILE"

echo "✅ Backup complete: $BACKUP_FILE"

# Retention policy: keep last 7 days of backups
find "$BACKUP_DIR" -type f -name "ultron_backup_*.sql.gz" -mtime +7 -delete
