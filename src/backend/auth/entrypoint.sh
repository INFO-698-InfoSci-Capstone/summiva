#!/bin/bash
set -e

# Create config directory structure if it doesn't exist
mkdir -p /app/config/settings

# If config files don't exist in the Docker environment, symlink them from the app source
if [ ! -f /app/config/settings/__init__.py ]; then
  echo "Creating config directories and symlinks..."
  
  # Create __init__.py files
  touch /app/config/__init__.py
  touch /app/config/settings/__init__.py
  
  # Copy settings file if it doesn't exist
  if [ ! -f /app/config/settings/settings.py ]; then
    cp /app/src/backend/auth/config/settings.py /app/config/settings/
    echo "Copied settings file to /app/config/settings/"
  fi
fi

# Export PROJECT_ROOT for use by the application
export PROJECT_ROOT=/app

# Check environment and start appropriate server
if [ "$ENVIRONMENT" = "development" ]; then
    echo "Starting in DEVELOPMENT mode with uvicorn and hot reload"
    # Start uvicorn with proper watch exclusion
    exec uvicorn auth.main:app --host 0.0.0.0 --port 8000 --reload \
        --reload-exclude="/app/postgresql/data" \
        --reload-exclude="/app/data" \
        --reload-exclude="*.pyc" \
        --reload-exclude="__pycache__"
else
    echo "Starting in PRODUCTION mode with gunicorn"
    # Use the wsgi.py file which properly sets up Python path
    exec gunicorn "wsgi:application" --config /app/src/backend/auth/gunicorn_config.py
fi