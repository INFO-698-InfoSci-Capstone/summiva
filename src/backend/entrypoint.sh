#!/bin/bash
set -e

if [ -z "$SERVICE_NAME" ]; then
    echo "Error: SERVICE_NAME environment variable is not set"
    exit 1
fi
export PYTHONPATH="/app"
echo "Starting Summiva service: $SERVICE_NAME"

if [ ! -f /app/$SERVICE_NAME/main.py ]; then
    echo "Error: main.py not found in /app/$SERVICE_NAME"
    exit 1
fi

exec gunicorn /app/$SERVICE_NAME/main:app --config /app/gunicorn_config.py
