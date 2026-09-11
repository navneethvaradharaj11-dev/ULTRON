#!/usr/bin/env bash
# ==============================================================================
# PROJECT ULTRON — AUTOMATED ROLLBACK SCRIPT
# ==============================================================================

set -euo pipefail

echo "⚠️ INITIATING ULTRON EMERGENCY ROLLBACK..."

ENV_FILE="/opt/ultron/.env.production"
if [ ! -f "$ENV_FILE" ]; then
    ENV_FILE=".env.production"
fi

# Stop running broken containers
echo "🛑 Stopping current container stack..."
docker compose --env-file "$ENV_FILE" down --remove-orphans

# Restart stable infrastructure
echo "🔄 Restoring previous known-good deployment..."
docker compose --env-file "$ENV_FILE" up -d mysql redis backend worker proxy

echo "✅ ROLLBACK COMPLETED: System restored to base state."
