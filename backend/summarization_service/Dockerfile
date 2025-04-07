FROM python:3.11-slim

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    PYTHONPATH="/app:/app/src:/app/utils:/app/summarization_service/src"

# Set work directory
WORKDIR /app

# Install system dependencies (for building common Python packages)
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy app code
COPY . .

# Port exposure
EXPOSE 8001

# Default: Run in production with gunicorn
# Can override with `--env` in docker-compose or command line
ENV SUMMIVA_ENV=production

CMD ["gunicorn", "-c", "/app/gunicorn_config.py", "src.main:app"]

