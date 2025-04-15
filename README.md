# Summiva

An Enterprise-Scale NLP System for Content Summarization, Tagging, Grouping, and Search

## Project Structure

```
summiva/
├── config/                  # Configuration files
│   ├── development/        # Development environment configs
│   ├── staging/           # Staging environment configs
│   └── production/        # Production environment configs
├── docs/                   # Documentation
│   ├── api/               # API documentation
│   ├── architecture/      # System architecture docs
│   ├── deployment/        # Deployment guides
│   ├── development/       # Development setup guides
│   └── user-guides/       # End-user documentation
├── infra/                  # Infrastructure
│   ├── kubernetes/        # Kubernetes manifests
│   ├── terraform/         # Infrastructure as code
│   └── scripts/           # Deployment scripts
├── monitoring/            # Monitoring and observability
│   ├── dashboards/        # Monitoring dashboards
│   ├── alerts/            # Alert configurations
│   └── metrics/           # Custom metrics
├── notebooks/             # Jupyter notebooks
├── research/              # Research papers and documents
├── src/                   # Source code
│   ├── backend/          # Backend services
│   │   ├── auth_service/
│   │   ├── celery_tasks/
│   │   ├── grouping_service/
│   │   ├── search_service/
│   │   ├── summarization_service/
│   │   └── tagging_service/
│   └── frontend/         # Frontend application
├── tests/                 # Test suites
│   ├── unit/             # Unit tests
│   ├── integration/      # Integration tests
│   ├── e2e/              # End-to-end tests
│   └── performance/      # Performance tests
└── logs/                 # Application logs
```

## Getting Started

### Prerequisites

- Python 3.8+
- Flutter/Dart
- Docker
- Kubernetes (for production deployment)

### Development Setup

1. Clone the repository
2. Set up the backend:
   ```bash
   cd src/backend
   python -m venv .venv
   source .venv/bin/activate  # or .venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```

3. Set up the frontend:
   ```bash
   cd src/frontend
   flutter pub get
   ```

4. Start the development environment:
   ```bash
   cd infra
   docker-compose up -d
   ```

## Contributing

Please read [CONTRIBUTING.md](docs/development/CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 