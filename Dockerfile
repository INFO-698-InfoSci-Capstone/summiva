# Use Python 3.11 slim base
FROM python:3.11-slim

# Create a non-root user
RUN useradd -m -u 1000 appuser

# Set working directory
WORKDIR /app

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
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
RUN pip install --no-cache-dir -r requirements.txt && pip install --no-cache-dir gunicorn

# Copy project files (codebase)
COPY src/backend /app

# Copy the entrypoint script
COPY src/backend/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh && chown appuser:appuser /app/entrypoint.sh

# Create expected service directories and assign ownership
RUN mkdir -p /app/data /app/logs /app/models \
    && chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check for readiness
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start the correct service based on SERVICE_NAME
ENTRYPOINT ["/bin/bash", "/app/entrypoint.sh"]
