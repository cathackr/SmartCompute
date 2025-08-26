# SmartCompute Deployment Guide

## 🚀 Quick Start

### Option 1: Development Setup
```bash
# Clone and setup
git clone <your-repo>
cd SmartCompute
./scripts/setup.sh

# Run interactive demo
python main.py

# Or start API server
python main.py --api
```

### Option 2: Docker (Recommended)
```bash
# Quick start
docker compose up -d

# Custom build
./scripts/build.sh
./scripts/deploy.sh development
```

## 🏗️ System Requirements

### Minimum Requirements
- **CPU**: 2+ cores (ARM64 or x86_64)
- **RAM**: 2GB+ (4GB+ recommended)
- **Storage**: 1GB+ free space
- **OS**: Linux, macOS, Windows (with WSL2)
- **Python**: 3.9+ (if not using Docker)

### Optimal Configuration
- **CPU**: 4+ cores with AVX2 support
- **RAM**: 8GB+ 
- **GPU**: NVIDIA (CUDA 11+), AMD (ROCm), or Intel integrated
- **Storage**: SSD with 10GB+ free space

## 📋 Deployment Options

### 1. Development Environment
```bash
# Automated setup
./scripts/setup.sh

# Manual setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-core.txt
alembic upgrade head
```

**Features Enabled:**
- ✅ SQLite database
- ✅ Local file storage
- ✅ Development logging
- ✅ Auto-reload

### 2. Docker Compose (Local Production)
```bash
# Start all services
docker compose up -d

# With monitoring stack
docker compose --profile monitoring up -d

# With production configs
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

**Features Enabled:**
- ✅ Multi-container architecture
- ✅ PostgreSQL database (optional)
- ✅ Redis caching
- ✅ Nginx reverse proxy
- ✅ Health checks
- ✅ Persistent volumes
- ✅ Monitoring (Prometheus + Grafana)

### 3. Kubernetes (Enterprise)
```bash
# Apply Kubernetes manifests
kubectl apply -f k8s/

# Or use Helm
helm install smartcompute ./helm/smartcompute
```

**Features Enabled:**
- ✅ High availability
- ✅ Auto-scaling
- ✅ Rolling updates
- ✅ Service discovery
- ✅ Ingress controller
- ✅ Persistent storage
- ✅ Monitoring & alerting

## 🔧 Configuration

### Environment Variables
```bash
# Core Configuration
DATABASE_URL=postgresql://user:pass@host:5432/db
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO

# Security
SECRET_KEY=your-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Performance
MONITORING_ENABLED=true
MONITORING_INTERVAL=5
CACHE_TTL=3600
MAX_HISTORY_SIZE=1000

# Optional: GPU Support
CUDA_VISIBLE_DEVICES=0
ENABLE_GPU_DETECTION=true
```

### Database Options

#### SQLite (Development)
```bash
DATABASE_URL=sqlite:///./data/smartcompute.db
```
- ✅ Zero configuration
- ✅ Single file
- ❌ Not suitable for production

#### PostgreSQL (Production)
```bash
DATABASE_URL=postgresql://user:password@host:5432/smartcompute
```
- ✅ ACID compliance
- ✅ High performance
- ✅ Backup & replication
- ✅ JSON support

## 🛡️ Security Configuration

### Production Checklist
- [ ] Change default passwords
- [ ] Enable HTTPS/TLS
- [ ] Configure firewall
- [ ] Set up authentication
- [ ] Enable audit logging
- [ ] Configure backup encryption
- [ ] Set resource limits
- [ ] Enable monitoring alerts

### SSL/TLS Setup
```bash
# Generate self-signed certificate (development only)
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes

# For production, use Let's Encrypt or your certificate authority
```

### Authentication (Optional)
SmartCompute supports multiple authentication methods:
- API Keys
- JWT tokens
- OAuth2
- LDAP integration

## 📊 Monitoring & Observability

### Built-in Monitoring
- **Health Checks**: `/health` endpoint
- **Metrics**: Prometheus-compatible metrics
- **Logging**: Structured JSON logging
- **Performance**: Real-time anomaly detection
- **Alerts**: Configurable alert thresholds

### External Integrations
- **Prometheus**: Metrics collection
- **Grafana**: Visualization dashboards
- **ELK Stack**: Log aggregation
- **PagerDuty**: Alert notifications
- **Slack**: Status notifications

## 🔄 Backup & Recovery

### Database Backup
```bash
# PostgreSQL backup
pg_dump smartcompute > backup.sql

# SQLite backup
cp data/smartcompute.db backup/smartcompute-$(date +%Y%m%d).db
```

### Application Data
```bash
# Create full backup
tar -czf smartcompute-backup-$(date +%Y%m%d).tar.gz \
    data/ logs/ reports/ .env
```

### Disaster Recovery
1. **RTO (Recovery Time Objective)**: < 15 minutes
2. **RPO (Recovery Point Objective)**: < 5 minutes
3. **Automated backups**: Daily at 2 AM UTC
4. **Backup retention**: 30 days
5. **Geographic replication**: Optional

## 🚦 Load Testing

### Performance Benchmarks
```bash
# Install load testing tools
pip install locust

# Run load tests
locust -f tests/performance/locustfile.py \
       --headless \
       --users 100 \
       --spawn-rate 10 \
       --run-time 60s \
       --host http://localhost:8000
```

### Expected Performance
- **API Response Time**: < 100ms (95th percentile)
- **Anomaly Detection**: < 50ms per check
- **System Optimization**: < 500ms per operation
- **Concurrent Users**: 1000+ (properly configured)
- **Memory Usage**: < 512MB base + 1MB per concurrent user

## 🛠️ Troubleshooting

### Common Issues

#### Port Already in Use
```bash
# Find process using port 8000
lsof -i :8000
# Kill the process
kill -9 <PID>
```

#### Database Connection Failed
```bash
# Check database status
docker compose exec postgres pg_isready
# View logs
docker compose logs postgres
```

#### High Memory Usage
```bash
# Check memory usage
docker stats
# Adjust limits in docker-compose.yml
```

#### GPU Not Detected
```bash
# Check NVIDIA drivers
nvidia-smi
# Verify Docker GPU support
docker run --rm --gpus all nvidia/cuda:11.0-runtime-ubuntu20.04 nvidia-smi
```

### Log Locations
- **Application Logs**: `logs/smartcompute.log`
- **Access Logs**: `logs/access.log`
- **Error Logs**: `logs/error.log`
- **Docker Logs**: `docker compose logs <service>`

### Debug Mode
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Enable verbose output
python main.py --api --verbose

# Run with profiler
python -m cProfile -o profile.stats main.py --api
```

## 📞 Support

### Getting Help
1. **Documentation**: Check this deployment guide
2. **Issues**: Create GitHub issue with logs
3. **Community**: Join our Discord/Slack
4. **Enterprise Support**: Contact sales team

### Enterprise Features
- **24/7 Support**: Phone & email support
- **SLA Guarantee**: 99.9% uptime
- **Custom Integrations**: API extensions
- **Professional Services**: Deployment assistance
- **Training**: Team training sessions

For enterprise inquiries: enterprise@smartcompute.ai