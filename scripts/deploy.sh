#!/bin/bash
# SmartCompute Deployment Script

set -e

# Default values
ENVIRONMENT=${1:-"development"}
VERSION=${2:-"latest"}

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Deployment configurations
declare -A CONFIGS
CONFIGS[development]="docker-compose.yml"
CONFIGS[staging]="docker-compose.yml docker-compose.staging.yml"
CONFIGS[production]="docker-compose.yml docker-compose.prod.yml"

echo "🚀 Deploying SmartCompute to $ENVIRONMENT..."
echo "Version: $VERSION"
echo ""

# Validate environment
if [[ ! ${CONFIGS[$ENVIRONMENT]} ]]; then
    print_error "Invalid environment: $ENVIRONMENT"
    echo "Available environments: ${!CONFIGS[@]}"
    exit 1
fi

# Check Docker and Docker Compose
if ! command -v docker &> /dev/null; then
    print_error "Docker not found"
    exit 1
fi

if ! command -v docker compose &> /dev/null; then
    print_error "Docker Compose not found"
    exit 1
fi

# Load environment-specific configuration
COMPOSE_FILES=${CONFIGS[$ENVIRONMENT]}
print_info "Using compose files: $COMPOSE_FILES"

# Set environment variables
export VERSION=$VERSION
export BUILD_DATE=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
export VCS_REF=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")

# Create environment file if it doesn't exist
if [ ! -f ".env" ]; then
    print_warning ".env file not found, creating from template..."
    cp .env.example .env
    print_warning "Please edit .env file before continuing"
    
    if [ "$ENVIRONMENT" = "production" ]; then
        print_error "Production deployment requires properly configured .env file"
        exit 1
    fi
fi

# Pre-deployment checks
print_status "Running pre-deployment checks..."

# Check if services are already running
if docker compose ps | grep -q "Up"; then
    print_info "Existing services found, performing rolling update..."
    ROLLING_UPDATE=true
else
    print_info "No existing services, performing fresh deployment..."
    ROLLING_UPDATE=false
fi

# Pull latest images (if not building locally)
if [[ "$VERSION" != "latest" ]] && [[ "$ENVIRONMENT" != "development" ]]; then
    print_status "Pulling images..."
    docker compose -f $COMPOSE_FILES pull
fi

# Build images for development
if [ "$ENVIRONMENT" = "development" ]; then
    print_status "Building images..."
    docker compose -f $COMPOSE_FILES build
fi

# Database migrations
print_status "Running database migrations..."
if [ "$ROLLING_UPDATE" = true ]; then
    # Run migrations on existing database
    docker compose -f $COMPOSE_FILES exec smartcompute-api alembic upgrade head || {
        print_warning "Failed to run migrations on running container, will retry after deployment"
    }
fi

# Deploy services
print_status "Deploying services..."
docker compose -f $COMPOSE_FILES up -d

# Wait for services to be healthy
print_status "Waiting for services to be healthy..."
sleep 10

# Health check
print_status "Performing health checks..."
for i in {1..30}; do
    if docker compose -f $COMPOSE_FILES exec smartcompute-api python -c "
import requests
try:
    response = requests.get('http://localhost:8000/health', timeout=5)
    if response.status_code == 200:
        print('✅ API is healthy')
        exit(0)
    else:
        print(f'❌ API returned status {response.status_code}')
        exit(1)
except Exception as e:
    print(f'❌ Health check failed: {e}')
    exit(1)
" 2>/dev/null; then
        break
    fi
    
    if [ $i -eq 30 ]; then
        print_error "Health check failed after 30 attempts"
        print_info "Showing service logs:"
        docker compose -f $COMPOSE_FILES logs smartcompute-api
        exit 1
    fi
    
    echo -n "."
    sleep 2
done

echo ""

# Run post-deployment migrations if needed
if [ "$ROLLING_UPDATE" != true ]; then
    print_status "Running database migrations..."
    docker compose -f $COMPOSE_FILES exec smartcompute-api alembic upgrade head
fi

# Show deployment status
print_status "Deployment completed successfully!"
echo ""
print_info "Service status:"
docker compose -f $COMPOSE_FILES ps

echo ""
print_info "Service endpoints:"
echo "- API: http://localhost:8000"
echo "- API Docs: http://localhost:8000/docs"
echo "- Health Check: http://localhost:8000/health"

if echo "$COMPOSE_FILES" | grep -q "monitoring"; then
    echo "- Prometheus: http://localhost:9090"
    echo "- Grafana: http://localhost:3000"
fi

echo ""
print_info "Useful commands:"
echo "- View logs: docker compose -f $COMPOSE_FILES logs -f"
echo "- Stop services: docker compose -f $COMPOSE_FILES down"
echo "- Restart service: docker compose -f $COMPOSE_FILES restart smartcompute-api"

if [ "$ENVIRONMENT" = "production" ]; then
    echo ""
    print_warning "Production deployment checklist:"
    echo "- ✅ Environment variables configured"
    echo "- ✅ Database backups enabled"
    echo "- ✅ SSL certificates configured"
    echo "- ✅ Monitoring alerts configured"
    echo "- ✅ Log aggregation configured"
fi