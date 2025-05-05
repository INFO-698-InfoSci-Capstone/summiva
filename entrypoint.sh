#!/usr/bin/env sh
set -e

# -----------------------------
# ENV AND SERVICE SETUP
# -----------------------------
SERVICE_NAME="${SERVICE_NAME:-backend}"
ENVIRONMENT="${ENVIRONMENT:-production}"
PORT="${PORT:-8000}"

echo "✅ Starting Summiva service: $SERVICE_NAME"
echo "🌐 Environment: $ENVIRONMENT"
echo "📦 Port: $PORT"
echo "📅 Startup Time: $(date)"

# -----------------------------
# LOGS AND CONFIG SETUP
# -----------------------------
mkdir -p /app/logs /app/config/settings

# Copy settings if not already there
if [ ! -f /app/config/settings/settings.py ]; then
  SETTINGS_SRC="/app/src/$SERVICE_NAME/config/settings/settings.py"
  if [ -f "$SETTINGS_SRC" ]; then
    cp "$SETTINGS_SRC" /app/config/settings/
    echo "📝 Copied settings.py to /app/config/settings/"
  fi
fi

# Create __init__.py if needed
touch /app/config/__init__.py /app/config/settings/__init__.py

# -----------------------------
# PYTHONPATH & MODULE RESOLUTION
# -----------------------------
export PYTHONPATH="/app/src:$PYTHONPATH"
if [ -d "/app/src/backend/${SERVICE_NAME}" ]; then
  APP_MODULE="src.backend.${SERVICE_NAME}.main:app"
elif [ -d "/app/src/${SERVICE_NAME}" ]; then
  APP_MODULE="src.${SERVICE_NAME}.main:app"
else
  echo "⚠️ WARNING: Service directory not found. Using fallback module."
  APP_MODULE="src.backend.main:app"
fi

echo "📂 Using app module: ${APP_MODULE}"

# -----------------------------
# DEVELOPMENT MODE
# -----------------------------
if [ "$ENVIRONMENT" = "development" ]; then
  echo "🔄 DEV mode – starting with uvicorn + hot reload"
  exec uvicorn "$APP_MODULE" \
    --host 0.0.0.0 --port $PORT --reload \
    --reload-exclude 'postgresql/data/*' \
    --reload-exclude 'data/*' \
    --reload-exclude '**/*.pyc' \
    --reload-exclude '**/__pycache__/*' \
    "$@"

# -----------------------------
# PRODUCTION MODE
# -----------------------------
else
  echo "🚀 PROD mode – starting with Gunicorn"

  # Detect worker count based on available CPUs
  WORKER_COUNT=${WORKER_COUNT:-$(nproc --all)}
  if [ "$WORKER_COUNT" -lt 2 ]; then WORKER_COUNT=2; fi
  if [ "$WORKER_COUNT" -gt 8 ]; then WORKER_COUNT=8; fi

  echo "👷 Using $WORKER_COUNT workers"

  CONFIG_PATH="/app/src/$SERVICE_NAME/config/gunicorn_config.py"
  if [ -f "$CONFIG_PATH" ]; then
    echo "🛠️ Gunicorn config found: $CONFIG_PATH"
    exec gunicorn "$APP_MODULE" \
      --config "$CONFIG_PATH" \
      --worker-class uvicorn.workers.UvicornWorker \
      --workers "$WORKER_COUNT" \
      "$@"
  else
    echo "⚠️ No gunicorn config found, starting with defaults"
    exec gunicorn "$APP_MODULE" \
      --bind 0.0.0.0:$PORT \
      --worker-class uvicorn.workers.UvicornWorker \
      --workers "$WORKER_COUNT" \
      --log-level info \
      --access-logfile - \
      --error-logfile - \
      "$@"
  fi
fi
