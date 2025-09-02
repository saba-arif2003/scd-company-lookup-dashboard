# Company Lookup Dashboard - Deployment Guide

This guide covers deploying the Company Lookup Dashboard to various production environments.

## 🎯 Deployment Overview

The application consists of two main components:
- **Backend**: FastAPI application serving REST API
- **Frontend**: React SPA served by Nginx

## 🐳 Docker Deployment (Recommended)

### Production Docker Compose

Create a `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  backend:
    build: 
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DEBUG=false
      - HOST=0.0.0.0
      - PORT=8000
      - SEC_USER_AGENT=Company Lookup Dashboard/1.0 (your-email@example.com)
      - ALLOWED_ORIGINS=["https://yourdomain.com"]
      - ALLOWED_HOSTS=["yourdomain.com","www.yourdomain.com"]
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/health/simple"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "80:80"
      - "443:443"
    environment:
      - VITE_API_BASE_URL=https://api.yourdomain.com/api/v1
    restart: unless-stopped
    depends_on:
      - backend

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - ./logs/nginx:/var/log/nginx
    depends_on:
      - backend
      - frontend
    restart: unless-stopped

  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    restart: unless-stopped
    command: redis-server --appendonly yes

volumes:
  redis-data:

networks:
  default:
    driver: bridge
```

### Deploy with Docker Compose

```bash
# Clone and setup
git clone <repository-url>
cd company-lookup-dashboard

# Setup environment
cp backend/.env.example backend/.env.prod
cp frontend/.env.example frontend/.env.prod

# Edit production environment variables
nano backend/.env.prod
nano frontend/.env.prod

# Deploy
docker-compose -f docker-compose.prod.yml up -d --build

# Verify deployment
docker-compose -f docker-compose.prod.yml ps
docker-compose -f docker-compose.prod.yml logs -f
```

## ☁️ Cloud Deployment

### AWS Deployment

#### Option 1: AWS ECS with Fargate

**1. Create ECS Cluster**
```bash
# Install AWS CLI
aws configure

# Create cluster
aws ecs create-cluster --cluster-name company-lookup-dashboard

# Create task definitions
aws ecs register-task-definition --cli-input-json file://ecs-task-definition.json
```

**ECS Task Definition (`ecs-task-definition.json`):**
```json
{
  "family": "company-lookup-dashboard",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "executionRoleArn": "arn:aws:iam::ACCOUNT:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "backend",
      "image": "your-ecr-repo/company-dashboard-backend:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "DEBUG",
          "value": "false"
        },
        {
          "name": "SEC_USER_AGENT",
          "value": "Company Lookup Dashboard/1.0 (your-email@example.com)"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/company-lookup-dashboard",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    },
    {
      "name": "frontend",
      "image": "your-ecr-repo/company-dashboard-frontend:latest",
      "portMappings": [
        {
          "containerPort": 80,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "VITE_API_BASE_URL",
          "value": "https://api.yourdomain.com/api/v1"
        }
      ]
    }
  ]
}
```

**2. Create ECS Service**
```bash
aws ecs create-service \
  --cluster company-lookup-dashboard \
  --service-name company-dashboard-service \
  --task-definition company-lookup-dashboard \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-12345,subnet-67890],securityGroups=[sg-abcdef],assignPublicIp=ENABLED}"
```

#### Option 2: AWS Elastic Beanstalk

**1. Install EB CLI**
```bash
pip install awsebcli
```

**2. Initialize and Deploy**
```bash
# Initialize Elastic Beanstalk
eb init company-lookup-dashboard --region us-east-1 --platform docker

# Create environment and deploy
eb create production --database.engine postgres

# Deploy updates
eb deploy
```

**Dockerrun.aws.json:**
```json
{
  "AWSEBDockerrunVersion": 2,
  "containerDefinitions": [
    {
      "name": "backend",
      "image": "your-backend-image:latest",
      "memory": 512,
      "portMappings": [
        {
          "hostPort": 8000,
          "containerPort": 8000
        }
      ]
    },
    {
      "name": "frontend",
      "image": "your-frontend-image:latest",
      "memory": 256,
      "portMappings": [
        {
          "hostPort": 80,
          "containerPort": 80
        }
      ]
    }
  ]
}
```

### Google Cloud Platform (GCP)

#### Cloud Run Deployment

**1. Build and Push Images**
```bash
# Configure gcloud
gcloud auth login
gcloud config set project your-project-id

# Build and push backend
cd backend
gcloud builds submit --tag gcr.io/your-project-id/company-dashboard-backend

# Build and push frontend  
cd ../frontend
gcloud builds submit --tag gcr.io/your-project-id/company-dashboard-frontend
```

