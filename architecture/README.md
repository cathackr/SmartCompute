# 🏗️ SmartCompute Production Architecture

## 🎯 Architecture Overview

SmartCompute production deployment follows a **microservices architecture** with clear separation of responsibilities for security, scalability, and maintainability.

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Load Balancer │    │   API Gateway    │    │  Secret Manager │
│   (nginx/HAProxy│ => │  (Auth & Rate    │ => │  (Vault/AWS)    │
│   + TLS)        │    │   Limiting)      │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         v                       v                       │
┌─────────────────┐    ┌──────────────────┐             │
│   Web Dashboard │    │   Public API     │             │
│   (Frontend)    │    │   (FastAPI)      │             │
│   Port: 3000    │    │   Port: 8000     │             │
└─────────────────┘    └──────────────────┘             │
                                │                        │
                                v                        │
                    ┌──────────────────┐                │
                    │  Message Queue   │                │
                    │  (RabbitMQ/Redis)│                │
                    │  Port: 6379      │                │
                    └──────────────────┘                │
                                │                        │
                                v                        │
┌─────────────────┐    ┌──────────────────┐             │
│  SmartCompute   │    │   PostgreSQL     │             │
│  Core Engine    │ => │   Database       │ <==========┘
│  (Internal)     │    │   Port: 5432     │
│  Port: 9000     │    │                  │
└─────────────────┘    └──────────────────┘
         │
         v
┌─────────────────┐
│  Payment Gateway│
│  Microservice   │
│  (Isolated)     │
│  Port: 9001     │
└─────────────────┘
```

## 🔧 Component Details

### 1. SmartCompute Core Engine (Internal Service)
- **Purpose**: Core detection and analysis logic
- **Network**: Internal only, no direct external access
- **Port**: 9000 (internal)
- **Database**: PostgreSQL with connection pooling
- **Communication**: Message queue (RabbitMQ/Redis) for job processing

### 2. Public API Service (External Interface)
- **Purpose**: User-facing API and authentication
- **Network**: External access via API Gateway
- **Port**: 8000 (behind reverse proxy)
- **Authentication**: JWT tokens, API keys
- **Rate Limiting**: Per-user/API key limits

### 3. Payment Gateway Service (Isolated)
- **Purpose**: Handle crypto payments and webhooks
- **Network**: Isolated with minimal access
- **Port**: 9001 (internal)
- **Security**: Webhook signature verification
- **Secrets**: HashiCorp Vault or AWS Secrets Manager

### 4. Web Dashboard (Frontend)
- **Purpose**: User interface and monitoring
- **Network**: Public access via load balancer
- **Port**: 3000 (behind nginx)
- **Technology**: React/Vue.js + API integration

## 🗄️ Data Architecture

### Database Migration Strategy
```sql
-- Current: JSON/SQLite files
-- Target: PostgreSQL with proper schema
-- Tool: Alembic migrations (already configured)

-- Migration path:
1. Export existing data from JSON/SQLite
2. Run Alembic migrations to create PostgreSQL schema
3. Import data with transformation scripts
4. Update connection strings in all services
```

### Message Queue Integration
```python
# Redis/RabbitMQ for inter-service communication
# Queue: smartcompute.analysis
# Message format: JSON with analysis requests

{
    "id": "analysis-123",
    "type": "threat_analysis",
    "data": {...},
    "priority": "high",
    "timestamp": "2024-08-27T10:30:00Z"
}
```

## 🔒 Security Architecture

### Network Security
```yaml
networks:
  public:
    # Load balancer, Web dashboard
  api:
    # Public API, Rate limiting
  internal:
    # SmartCompute Core, Database
  isolated:
    # Payment gateway, Secrets
```

### Authentication & Authorization
```python
# JWT-based authentication
# Role-based access control (RBAC)
# API key management
# Rate limiting per user/key
```

### Secret Management
```yaml
# HashiCorp Vault or AWS Secrets Manager
secrets:
  database:
    postgres_password: "vault:secret/db/password"
  payment:
    webhook_secret: "vault:secret/payment/webhook"
  api:
    jwt_secret: "vault:secret/api/jwt"
```

## 📊 Deployment Configuration

### Docker Compose Production
```yaml
version: '3.8'
services:
  smartcompute-core:
    build: ./services/core
    networks: [internal]
    environment:
      - DATABASE_URL=postgresql://...
      - QUEUE_URL=redis://queue:6379
    
  api-service:
    build: ./services/api  
    networks: [api, internal]
    depends_on: [smartcompute-core, queue]
    
  payment-service:
    build: ./services/payment
    networks: [isolated]
    environment:
      - VAULT_ADDR=${VAULT_ADDR}
      - VAULT_TOKEN=${VAULT_TOKEN}
```

### Kubernetes Deployment
```yaml
# Namespace separation
# NetworkPolicies for traffic control
# SecretManager CSI driver integration
# Horizontal Pod Autoscaling
```

## 🚀 Implementation Roadmap

### Phase 1: Service Separation (Week 1)
- [ ] Extract SmartCompute core to separate service
- [ ] Implement message queue communication
- [ ] Set up PostgreSQL with Alembic migrations
- [ ] Create API gateway with authentication

### Phase 2: Security Hardening (Week 2)  
- [ ] Implement secret management integration
- [ ] Set up network isolation
- [ ] Add comprehensive logging and monitoring
- [ ] Payment service isolation

### Phase 3: Scaling & Monitoring (Week 3)
- [ ] Load balancing configuration
- [ ] Monitoring and alerting (Prometheus/Grafana)
- [ ] Performance optimization
- [ ] Disaster recovery procedures

## 🔍 Monitoring & Observability

### Metrics Collection
```python
# Application metrics
- Request latency (P50, P95, P99)
- Error rates by service
- Queue depth and processing time
- Database connection pool usage

# Infrastructure metrics  
- CPU, Memory, Disk usage
- Network throughput
- Database performance
- Message queue health
```

### Logging Strategy
```json
{
  "service": "smartcompute-core",
  "level": "INFO",
  "message": "Analysis completed",
  "request_id": "req-123",
  "processing_time_ms": 45.2,
  "timestamp": "2024-08-27T10:30:00Z"
}
```

### Health Checks
```yaml
# Each service exposes /health endpoint
# Load balancer health monitoring
# Database connection validation
# Queue connectivity checks
```

This architecture ensures scalability, security, and maintainability while following industry best practices for microservices deployment.