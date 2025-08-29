#!/bin/bash
# Setup SmartCompute Monitoring Infrastructure

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "Setting up SmartCompute monitoring infrastructure..."

# Check if Docker and Docker Compose are installed
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "Error: Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create monitoring directories
echo "Creating monitoring directories..."
mkdir -p "$PROJECT_ROOT/monitoring/grafana/provisioning/datasources"
mkdir -p "$PROJECT_ROOT/monitoring/grafana/provisioning/dashboards"
mkdir -p "$PROJECT_ROOT/monitoring/alerts"
mkdir -p "$PROJECT_ROOT/logs/smartcompute"

# Set proper permissions for Grafana
echo "Setting permissions for Grafana..."
sudo chown -R 472:472 "$PROJECT_ROOT/monitoring/grafana" 2>/dev/null || echo "Warning: Could not set Grafana permissions (run as root if needed)"

# Create log directories with proper permissions
echo "Setting up log directories..."
sudo mkdir -p /var/log/smartcompute 2>/dev/null || mkdir -p "$PROJECT_ROOT/logs"
sudo chown -R $USER:$USER /var/log/smartcompute 2>/dev/null || echo "Using local logs directory"

# Load environment variables
if [ -f "$PROJECT_ROOT/.env.production" ]; then
    echo "Loading production environment..."
    export $(cat "$PROJECT_ROOT/.env.production" | grep -v '^#' | xargs)
elif [ -f "$PROJECT_ROOT/.env.development" ]; then
    echo "Loading development environment..."
    export $(cat "$PROJECT_ROOT/.env.development" | grep -v '^#' | xargs)
else
    echo "Warning: No environment file found. Using defaults."
    export GRAFANA_PASSWORD="${GRAFANA_PASSWORD:-admin123}"
    export DB_PASSWORD="${DB_PASSWORD:-password}"
    export REDIS_PASSWORD="${REDIS_PASSWORD:-redis_password}"
fi

# Validate Prometheus configuration
echo "Validating Prometheus configuration..."
if command -v promtool &> /dev/null; then
    promtool check config "$PROJECT_ROOT/monitoring/prometheus.yml"
    promtool check rules "$PROJECT_ROOT/monitoring/alerts/smartcompute-alerts.yml"
    echo "Prometheus configuration is valid."
else
    echo "Warning: promtool not available. Skipping configuration validation."
fi

# Create external network if it doesn't exist
echo "Creating Docker networks..."
docker network create smartcompute_internal 2>/dev/null || echo "Network smartcompute_internal already exists"

# Start monitoring stack
echo "Starting monitoring services..."
cd "$PROJECT_ROOT/monitoring"

# Check if monitoring stack is already running
if docker-compose -f docker-compose.monitoring.yml ps -q | grep -q .; then
    echo "Monitoring stack is already running. Updating services..."
    docker-compose -f docker-compose.monitoring.yml pull
    docker-compose -f docker-compose.monitoring.yml up -d --remove-orphans
else
    echo "Starting monitoring stack..."
    docker-compose -f docker-compose.monitoring.yml up -d
fi

# Wait for services to be healthy
echo "Waiting for services to be healthy..."
sleep 30

# Check service health
echo "Checking service health..."
services=("prometheus" "grafana" "alertmanager" "node-exporter")
all_healthy=true

for service in "${services[@]}"; do
    if docker-compose -f docker-compose.monitoring.yml ps "$service" | grep -q "Up (healthy)"; then
        echo "✅ $service is healthy"
    else
        echo "❌ $service is not healthy"
        all_healthy=false
    fi
done

if [ "$all_healthy" = true ]; then
    echo ""
    echo "🎉 Monitoring stack is up and running!"
    echo ""
    echo "Access URLs (localhost only):"
    echo "  Grafana:      http://localhost:3000 (admin / $GRAFANA_PASSWORD)"
    echo "  Prometheus:   http://localhost:9090"
    echo "  Alertmanager: http://localhost:9093"
    echo "  Node Metrics: http://localhost:9100"
    echo ""
    echo "Default Grafana Credentials:"
    echo "  Username: admin"
    echo "  Password: $GRAFANA_PASSWORD"
    echo ""
    echo "Dashboards will be automatically imported. Check the 'SmartCompute' folder in Grafana."
    echo ""
    echo "To stop monitoring: docker-compose -f monitoring/docker-compose.monitoring.yml down"
    echo "To view logs: docker-compose -f monitoring/docker-compose.monitoring.yml logs -f [service]"
else
    echo ""
    echo "❌ Some services are not healthy. Check the logs:"
    echo "docker-compose -f monitoring/docker-compose.monitoring.yml logs"
    exit 1
fi

# Test metrics endpoints
echo ""
echo "Testing metrics endpoints..."
if curl -s http://localhost:9090/api/v1/status/config > /dev/null; then
    echo "✅ Prometheus API is responding"
else
    echo "❌ Prometheus API is not responding"
fi

if curl -s http://localhost:3000/api/health > /dev/null; then
    echo "✅ Grafana API is responding"
else
    echo "❌ Grafana API is not responding"
fi

echo ""
echo "Monitoring setup completed successfully!"
echo ""
echo "Next steps:"
echo "1. Start your SmartCompute services"
echo "2. Visit http://localhost:3000 to view dashboards"
echo "3. Configure alert notifications in Alertmanager"
echo "4. Customize dashboards as needed"