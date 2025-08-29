#!/bin/bash
# SmartCompute Secure Deployment Script
# Deploys production-ready SmartCompute with complete security

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Configuration
ENVIRONMENT=${ENVIRONMENT:-production}
COMPOSE_FILE="docker-compose.production-secure.yml"
BACKUP_DIR="/opt/smartcompute/backups"
LOG_FILE="/var/log/smartcompute/deployment.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    local level=$1
    shift
    local message="$@"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    case $level in
        ERROR)
            echo -e "${RED}[ERROR]${NC} $message" >&2
            echo "[$timestamp] [ERROR] $message" >> "$LOG_FILE"
            ;;
        WARN)
            echo -e "${YELLOW}[WARN]${NC} $message"
            echo "[$timestamp] [WARN] $message" >> "$LOG_FILE"
            ;;
        INFO)
            echo -e "${GREEN}[INFO]${NC} $message"
            echo "[$timestamp] [INFO] $message" >> "$LOG_FILE"
            ;;
        DEBUG)
            echo -e "${BLUE}[DEBUG]${NC} $message"
            echo "[$timestamp] [DEBUG] $message" >> "$LOG_FILE"
            ;;
    esac
}

# Error handler
error_exit() {
    log ERROR "$1"
    exit 1
}

# Check prerequisites
check_prerequisites() {
    log INFO "Checking prerequisites..."
    
    # Check if running as root or with sudo
    if [[ $EUID -eq 0 ]]; then
        log WARN "Running as root. Consider using a dedicated user with docker group membership."
    fi
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        error_exit "Docker is not installed. Please install Docker first."
    fi
    
    # Check Docker Compose
    if ! docker compose version &> /dev/null; then
        error_exit "Docker Compose is not installed or not accessible."
    fi
    
    # Check minimum Docker version
    DOCKER_VERSION=$(docker --version | grep -oE '[0-9]+\.[0-9]+' | head -1)
    REQUIRED_VERSION="20.10"
    if ! printf '%s\n%s\n' "$REQUIRED_VERSION" "$DOCKER_VERSION" | sort -V -C; then
        error_exit "Docker version $DOCKER_VERSION is too old. Minimum required: $REQUIRED_VERSION"
    fi
    
    # Check available disk space
    AVAILABLE_SPACE=$(df "$PROJECT_ROOT" | tail -1 | awk '{print $4}')
    REQUIRED_SPACE=5242880  # 5GB in KB
    if [ "$AVAILABLE_SPACE" -lt "$REQUIRED_SPACE" ]; then
        error_exit "Insufficient disk space. Available: ${AVAILABLE_SPACE}KB, Required: ${REQUIRED_SPACE}KB"
    fi
    
    # Check if ports are available
    REQUIRED_PORTS=(80 443 5432 6379 9443 9444)
    for port in "${REQUIRED_PORTS[@]}"; do
        if ss -tuln | grep -q ":$port "; then
            log WARN "Port $port is already in use. This may cause conflicts."
        fi
    done
    
    log INFO "Prerequisites check completed"
}

# Setup directories and permissions
setup_directories() {
    log INFO "Setting up directories and permissions..."
    
    # Create necessary directories
    sudo mkdir -p "$BACKUP_DIR"
    sudo mkdir -p "/var/log/smartcompute"
    sudo mkdir -p "/opt/smartcompute/certs"
    sudo mkdir -p "/opt/smartcompute/data"
    
    # Set permissions
    sudo chown -R $USER:$USER "$BACKUP_DIR"
    sudo chown -R $USER:$USER "/var/log/smartcompute"
    
    # Create log file
    touch "$LOG_FILE"
    
    log INFO "Directory setup completed"
}