**2. Deploy to Cloud Run**
```bash
# Deploy backend
gcloud run deploy company-dashboard-backend \
  --image gcr.io/your-project-id/company-dashboard-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars="DEBUG=false,SEC_USER_AGENT=Company Lookup Dashboard/1.0 (your-email@example.com)"

# Deploy frontend
gcloud run deploy company-dashboard-frontend \
  --image gcr.io/your-project-id/company-dashboard-frontend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Azure Deployment

#### Azure Container Instances

**1. Create Resource Group**
```bash
az group create --name company-dashboard-rg --location eastus
```

**2. Deploy Containers**
```bash
# Deploy backend
az container create \
  --resource-group company-dashboard-rg \
  --name company-dashboard-backend \
  --image your-registry/company-dashboard-backend:latest \
  --dns-name-label company-dashboard-api \
  --ports 8000 \
  --environment-variables DEBUG=false SEC_USER_AGENT="Company Lookup Dashboard/1.0 (your-email@example.com)"

# Deploy frontend
az container create \
  --resource-group company-dashboard-rg \
  --name company-dashboard-frontend \
  --image your-registry/company-dashboard-frontend:latest \
  --dns-name-label company-dashboard-web \
  --ports 80
```

## 🖥️ Traditional Server Deployment

### Ubuntu/Debian Server

**1. Server Setup**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3.11 python3.11-venv python3.11-dev \
                    nodejs npm nginx postgresql redis-server \
                    supervisor certbot python3-certbot-nginx

# Create application user
sudo useradd -m -s /bin/bash appuser
sudo su - appuser
```

**2. Backend Deployment**
```bash
# Clone repository
git clone <repository-url> /home/appuser/company-dashboard
cd /home/appuser/company-dashboard/backend

# Setup Python environment
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Setup environment
cp .env.example .env.prod
# Edit .env.prod with production settings

# Test the application
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**3. Frontend Build**
```bash
cd /home/appuser/company-dashboard/frontend

# Install dependencies and build
npm ci --only=production
npm run build

# Copy build files to nginx directory
sudo cp -r dist/* /var/www/company-dashboard/
sudo chown -R www-data:www-data /var/www/company-dashboard/
```

**4. Nginx Configuration**
```nginx
# /etc/nginx/sites-available/company-dashboard
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;
    
    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
    
    # Frontend
    location / {
        root /var/www/company-dashboard;
        index index.html;
        try_files $uri $uri/ /index.html;
        
        # Cache static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
    
    # Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
}
```

**5. SSL Certificate**
```bash
# Generate SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Enable nginx site
sudo ln -s /etc/nginx/sites-available/company-dashboard /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

**6. Process Management with Supervisor**
```ini
# /etc/supervisor/conf.d/company-dashboard.conf
[program:company-dashboard-backend]
command=/home/appuser/company-dashboard/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
directory=/home/appuser/company-dashboard/backend
user=appuser
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/company-dashboard/backend.log
environment=PATH="/home/appuser/company-dashboard/backend/venv/bin"

[program:company-dashboard-worker]
command=/home/appuser/company-dashboard/backend/venv/bin/python -m app.worker
directory=/home/appuser/company-dashboard/backend
user=appuser
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/company-dashboard/worker.log
```

**Start Services:**
```bash
# Create log directory
sudo mkdir -p /var/log/company-dashboard
sudo chown appuser:appuser /var/log/company-dashboard

# Start supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start all
```

## 📊 Production Configuration

### Environment Variables

**Backend Production (.env.prod):**
```bash
# Application
DEBUG=false
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=WARNING

# Security
ALLOWED_ORIGINS=["https://yourdomain.com","https://www.yourdomain.com"]
ALLOWED_HOSTS=["yourdomain.com","www.yourdomain.com"]

# Performance
CACHE_TTL_SECONDS=600
RATE_LIMIT_PER_MINUTE=120
RATE_LIMIT_PER_HOUR=5000

# Monitoring
ENABLE_METRICS=true
SENTRY_DSN=your-sentry-dsn

# Database (if using)
DATABASE_URL=postgresql://user:pass@localhost/company_dashboard

# Redis (if using)
REDIS_URL=redis://localhost:6379/0
```

**Frontend Production (.env.prod):**
```bash
VITE_API_BASE_URL=https://yourdomain.com/api/v1
VITE_APP_ENV=production
VITE_ENABLE_ANALYTICS=true
```

### Monitoring and Logging

**1. Application Monitoring**
```python
# Add to backend/app/main.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

if not settings.DEBUG:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        integrations=[FastApiIntegration()],
        traces_sample_rate=0.1,
    )
```

**2. Health Check Monitoring**
```bash
# Add to crontab for health monitoring
*/5 * * * * curl -f http://localhost:8000/api/v1/health/simple || echo "API is down" | mail -s "Alert: API Down" admin@yourdomain.com
```

**3. Log Rotation**
```bash
# /etc/logrotate.d/company-dashboard
/var/log/company-dashboard/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 appuser appuser
    postrotate
        supervisorctl restart company-dashboard-backend
    endscript
}
```

## 🔒 Security Considerations

### Production Security Checklist

- [ ] **HTTPS**: SSL/TLS certificates installed and configured
- [ ] **Environment Variables**: All secrets in environment variables, not code
- [ ] **CORS**: Restrictive CORS settings for production domains only
- [ ] **Rate Limiting**: Appropriate rate limits configured
- [ ] **Input Validation**: All inputs validated and sanitized
- [ ] **Security Headers**: All security headers configured in Nginx
- [ ] **Firewall**: Only necessary ports open (80, 443, 22)
- [ ] **User Permissions**: Application runs as non-root user
- [ ] **Updates**: Regular security updates applied
- [ ] **Monitoring**: Security monitoring and alerting configured
- [ ] **Backups**: Regular backups of application data and configuration

### Firewall Configuration
```bash
# Ubuntu UFW
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

