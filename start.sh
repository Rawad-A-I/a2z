#!/bin/bash

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
echo "Starting Gunicorn on port ${PORT:-8000}..."
exec gunicorn ecomm.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 3
