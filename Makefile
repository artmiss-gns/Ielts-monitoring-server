# Makefile for IELTS Monitoring System Docker Management

.PHONY: help build up down logs shell clean backup restore test

# Default target
help: ## Show this help message
	@echo "🐳 IELTS Monitoring System - Docker Management"
	@echo ""
	@echo "Available commands:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# Build commands
build: ## Build Docker image
	@echo "🔨 Building Docker image..."
	./docker/docker-build.sh --type production

build-dev: ## Build development Docker image
	@echo "🔨 Building development Docker image..."
	./docker/docker-build.sh --type development

# Deployment commands
up: ## Start services in production mode
	@echo "🚀 Starting IELTS monitoring system..."
	docker compose up -d

up-dev: ## Start services in development mode
	@echo "🚀 Starting development environment..."
	docker compose --profile dev up -d

up-prod: ## Deploy to production (use Koyeb - see docs/KOYEB_DEPLOYMENT.md)
	@echo "⚠️  For production deployment, use Koyeb platform"
	@echo "📖 See docs/KOYEB_DEPLOYMENT.md for deployment guide"
	@echo "🐳 Building production image..."
	docker build --target production -t ielts-monitor:latest .

up-sim: ## Start with simulation server
	@echo "🚀 Starting with simulation server..."
	docker compose --profile simulation up -d

up-monitoring: ## Start with full monitoring stack
	@echo "🚀 Starting with monitoring stack..."
	docker compose --profile monitoring up -d

# Management commands
down: ## Stop all services
	@echo "🛑 Stopping services..."
	docker compose down

restart: ## Restart main service
	@echo "🔄 Restarting IELTS monitor..."
	docker compose restart ielts-monitor

# Monitoring commands
logs: ## Show logs for main service
	docker compose logs -f ielts-monitor

logs-all: ## Show logs for all services
	docker compose logs -f

status: ## Show service status
	@echo "📊 Service Status:"
	docker compose ps
	@echo ""
	@echo "📈 Resource Usage:"
	docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"

health: ## Check service health
	@echo "🏥 Health Check:"
	docker compose exec ielts-monitor python -c "import sys; print('✅ Service is healthy'); sys.exit(0)" || echo "❌ Service is unhealthy"

# Development commands
shell: ## Open shell in running container
	docker compose exec ielts-monitor /bin/bash

shell-root: ## Open root shell in running container
	docker compose exec --user root ielts-monitor /bin/bash

test: ## Run tests in container
	@echo "🧪 Running tests..."
	docker compose exec ielts-monitor python -m pytest tests/ -v

test-once: ## Run single monitoring check
	@echo "🔍 Running single check..."
	docker compose exec ielts-monitor python -m src.ielts_monitor --once --verbose

# Data management
backup: ## Backup persistent data
	@echo "💾 Creating backup..."
	@mkdir -p backups
	docker run --rm -v ielts-monitor-data:/data -v $(PWD)/backups:/backup alpine tar czf /backup/ielts-data-$(shell date +%Y%m%d-%H%M%S).tar.gz -C /data .
	@echo "✅ Backup created in backups/ directory"

restore: ## Restore from backup (specify BACKUP_FILE=filename)
	@if [ -z "$(BACKUP_FILE)" ]; then \
		echo "❌ Please specify BACKUP_FILE=filename"; \
		echo "Available backups:"; \
		ls -la backups/; \
		exit 1; \
	fi
	@echo "📥 Restoring from $(BACKUP_FILE)..."
	docker run --rm -v ielts-monitor-data:/data -v $(PWD)/backups:/backup alpine tar xzf /backup/$(BACKUP_FILE) -C /data
	@echo "✅ Restore completed"

clear-state: ## Clear notification state
	@echo "🗑️ Clearing notification state..."
	docker compose exec ielts-monitor rm -f /app/data/notification_state.json
	@echo "✅ Notification state cleared"

# Maintenance commands
update: ## Pull latest images and restart
	@echo "🔄 Updating system..."
	docker compose pull
	docker compose up -d
	@echo "✅ Update completed"

clean: ## Clean up unused Docker resources
	@echo "🧹 Cleaning up Docker resources..."
	docker system prune -f
	docker volume prune -f
	@echo "✅ Cleanup completed"

clean-all: ## Clean up all Docker resources (including images)
	@echo "🧹 Cleaning up all Docker resources..."
	docker compose down --rmi all --volumes --remove-orphans
	docker system prune -af
	@echo "✅ Complete cleanup finished"

# Configuration commands
config: ## Validate and show configuration
	@echo "⚙️ Docker Compose Configuration:"
	docker compose config

config-prod: ## Show production deployment info
	@echo "⚙️ Production Deployment:"
	@echo "🌐 Platform: Koyeb (serverless)"
	@echo "📖 Guide: docs/KOYEB_DEPLOYMENT.md"
	@echo "🐳 Image: docker build --target production -t ielts-monitor ."

edit-config: ## Edit configuration file
	${EDITOR:-nano} config.yaml

# Koyeb deployment
koyeb-build: ## Build and tag image for Koyeb deployment
	@echo "🐳 Building image for Koyeb..."
	docker build --target production -t ielts-monitor:koyeb .
	@echo "✅ Image built successfully!"
	@echo "📝 Next steps:"
	@echo "  1. Tag: docker tag ielts-monitor:koyeb your-username/ielts-monitor:latest"
	@echo "  2. Push: docker push your-username/ielts-monitor:latest"
	@echo "  3. Deploy on Koyeb using the pushed image"
	@echo "📖 Full guide: docs/KOYEB_DEPLOYMENT.md"

# Quick commands
quick-start: build up logs ## Build, start, and show logs
quick-dev: build-dev up-dev logs ## Quick development setup
quick-prod: build config-prod ## Quick production setup

# Information commands
info: ## Show system information
	@echo "ℹ️ System Information:"
	@echo "Docker version: $(shell docker --version)"
	@echo "Docker Compose version: $(shell docker-compose --version)"
	@echo "Available memory: $(shell free -h | awk '/^Mem:/ {print $$2}' 2>/dev/null || echo 'N/A')"
	@echo "Available disk space: $(shell df -h . | awk 'NR==2 {print $$4}' 2>/dev/null || echo 'N/A')"
	@echo ""
	@echo "📁 Project structure:"
	@ls -la | grep -E "(docker|config|src)"

# Development helpers
dev-setup: ## Setup development environment
	@echo "🛠️ Setting up development environment..."
	@mkdir -p logs data
	@chmod +x docker/docker-entrypoint.sh docker/docker-build.sh
	@echo "✅ Development environment ready"

# Production helpers
prod-deploy: build config-prod up-prod status ## Complete production deployment
	@echo "🎉 Production deployment completed!"
	@echo "Monitor logs with: make logs"
	@echo "Check status with: make status"
