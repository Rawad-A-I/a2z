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

# Start Gunicorn with Railway's PORT variable (use braces for proper expansion)
echo "Starting Gunicorn on port ${PORT}..."
exec gunicorn ecomm.wsgi:application --bind 0.0.0.0:${PORT} --workers 3
