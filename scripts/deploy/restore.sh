#!/usr/bin/env bash
# ==============================================================================
# PROJECT ULTRON — AUTOMATED DATABASE RESTORE SCRIPT
# ==============================================================================

set -euo pipefail

BACKUP_FILE="${1:-}"

if [ -z "$BACKUP_FILE" ] || [ ! -f "$BACKUP_FILE" ]; then
  echo "❌ Error: Please provide a valid backup filepath."
  echo "Usage: ./restore.sh /path/to/backup.sql.gz"
  exit 1
fi

echo "⚠️ Restoring Database from $BACKUP_FILE..."
gunzip -c "$BACKUP_FILE" | docker compose exec -T mysql mysql -u ultron_user -p"$MYSQL_PASSWORD" ultron_prod

echo "✅ Database restore complete!"
