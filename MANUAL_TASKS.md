# Manual Configuration Tasks for Multi-Agent RCA Platform

This document lists all manual configuration steps required to deploy the platform. Follow these steps after automated setup completes.

## 1. Environment Variables Configuration

Create a `.env` file in the project root with the following variables:

```bash
# LLM API Keys (REQUIRED)
OPENAI_API_KEY=sk-your-openai-api-key-here
ANTHROPIC_API_KEY=sk-ant-your-anthropic-api-key-here

# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/rca_platform
DATABASE_TEST_URL=postgresql://username:password@localhost:5432/rca_platform_test

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Vector Database (Qdrant)
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=your-qdrant-api-key  # Optional for local

# Authentication (OAuth2/SSO)
OAUTH2_CLIENT_ID=your-azure-ad-client-id
OAUTH2_CLIENT_SECRET=your-azure-ad-client-secret
OAUTH2_TENANT_ID=your-azure-ad-tenant-id
JWT_SECRET_KEY=generate-random-256-bit-key
JWT_ALGORITHM=RS256

# Object Storage (MinIO/S3)
S3_ENDPOINT=http://localhost:9000
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin
S3_BUCKET_STDF=stdf-files
S3_BUCKET_REPORTS=rca-reports
S3_BUCKET_WAFER_MAPS=wafer-maps

# Application Settings
ENVIRONMENT=development  # development, staging, production
LOG_LEVEL=INFO
API_RATE_LIMIT=100  # requests per minute per user
MAX_CONCURRENT_RCAS=10

# Monitoring
PROMETHEUS_PORT=9090
GRAFANA_ADMIN_PASSWORD=your-secure-password

# Email Notifications (Optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=notifications@company.com
SMTP_PASSWORD=your-smtp-password

# Frontend Configuration
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000
```

## 2. PostgreSQL Database Setup

### Create Database
```bash
# Connect to PostgreSQL
psql -U postgres

# Create database and user
CREATE DATABASE rca_platform;
CREATE USER rca_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE rca_platform TO rca_user;

# Create test database
CREATE DATABASE rca_platform_test;
GRANT ALL PRIVILEGES ON DATABASE rca_platform_test TO rca_user;
```

### Run Migrations
```bash
cd backend
alembic upgrade head
```

## 3. Redis Setup

### Install Redis (if not using Docker)
```bash
# macOS
brew install redis
brew services start redis

# Verify connection
redis-cli ping  # Should return PONG
```

## 4. Vector Database (Qdrant) Setup

### Option A: Docker (Recommended)
```bash
docker run -p 6333:6333 qdrant/qdrant
```

### Option B: Cloud Deployment
1. Sign up at https://cloud.qdrant.io/
2. Create a cluster
3. Copy API URL and API key to .env file

## 5. Object Storage (MinIO) Setup

### Docker Setup
```bash
docker run -p 9000:9000 -p 9001:9001 \
  -e MINIO_ROOT_USER=minioadmin \
  -e MINIO_ROOT_PASSWORD=minioadmin \
  minio/minio server /data --console-address ":9001"
```

### Create Buckets
```bash
# Install MinIO client
brew install minio/stable/mc

# Configure client
mc alias set local http://localhost:9000 minioadmin minioadmin

# Create buckets
mc mb local/stdf-files
mc mb local/rca-reports
mc mb local/wafer-maps
```

## 6. OAuth2/SSO Configuration (Azure AD)

### Register Application in Azure AD
1. Go to Azure Portal > Azure Active Directory > App registrations
2. Click "New registration"
3. Name: "RCA Platform"
4. Redirect URI: `http://localhost:8000/auth/callback` (development)
5. Copy Application (client) ID → OAUTH2_CLIENT_ID
6. Copy Directory (tenant) ID → OAUTH2_TENANT_ID
7. Go to Certificates & secrets > New client secret
8. Copy secret value → OAUTH2_CLIENT_SECRET

### Configure API Permissions
1. API permissions > Add permission > Microsoft Graph
2. Add: `User.Read`, `email`, `openid`, `profile`
3. Grant admin consent

## 7. LLM API Access

### OpenAI Setup
1. Sign up at https://platform.openai.com/
2. Create API key: https://platform.openai.com/api-keys
3. Add to .env: `OPENAI_API_KEY=sk-...`
4. Set up billing: https://platform.openai.com/account/billing

### Anthropic Setup (Fallback)
1. Sign up at https://console.anthropic.com/
2. Create API key
3. Add to .env: `ANTHROPIC_API_KEY=sk-ant-...`

## 8. Knowledge Base Embedding (One-Time Setup)

### Prepare Historical RCA Reports
1. Collect PDF/Word reports (50K+ documents)
2. Place in `data/historical_rcas/` directory
3. Run embedding pipeline:
```bash
cd backend
python scripts/embed_knowledge_base.py --input_dir ../data/historical_rcas --batch_size 100
```

Expected duration: 8-12 hours for 50K documents

## 9. Test Data Preparation

### Sample STDF Files
1. Place sample STDF files in `data/sample_stdf/`
2. Format: `{LOT_ID}_{WAFER_ID}.stdf`
3. Minimum: 5 sample files for testing

### Wafer Map Images
1. Generate from STDF files:
```bash
python scripts/generate_wafer_maps.py --input_dir data/sample_stdf --output_dir data/sample_wafer_maps
```

## 10. Frontend Build and Deploy

### Install Dependencies
```bash
cd frontend
npm install
```

### Build for Production
```bash
npm run build
```

