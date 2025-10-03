#!/bin/bash
set -e

echo "Starting Django app..."

# Set default PORT if not provided
export PORT=${PORT:-8000}
echo "Using PORT: $PORT"

# Run migrations
echo "Running migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

# Start Gunicorn
echo "Starting Gunicorn on port $PORT..."
exec gunicorn ecomm.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 3 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info
