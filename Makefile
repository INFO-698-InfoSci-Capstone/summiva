# -----------------------------
# 🛠️ Configuration
# -----------------------------
SERVICE_NAME ?= summarization
ENVIRONMENT ?= production
PORT ?= 8000
IMAGE_NAME = summiva-service
USER_ID ?= 1000

# Microservices and fixed ports
SERVICES = summarization tagging grouping search clustering
PORTS = 8001 8002 8003 8004 8005

# -----------------------------
# 🚀 Docker Compose Targets
# -----------------------------
COMPOSE_PROJECT_NAME = summiva

.PHONY: compose-up
compose-up:
	docker-compose -f docker-compose.yml \
		--project-name $(COMPOSE_PROJECT_NAME) \
		--profile postgres --profile redis --profile mongodb --profile dev up

.PHONY: compose-down
compose-down:
	docker-compose -f docker-compose.yml \
		--project-name $(COMPOSE_PROJECT_NAME) \
		down --remove-orphans

# -----------------------------
# 🔧 Docker Image Build
# -----------------------------
.PHONY: docker-build
docker-build:
	docker build -t $(IMAGE_NAME) --build-arg USER_ID=$(USER_ID) .

# -----------------------------
# ▶️ Run a Single Service (Prod)
# -----------------------------
.PHONY: run-prod
run-prod:
	docker run --rm \
		-e SERVICE_NAME=$(SERVICE_NAME) \
		-e ENVIRONMENT=$(ENVIRONMENT) \
		-p $(PORT):8000 \
		$(IMAGE_NAME)

# -----------------------------
# ▶️ Run a Single Service (Dev)
# -----------------------------
.PHONY: run-dev
run-dev:
	docker run --rm \
		-e SERVICE_NAME=$(SERVICE_NAME) \
		-e ENVIRONMENT=development \
		-v $(shell pwd)/src:/app/src \
		-p $(PORT):8000 \
		$(IMAGE_NAME)

# -----------------------------
# ▶️ Run All Services in Background
# -----------------------------
.PHONY: run-all
run-all: docker-build
	@i=0; \
	for service in $(SERVICES); do \
		port=$$(echo $(PORTS) | cut -d' ' -f $$((i+1))); \
		echo "🚀 Starting $$service on port $$port..."; \
		docker run -d \
			-e SERVICE_NAME=$$service \
			-e ENVIRONMENT=$(ENVIRONMENT) \
			-p $$port:8000 \
			--name summiva-$$service \
			$(IMAGE_NAME); \
		i=$$((i+1)); \
	done

# -----------------------------
# ⏹ Stop All Background Services
# -----------------------------
.PHONY: stop-all
stop-all:
	@for service in $(SERVICES); do \
		echo "🛑 Stopping $$service..."; \
		docker stop summiva-$$service 2>/dev/null || true; \
	done

# -----------------------------
# 🧹 Clean Docker Artifacts
# -----------------------------
.PHONY: clean
clean:
	docker system prune -f

# -----------------------------
# 📦 Install Python Dependencies
# -----------------------------
.PHONY: install-deps
install-deps:
	docker run --rm \
		-v $(shell pwd)/src:/app/src \
		-w /app/src/$(SERVICE_NAME) \
		$(IMAGE_NAME) pip install -r requirements.txt

# -----------------------------
# 🔥 Remove ALL Docker Resources
# -----------------------------
.PHONY: nuke-docker
nuke-docker:
	@echo "⚠️  WARNING: This will remove all Docker containers, images, volumes, and networks!"
	@read -p "Are you sure you want to proceed? (y/N): " confirm; \
	if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
		echo "🔥 Removing EVERYTHING..."; \
		docker container prune -f && \
		docker image prune -a -f && \
		docker volume prune -f && \
		docker network prune -f; \
	else \
		echo "❌ Operation cancelled."; \
	fi

# -----------------------------
# 📘 Help
# -----------------------------
.PHONY: help
help:
	@echo "🛠️  Available Targets:"
	@echo "  docker-build     - Build the Docker image"
	@echo "  run-prod         - Run one service in production mode"
	@echo "  run-dev          - Run one service in development mode"
	@echo "  run-auth-dev     - Run the Auth service in development mode with dependencies"
	@echo "  run-all          - Build and run all services with fixed ports"
	@echo "  stop-all         - Stop all running services"
	@echo "  clean            - Prune unused Docker resources"
	@echo "  install-deps     - Install Python dependencies into service"
	@echo "  nuke-docker      - Remove ALL Docker containers, images, volumes, and networks"
	@echo "  compose-up       - Start all services using Docker Compose"
	@echo "  compose-down     - Stop and remove Docker Compose containers"
	@echo "  help             - Show this help message"