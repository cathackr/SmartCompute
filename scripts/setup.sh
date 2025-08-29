#!/bin/bash
# SmartCompute Setup Script

set -e

echo "🚀 Setting up SmartCompute..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if Python 3.11+ is available
check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        if (( $(echo "$PYTHON_VERSION >= 3.9" | bc -l) )); then
            print_status "Python $PYTHON_VERSION detected"
            return 0
        else
            print_error "Python 3.9+ required, found $PYTHON_VERSION"
            return 1
        fi
    else
        print_error "Python 3 not found"
        return 1
    fi
}

# Create virtual environment
setup_venv() {
    print_status "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip setuptools wheel
    print_status "Virtual environment created"
}

# Install dependencies
install_dependencies() {
    print_status "Installing dependencies..."
    if [ -f "requirements-core.txt" ]; then
        pip install -r requirements-core.txt
    else
        print_error "requirements-core.txt not found"
        return 1
    fi
    print_status "Dependencies installed"
}

# Setup database
setup_database() {
    print_status "Setting up database..."
    if [ ! -f ".env" ]; then
        cp .env.example .env
        print_status "Environment file created from template"
        print_warning "Please edit .env file with your configuration"
    fi
    
    # Run database migrations
    alembic upgrade head
    print_status "Database migrations completed"
}

# Run tests
run_tests() {
    print_status "Running tests..."
    python -m pytest tests/ -v --tb=short
    if [ $? -eq 0 ]; then
        print_status "All tests passed"
    else
        print_warning "Some tests failed, but continuing setup"
    fi
}

# Create necessary directories
create_directories() {
    mkdir -p data logs reports
    print_status "Created necessary directories"
}

# Main setup function
main() {
    echo "SmartCompute Setup Script"
    echo "=========================="
    
    if ! check_python; then
        exit 1
    fi
    
    setup_venv
    install_dependencies
    create_directories
    setup_database
    run_tests
    
    echo ""
    print_status "Setup completed successfully!"
    echo ""
    echo "Next steps:"
    echo "1. Activate virtual environment: source venv/bin/activate"
    echo "2. Edit .env file with your configuration"
    echo "3. Start the application: python main.py"
    echo "4. Or start API server: python main.py --api"
    echo ""
    echo "For Docker deployment:"
    echo "docker compose up -d"
    echo ""
    echo "Happy monitoring! 🛡️"
}

# Run main function
main "$@"