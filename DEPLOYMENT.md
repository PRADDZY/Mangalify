# Mangalify Deployment Guide

Quick reference for deploying Mangalify in production environments.

## 🐳 Docker Deployment (Recommended)

### Prerequisites
- Docker 20.10+
- Docker Compose 1.29+
- `.env` file configured

### Quick Start

```bash
# 1. Clone repository
git clone https://github.com/PRADDZY/Mangalify.git
cd Mangalify

# 2. Configure environment
cp .env.example .env
# Edit .env with your credentials

# 3. Start services
docker-compose up -d

# 4. Check logs
docker logs -f mangalify-bot

# 5. Check health
docker ps --filter name=mangalify
```

### Common Commands

```bash
# Stop services
docker-compose down

# Restart bot only
docker-compose restart mangalify-bot

# View MongoDB logs
docker logs -f mangalify-mongodb

# Execute command in container
docker exec -it mangalify-bot python -c "print('Hello')"

# Update to latest version
git pull origin main
docker-compose build --no-cache
docker-compose up -d
```

### Production Optimizations

1. **Use Docker volumes for persistence**:
   ```yaml
   # Already configured in docker-compose.yml
   volumes:
     - mongodb-data:/data/db
   ```

2. **Enable restart policies**:
   ```yaml
   restart: unless-stopped  # Already set
   ```

3. **Monitor resource usage**:
   ```bash
   docker stats mangalify-bot
   ```

## 🐧 Linux Systemd Deployment

### Prerequisites
- Python 3.11+
- MongoDB installed and running
- System user for bot

### Installation Steps

```bash
# 1. Clone repository
sudo mkdir -p /opt/mangalify
sudo git clone https://github.com/PRADDZY/Mangalify.git /opt/mangalify

# 2. Create bot user
sudo useradd -r -s /bin/false -d /opt/mangalify botuser
sudo chown -R botuser:botuser /opt/mangalify

# 3. Install Python dependencies
cd /opt/mangalify
sudo -u botuser python3 -m venv venv
sudo -u botuser venv/bin/pip install -r requirements.txt

# 4. Configure environment
sudo -u botuser cp .env.example .env
sudo -u botuser nano .env  # Edit with credentials

# 5. Install systemd service
sudo cp mangalify.service /etc/systemd/system/
sudo systemctl daemon-reload

# 6. Enable and start
sudo systemctl enable mangalify
sudo systemctl start mangalify

# 7. Check status
sudo systemctl status mangalify
```

### Common Commands

```bash
# View logs (live)
sudo journalctl -u mangalify -f

# View logs (last 100 lines)
sudo journalctl -u mangalify -n 100

# Restart service
sudo systemctl restart mangalify

# Stop service
sudo systemctl stop mangalify

# Check service status
sudo systemctl status mangalify

# View service configuration
systemctl cat mangalify

# Update to latest version
cd /opt/mangalify
sudo -u botuser git pull origin main
sudo systemctl restart mangalify
```

## ☁️ Cloud Deployment Options

### AWS EC2

1. **Launch EC2 instance** (t3.micro recommended)
2. **Install Docker**:
   ```bash
   sudo yum update -y
   sudo yum install docker -y
   sudo systemctl start docker
   sudo usermod -a -G docker ec2-user
   ```
3. **Follow Docker deployment steps above**

### Google Cloud Run

1. **Build and push image**:
   ```bash
   gcloud builds submit --tag gcr.io/PROJECT_ID/mangalify
   ```
2. **Deploy**:
   ```bash
   gcloud run deploy mangalify \
     --image gcr.io/PROJECT_ID/mangalify \
     --platform managed
   ```

### Azure Container Instances

```bash
az container create \
  --resource-group myResourceGroup \
  --name mangalify \
  --image mangalify:latest \
  --cpu 1 \
  --memory 1
```

### DigitalOcean Droplet

1. **Create Droplet** (Basic plan - $6/month)
2. **Install Docker** using one-click app
3. **Follow Docker deployment steps**

## 🔒 Security Best Practices

### Environment Variables

```bash
# Never commit .env files
echo ".env" >> .gitignore

# Set restrictive permissions
chmod 600 .env
chown botuser:botuser .env  # For systemd
```

### MongoDB Security

```bash
# Use authentication (already configured in docker-compose.yml)
MONGO_USERNAME=admin
MONGO_PASSWORD=strong_random_password_here

# Restrict network access
# In docker-compose.yml, remove ports: if not needed externally
```

### Discord Bot Permissions

Minimal required permissions:
- Send Messages
- Embed Links
- Manage Roles (for birthday role)
- Use Slash Commands

### API Keys