### Configure Nginx (Production)
```nginx
server {
    listen 80;
    server_name rca-platform.internal;

    location / {
        root /var/www/rca-platform/frontend/build;
        try_files $uri /index.html;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }

    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

## 11. Monitoring Setup

### Prometheus Configuration
Create `monitoring/prometheus.yml`:
```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'rca-platform'
    static_configs:
      - targets: ['localhost:8000']
```

### Grafana Dashboards
1. Access Grafana: http://localhost:3000
2. Login: admin / (password from .env)
3. Import dashboards from `monitoring/grafana/dashboards/`

## 12. SSL/TLS Certificates (Production)

### Generate Self-Signed (Development)
```bash
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout certs/server.key -out certs/server.crt
```

### Let's Encrypt (Production)
```bash
certbot --nginx -d rca-platform.internal
```

## 13. Kubernetes Deployment (Production)

### Configure kubectl
```bash
# Set up cluster connection
kubectl config use-context production-cluster

# Create namespace
kubectl create namespace rca-platform

# Create secrets
kubectl create secret generic rca-secrets \
  --from-env-file=.env \
  --namespace=rca-platform
```

### Deploy Services
```bash
cd k8s
kubectl apply -f postgres/ -n rca-platform
kubectl apply -f redis/ -n rca-platform
kubectl apply -f qdrant/ -n rca-platform
kubectl apply -f backend/ -n rca-platform
kubectl apply -f frontend/ -n rca-platform
kubectl apply -f monitoring/ -n rca-platform
```

## 14. Initial User Setup

### Create Admin User
```bash
cd backend
python scripts/create_admin_user.py \
  --email admin@company.com \
  --name "Admin User" \
  --role rca_admin
```

### Import User Roles from Azure AD Groups
```bash
python scripts/sync_azure_ad_users.py
```

## 15. Testing the Deployment

### Run Health Checks
```bash
# API health
curl http://localhost:8000/health

# Database connection
curl http://localhost:8000/health/db

# Redis connection
curl http://localhost:8000/health/redis

# Vector DB connection
curl http://localhost:8000/health/vectordb
```

### Submit Test RCA
```bash
curl -X POST http://localhost:8000/api/v1/rca/submit \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "lot_id": "DEV1_LOT123",
    "wafer_id": "W05",
    "bin": 5,
    "priority": "normal"
  }'
```

## 16. Backup Configuration

### PostgreSQL Automated Backups
```bash
# Create backup script
cat > /etc/cron.daily/backup-rca-db << 'EOF'
#!/bin/bash
pg_dump -U rca_user rca_platform | gzip > /backups/rca_platform_$(date +%Y%m%d).sql.gz
# Keep last 30 days
find /backups -name "rca_platform_*.sql.gz" -mtime +30 -delete
EOF

chmod +x /etc/cron.daily/backup-rca-db
```

### Vector Database Backups
```bash
# Qdrant snapshots
curl -X POST http://localhost:6333/collections/rca_knowledge_base/snapshots
```

## 17. Security Hardening (Production)

### Firewall Rules
```bash
# Allow only necessary ports
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw enable
```

### Disable Root SSH
```bash
# Edit /etc/ssh/sshd_config
PermitRootLogin no
PasswordAuthentication no  # Use SSH keys only
```

### Set Up Fail2Ban
```bash
apt install fail2ban
systemctl enable fail2ban
```

## 18. Performance Tuning

### PostgreSQL
Edit `/etc/postgresql/16/main/postgresql.conf`:
```
shared_buffers = 4GB
effective_cache_size = 12GB
maintenance_work_mem = 1GB
max_connections = 200
work_mem = 20MB
```

### Redis
Edit `/etc/redis/redis.conf`:
```
maxmemory 4gb
maxmemory-policy allkeys-lru
```

## 19. Logging Configuration

### Centralized Logging (Optional)
```bash
# Install Filebeat
wget https://artifacts.elastic.co/downloads/beats/filebeat/filebeat-8.11.0-linux-x86_64.tar.gz
tar xvf filebeat-8.11.0-linux-x86_64.tar.gz

# Configure Filebeat to forward logs to OpenSearch
```

## 20. Disaster Recovery Testing

### Schedule Regular DR Drills
```bash
# Quarterly DR test checklist:
# 1. Restore database from backup
# 2. Verify all services start successfully
# 3. Submit test RCA and verify completion
# 4. Document recovery time (target: <4 hours)
```

## Troubleshooting

### Common Issues

**Issue**: Agent timeout errors
- Check LLM API keys are valid
- Verify rate limits not exceeded
- Check network connectivity to OpenAI/Anthropic

**Issue**: Database connection errors
- Verify PostgreSQL is running: `systemctl status postgresql`
- Check credentials in .env file
- Ensure database exists: `psql -U postgres -l`

**Issue**: Vector search returns no results
- Verify Qdrant is running: `curl http://localhost:6333/health`
- Check collection exists: `curl http://localhost:6333/collections`
- Re-run embedding pipeline if needed

**Issue**: WebSocket connection fails
- Check firewall allows WebSocket connections
- Verify nginx proxy configuration
- Check browser console for CORS errors

## Support

For technical support:
- Email: rca-platform-support@company.com
- Slack: #rca-platform-support
- Documentation: http://docs.rca-platform.internal

## Next Steps After Setup

1. **Pilot Program**: Onboard 10 test users
2. **Training**: Schedule 2-hour training session
3. **Monitoring**: Review Grafana dashboards daily for first week
4. **Feedback**: Weekly meetings with pilot users
5. **Optimization**: Tune LLM prompts based on accuracy metrics

---

**Document Version**: 1.0  
**Last Updated**: 2025-12-05  
**Estimated Setup Time**: 4-6 hours (excluding knowledge base embedding)
