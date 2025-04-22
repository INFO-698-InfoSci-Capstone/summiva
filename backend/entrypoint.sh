shell
#!/bin/bash
set -e

# Wait for the database to be ready
if [ "$DATABASE_HOSTNAME" ]; then
  echo "Waiting for database..."
  while ! nc -z $DATABASE_HOSTNAME 5432; do
    sleep 1
  done
  echo "Database is up!"
fi

# Apply database migrations
echo "Applying database migrations..."
alembic upgrade head

# Start the application
echo "Starting the application..."
uvicorn main:app --host 0.0.0.0 --port 8000