- Rotate keys every 90 days
- Use separate keys for dev/prod
- Monitor usage in provider dashboards

## 📊 Monitoring

### Health Checks

```bash
# Docker health status
docker inspect mangalify-bot --format='{{.State.Health.Status}}'

# Systemd service status
systemctl is-active mangalify

# Check MongoDB connection
docker exec mangalify-mongodb mongosh --eval "db.adminCommand('ping')"
```

### Log Aggregation

**Option 1: JSON logs with ELK Stack**

Set `LOG_FORMAT=json` in `.env`, then ship to Elasticsearch.

**Option 2: Cloud logging**

```bash
# AWS CloudWatch
docker logs -f mangalify-bot | aws logs put-log-events ...

# Google Cloud Logging
gcloud logging write mangalify "Bot started"
```

### Metrics to Monitor

- **Bot uptime**: `systemctl status mangalify` or Docker health
- **Task execution**: Check `scheduler_meta` collection in MongoDB
- **Error rate**: Count ERROR logs per hour
- **API success rate**: Monitor WARNING logs for API failures
- **Memory usage**: `docker stats` or `top`

### Alerting

**Example: Email on service failure** (systemd)

```ini
# /etc/systemd/system/mangalify.service
[Unit]
OnFailure=status-email@%n.service
```

## 🔄 Backup & Recovery

### MongoDB Backups

**Docker**:
```bash
# Backup
docker exec mangalify-mongodb mongodump --out /tmp/backup
docker cp mangalify-mongodb:/tmp/backup ./backup-$(date +%F)

# Restore
docker cp ./backup-2026-01-06 mangalify-mongodb:/tmp/backup
docker exec mangalify-mongodb mongorestore /tmp/backup
```

**Systemd**:
```bash
# Backup
mongodump --uri="mongodb://localhost:27017" --db=mangalify --out=./backup-$(date +%F)

# Restore
mongorestore --uri="mongodb://localhost:27017" --db=mangalify ./backup-2026-01-06
```

### Automated Backups

**Cron job** (runs daily at 2 AM):
```bash
crontab -e
# Add:
0 2 * * * /opt/mangalify/scripts/backup.sh
```

**backup.sh**:
```bash
#!/bin/bash
BACKUP_DIR="/var/backups/mangalify"
DATE=$(date +%F)
docker exec mangalify-mongodb mongodump --out /tmp/backup
docker cp mangalify-mongodb:/tmp/backup "$BACKUP_DIR/backup-$DATE"
# Keep last 7 days
find "$BACKUP_DIR" -type d -mtime +7 -delete
```

## 🚨 Troubleshooting

### Bot Won't Start

```bash
# Check logs
docker logs mangalify-bot
journalctl -u mangalify -xe

# Common issues:
# - Missing environment variables
# - Invalid Discord token
# - MongoDB connection failed
# - Port conflicts
```

### MongoDB Connection Issues

```bash
# Test connection
docker exec mangalify-bot python -c "from motor.motor_asyncio import AsyncIOMotorClient; client = AsyncIOMotorClient('mongodb://mongodb:27017'); print('OK')"

# Check MongoDB is running
docker ps | grep mongodb
systemctl status mongod
```

### API Rate Limits

```bash
# Check logs for rate limit errors
docker logs mangalify-bot | grep "rate limit"

# Solutions:
# - Wait for rate limit reset
# - Upgrade API plan
# - Reduce API call frequency
```

### Memory Issues

```bash
# Check memory usage
docker stats mangalify-bot

# Increase memory limit in docker-compose.yml
deploy:
  resources:
    limits:
      memory: 512M
```

## 📦 Updates & Maintenance

### Updating Bot

```bash
# Docker
cd /path/to/Mangalify
git pull origin main
docker-compose build
docker-compose up -d

# Systemd
cd /opt/mangalify
sudo -u botuser git pull origin main
sudo -u botuser venv/bin/pip install -r requirements.txt
sudo systemctl restart mangalify
```

### Database Maintenance

```bash
# Compact database
docker exec mangalify-mongodb mongosh --eval "db.runCommand({ compact: 'birthdays' })"

# Rebuild indexes
docker exec mangalify-mongodb mongosh mangalify --eval "db.birthdays.reIndex()"

# Check database size
docker exec mangalify-mongodb mongosh --eval "db.stats()"
```

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/PRADDZY/Mangalify/issues)
- **Documentation**: [API Docs](./API.md) | [Contributing](./CONTRIBUTING.md)
- **Discussions**: [GitHub Discussions](https://github.com/PRADDZY/Mangalify/discussions)

---

*Last Updated: January 6, 2026*
