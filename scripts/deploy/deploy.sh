#!/usr/bin/env bash
# ==============================================================================
# PROJECT ULTRON — ZERO-DOWNTIME DEPLOYMENT & HEALTH VERIFICATION SCRIPT
# ==============================================================================

set -euo pipefail

echo "🚀 Starting ULTRON Deployment Process..."

ENV_FILE="/opt/ultron/.env.production"
if [ ! -f "$ENV_FILE" ]; then
    ENV_FILE=".env.production"
fi

# 1. Environment validation
if [ ! -f "$ENV_FILE" ]; then
    echo "❌ Error: Production env file not found at $ENV_FILE"
    exit 1
fi

# 2. Build & pull containers
echo "🔨 Building Docker containers..."
docker compose --env-file "$ENV_FILE" build --no-cache

# 3. Start Database & Redis dependencies
echo "🗄️ Launching Database & Redis services..."
docker compose --env-file "$ENV_FILE" up -d mysql redis

# Wait for DB readiness
echo "⏳ Waiting for MySQL database readiness..."
sleep 10

# 4. Run database migrations
echo "🔄 Executing Database Migrations..."
docker compose --env-file "$ENV_FILE" run --rm backend python -m app.database.migrate

# 5. Launch full stack
echo "🚀 Starting full stack..."
docker compose --env-file "$ENV_FILE" up -d

# 6. Verify health & endpoints
echo "🔍 Verifying deployment health..."
sleep 5

HEALTH_URL="http://localhost:8000/health/live"
READINESS_URL="http://localhost:8000/health/ready"

if curl -s -f "$HEALTH_URL" > /dev/null && curl -s -f "$READINESS_URL" > /dev/null; then
    echo "✅ DEPLOYMENT SUCCESSFUL: Live & Ready health checks passed!"
else
    echo "❌ HEALTH CHECK FAILED: Initiating Automatic Rollback!"
    bash ./scripts/deploy/rollback.sh
    exit 1
fi
