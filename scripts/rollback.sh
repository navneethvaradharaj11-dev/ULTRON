#!/usr/bin/env bash
set -e

echo "=========================================="
echo "ULTRON PRODUCTION CONTAINER ROLLBACK SCRIPT"
echo "=========================================="

PREVIOUS_TAG="${1:-previous}"

echo "Rolling back Docker stack to tag: ${PREVIOUS_TAG}..."

docker-compose down || true
docker tag ultron-backend:${PREVIOUS_TAG} ultron-backend:latest
docker-compose up -d

echo "Verifying health endpoint after rollback..."
sleep 5
curl -f http://localhost:8000/api/v1/health || {
  echo "ROLLBACK FAILED: Health check failed after rollback!"
  exit 1
}

echo "ROLLBACK SUCCESSFUL!"
