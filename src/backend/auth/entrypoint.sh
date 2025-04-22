#!/bin/bash
set -e

# Start uvicorn with proper watch exclusion
exec uvicorn auth.main:app --host 0.0.0.0 --port 8000 --reload --reload-exclude="/app/postgresql/data" --reload-exclude="/app/data"