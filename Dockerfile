# Use Python 3.12 slim base (more stable)
FROM python:3.12-slim

# Create a non-root user
RUN useradd -m -u 1000 appuser

# Set working directory
WORKDIR /app

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src \
    PORT=8000 \
    PATH="/home/appuser/.local/bin:$PATH"

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY src/backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && pip install --no-cache-dir gunicorn uvicorn

# Copy the source code
COPY src /app/src

# Create missing __init__.py files
RUN find /app/src -type d ! -exec test -e {}/__init__.py \; -exec touch {}/__init__.py \;

# Create service directories
RUN mkdir -p /app/src/data /app/src/logs /app/src/models \
    && mkdir -p /app/src/exclude_patterns \
    && echo "postgresql/data" > /app/src/exclude_patterns/reload_exclude.txt \
    && chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check for readiness
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command
CMD ["sh", "-c", "\
    if [ \"$SERVICE_NAME\" = \"backend\" ]; then \
        cd /app/src && uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload --reload-exclude \"./postgresql/data/*\" --reload-exclude \"./data/*\" --reload-exclude \"*.pyc\" --reload-exclude \"./__pycache__\"; \
    elif [ \"$SERVICE_NAME\" = \"auth\" ]; then \
        cd /app/src && uvicorn backend.auth.main:app --host 0.0.0.0 --port 8000 --reload --reload-exclude \"./postgresql/data/*\" --reload-exclude \"./data/*\" --reload-exclude \"*.pyc\" --reload-exclude \"./__pycache__\"; \
    elif [ \"$SERVICE_NAME\" = \"summarization\" ]; then \
        cd /app/src && uvicorn backend.summarization.main:app --host 0.0.0.0 --port 8000 --reload --reload-exclude \"./postgresql/data/*\" --reload-exclude \"./data/*\" --reload-exclude \"*.pyc\" --reload-exclude \"./__pycache__\"; \
    else \
        cd /app/src && uvicorn backend.${SERVICE_NAME}.main:app --host 0.0.0.0 --port 8000 --reload --reload-exclude \"./postgresql/data/*\" --reload-exclude \"./data/*\" --reload-exclude \"*.pyc\" --reload-exclude \"./__pycache__\"; \
    fi"]