# Generate or check TLS certificates
setup_certificates() {
    log INFO "Setting up TLS certificates..."
    
    cd "$PROJECT_ROOT"
    
    # Generate certificates if they don't exist
    if [ ! -f "security/tls/ca/ca-cert.pem" ]; then
        log INFO "Generating TLS certificates..."
        bash security/tls/generate-certs.sh
    else
        log INFO "TLS certificates already exist"
        
        # Check certificate expiry
        EXPIRY_DATE=$(openssl x509 -in security/tls/ca/ca-cert.pem -noout -enddate | cut -d= -f2)
        EXPIRY_TIMESTAMP=$(date -d "$EXPIRY_DATE" +%s)
        CURRENT_TIMESTAMP=$(date +%s)
        DAYS_UNTIL_EXPIRY=$(( (EXPIRY_TIMESTAMP - CURRENT_TIMESTAMP) / 86400 ))
        
        if [ "$DAYS_UNTIL_EXPIRY" -lt 30 ]; then
            log WARN "Certificates expire in $DAYS_UNTIL_EXPIRY days. Consider renewing."
        fi
    fi
    
    # Generate DH parameters for NGINX if not present
    if [ ! -f "nginx/dhparam.pem" ]; then
        log INFO "Generating Diffie-Hellman parameters (this may take a while)..."
        openssl dhparam -out nginx/dhparam.pem 2048
    fi
    
    log INFO "Certificate setup completed"
}

# Setup Docker secrets
setup_secrets() {
    log INFO "Setting up Docker secrets..."
    
    # Generate secrets if they don't exist
    declare -A secrets=(
        ["db_password"]="$(openssl rand -hex 16)"
        ["redis_password"]="$(openssl rand -hex 16)"
        ["jwt_secret"]="$(openssl rand -hex 32)"
        ["payment_webhook_secret"]="$(openssl rand -hex 24)"
        ["vault_root_token"]="$(openssl rand -hex 16)"
    )
    
    for secret_name in "${!secrets[@]}"; do
        if ! docker secret ls --format "{{.Name}}" | grep -q "^${secret_name}$"; then
            echo "${secrets[$secret_name]}" | docker secret create "$secret_name" -
            log INFO "Created Docker secret: $secret_name"
        else
            log INFO "Docker secret already exists: $secret_name"
        fi
    done
    
    log INFO "Docker secrets setup completed"
}

# Pre-deployment validation
validate_configuration() {
    log INFO "Validating configuration..."
    
    cd "$PROJECT_ROOT"
    
    # Validate Docker Compose file
    if ! docker compose -f "$COMPOSE_FILE" config > /dev/null; then
        error_exit "Docker Compose file validation failed"
    fi
    
    # Validate NGINX configuration
    if [ -f "nginx/production-secure.conf" ]; then
        # Test NGINX config in container
        if docker run --rm -v "$PROJECT_ROOT/nginx/production-secure.conf:/etc/nginx/nginx.conf:ro" nginx:alpine nginx -t; then
            log INFO "NGINX configuration is valid"
        else
            error_exit "NGINX configuration validation failed"
        fi
    fi
    
    # Check if all required certificates exist
    REQUIRED_CERTS=(
        "security/tls/ca/ca-cert.pem"
        "security/tls/server/smartcompute-nginx-cert.pem"
        "security/tls/client/api-client-cert.pem"
    )
    
    for cert in "${REQUIRED_CERTS[@]}"; do
        if [ ! -f "$cert" ]; then
            error_exit "Required certificate not found: $cert"
        fi
    done
    
    log INFO "Configuration validation completed"
}

# Create backup
create_backup() {
    log INFO "Creating backup..."
    
    local backup_timestamp=$(date '+%Y%m%d_%H%M%S')
    local backup_file="$BACKUP_DIR/smartcompute_backup_$backup_timestamp.tar.gz"
    
    # Backup data volumes
    docker run --rm \
        -v smartcompute_postgres_data:/data/postgres:ro \
        -v smartcompute_redis_data:/data/redis:ro \
        -v smartcompute_vault_data:/data/vault:ro \
        -v "$BACKUP_DIR:/backup" \
        alpine:latest \
        tar -czf "/backup/smartcompute_backup_$backup_timestamp.tar.gz" -C /data .
    
    # Backup configuration files
    tar -czf "$BACKUP_DIR/config_backup_$backup_timestamp.tar.gz" \
        -C "$PROJECT_ROOT" \
        docker-compose.production-secure.yml \
        nginx/ \
        security/ \
        scripts/
    
    # Keep only last 7 backups
    find "$BACKUP_DIR" -name "smartcompute_backup_*.tar.gz" -type f -mtime +7 -delete
    find "$BACKUP_DIR" -name "config_backup_*.tar.gz" -type f -mtime +7 -delete
    
    log INFO "Backup created: $backup_file"
}

