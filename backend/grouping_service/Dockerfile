FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install -r /app/requirements.txt

COPY . /app

# Set PYTHONPATH to include src for module imports
ENV PYTHONPATH="/app/src"

EXPOSE 8001
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8001"]


# Base image
FROM python:3.11-slim

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    PYTHONPATH="/app/src"

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

CMD ["gunicorn", "-c", "gunicorn_config.py", "src.main:app"]

