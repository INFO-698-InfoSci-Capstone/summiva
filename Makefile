# -----------------------------
# 🛠️ Configuration
# -----------------------------
SERVICE_NAME ?= summarization
ENVIRONMENT ?= production
PORT ?= 8000
IMAGE_NAME = summiva-service
USER_ID ?= 1000

SERVICES = summarization tagging grouping search clustering
PORTS = 8001 8002 8003 8004 8005

COMPOSE_PROJECT_NAME = summiva

# -----------------------------
# 🚀 Docker Compose
# -----------------------------
.PHONY: compose-up
compose-up:
	docker-compose -f docker-compose.yml \
		--project-name $(COMPOSE_PROJECT_NAME) \
		--profile postgres --profile redis --profile mongodb --profile dev up

.PHONY: compose-down
compose-down:
	docker-compose -f docker-compose.yml \
		--project-name $(COMPOSE_PROJECT_NAME) down --remove-orphans

# -----------------------------
# 🔧 Docker Build & Run
# -----------------------------
.PHONY: docker-build
docker-build:
	docker build -t $(IMAGE_NAME) --build-arg USER_ID=$(USER_ID) .

.PHONY: run-dev
run-dev:
	docker run --rm \
		-e SERVICE_NAME=$(SERVICE_NAME) \
		-e ENVIRONMENT=development \
		-v $(shell pwd)/src:/app/src \
		-p $(PORT):8000 \
		$(IMAGE_NAME)

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

.PHONY: stop-all
stop-all:
	@for service in $(SERVICES); do \
		docker stop summiva-$$service 2>/dev/null || true; \
	done

# -----------------------------
# 🧹 Cleanup
# -----------------------------
.PHONY: clean
clean:
	-docker stop $(shell docker ps -q)
	-docker rm -f $(shell docker ps -aq)
	-docker rmi -f $(shell docker images -q)
	-docker network prune -f
	-docker volume prune -f
	-docker system prune -a -f --volumes
	
# -----------------------------
# 📘 Help
# -----------------------------
.PHONY: help
help:
	@echo "🛠️  Available Targets:"
	@echo "  docker-build   - Build Docker image"
	@echo "  run-dev        - Run one service in development mode"
	@echo "  run-all        - Run all services in background with fixed ports"
	@echo "  stop-all       - Stop all services"
	@echo "  clean          - Prune unused Docker resources"
	@echo "  compose-up     - Start services using Docker Compose"
	@echo "  compose-down   - Stop and clean Docker Compose containers"