# Deploy services
deploy_services() {
    log INFO "Starting deployment..."
    
    cd "$PROJECT_ROOT"
    
    # Pull latest images
    log INFO "Pulling latest images..."
    docker compose -f "$COMPOSE_FILE" pull
    
    # Build custom images
    log INFO "Building custom images..."
    docker compose -f "$COMPOSE_FILE" build --no-cache
    
    # Start services in dependency order
    log INFO "Starting core infrastructure..."
    docker compose -f "$COMPOSE_FILE" up -d cert-generator postgres redis vault
    
    # Wait for core services to be healthy
    log INFO "Waiting for core services to be healthy..."
    docker compose -f "$COMPOSE_FILE" up -d --wait postgres redis vault
    
    # Start application services
    log INFO "Starting application services..."
    docker compose -f "$COMPOSE_FILE" up -d smartcompute-core api-service payment-service
    
    # Wait for application services
    docker compose -f "$COMPOSE_FILE" up -d --wait smartcompute-core api-service payment-service
    
    # Start frontend and proxy
    log INFO "Starting frontend services..."
    docker compose -f "$COMPOSE_FILE" up -d dashboard nginx
    
    # Wait for all services
    docker compose -f "$COMPOSE_FILE" up -d --wait
    
    log INFO "All services started successfully"
}

