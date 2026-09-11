#!/usr/bin/env bash
# ==============================================================================
# PROJECT ULTRON — UFW FIREWALL HARDENING SCRIPT
# ==============================================================================

set -euo pipefail

echo "🛡️ Hardening Firewall (UFW) for ULTRON Production..."

# Reset default rules
ufw --force reset
ufw default deny incoming
ufw default allow outgoing

# Allow standard SSH (port 22)
ufw allow 22/tcp comment 'SSH'

# Allow HTTP and HTTPS
ufw allow 80/tcp comment 'HTTP'
ufw allow 443/tcp comment 'HTTPS'

# Explicitly block sensitive backend ports from external interface
ufw deny 3306/tcp comment 'MySQL - Internal Only'
ufw deny 6379/tcp comment 'Redis - Internal Only'
ufw deny 8000/tcp comment 'FastAPI - Proxy Only'
ufw deny 9222/tcp comment 'Playwright Debug - Internal Only'

# Enable firewall
ufw --force enable

echo "✅ UFW Firewall Hardened and Active."
ufw status verbose
