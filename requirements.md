# Summiva: Package Requirements

This document outlines the package requirements for the Summiva project, an enterprise-scale NLP system for content summarization, tagging, grouping, and search.

## Backend Requirements

```
# Core Framework
fastapi>=0.100.0         # Fast API framework with high performance
uvicorn[standard]>=0.23.0 # ASGI server implementation
gunicorn>=21.2.0         # WSGI HTTP server for deploying FastAPI applications
aiohttp>=3.9.0          # Asynchronous HTTP client/server framework
python-dotenv>=1.0.0    # Environment variable management
beautifulsoup4>=4.12.0  # Library for pulling data out of HTML/XML files

# Settings & Environment
pydantic>=2.0.0         # Data validation and settings management
pydantic-settings>=2.0.0 # Settings management for Pydantic
email-validator>=2.0.0  # Email validation for Pydantic

# Database
sqlalchemy>=2.0.0       # SQL toolkit and ORM
psycopg2-binary>=2.9.6  # PostgreSQL database adapter
alembic>=1.12.0         # Database migration tool for SQLAlchemy

# Authentication & Security
python-jose[cryptography]>=3.3.0  # JavaScript Object Signing and Encryption implementation
passlib[bcrypt]>=1.7.4   # Password hashing library
python-multipart>=0.0.6  # Multipart form data parser
itsdangerous>=2.1.2      # Various helpers to pass trusted data to untrusted environments
PyJWT>=2.8.0             # JSON Web Token implementation

# Messaging / Caching
celery>=5.3.0           # Distributed task queue
redis>=5.0.0            # Redis Python client
aio_pika>=9.0.0         # AsyncIO AMQP client

# NLP / ML Libraries
transformers>=4.36.0    # State-of-the-art Natural Language Processing for PyTorch
torch>=2.0.0            # PyTorch machine learning framework
scikit-learn>=1.3.0     # Machine learning library for Python
sentence-transformers>=2.2.0  # Sentence embeddings for NLP
spacy>=3.7.0            # Industrial-strength Natural Language Processing
bertopic>=0.15.0        # Topic modeling with transformers
faiss-cpu>=1.7.4        # Library for efficient similarity search
better-profanity>=0.7.0 # Profanity filter for content moderation
trafilatura>=1.6.0      # Web scraping tool for text extraction
optimum>=1.14.0         # Performance optimization tools for transformers

# LLM Support
bitsandbytes>=0.39.0    # Quantization and acceleration of LLM operations
accelerate>=0.25.0      # Library to accelerate PyTorch training
peft>=0.6.0             # Parameter-Efficient Fine-Tuning for transformers

# Search
elasticsearch>=8.10.0   # Python client for Elasticsearch

# HTTP Client
httpx>=0.25.0           # Fully featured async HTTP client

# MongoDB
pymongo>=4.6.0          # MongoDB Python driver

# Logging & Utilities
pyyaml>=6.0.0           # YAML parser and emitter
loguru>=0.7.0           # Python logging made simple
tenacity>=8.2.0         # Retrying library for Python
python-dateutil>=2.8.2  # Extensions to the standard Python datetime module
prometheus-client>=0.17.0 # Python client for Prometheus monitoring
prometheus-fastapi-instrumentator>=6.1.0 # Prometheus instrumentation for FastAPI
```

## Frontend Requirements

```
nicegui>=1.3.8          # UI framework for Python
requests>=2.28.0        # HTTP library
python-dotenv>=1.0.0    # Environment variable management
uvicorn>=0.23.0         # ASGI server
fastapi>=0.100.0        # FastAPI for frontend services
```

## Development Requirements

```
# Testing
pytest>=7.4.0           # Testing framework
pytest-asyncio>=0.21.0  # Async testing for pytest
httpx[test]>=0.25.0     # HTTP client with test support

# Code Quality
black>=23.9.0           # Code formatter
isort>=5.12.0           # Import sorter
flake8>=6.1.0           # Linter
mypy>=1.5.0             # Static type checker

# Development Tools
pre-commit>=3.5.0       # Git hook scripts
```

## Installation Instructions

### Backend

```bash
# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate

# Install production dependencies
cd src/backend
pip install -r requirements.txt

# Install development dependencies (optional)
pip install -r requirements-dev.txt
```

### Frontend

```bash
# Create virtual environment (if not already created)
python -m venv frontend-venv
.\frontend-venv\Scripts\Activate

# Install frontend dependencies
cd src/frontend
pip install -r requirements.txt
```

### Using Docker Compose (Recommended)

```bash
# Start all services
docker-compose up -d

# Start only database services
docker-compose --profile db up -d
```

---

*Note: Version numbers are minimum required versions and may be updated based on security patches and feature requirements.*
