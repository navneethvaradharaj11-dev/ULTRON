# PROJECT ULTRON — VPS DEPLOYMENT GUIDE

---

## 1. Prerequisites & Target Specs

* **Operating System**: Ubuntu 22.04 LTS or Ubuntu 24.04 LTS
* **Recommended Specs**: 4 vCPU / 8 GB RAM / 80 GB NVMe SSD (DigitalOcean Droplet or Hetzner Cloud)
* **Domain Name**: Valid A record pointing to target VPS IP address

---

## 2. One-Command VPS Provisioning Instructions

Once SSH access to the VPS is established, execute:

```bash
# 1. Clone ULTRON Repository
git clone https://github.com/your-org/ultron.git /opt/ultron
cd /opt/ultron

# 2. Configure Production Secrets
cp .env.production.example /opt/ultron/.env.production
nano /opt/ultron/.env.production

# 3. Execute Bootstrap Automation Script
sudo bash ./scripts/deploy/bootstrap.sh

# 4. (Optional) Provision SSL Certificate
sudo bash ./scripts/deploy/setup_https.sh your-domain.com admin@your-domain.com
```