## 📈 Performance Optimization

### Backend Optimization
- **Workers**: Use multiple uvicorn workers (`--workers 4`)
- **Database**: Connection pooling if using database
- **Caching**: Redis for distributed caching
- **CDN**: CloudFlare or AWS CloudFront for static assets

### Frontend Optimization
- **Bundle Analysis**: Analyze and optimize bundle size
- **CDN**: Serve static assets from CDN
- **Compression**: Gzip/Brotli compression in Nginx
- **Caching**: Aggressive caching for static assets

## 🚨 Monitoring and Alerting

### Key Metrics to Monitor
- **API Response Times**: Average response time < 500ms
- **Error Rates**: Error rate < 1%
- **Uptime**: Target 99.9% uptime
- **External API Status**: Yahoo Finance and SEC API availability
- **System Resources**: CPU, memory, disk usage
- **Security**: Failed login attempts, unusual traffic patterns

### Alerting Rules
```yaml
# Example Prometheus alerting rules
groups:
- name: company-dashboard
  rules:
  - alert: APIHighErrorRate
    expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
    for: 2m
    labels:
      severity: critical
    annotations:
      summary: High error rate detected
      
  - alert: APIHighResponseTime
    expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: High response time detected
```

## 🔄 Backup and Recovery

### Backup Strategy
```bash
#!/bin/bash
# backup-script.sh
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/company-dashboard"

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup application code
tar -czf $BACKUP_DIR/app-$DATE.tar.gz /home/appuser/company-dashboard

# Backup configuration
cp -r /etc/nginx/sites-available/company-dashboard $BACKUP_DIR/nginx-$DATE.conf
cp /home/appuser/company-dashboard/backend/.env.prod $BACKUP_DIR/env-$DATE.backup

# Backup logs
tar -czf $BACKUP_DIR/logs-$DATE.tar.gz /var/log/company-dashboard

# Cleanup old backups (keep 30 days)
find $BACKUP_DIR -type f -mtime +30 -delete

echo "Backup completed: $DATE"
```

### Recovery Procedure
1. **Stop Services**: `sudo supervisorctl stop all`
2. **Restore Code**: Extract backup files
3. **Update Configuration**: Restore environment and nginx config
4. **Test Configuration**: `nginx -t` and test API endpoints
5. **Start Services**: `sudo supervisorctl start all`
6. **Verify**: Check health endpoints and functionality

## 📋 Deployment Checklist

### Pre-Deployment
- [ ] Code reviewed and tested
- [ ] Environment variables configured
- [ ] SSL certificates ready
- [ ] DNS configured
- [ ] Monitoring setup
- [ ] Backup procedures tested

### Deployment
- [ ] Deploy to staging first
- [ ] Run smoke tests
- [ ] Deploy to production
- [ ] Verify all endpoints working
- [ ] Check monitoring dashboards
- [ ] Test from external network

### Post-Deployment
- [ ] Monitor error rates
- [ ] Check performance metrics
- [ ] Verify external integrations
- [ ] Document any issues
- [ ] Update team on deployment status

This completes the comprehensive deployment guide. The application can now be deployed to various environments with proper security, monitoring, and performance optimizations.