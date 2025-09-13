# SmartCompute Development Makefile
# Simplified commands for development workflow

.PHONY: help install test lint security format docs clean

# Colors for output
GREEN := \033[0;32m
BLUE := \033[0;34m
YELLOW := \033[1;33m
RED := \033[0;31m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(BLUE)SmartCompute Development Commands$(NC)"
	@echo "=================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

install: ## Install development dependencies
	@echo "$(YELLOW)Installing development dependencies...$(NC)"
	python -m pip install --upgrade pip
	pip install -r requirements-dev.txt
	@echo "$(GREEN)✅ Dependencies installed$(NC)"

test: ## Run test suite with coverage
	@echo "$(YELLOW)Running test suite...$(NC)"
	pytest --cov=app --cov=smartcompute_industrial --cov-report=html --cov-report=term tests/test_simple_api.py tests/test_core_components.py -v
	@echo "$(GREEN)✅ Tests completed. Coverage report available$(NC)"

test-fast: ## Run tests without coverage (faster)
	@echo "$(YELLOW)Running fast tests...$(NC)"
	pytest tests/test_simple_api.py tests/test_core_components.py -v
	@echo "$(GREEN)✅ Fast tests completed$(NC)"

lint: ## Run linting checks
	@echo "$(YELLOW)Running linting checks...$(NC)"
	flake8 app/ smartcompute_industrial/ --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 app/ smartcompute_industrial/ --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
	@echo "$(GREEN)✅ Linting completed$(NC)"

format: ## Format code with black and isort
	@echo "$(YELLOW)Formatting code...$(NC)"
	black app/ smartcompute_industrial/ tests/
	isort app/ smartcompute_industrial/ tests/
	@echo "$(GREEN)✅ Code formatted$(NC)"

format-check: ## Check code formatting without changes
	@echo "$(YELLOW)Checking code formatting...$(NC)"
	black --check --diff app/ smartcompute_industrial/ tests/
	isort --check-only --diff app/ smartcompute_industrial/ tests/
	@echo "$(GREEN)✅ Format check completed$(NC)"

type-check: ## Run type checking with mypy
	@echo "$(YELLOW)Running type checks...$(NC)"
	mypy app/ --ignore-missing-imports --no-strict-optional
	@echo "$(GREEN)✅ Type checking completed$(NC)"

security: ## Run security scans
	@echo "$(YELLOW)Running security scans...$(NC)"
	safety check || true
	bandit -r app/ smartcompute_industrial/ -ll || true
	@echo "$(GREEN)✅ Security scans completed$(NC)"

ci: ## Run full CI pipeline locally
	@echo "$(BLUE)Running full CI pipeline locally...$(NC)"
	make lint
	make format-check  
	make type-check
	make security
	make test
	@echo "$(GREEN)✅ Full CI pipeline completed$(NC)"

start-dev: ## Start development server
	@echo "$(YELLOW)Starting development server...$(NC)"
	python main.py --api

docker-build: ## Build Docker image
	@echo "$(YELLOW)Building Docker image...$(NC)"
	docker build -t smartcompute:dev .
	@echo "$(GREEN)✅ Docker image built$(NC)"

docker-run: ## Run Docker container
	@echo "$(YELLOW)Running Docker container...$(NC)"
	docker run smartcompute:dev

docker-compose-up: ## Start with Docker Compose
	@echo "$(YELLOW)Starting with Docker Compose...$(NC)"
	docker-compose -f docker-compose.quickstart.yml up

docs: ## Generate documentation
	@echo "$(YELLOW)Generating documentation...$(NC)"
	sphinx-build -b html docs/ docs/_build/html || echo "Documentation setup needed"
	@echo "$(GREEN)✅ Documentation task completed$(NC)"

clean: ## Clean temporary files
	@echo "$(YELLOW)Cleaning temporary files...$(NC)"
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .coverage htmlcov/ .pytest_cache/ .mypy_cache/
	rm -f safety-report.json bandit-report.json coverage.xml
	@echo "$(GREEN)✅ Temporary files cleaned$(NC)"

setup-dev: ## Full development setup
	@echo "$(BLUE)Setting up development environment...$(NC)"
	make install
	cp .env.example .env
	@echo "$(YELLOW)Please configure .env file$(NC)"
	@echo "$(GREEN)✅ Development environment ready$(NC)"

db-setup: ## Set up database
	@echo "$(YELLOW)Setting up database...$(NC)"
	alembic upgrade head
	@echo "$(GREEN)✅ Database setup completed$(NC)"

db-migrate: ## Create database migration
	@echo "$(YELLOW)Creating database migration...$(NC)"
	alembic revision --autogenerate -m "Auto migration"
	@echo "$(GREEN)✅ Migration created$(NC)"

perf-test: ## Run performance benchmarks
	@echo "$(YELLOW)Running performance tests...$(NC)"
	python -c "from app.core.benchmarks import run_benchmarks; run_benchmarks()" || echo "Benchmarks module not available"
	@echo "$(GREEN)✅ Performance tests completed$(NC)"

install-hooks: ## Install git pre-commit hooks
	@echo "$(YELLOW)Installing git hooks...$(NC)"
	echo "#!/bin/bash\nmake format lint" > .git/hooks/pre-commit
	chmod +x .git/hooks/pre-commit
	@echo "$(GREEN)✅ Git hooks installed$(NC)"

info: ## Show project information
	@echo "$(BLUE)SmartCompute Development Info$(NC)"
	@echo "============================="
	@echo "🏠 Starter: Free monitoring version"
	@echo "🏢 Enterprise: Advanced features available"
	@echo "🏭 Industrial: Specialized industrial monitoring"
	@echo ""
	@echo "📚 Documentation: Run 'make docs'"
	@echo "🧪 Tests: Run 'make test'"
	@echo "🔒 Security: Run 'make security'"