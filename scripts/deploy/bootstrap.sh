#!/usr/bin/env bash
# ==============================================================================
# PROJECT ULTRON — ONE-COMMAND PRODUCTION VPS BOOTSTRAP SCRIPT
# Target OS: Ubuntu 22.04 LTS / 24.04 LTS
# ==============================================================================

set -euo pipefail

echo "=================================================="
echo "🚀 ULTRON PRODUCTION VPS BOOTSTRAP INITIATED"
echo "=================================================="

# 1. Root check
if [ "$EUID" -ne 0 ]; then
  echo "❌ Error: Bootstrap script must be run as root (or via sudo)."
  exit 1
fi

# 2. System updates & essential tools
echo "📦 Updating system packages..."
apt-get update -q && apt-get install -y -q curl git ufw ca-certificates gnupg lsb-release

# 3. Docker installation check
if ! command -v docker &> /dev/null; then
    echo "🐳 Installing Docker Engine..."
    mkdir -p /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
    apt-get update -q
    apt-get install -y -q docker-ce docker-ce-cli containerd.io docker-compose-plugin
else
    echo "✅ Docker Engine is already installed."
fi

# 4. Create deployment directory structure
echo "📁 Setting up production workspace..."
mkdir -p /opt/ultron/backups
mkdir -p /opt/ultron/logs
mkdir -p /opt/ultron/certbot

# 5. Environment & secrets verification
if [ ! -f "/opt/ultron/.env.production" ]; then
    echo "⚠️ Warning: /opt/ultron/.env.production not found."
    echo "Please copy .env.production.example to /opt/ultron/.env.production and populate real secrets."
    exit 1
fi

# 6. Execute UFW Firewall Setup
if [ -f "./scripts/deploy/setup_firewall.sh" ]; then
    echo "🛡️ Configuring Firewall rules..."
    bash ./scripts/deploy/setup_firewall.sh
fi

# 7. Execute Deployment pipeline
echo "🚀 Launching ULTRON Container Stack..."
bash ./scripts/deploy/deploy.sh

echo "=================================================="
echo "✅ ULTRON PRODUCTION VPS BOOTSTRAP COMPLETE"
echo "=================================================="
