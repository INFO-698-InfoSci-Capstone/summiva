#!/bin/bash
set -e

if [ -z "$SERVICE_NAME" ]; then
    echo "Error: SERVICE_NAME environment variable is not set"
    exit 1
fi

echo "Starting Summiva service: $SERVICE_NAME"

cd /app/$SERVICE_NAME

if [ ! -f main.py ]; then
    echo "Error: main.py not found in /app/$SERVICE_NAME"
    exit 1
fi

exec gunicorn main:app --config ../gunicorn_config.py
