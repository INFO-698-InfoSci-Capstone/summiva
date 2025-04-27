# Summiva Backend

The backend service for Summiva, an enterprise-scale NLP system for content summarization, tagging, grouping, and search.

## Services

- **Summarization Service**: Handles text summarization using advanced NLP models
- **Tagging Service**: Automatically tags content with relevant categories
- **Search Service**: Provides semantic search capabilities
- **Grouping Service**: Groups similar content together
- **Auth Service**: Handles user authentication and authorization

## Setup

1. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Run the development server:
```bash
uvicorn main:app --reload
```

## Configuration

Configuration is managed through the centralized config system in `config/base.py`. Override settings using environment variables or a `.env` file.

## API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Testing

Run tests with:
```bash
pytest
```

## Deployment

See the `infra/` directory for deployment configurations:
- Docker
- Kubernetes
- Terraform

## Monitoring

Monitoring is optional and can be enabled by setting `ENABLE_MONITORING=true` in your environment.
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 
