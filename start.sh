#!/bin/bash

# Set default PORT if not provided
export PORT=${PORT:-8000}
echo "Using PORT: $PORT"

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate --noinput

# Create superuser if it doesn't exist
echo "Creating superuser..."
python manage.py create_superuser

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start Gunicorn with proper port handling
echo "Starting Gunicorn on port $PORT..."
exec gunicorn ecomm.wsgi:application --bind 0.0.0.0:$PORT --workers 3
