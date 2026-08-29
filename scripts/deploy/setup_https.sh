#!/usr/bin/env bash
# ==============================================================================
# PROJECT ULTRON — AUTOMATED DOMAIN & HTTPS (LET'S ENCRYPT) SETUP
# ==============================================================================

set -euo pipefail

DOMAIN="${1:-}"
EMAIL="${2:-admin@$DOMAIN}"

if [ -z "$DOMAIN" ]; then
  echo "❌ Error: Usage: ./setup_https.sh <DOMAIN_NAME> [EMAIL]"
  exit 1
fi

echo "🔒 Provisioning Let's Encrypt SSL Certificate for $DOMAIN..."

# Check certbot installation
if ! command -v certbot &> /dev/null; then
    apt-get update -q && apt-get install -y -q certbot python3-certbot-nginx
fi

# Request certificate
certbot --nginx -d "$DOMAIN" --non-interactive --agree-tos -m "$EMAIL" --redirect

# Test automatic renewal cron
certbot renew --dry-run

echo "✅ HTTPS SSL Certificate configured with auto-renewal for $DOMAIN."
