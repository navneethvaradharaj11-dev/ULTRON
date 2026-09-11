# PROJECT ULTRON — PHASE 12.3 REAL CLOUD PROVISIONING REQUIREMENTS

---

## 1. Cloud Infrastructure Provisioning Request

> **Status**: **`CLOUD PROVISIONING REQUIRED`**  
> **Reason**: Real cloud VPS deployment cannot proceed without an active cloud server, public IP address, registered domain name, and SSH access credentials.

---

## 2. Infrastructure Requirements Checklist

To deploy PROJECT ULTRON to production, the following resources must be provisioned:

| Requirement Category | Specified Requirement Details |
| :--- | :--- |
| **Cloud Provider** | **DigitalOcean** (Recommended Droplet) or **Hetzner Cloud** |
| **VPS Size / Profile** | **4 vCPU / 8 GB RAM / 80 GB NVMe SSD** |
| **Operating System** | Ubuntu 22.04 LTS (64-bit) |
| **Public Networking** | 1 Dedicated IPv4 Address + IPv6 (optional) |
| **Domain Name / DNS** | Registered domain (e.g., `api.ultron-agent.com`) with `A` record pointing to Public IPv4 |
| **SSL Certificate** | Let's Encrypt TLS Certificate (managed via Certbot or Nginx SSL container) |
| **SSH Key Access** | Public SSH Key added to root/sudo user on VPS |
| **Allowed Inbound Ports** | Port `22` (SSH), Port `80` (HTTP), Port `443` (HTTPS) |

---

## 3. Required Action Steps for Cloud Deployment

Once the VPS Droplet and Domain are purchased:
1. Set DNS `A` record `api.<YOUR-DOMAIN>` -> `<YOUR-VPS-IP>`.
2. Provide SSH login command: `ssh root@<YOUR-VPS-IP>`.
3. Provide production domain name for Nginx SSL binding.
4. Execute `docs/production/phase12.2-vps-deployment-runbook.md`.
