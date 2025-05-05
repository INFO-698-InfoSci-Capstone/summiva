![Summiva Logo](assets/summiva-logo.png)

# Summiva

An enterprise-scale NLP system designed for content summarization, tagging, grouping, and search.

## Overview

Summiva is a microservice-based system for processing and analyzing text content using NLP techniques. It provides the following core features:

- **Text Summarization**: Generate concise summaries of long documents
- **Content Tagging**: Automatically tag content with relevant keywords and entities
- **Content Grouping**: Semantically group similar content
- **Search**: Full-text and semantic search across content

## Prerequisites

- Docker
- Docker Compose
- Make (optional, for using the Makefile)

## Quick Start

1. Clone the repository and navigate to the project root

2. Copy the `.env.example` file to a new file called `.env`:
```bash
cp .env.example .env
```

3. Modify the `.env` file to set your desired environment variables

4. Start the development environment:
```bash
./run.sh dev
# or
make dev
```

## Development Workflow

### Using Docker Compose Profiles

The project uses Docker Compose profiles to manage different service groups:

```bash
# Start only the core dev services (backend, auth, and databases)
./run.sh dev

# Start only API services (backend & auth)
./run.sh api

# Start only NLP services (summarization, tagging, grouping)
./run.sh nlp

# Start all services
./run.sh all

# Start only the databases
./run.sh db

# Start the monitoring stack
./run.sh metrics
```

### Using Makefile Commands

```bash
# Show all available make commands
make help

# Start development environment
make dev

# Build all containers
make build

# Run all tests
make test

# Run specific test types
make test-unit
make test-integration
make test-e2e
make test-performance

# Format code
make format

# Run linters
make lint

# Run database migrations
make migrate

# View logs
make logs
# View logs for a specific service
SERVICE=backend make logs

# Check services status
make status

# Clean up environment
make clean
```

## Project Structure

```
summiva/
├── assets/             # Static assets
├── config/             # Configuration files
│   ├── logging/        # Logging configuration
│   └── settings/       # Application settings
├── data/               # Data directory
├── docs/               # Documentation
├── infra/              # Infrastructure configuration
│   ├── backup/         # Backup configuration
│   ├── docker/         # Docker configuration
│   ├── kubernetes/     # Kubernetes manifests
│   ├── monitoring/     # Monitoring configuration
│   ├── scripts/        # Infrastructure scripts
│   └── terraform/      # Terraform configuration
├── src/                # Source code
│   ├── backend/        # Backend services
│   │   ├── auth/       # Authentication service
│   │   ├── core/       # Core shared modules
│   │   ├── grouping/   # Content grouping service
│   │   ├── search/     # Search service
│   │   ├── summarization/  # Summarization service
│   │   └── tagging/    # Tagging service
│   ├── data/           # Data processing scripts
│   └── frontend/       # Frontend code
└── tests/              # Test suite
    ├── e2e/            # End-to-end tests
    ├── integration/    # Integration tests
    ├── performance/    # Performance tests
    └── unit/           # Unit tests
```

## Testing

```bash
# Run all tests
./run.sh test
# or
make test

# Run specific test suites
make test-unit
make test-integration
make test-e2e
make test-performance
```

## Deployment

### Development Environment

```bash
./run.sh dev
# or
make dev
```

### Production Deployment

```bash
# Deploy to production
docker compose -f docker-compose.prod.yml up -d

# Scale specific services
docker compose -f docker-compose.prod.yml up -d --scale backend=3 --scale auth=2
```

## Monitoring

The project includes a comprehensive monitoring stack:

- **Prometheus**: Metrics collection
- **Grafana**: Metrics visualization
- **ELK Stack**: Centralized logging (Elasticsearch, Logstash, Kibana)

Start the monitoring services:

```bash
./run.sh metrics
# or
make metrics
```

Access the dashboards:
- Grafana: http://localhost:3000
- Prometheus: http://localhost:9090
- Kibana: http://localhost:5601

## License

See the [LICENSE](LICENSE) file for license rights and limitations.