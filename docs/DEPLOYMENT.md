# 🚀 MarketMind AI - Deployment Guide

Complete guide for deploying MarketMind AI to production environments.

## Table of Contents

- [Pre-Deployment Checklist](#pre-deployment-checklist)
- [Infrastructure Requirements](#infrastructure-requirements)
- [Deployment Options](#deployment-options)
- [Environment Configuration](#environment-configuration)
- [Security Hardening](#security-hardening)
- [Monitoring & Logging](#monitoring--logging)
- [Scaling Strategies](#scaling-strategies)
- [Troubleshooting](#troubleshooting)

---

## Pre-Deployment Checklist

### Code Readiness

- [ ] All tests passing (`pytest tests/`)
- [ ] Code linted (`flake8 app/`)
- [ ] Type checking clean (`mypy app/`)
- [ ] Documentation updated
- [ ] No hardcoded secrets or API keys
- [ ] `.gitignore` properly configured
- [ ] Version tagged (`git tag v2.0.0`)

### Infrastructure Readiness

- [ ] Redis instance provisioned
- [ ] SSL certificates obtained
- [ ] Domain name configured
- [ ] API keys acquired (Nebius, ScrapeGraph)
- [ ] Monitoring tools setup
- [ ] Backup strategy defined
- [ ] Disaster recovery plan documented

### Security Readiness

- [ ] Environment variables secured
- [ ] Firewall rules configured
- [ ] Rate limiting enabled
- [ ] HTTPS enforced
- [ ] API authentication implemented (if public)
- [ ] Security headers configured
- [ ] Vulnerability scan completed

---

## Infrastructure Requirements

### Minimum Production Requirements

| Resource | Minimum | Recommended | Notes |
|----------|---------|-------------|-------|
| **CPU** | 2 cores | 4 cores | Per instance |
| **RAM** | 2 GB | 4 GB | Per instance |
| **Disk** | 20 GB | 50 GB | SSD preferred |
| **Redis** | 1 GB | 2 GB | Separate instance |
| **Network** | 100 Mbps | 1 Gbps | Bandwidth |

### Supported Platforms

- ✅ **AWS** (EC2, ECS, Lambda)
- ✅ **Google Cloud** (Compute Engine, Cloud Run)
- ✅ **Azure** (VMs, Container Instances)
- ✅ **DigitalOcean** (Droplets, App Platform)
- ✅ **Heroku** (Standard dyno)
- ✅ **Docker** (Any Docker host)
- ✅ **Kubernetes** (Any K8s cluster)

---

## Deployment Options

### Option 1: Docker Deployment (Recommended)

#### Create Dockerfile

```dockerfile
# Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8080/health')"

# Run application
CMD ["python", "run.py"]
```

#### Create docker-compose.yml

```yaml
version: '3.8'

services:
  marketmind:
    build: .
    ports:
      - "8080:8080"
    environment:
      - NEBIUS_API_KEY=${NEBIUS_API_KEY}
      - SMARTCRAWLER_API_KEY=${SMARTCRAWLER_API_KEY}
      - REDIS_URL=redis://redis:6379/0
      - RATE_LIMIT_PER_USER=3
      - RATE_LIMIT_PLATFORM=200
      - CACHE_TTL_DAYS=7
    depends_on:
      - redis
    restart: unless-stopped
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped
    command: redis-server --appendonly yes

volumes:
  redis_data:
```

#### Deploy with Docker Compose

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f marketmind

# Stop services
docker-compose down

# Update and restart
docker-compose pull
docker-compose up -d --build
```

---

### Option 2: AWS Deployment

#### EC2 Deployment

```bash
# 1. Launch EC2 instance (Ubuntu 22.04, t3.medium)

# 2. SSH into instance
ssh -i your-key.pem ubuntu@your-ec2-ip

# 3. Install dependencies
sudo apt update
sudo apt install -y python3.11 python3-pip redis-server git

# 4. Clone repository
git clone https://github.com/yourusername/marketmind-ai.git
cd marketmind-ai

# 5. Setup virtual environment
python3.11 -m venv venv
source venv/bin/activate

# 6. Install Python dependencies
pip install -r requirements.txt

# 7. Configure environment
cp api.env.example api.env
nano api.env  # Add your API keys

# 8. Start Redis
sudo systemctl start redis
sudo systemctl enable redis

# 9. Run with systemd (see systemd section)
```

#### Create systemd service

```ini
# /etc/systemd/system/marketmind.service
[Unit]
Description=MarketMind AI Agent
After=network.target redis.service
Requires=redis.service

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/marketmind-ai
Environment="PATH=/home/ubuntu/marketmind-ai/venv/bin"
EnvironmentFile=/home/ubuntu/marketmind-ai/api.env
ExecStart=/home/ubuntu/marketmind-ai/venv/bin/python run.py
Restart=always
RestartSec=10

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=marketmind

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable marketmind
sudo systemctl start marketmind

# Check status
sudo systemctl status marketmind

# View logs
sudo journalctl -u marketmind -f
```

---

### Option 3: Kubernetes Deployment

#### Create Kubernetes manifests

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: marketmind
  labels:
    app: marketmind
spec:
  replicas: 3
  selector:
    matchLabels:
      app: marketmind
  template:
    metadata:
      labels:
        app: marketmind
    spec:
      containers:
      - name: marketmind
        image: yourregistry/marketmind:2.0.0
        ports:
        - containerPort: 8080
        env:
        - name: NEBIUS_API_KEY
          valueFrom:
            secretKeyRef:
              name: marketmind-secrets
              key: nebius-api-key
        - name: SMARTCRAWLER_API_KEY
          valueFrom:
            secretKeyRef:
              name: marketmind-secrets
              key: smartcrawler-api-key
        - name: REDIS_URL
          value: "redis://redis-service:6379/0"
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 10
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: marketmind-service
spec:
  selector:
    app: marketmind
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8080
  type: LoadBalancer
---
apiVersion: v1
kind: Secret
metadata:
  name: marketmind-secrets
type: Opaque
data:
  nebius-api-key: <base64-encoded-key>
  smartcrawler-api-key: <base64-encoded-key>
```

```bash
# Deploy to Kubernetes
kubectl apply -f k8s/

# Check deployment
kubectl get deployments
kubectl get pods
kubectl get services

# View logs
kubectl logs -f deployment/marketmind

# Scale deployment
kubectl scale deployment/marketmind --replicas=5
```

---

### Option 4: Serverless Deployment (AWS Lambda)

**Note**: Lambda has limitations (15-minute timeout, cold starts). Consider for light usage only.

```python
# lambda_handler.py
import json
from app.agent import SmartGTMAgent
from sentient_agent_framework import DefaultServer

agent = SmartGTMAgent()

def lambda_handler(event, context):
    """AWS Lambda handler"""
    # Parse request
    body = json.loads(event['body'])
    
    # Process request (simplified)
    # Note: Implement proper async handling for production
    
    return {
        'statusCode': 200,
        'body': json.dumps({'status': 'processing'})
    }
```

---

## Environment Configuration

### Production Environment Variables

```bash
# Required
NEBIUS_API_KEY=prod_sk_xxxxxxxxxxxxx
SMARTCRAWLER_API_KEY=prod_sg_xxxxxxxxxxxxx
REDIS_URL=redis://:password@prod-redis.example.com:6379/0

# Rate Limiting (tune for production)
RATE_LIMIT_PER_USER=10       # Higher for paid users
RATE_LIMIT_PLATFORM=1000     # Scale with infrastructure

# Caching
CACHE_TTL_DAYS=14            # Longer cache for production

# Logging
LOG_LEVEL=INFO               # Use INFO or WARNING in production
```

### Redis Production Configuration

```conf
# redis.conf

# Persistence
save 900 1        # Save after 900 seconds if 1 key changed
save 300 10       # Save after 300 seconds if 10 keys changed
save 60 10000     # Save after 60 seconds if 10000 keys changed

appendonly yes
appendfsync everysec

# Memory Management
maxmemory 2gb
maxmemory-policy allkeys-lru

# Security
requirepass your_strong_password_here
bind 127.0.0.1  # Or specific IP

# Performance
tcp-backlog 511
timeout 0
tcp-keepalive 300
```

---

## Security Hardening

### 1. HTTPS/SSL Configuration

#### Using Nginx as Reverse Proxy

```nginx
# /etc/nginx/sites-available/marketmind

upstream marketmind {
    server localhost:8080;
    keepalive 64;
}

server {
    listen 80;
    server_name api.marketmind.ai;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.marketmind.ai;

    # SSL certificates
    ssl_certificate /etc/letsencrypt/live/api.marketmind.ai/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.marketmind.ai/privkey.pem;

    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Security headers
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=31536000" always;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    limit_req zone=api_limit burst=20 nodelay;

    location / {
        proxy_pass http://marketmind;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts for long requests
        proxy_connect_timeout 600s;
        proxy_send_timeout 600s;
        proxy_read_timeout 600s;
    }
}
```

### 2. Firewall Configuration

```bash
# Ubuntu/Debian (UFW)
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# AWS Security Group Rules
Inbound:
- Port 22 (SSH): Your IP only
- Port 80 (HTTP): 0.0.0.0/0
- Port 443 (HTTPS): 0.0.0.0/0
- Port 6379 (Redis): Internal VPC only

Outbound:
- All traffic: 0.0.0.0/0
```

### 3. API Authentication (Recommended)

```python
# app/middleware/auth.py

from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader

API_KEY_HEADER = APIKeyHeader(name="X-API-Key")

async def verify_api_key(api_key: str = Security(API_KEY_HEADER)):
    """Verify API key"""
    valid_keys = settings.API_KEYS  # Load from secure storage
    
    if api_key not in valid_keys:
        raise HTTPException(status_code=403, detail="Invalid API key")
    
    return api_key
```

---

## Monitoring & Logging

### Application Logging

```python
# Configure structured logging for production

import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)

# Apply to handlers
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger.addHandler(handler)
```

### Monitoring Stack

#### Prometheus Metrics

```python
# app/middleware/metrics.py

from prometheus_client import Counter, Histogram, Gauge

# Define metrics
REQUEST_COUNT = Counter('marketmind_requests_total', 'Total requests')
REQUEST_DURATION = Histogram('marketmind_request_duration_seconds', 'Request duration')
ACTIVE_REQUESTS = Gauge('marketmind_active_requests', 'Active requests')
CACHE_HITS = Counter('marketmind_cache_hits_total', 'Cache hits')
CACHE_MISSES = Counter('marketmind_cache_misses_total', 'Cache misses')

# Expose metrics endpoint
from prometheus_client import generate_latest

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

#### Health Check Endpoint

```python
# app/routes/health.py

@app.get("/health")
async def health_check():
    """Comprehensive health check"""
    health_status = {
        "status": "healthy",
        "version": "2.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {}
    }
    
    # Check Redis
    try:
        cache_manager.redis_client.ping()
        health_status["checks"]["redis"] = "connected"
    except:
        health_status["checks"]["redis"] = "disconnected"
        health_status["status"] = "degraded"
    
    # Check LLM service
    try:
        # Quick health check
        health_status["checks"]["llm"] = "available"
    except:
        health_status["checks"]["llm"] = "unavailable"
        health_status["status"] = "degraded"
    
    return health_status
```

---

## Scaling Strategies

### Horizontal Scaling

```yaml
# Load balancer configuration (example)

# Multiple instances behind load balancer
Instance 1: marketmind-1.internal:8080
Instance 2: marketmind-2.internal:8080
Instance 3: marketmind-3.internal:8080

# Shared Redis cluster
Redis Master: redis-master.internal:6379
Redis Replica 1: redis-replica-1.internal:6379
Redis Replica 2: redis-replica-2.internal:6379
```

### Auto-Scaling (Kubernetes)

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: marketmind-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: marketmind
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

---

## Backup & Disaster Recovery

### Redis Backup Strategy

```bash
# Automated backup script

#!/bin/bash
# backup-redis.sh

BACKUP_DIR="/backups/redis"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup
redis-cli --rdb $BACKUP_DIR/dump_$DATE.rdb

# Compress
gzip $BACKUP_DIR/dump_$DATE.rdb

# Upload to S3 (example)
aws s3 cp $BACKUP_DIR/dump_$DATE.rdb.gz s3://your-bucket/redis-backups/

# Delete local backups older than 7 days
find $BACKUP_DIR -name "dump_*.rdb.gz" -mtime +7 -delete

# Cron: 0 2 * * * /path/to/backup-redis.sh
```

---

## Troubleshooting

### Common Production Issues

#### High Memory Usage

```bash
# Check memory usage
docker stats marketmind

# Solution: Increase memory limits or reduce cache size
# In settings.py:
MAX_CONTENT_LENGTH = 5000  # Reduce from 10000
CACHE_TTL_DAYS = 3  # Reduce cache time
```

#### Slow Response Times

```bash
# Check thread count
ps -eLf | grep python | wc -l

# Check Redis latency
redis-cli --latency

# Solution: Increase workers, optimize Redis
```

#### Redis Connection Errors

```bash
# Check Redis status
redis-cli ping

# Check connections
redis-cli CLIENT LIST

# Solution: Increase max connections
# In redis.conf: maxclients 10000
```

---

**For additional support, contact: support@marketmind.ai**
