# Makefile for Aura Audit AI Python Monorepo
# Provides automation for common development, testing, and deployment tasks

.PHONY: help install install-dev install-libs test test-service test-coverage lint format type-check security-check pre-commit clean docker-build docker-up docker-down docs

# Default target
.DEFAULT_GOAL := help

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

##@ General

help: ## Display this help message
	@echo "$(BLUE)Aura Audit AI - Development Commands$(NC)"
	@echo ""
	@awk 'BEGIN {FS = ":.*##"; printf "Usage:\n  make $(YELLOW)<target>$(NC)\n"} /^[a-zA-Z_0-9-]+:.*?##/ { printf "  $(BLUE)%-20s$(NC) %s\n", $$1, $$2 } /^##@/ { printf "\n$(GREEN)%s$(NC)\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Installation

install: ## Install all dependencies for all services
	@echo "$(BLUE)Installing dependencies for all services...$(NC)"
	@pip install -e lib/service_client
	@pip install -e lib/event_bus
	@pip install -e lib/common_core
	@for dir in services/*/; do \
		if [ -f "$$dir/requirements.txt" ]; then \
			echo "$(GREEN)Installing $$dir$(NC)"; \
			pip install -r "$$dir/requirements.txt"; \
		fi; \
	done
	@echo "$(GREEN)✓ All dependencies installed$(NC)"

install-dev: ## Install development dependencies
	@echo "$(BLUE)Installing development dependencies...$(NC)"
	@pip install -e ".[dev]"
	@pre-commit install
	@echo "$(GREEN)✓ Development environment ready$(NC)"

install-libs: ## Install shared libraries only
	@echo "$(BLUE)Installing shared libraries...$(NC)"
	@pip install -e lib/service_client
	@pip install -e lib/event_bus
	@pip install -e lib/common_core
	@echo "$(GREEN)✓ Shared libraries installed$(NC)"

##@ Code Quality

lint: ## Run linter (ruff) on all services
	@echo "$(BLUE)Running ruff linter...$(NC)"
	@ruff check services/ lib/ --fix
	@echo "$(GREEN)✓ Linting complete$(NC)"

format: ## Format code with black and isort
	@echo "$(BLUE)Formatting code...$(NC)"
	@black services/ lib/ --line-length 100
	@isort services/ lib/ --profile black
	@echo "$(GREEN)✓ Code formatted$(NC)"

type-check: ## Run type checking with mypy
	@echo "$(BLUE)Running mypy type checker...$(NC)"
	@mypy services/ --ignore-missing-imports
	@echo "$(GREEN)✓ Type checking complete$(NC)"

security-check: ## Run security scanner (bandit)
	@echo "$(BLUE)Running security scanner...$(NC)"
	@bandit -r services/ lib/ -c pyproject.toml
	@echo "$(GREEN)✓ Security scan complete$(NC)"

pre-commit: ## Run pre-commit hooks on all files
	@echo "$(BLUE)Running pre-commit hooks...$(NC)"
	@pre-commit run --all-files
	@echo "$(GREEN)✓ Pre-commit checks complete$(NC)"

##@ Testing

test: ## Run all tests with pytest
	@echo "$(BLUE)Running all tests...$(NC)"
	@pytest services/ -v --tb=short --cov=services --cov-report=term-missing --cov-report=html
	@echo "$(GREEN)✓ Tests complete$(NC)"
	@echo "$(YELLOW)Coverage report: htmlcov/index.html$(NC)"

test-service: ## Run tests for a specific service (usage: make test-service SERVICE=identity)
	@if [ -z "$(SERVICE)" ]; then \
		echo "$(RED)Error: SERVICE not specified$(NC)"; \
		echo "Usage: make test-service SERVICE=identity"; \
		exit 1; \
	fi
	@echo "$(BLUE)Running tests for $(SERVICE) service...$(NC)"
	@cd services/$(SERVICE) && pytest tests/ -v --tb=short --cov=app --cov-report=term-missing
	@echo "$(GREEN)✓ Tests complete for $(SERVICE)$(NC)"

test-coverage: ## Run tests with detailed coverage report
	@echo "$(BLUE)Running tests with coverage...$(NC)"
	@pytest services/ -v --cov=services --cov-report=term-missing --cov-report=html --cov-report=xml --cov-fail-under=70
	@echo "$(GREEN)✓ Coverage report generated$(NC)"
	@echo "$(YELLOW)HTML report: htmlcov/index.html$(NC)"
	@echo "$(YELLOW)XML report: coverage.xml$(NC)"

test-fast: ## Run tests without coverage (faster)
	@echo "$(BLUE)Running fast tests...$(NC)"
	@pytest services/ -v --tb=short -x
	@echo "$(GREEN)✓ Fast tests complete$(NC)"

test-integration: ## Run integration tests only
	@echo "$(BLUE)Running integration tests...$(NC)"
	@pytest services/ -v -m integration
	@echo "$(GREEN)✓ Integration tests complete$(NC)"

test-unit: ## Run unit tests only
	@echo "$(BLUE)Running unit tests...$(NC)"
	@pytest services/ -v -m unit
	@echo "$(GREEN)✓ Unit tests complete$(NC)"

##@ Docker

docker-build: ## Build all Docker images
	@echo "$(BLUE)Building Docker images...$(NC)"
	@docker-compose build
	@echo "$(GREEN)✓ Docker images built$(NC)"

docker-up: ## Start all services with Docker Compose
	@echo "$(BLUE)Starting services...$(NC)"
	@docker-compose up -d
	@echo "$(GREEN)✓ Services started$(NC)"
	@echo "$(YELLOW)View logs: docker-compose logs -f$(NC)"

docker-down: ## Stop all Docker services
	@echo "$(BLUE)Stopping services...$(NC)"
	@docker-compose down
	@echo "$(GREEN)✓ Services stopped$(NC)"

docker-logs: ## View Docker logs
	@docker-compose logs -f

docker-ps: ## Show running containers
	@docker-compose ps

##@ Database

db-migrate: ## Run database migrations
	@echo "$(BLUE)Running database migrations...$(NC)"
	@cd database && psql $(DATABASE_URL) -f migrations/0001_init.sql
	@echo "$(GREEN)✓ Migrations complete$(NC)"

db-reset: ## Reset database (⚠️  DESTRUCTIVE)
	@echo "$(RED)⚠️  This will delete all data!$(NC)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker-compose down -v; \
		docker-compose up -d db; \
		sleep 3; \
		make db-migrate; \
	fi

##@ Code Analysis

sloc: ## Count source lines of code
	@echo "$(BLUE)Counting source lines of code...$(NC)"
	@echo "$(YELLOW)Python:$(NC)"
	@find services -name "*.py" -not -path "*/tests/*" -not -path "*/__pycache__/*" | xargs wc -l | tail -1
	@echo "$(YELLOW)TypeScript/JavaScript:$(NC)"
	@find frontend admin-portal client-portal -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name "*.jsx" | wc -l
	@echo "$(GREEN)✓ SLOC analysis complete$(NC)"

complexity: ## Analyze code complexity
	@echo "$(BLUE)Analyzing code complexity...$(NC)"
	@radon cc services/ -a -s
	@echo "$(GREEN)✓ Complexity analysis complete$(NC)"

deps-check: ## Check for outdated dependencies
	@echo "$(BLUE)Checking for outdated dependencies...$(NC)"
	@pip list --outdated
	@echo "$(GREEN)✓ Dependency check complete$(NC)"

deps-audit: ## Audit dependencies for security vulnerabilities
	@echo "$(BLUE)Auditing dependencies...$(NC)"
	@pip-audit
	@echo "$(GREEN)✓ Security audit complete$(NC)"

##@ Documentation

docs: ## Generate API documentation
	@echo "$(BLUE)Generating documentation...$(NC)"
	@echo "$(YELLOW)API docs available at:$(NC)"
	@echo "  - Identity: http://localhost:8000/docs"
	@echo "  - Analytics: http://localhost:8001/docs"
	@echo "  - Engagement: http://localhost:8002/docs"
	@echo "$(GREEN)✓ Documentation ready$(NC)"

##@ Utilities

clean: ## Clean build artifacts, cache files, and test outputs
	@echo "$(BLUE)Cleaning build artifacts...$(NC)"
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete
	@find . -type f -name "*.pyo" -delete
	@find . -type f -name ".coverage" -delete
	@rm -rf htmlcov/ coverage.xml .coverage
	@rm -rf dist/ build/
	@echo "$(GREEN)✓ Cleanup complete$(NC)"

check: format lint type-check test ## Run all quality checks (format, lint, type-check, test)
	@echo "$(GREEN)✓ All checks passed!$(NC)"

ci: ## Run CI pipeline locally
	@echo "$(BLUE)Running CI pipeline...$(NC)"
	@make format
	@make lint
	@make type-check
	@make security-check
	@make test-coverage
	@echo "$(GREEN)✓ CI pipeline complete$(NC)"

services-status: ## Check status of all services
	@echo "$(BLUE)Checking service status...$(NC)"
	@for port in 8000 8001 8002 8003 8004 8005 8006 8007 8008 8009; do \
		service=$$(curl -s http://localhost:$$port/health 2>/dev/null | jq -r '.service // "offline"'); \
		if [ "$$service" != "offline" ]; then \
			echo "$(GREEN)✓ Port $$port: $$service$(NC)"; \
		else \
			echo "$(RED)✗ Port $$port: offline$(NC)"; \
		fi; \
	done

dev-setup: install-dev install-libs ## Complete development environment setup
	@echo "$(GREEN)✓ Development environment ready!$(NC)"
	@echo "$(YELLOW)Next steps:$(NC)"
	@echo "  1. Copy .env.example to .env and configure"
	@echo "  2. Run: make docker-up"
	@echo "  3. Run: make db-migrate"
	@echo "  4. Run: make test"