# Post-deployment validation
post_deployment_validation() {
    log INFO "Running post-deployment validation..."
    
    # Check service health
    local failed_services=()
    
    services=("postgres" "redis" "vault" "smartcompute-core" "api-service" "payment-service" "dashboard" "nginx")
    
    for service in "${services[@]}"; do
        if ! docker compose -f "$COMPOSE_FILE" ps "$service" | grep -q "healthy\|running"; then
            failed_services+=("$service")
        fi
    done
    
    if [ ${#failed_services[@]} -gt 0 ]; then
        log ERROR "The following services are not healthy: ${failed_services[*]}"
        return 1
    fi
    
    # Test endpoints
    log INFO "Testing service endpoints..."
    
    # Test HTTPS endpoints
    if ! curl -k -f -s https://localhost/health > /dev/null; then
        log WARN "HTTPS health check failed"
    else
        log INFO "HTTPS endpoint is responding"
    fi
    
    # Test certificate validation
    if openssl s_client -connect localhost:443 -verify_return_error < /dev/null > /dev/null 2>&1; then
        log INFO "TLS certificate validation passed"
    else
        log WARN "TLS certificate validation failed (expected for self-signed certificates)"
    fi
    
    log INFO "Post-deployment validation completed"
}

# Setup monitoring and alerting
setup_monitoring() {
    log INFO "Setting up monitoring and alerting..."
    
    cd "$PROJECT_ROOT"
    
    # Deploy monitoring stack if requested
    if [ "${ENABLE_MONITORING:-true}" == "true" ]; then
        if [ -f "monitoring/docker-compose.monitoring.yml" ]; then
            docker compose -f monitoring/docker-compose.monitoring.yml up -d
            log INFO "Monitoring stack deployed"
        fi
    fi
    
    # Setup log rotation
    cat > /etc/logrotate.d/smartcompute << EOF
/var/log/smartcompute/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 0644 $USER $USER
    postrotate
        docker kill -s USR1 smartcompute-nginx 2>/dev/null || true
    endscript
}
EOF
    
    log INFO "Monitoring and alerting setup completed"
}

# Print deployment summary
print_summary() {
    log INFO "Deployment completed successfully!"
    
    echo ""
    echo "🎉 SmartCompute Secure Deployment Summary"
    echo "=========================================="
    echo ""
    echo "🌐 Service URLs:"
    echo "  • API (HTTPS):      https://localhost/api/v1/"
    echo "  • Dashboard (HTTPS): https://localhost/"
    echo "  • Health Check:      https://localhost/health"
    echo ""
    echo "🔐 Security Features Enabled:"
    echo "  • TLS 1.2/1.3 with strong ciphers"
    echo "  • mTLS for internal service communication"
    echo "  • Rate limiting and DDoS protection"
    echo "  • Circuit breakers for external APIs"
    echo "  • Web Application Firewall (WAF)"
    echo "  • Security headers and CSP"
    echo ""
    echo "📊 Monitoring:"
    if [ "${ENABLE_MONITORING:-true}" == "true" ]; then
        echo "  • Grafana:    http://localhost:3000"
        echo "  • Prometheus: http://localhost:9090"
        echo "  • Logs:       /var/log/smartcompute/"
    else
        echo "  • Monitoring disabled"
    fi
    echo ""
    echo "🔧 Management Commands:"
    echo "  • View logs:         docker compose -f $COMPOSE_FILE logs -f [service]"
    echo "  • Check status:      docker compose -f $COMPOSE_FILE ps"
    echo "  • Scale service:     docker compose -f $COMPOSE_FILE up -d --scale [service]=N"
    echo "  • Stop all:          docker compose -f $COMPOSE_FILE down"
    echo "  • Update services:   bash $0 --update"
    echo ""
    echo "⚠️  Important Notes:"
    echo "  • Change default passwords in production"
    echo "  • Configure DNS for your domains"
    echo "  • Set up proper SSL certificates (Let's Encrypt)"
    echo "  • Configure backup strategy"
    echo "  • Monitor security logs regularly"
    echo ""
}

# Update deployment
update_deployment() {
    log INFO "Updating deployment..."
    
    create_backup
    
    cd "$PROJECT_ROOT"
    
    # Pull latest images
    docker compose -f "$COMPOSE_FILE" pull
    
    # Rolling update services
    services=("api-service" "smartcompute-core" "payment-service" "dashboard")
    
    for service in "${services[@]}"; do
        log INFO "Updating service: $service"
        docker compose -f "$COMPOSE_FILE" up -d --no-deps "$service"
        
        # Wait for service to be healthy
        sleep 10
        if ! docker compose -f "$COMPOSE_FILE" ps "$service" | grep -q "healthy\|running"; then
            error_exit "Failed to update service: $service"
        fi
    done
    
    # Reload NGINX
    docker compose -f "$COMPOSE_FILE" exec nginx nginx -s reload
    
    log INFO "Update completed successfully"
}

# Rollback deployment
rollback_deployment() {
    log INFO "Rolling back deployment..."
    
    local backup_file=$(find "$BACKUP_DIR" -name "smartcompute_backup_*.tar.gz" -type f | sort -r | head -1)
    
    if [ -z "$backup_file" ]; then
        error_exit "No backup found for rollback"
    fi
    
    log INFO "Rolling back to: $backup_file"
    
    # Stop services
    docker compose -f "$COMPOSE_FILE" down
    
    # Restore data volumes
    docker run --rm \
        -v smartcompute_postgres_data:/data/postgres \
        -v smartcompute_redis_data:/data/redis \
        -v smartcompute_vault_data:/data/vault \
        -v "$BACKUP_DIR:/backup" \
        alpine:latest \
        sh -c "rm -rf /data/* && tar -xzf /backup/$(basename "$backup_file") -C /data"
    
    # Restart services
    deploy_services
    
    log INFO "Rollback completed"
}

# Main execution
main() {
    case "${1:-deploy}" in
        deploy)
            log INFO "Starting SmartCompute secure deployment..."
            check_prerequisites
            setup_directories
            setup_certificates
            setup_secrets
            validate_configuration
            create_backup
            deploy_services
            post_deployment_validation
            setup_monitoring
            print_summary
            ;;
        update)
            update_deployment
            ;;
        rollback)
            rollback_deployment
            ;;
        backup)
            create_backup
            ;;
        validate)
            validate_configuration
            ;;
        certificates)
            setup_certificates
            ;;
        secrets)
            setup_secrets
            ;;
        --help|-h)
            echo "SmartCompute Secure Deployment Script"
            echo ""
            echo "Usage: $0 [COMMAND]"
            echo ""
            echo "Commands:"
            echo "  deploy      Full deployment (default)"
            echo "  update      Update existing deployment"
            echo "  rollback    Rollback to previous backup"
            echo "  backup      Create backup only"
            echo "  validate    Validate configuration only"
            echo "  certificates Generate/check certificates only"
            echo "  secrets     Setup Docker secrets only"
            echo ""
            echo "Environment Variables:"
            echo "  ENVIRONMENT=production|staging|development"
            echo "  ENABLE_MONITORING=true|false"
            echo ""
            ;;
        *)
            error_exit "Unknown command: $1. Use --help for usage information."
            ;;
    esac
}

# Run main function
main "$@"