#!/bin/bash
# SmartCompute Build Script

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Build information
BUILD_DATE=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
VCS_REF=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")
VERSION=${1:-"1.0.0"}

echo "🏗️  Building SmartCompute Docker images..."
echo "Version: $VERSION"
echo "VCS Ref: $VCS_REF"
echo "Build Date: $BUILD_DATE"
echo ""

# Build main application image
print_status "Building main application image..."
docker build \
    --build-arg BUILD_DATE="$BUILD_DATE" \
    --build-arg VCS_REF="$VCS_REF" \
    --build-arg VERSION="$VERSION" \
    -t smartcompute:latest \
    -t smartcompute:$VERSION \
    .

# Build test image
print_status "Building test image..."
docker build \
    -f Dockerfile.test \
    -t smartcompute:test \
    .

# Run security scan if trivy is available
if command -v trivy &> /dev/null; then
    print_status "Running security scan..."
    trivy image smartcompute:latest
else
    print_warning "Trivy not found, skipping security scan"
fi

# Run basic smoke test
print_status "Running smoke test..."
docker run --rm smartcompute:test python -c "
import app.core.smart_compute
import app.core.portable_system
print('✅ All modules imported successfully')
"

print_status "Build completed successfully!"
echo ""
echo "Available images:"
echo "- smartcompute:latest"
echo "- smartcompute:$VERSION"
echo "- smartcompute:test"
echo ""
echo "To run: docker compose up -d"