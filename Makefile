# SmartCompute v3.0.0 Development Makefile

.PHONY: help install install-dev test test-fast lint format format-check type-check security ci start-dev docker-build docker-run docker-compose-up docs clean setup-dev info

# Colors for output
GREEN := \033[0;32m
BLUE := \033[0;34m
YELLOW := \033[1;33m
RED := \033[0;31m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(BLUE)SmartCompute v3.0.0 Development Commands$(NC)"
	@echo "========================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

install: ## Install package in editable mode
	@echo "$(YELLOW)Installing SmartCompute...$(NC)"
	python -m pip install --upgrade pip
	pip install -e .
	@echo "$(GREEN)Installed (Starter tier)$(NC)"

install-dev: ## Install with dev dependencies
	@echo "$(YELLOW)Installing dev dependencies...$(NC)"
	python -m pip install --upgrade pip
	pip install -e ".[dev]"
	@echo "$(GREEN)Dev environment ready$(NC)"

test: ## Run test suite with coverage
	@echo "$(YELLOW)Running test suite...$(NC)"
	pytest --cov=smartcompute --cov-report=html --cov-report=term tests/ -v
	@echo "$(GREEN)Tests completed$(NC)"

test-fast: ## Run tests without coverage (faster)
	@echo "$(YELLOW)Running fast tests...$(NC)"
	pytest tests/ -v -x
	@echo "$(GREEN)Fast tests completed$(NC)"

lint: ## Run linting checks
	@echo "$(YELLOW)Running linting checks...$(NC)"
	flake8 src/smartcompute/ --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 src/smartcompute/ --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
	@echo "$(GREEN)Linting completed$(NC)"

format: ## Format code with black and isort
	@echo "$(YELLOW)Formatting code...$(NC)"
	black src/smartcompute/ tests/
	isort src/smartcompute/ tests/
	@echo "$(GREEN)Code formatted$(NC)"

format-check: ## Check code formatting without changes
	@echo "$(YELLOW)Checking code formatting...$(NC)"
	black --check --diff src/smartcompute/ tests/
	isort --check-only --diff src/smartcompute/ tests/
	@echo "$(GREEN)Format check completed$(NC)"

type-check: ## Run type checking with mypy
	@echo "$(YELLOW)Running type checks...$(NC)"
	mypy src/smartcompute/ --ignore-missing-imports --no-strict-optional
	@echo "$(GREEN)Type checking completed$(NC)"

security: ## Run security scans
	@echo "$(YELLOW)Running security scans...$(NC)"
	bandit -r src/smartcompute/ -ll || true
	@echo "$(GREEN)Security scans completed$(NC)"

ci: ## Run full CI pipeline locally
	@echo "$(BLUE)Running full CI pipeline locally...$(NC)"
	make lint
	make format-check
	make type-check
	make security
	make test
	@echo "$(GREEN)Full CI pipeline completed$(NC)"

start-dev: ## Start development server
	@echo "$(YELLOW)Starting development server...$(NC)"
	smartcompute serve --port 5000

docker-build: ## Build Docker image
	@echo "$(YELLOW)Building Docker image...$(NC)"
	docker build -t smartcompute:3.0.0 .
	@echo "$(GREEN)Docker image built$(NC)"

docker-run: ## Run Docker container
	@echo "$(YELLOW)Running Docker container...$(NC)"
	docker run -p 5000:5000 smartcompute:3.0.0

docker-compose-up: ## Start with Docker Compose
	@echo "$(YELLOW)Starting with Docker Compose...$(NC)"
	docker-compose up

docs: ## Generate documentation
	@echo "$(YELLOW)Generating documentation...$(NC)"
	sphinx-build -b html docs/ docs/_build/html || echo "Documentation setup needed"
	@echo "$(GREEN)Documentation task completed$(NC)"

clean: ## Clean temporary files
	@echo "$(YELLOW)Cleaning temporary files...$(NC)"
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .coverage htmlcov/ .pytest_cache/ .mypy_cache/
	rm -rf dist/ build/ *.egg-info/ src/*.egg-info/
	rm -f safety-report.json bandit-report.json coverage.xml
	@echo "$(GREEN)Temporary files cleaned$(NC)"

setup-dev: ## Full development setup
	@echo "$(BLUE)Setting up development environment...$(NC)"
	make install-dev
	cp .env.example .env 2>/dev/null || true
	@echo "$(GREEN)Development environment ready$(NC)"

info: ## Show project information
	@echo "$(BLUE)SmartCompute v3.0.0 Info$(NC)"
	@echo "========================"
	@echo "Starter:    Free monitoring + dashboard (pip install smartcompute[free])"
	@echo "Enterprise: XDR/SIEM/ML (pip install smartcompute[enterprise])"
	@echo "            (enterprise includes free dependencies)"
	@echo "Industrial: SCADA/protocols (pip install smartcompute[industrial])"
	@echo ""
	@echo "Commands:   smartcompute --help"
	@echo "Tests:      make test"
	@echo "Security:   make security"
