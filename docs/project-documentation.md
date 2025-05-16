# Summiva: Enterprise-Scale NLP System

## Project Overview

Summiva is an enterprise-scale Natural Language Processing (NLP) system designed for content summarization, tagging, grouping, and search. The application leverages state-of-the-art machine learning models and distributed processing to provide advanced content analysis capabilities.

## Architecture

The system follows a microservices architecture with the following components:

- **Backend API Services**: FastAPI-based microservices for authentication, summarization, tagging, grouping, and search
- **Frontend Interface**: NiceGUI-based web interface
- **Data Storage**: PostgreSQL, MongoDB, and Redis
- **Task Processing**: Celery for distributed task execution
- **Monitoring**: Prometheus and Grafana
- **Deployment**: Docker and Kubernetes support

## Dependencies

### Backend Core Dependencies

```
# Core Framework
fastapi                                # Web framework
uvicorn[standard]                      # ASGI server
gunicorn                               # WSGI HTTP Server
aiohttp                                # Async HTTP client/server
python-dotenv                          # Environment variable management
beautifulsoup4                         # HTML parsing for content ingestion

# Settings & Environment
pydantic                               # Data validation and settings management
pydantic-settings                      # Settings management
email-validator                        # Email validation

# Database
sqlalchemy                             # ORM for PostgreSQL
psycopg2-binary                        # PostgreSQL driver
alembic                                # Database migrations

# Authentication & Security
python-jose[cryptography]              # JWT token handling
passlib[bcrypt]                        # Password hashing
python-multipart                       # Form data parsing
itsdangerous                           # Safe data signing
PyJWT                                  # JWT implementation

# Messaging / Caching
celery                                 # Distributed task queue
redis                                  # Redis client
aio_pika                               # AMQP client for RabbitMQ
```

### NLP and Machine Learning Dependencies

```
# NLP / ML Libraries
transformers                           # Hugging Face transformers for NLP models
torch                                  # PyTorch for deep learning
scikit-learn                           # Traditional ML algorithms
sentence-transformers                  # State-of-the-art sentence embeddings
spacy                                  # NLP processing
bertopic                               # Topic modeling with transformers
faiss-cpu                              # Vector similarity search
better-profanity                       # Content moderation
trafilatura                            # Web content extraction
optimum                                # Performance optimization for ML models

# LLM Support
bitsandbytes                           # Quantization and optimization
accelerate                             # Hardware acceleration
peft                                   # Parameter-efficient fine-tuning
```

### Additional Services and Utilities

```
# Search
elasticsearch                          # Elasticsearch client

# HTTP Client
httpx                                  # Modern HTTP client

# MongoDB
pymongo                                # MongoDB client

# Logging & Utilities
pyyaml                                 # YAML parsing for configuration
loguru                                 # Improved logging
tenacity                               # Retry library
python-dateutil                        # Date utilities
prometheus-client                      # Metrics collection
prometheus-fastapi-instrumentator      # FastAPI metrics
```

### Frontend Dependencies

```
nicegui>=1.3.8                         # UI framework
requests>=2.28.0                       # HTTP client
python-dotenv>=1.0.0                   # Environment variables
uvicorn>=0.23.0                        # ASGI server
fastapi>=0.100.0                       # Web framework
```

### Development Dependencies

```
pytest                                 # Testing
pytest-asyncio                         # Async testing
httpx[test]                            # HTTP client testing
black                                  # Code formatting
isort                                  # Import sorting
flake8                                 # Linting
mypy                                   # Type checking
pre-commit                             # Git hooks
```

## Key Features

1. **Content Summarization**
   - Text extraction from URLs and raw content
   - Abstractive summarization using transformer models
   - Asynchronous processing with Celery for large documents

2. **Semantic Search**
   - Hybrid search combining Elasticsearch and FAISS
   - Vector embeddings for semantic search
   - Faceted filtering and metadata search

3. **Document Tagging**
   - Automatic tag extraction from content
   - Custom tag models and taxonomies
   - Confidence scoring for extracted tags

4. **Content Grouping**
   - Topic clustering and document grouping
   - Multiple algorithm support (BERTopic, etc.)
   - Group visualization and analytics

5. **Authentication & Security**
   - JWT token-based authentication
   - Role-based access control
   - Security middleware and protection

## Infrastructure Components

The project uses Docker and Docker Compose for containerization and orchestration, with services for:

- PostgreSQL - Relational database for structured data
- Redis - Caching and task broker
- MongoDB - Document database for unstructured content
- Prometheus - Metrics collection
- Grafana - Metrics visualization
- Elasticsearch - Full-text search
- Nginx - Web server and reverse proxy

## Deployment

The project includes Docker configurations for both development and production environments:

- `docker-compose.yml` - Development environment
- `docker-compose.prod.yml` - Production environment
- Kubernetes configuration files for cloud deployment

## Development Setup

1. **Clone the repository**

2. **Create virtual environment**
   ```bash
   python -m venv venv
   .\venv\Scripts\Activate
   ```

3. **Install dependencies**
   ```bash
   cd src/backend
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # For development
   ```

4. **Start infrastructure services**
   ```bash
   docker-compose --profile db up -d
   ```

5. **Run migrations**
   ```bash
   cd src/backend
   alembic upgrade head
   ```

6. **Start the backend services**
   ```bash
   cd src/backend
   uvicorn main:app --reload
   ```

7. **Start the frontend**
   ```bash
   cd src/frontend
   python app.py
   ```

## Project Structure

- `/src/backend` - Backend services and API endpoints
- `/src/frontend` - Frontend UI components and pages
- `/config` - Configuration files and settings
- `/infra` - Infrastructure configuration (Docker, Kubernetes, etc.)
- `/docs` - Documentation and architecture diagrams

## Monitoring and Observability

The application includes:
- Prometheus metrics for system monitoring
- Grafana dashboards for visualization
- Structured logging with Loguru
- Performance tracing

## Conclusion

Summiva is a sophisticated NLP system with multiple microservices, advanced ML capabilities, and proper infrastructure for monitoring and scaling. The application demonstrates enterprise-level architecture patterns and leverages modern technologies for natural language processing tasks.

---

*Last Updated: May 16, 2025*
