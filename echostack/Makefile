# EchoStack Makefile
# Comprehensive build, test, and deployment commands

.PHONY: help build up down restart logs clean test lint format docker-build docker-push deploy dev prod

# Default target
help: ## Show this help message
	@echo "EchoStack Development Commands"
	@echo "=============================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Development commands
dev: ## Start development environment
	docker-compose -f docker-compose.yml -f docker-compose.override.yml up --build

dev-monitoring: ## Start development environment with monitoring
	docker-compose -f docker-compose.yml -f docker-compose.override.yml --profile monitoring up --build

# Production commands
prod: ## Start production environment
	docker-compose up -d --build

prod-monitoring: ## Start production environment with monitoring
	docker-compose --profile monitoring up -d --build

# Basic Docker Compose commands
build: ## Build all services
	docker-compose build

up: ## Start all services
	docker-compose up -d

down: ## Stop all services
	docker-compose down

restart: ## Restart all services
	docker-compose restart

logs: ## Show logs from all services
	docker-compose logs -f

logs-echostack: ## Show logs from echostack service
	docker-compose logs -f echostack

# Database commands
db-init: ## Initialize database
	docker-compose exec echostack_db psql -U echostack -d echostack -f /docker-entrypoint-initdb.d/init.sql

db-shell: ## Open database shell
	docker-compose exec echostack_db psql -U echostack -d echostack

db-reset: ## Reset database (WARNING: destroys data)
	docker-compose down -v
	docker-compose up -d echostack_db
	sleep 10
	make db-init

# Redis commands
redis-shell: ## Open Redis shell
	docker-compose exec echostack_redis redis-cli

# Testing commands
test: ## Run tests
	docker-compose exec echostack python -m pytest tests/ -v

test-coverage: ## Run tests with coverage
	docker-compose exec echostack python -m pytest tests/ --cov=echostack_module --cov-report=html

lint: ## Run linting
	docker-compose exec echostack flake8 echostack_module tests
	docker-compose exec echostack mypy echostack_module

format: ## Format code
	docker-compose exec echostack black echostack_module tests
	docker-compose exec echostack isort echostack_module tests

# Docker commands
docker-build: ## Build Docker image
	docker build -t echostack:latest .

docker-push: ## Push Docker image to registry
	docker tag echostack:latest your-registry/echostack:latest
	docker push your-registry/echostack:latest

# Cleanup commands
clean: ## Remove containers, networks, and volumes
	docker-compose down -v --remove-orphans

clean-images: ## Remove Docker images
	docker-compose down --rmi all

clean-all: ## Complete cleanup
	docker-compose down -v --remove-orphans --rmi all
	docker system prune -f

# Health checks
health: ## Check health of all services
	@echo "Checking EchoStack health..."
	@curl -f http://localhost:8003/health || echo "EchoStack is not healthy"
	@echo "Checking PostgreSQL..."
	@docker-compose exec echostack_db pg_isready -U echostack || echo "PostgreSQL is not healthy"
	@echo "Checking Redis..."
	@docker-compose exec echostack_redis redis-cli ping || echo "Redis is not healthy"

# Deployment
deploy: ## Deploy to production (customize for your environment)
	@echo "Deploying EchoStack to production..."
	# Add your deployment commands here
	# Example: kubectl apply -f k8s/
	# Example: ansible-playbook deploy.yml

# Development utilities
shell: ## Open shell in echostack container
	docker-compose exec echostack bash

python-shell: ## Open Python shell in echostack container
	docker-compose exec echostack python

update-deps: ## Update Python dependencies
	docker-compose exec echostack pip install --upgrade -r requirements.txt

# Monitoring
monitoring-up: ## Start monitoring stack
	docker-compose --profile monitoring up -d

monitoring-down: ## Stop monitoring stack
	docker-compose --profile monitoring down

grafana-url: ## Show Grafana URL
	@echo "Grafana: http://localhost:3000 (admin/admin2025)"

prometheus-url: ## Show Prometheus URL
	@echo "Prometheus: http://localhost:9090"