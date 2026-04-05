# 🚀 Deployment Guide

This guide details the steps to transition the FailSafe Social API from local development to a live production environment.

## 📦 How to get this live

### 1. Provision the Infrastructure
For a basic scalable deployment, we recommend hosting the Docker containers on a VPS (like DigitalOcean Droplet, AWS EC2, or Azure VM) or a managed container service (like AWS ECS).
- Provision a machine with at least 1GB RAM and 1 CPU core.
- Install Docker and Docker-Compose.

### 2. Configure Environment Variables
On the server, safely create a `.env` file containing the production secrets:
```ini
FLASK_ENV=production
DATABASE_NAME=prod_db
DATABASE_HOST=db.internal.network
DATABASE_PORT=5432
DATABASE_USER=secure_user
DATABASE_PASSWORD=super_secret_password
```

### 3. Deploy 
1. SSH into the production server.
2. Pull the latest release from the main branch.
3. Bring down the old containers and launch the new image:
```bash
docker-compose down
docker-compose up -d --build
```
4. Verify deployment health:
```bash
curl http://localhost:5000/health
```

---

## 🔙 How to Rollback

If a deployment introduces critical bugs that bypass our CI testing, we must immediately roll back to the previous stable state.

### Using Docker Image Tags
If you deploy utilizing tagged images (recommended):
```bash
docker stop failsafe-api
docker run -d --name failsafe-api --restart always failsafe/api:v1.0.1
```

### Using Git Rollback (Emergency Override)
If managing deployment via Git on the VPS:
```bash
# Hard reset to the previous known stable commit
git reset --hard HEAD~1
# Rebuild and relaunch the container
docker-compose up -d --build
```
> **Note:** Rolling back application code does *not* roll back database state or migrations. If a change irreversibly corrupted the database logic, a Point-In-Time recovery from daily PostgreSQL backups must be executed.
