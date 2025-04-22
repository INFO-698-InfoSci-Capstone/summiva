#!/bin/bash
set -e

# Start the backend service
echo "Starting backend service..."
uvicorn main:app --host 0.0.0.0 --port 8000