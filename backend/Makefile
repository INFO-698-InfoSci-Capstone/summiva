# File: Makefile (placed inside D:\summiva\backend)

ROOT_COMPOSE = -f docker-compose.yml
AUTH_COMPOSE = -f auth-service/docker-compose.yml
SUMMARIZATION_COMPOSE = -f summarization_service/docker-compose.yml

# Build and start everything from root docker-compose.yml
up:
	docker compose $(ROOT_COMPOSE) up --build

# Start everything in detached mode
start:
	docker compose $(ROOT_COMPOSE) up -d

# Stop all services
stop:
	docker compose $(ROOT_COMPOSE) down

# View logs for all services
logs:
	docker compose $(ROOT_COMPOSE) logs -f

# View logs for a specific service (make logs-service SERVICE=auth-service)
logs-service:
	docker compose $(ROOT_COMPOSE) logs -f $(SERVICE)

# Restart a single service (make restart SERVICE=summarization-service)
restart:
	docker compose $(ROOT_COMPOSE) restart $(SERVICE)

# Rebuild all images without starting
build:
	docker compose $(ROOT_COMPOSE) build

# Clean everything including volumes and orphans
clean:
	docker compose $(ROOT_COMPOSE) down -v --remove-orphans

# Show running containers
ps:
	docker compose $(ROOT_COMPOSE) ps

# Bash into a running service (make bash SERVICE=auth-service)
bash:
	docker compose $(ROOT_COMPOSE) exec $(SERVICE) /bin/bash

# -------------------------
# Run individual service setups (for development)
# -------------------------

# Run only auth-service and its DB
dev-auth:
	docker compose $(AUTH_COMPOSE) up --build

# Run only summarization service stack
dev-summarization:
	docker compose $(SUMMARIZATION_COMPOSE) up --build

# Clean individual dev service
clean-auth:
	docker compose $(AUTH_COMPOSE) down -v --remove-orphans

clean-summarization:
	docker compose $(SUMMARIZATION_COMPOSE) down -v --remove-orphans