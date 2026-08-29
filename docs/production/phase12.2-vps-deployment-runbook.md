# PROJECT ULTRON — VPS PRODUCTION DEPLOYMENT RUNBOOK

---

## 1. Step-by-Step VPS Setup Runbook

### Step 1: Provision Ubuntu 22.04 LTS VPS
Provision a **4 vCPU / 8 GB RAM / 80 GB SSD** VPS instance (DigitalOcean Droplet or Hetzner CX32).

### Step 2: OS & SSH Hardening
```bash
# Update packages
sudo apt update && sudo apt upgrade -y

# Configure firewall
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### Step 3: Install Docker & Docker Compose
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

### Step 4: Deploy ULTRON Stack
```bash
# Clone repository
git clone https://github.com/org/ultron.git /opt/ultron
cd /opt/ultron

# Set environment
cp .env.production.example .env
nano .env

# Set mandatory production variables:
# ENVIRONMENT=production
# DEBUG=False
# JWT_SECRET=<secure_32_byte_secret>
# MYSQL_PASSWORD=<strong_mysql_password>

# Build and start container stack
docker-compose up --build -d
```

### Step 5: Verification & Health Check Probes
```bash
curl -f http://localhost/health/live
curl -f http://localhost/health/ready
curl -f http://localhost/metrics
```
