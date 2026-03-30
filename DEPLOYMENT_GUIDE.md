# Deployment Guide

## Quick Start (Development)

```bash
# 1. Clone and setup
cd aws-architecture-failure-detection-system

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run development server
python app.py
```

Visit: http://localhost:8000

---

## Docker Deployment (Recommended)

### Prerequisites
- Docker 20.10+
- Docker Compose 2.0+

### Production Deployment

```bash
# 1. Clone repository
git clone https://github.com/karthikc1125/aws-architecture-failure-detection-system.git
cd aws-architecture-failure-detection-system

# 2. Setup environment
cp .env.example .env
# Edit .env with production values
nano .env

# 3. Build and run
docker-compose up -d

# 4. Verify
curl http://localhost/health

# 5. View logs
docker-compose logs -f app
```

### Manual Docker Build

```bash
# Build image
docker build -t aws-architect:latest .

# Run container
docker run -d \
  -p 8000:8000 \
  -e ENVIRONMENT=production \
  -e DEBUG=false \
  -e OPENROUTER_API_KEY=your_key \
  -v /data/logs:/app/logs \
  --restart unless-stopped \
  --name aws-architect \
  aws-architect:latest

# Check health
curl http://localhost:8000/health
```

---

## Cloud Deployment

### AWS EC2

```bash
# 1. Launch EC2 instance (Ubuntu 22.04)
# - t3.medium or larger
# - Security group: Allow 80, 443, 22

# 2. SSH into instance
ssh -i key.pem ubuntu@your-instance-ip

# 3. Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# 4. Clone and deploy
git clone https://github.com/karthikc1125/aws-architecture-failure-detection-system.git
cd aws-architecture-failure-detection-system
cp .env.example .env
# Edit .env
docker-compose up -d

# 5. Setup domain (optional)
# Point your domain to the EC2 public IP
# Update nginx.conf with your domain
# Generate SSL certificate (Let's Encrypt)
```

### AWS ECS (Fargate)

```bash
# 1. Push image to ECR
aws ecr create-repository --repository-name aws-architect
docker build -t aws-architect:latest .
docker tag aws-architect:latest YOUR_AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/aws-architect:latest
docker push YOUR_AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/aws-architect:latest

# 2. Create ECS cluster and service (use AWS console or CLI)
# 3. Configure load balancer and auto-scaling
```

### AWS Lambda + API Gateway

```bash
# For serverless deployment
# Use serverless-framework or AWS SAM
# Adjust api/main.py for Lambda handler
# Requires API Gateway integration
```

---

## Kubernetes Deployment

### Create manifests

**deployment.yaml**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: aws-architect
spec:
  replicas: 3
  selector:
    matchLabels:
      app: aws-architect
  template:
    metadata:
      labels:
        app: aws-architect
    spec:
      containers:
      - name: app
        image: YOUR_REGISTRY/aws-architect:latest
        ports:
        - containerPort: 8000
        env:
        - name: ENVIRONMENT
          value: "production"
        - name: OPENROUTER_API_KEY
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: openrouter-key
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
```

**service.yaml**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: aws-architect-service
spec:
  selector:
    app: aws-architect
  type: LoadBalancer
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
```

Deploy:
```bash
kubectl create secret generic app-secrets --from-literal=openrouter-key=YOUR_KEY
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
```

---

## SSL/TLS Certificate (Let's Encrypt)

```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Generate certificate
sudo certbot certonly --standalone -d your-domain.com

# Update nginx.conf with certificate paths
sudo certbot renew --dry-run

# Auto-renewal (crontab)
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

---

## Monitoring & Maintenance

### Health Monitoring
```bash
# Continuous monitoring
watch curl http://localhost:8000/health

# Container monitoring
docker stats aws-architect-app
```

### Log Management
```bash
# View logs
docker-compose logs app

# Follow logs in real-time
docker-compose logs -f app

# Export logs
docker-compose logs app > logs/app.log
```

### Database Backups (if using PostgreSQL)
```bash
# Backup vector store
docker-compose exec app tar czf - /app/vector_store | \
  tar xzf - -C ./backups/

# Backup analysis data
docker-compose exec app tar czf - /app/data | \
  tar xzf - -C ./backups/
```

### Update Application
```bash
# Pull latest code
git pull origin main

# Rebuild Docker image
docker-compose build --no-cache

# Restart with new image
docker-compose up -d
```

---

## Performance Tuning

### Increase Worker Count
```bash
# Edit docker-compose.yml or Dockerfile
# Change gunicorn command:
CMD ["gunicorn", "-w", "8", "-k", "uvicorn.workers.UvicornWorker", ...]
```

### Database Connection Pooling
```python
# Add to api/config.py
SQLALCHEMY_POOL_SIZE = 20
SQLALCHEMY_MAX_OVERFLOW = 40
```

### Caching Strategy
```python
# Add Redis for embeddings cache
from redis import Redis
cache = Redis(host='redis', port=6379)
```

---

## Troubleshooting

### Container fails to start
```bash
# Check logs
docker-compose logs app

# Rebuild
docker-compose build --no-cache
docker-compose up -d
```

### Health check fails
```bash
# Test endpoint manually
curl -v http://localhost:8000/health

# Check container running
docker ps | grep aws-architect
```

### High memory usage
```bash
# Check Python memory
docker-compose exec app ps aux

# Limit memory in docker-compose.yml
mem_limit: 1g
mem_reservation: 512m
```

### API timeout errors
```bash
# Increase timeout in .env
LLM_TIMEOUT=60
ANALYSIS_TIMEOUT=120

# Restart with new settings
docker-compose down
docker-compose up -d
```

---

## Security Checklist

- [ ] Change default API keys
- [ ] Enable HTTPS/SSL
- [ ] Restrict CORS origins
- [ ] Setup firewall rules
- [ ] Enable authentication/API keys
- [ ] Regular security updates
- [ ] Enable audit logging
- [ ] Backup sensitive data regularly
- [ ] Monitor for unauthorized access
- [ ] Setup rate limiting

---

## Backup & Disaster Recovery

```bash
# Full backup
docker-compose exec app tar czf - /app | \
  tar xzf - -C /backup/$(date +%Y%m%d)

# Database backup (PostgreSQL)
docker exec aws-architect-db \
  pg_dump -U postgres app_db | \
  gzip > /backup/db_$(date +%Y%m%d).sql.gz

# Restore from backup
docker-compose down
tar xzf /backup/app_backup.tar.gz
docker-compose up -d
```

---

## Support & Issues

- Check logs: `docker-compose logs app`
- GitHub Issues: https://github.com/karthikc1125/aws-architecture-failure-detection-system/issues
- Documentation: See PRODUCTION_IMPROVEMENTS.md
