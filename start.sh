#!/bin/bash

# Run deployment fix first
echo "🔧 Running deployment fix..."
chmod +x deploy_fix.sh
./deploy_fix.sh

# Create superuser if it doesn't exist
echo "Creating superuser..."
python manage.py create_superuser

# Run migrations automatically
echo "Running database migrations..."
python manage.py migrate --noinput || true

# Fake the 0033 migration if tables already exist
echo "Checking for existing Close Cash tables..."
python manage.py migrate accounts 0033_close_cash_models --fake || echo "Migration 0033 already applied or not needed"

# Import Close Cash schemas if Close Cash folder exists (DISABLED - using new employee forms system)
# echo "Importing Close Cash schemas..."
# if [ -d "Close Cash" ]; then
#     echo "Close Cash folder found, importing schemas..."
#     python manage.py import_close_cash_from_excel || echo "Close Cash import failed, continuing..."
# else
#     echo "Close Cash folder not found, skipping import..."
# fi

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput || true

# Start Gunicorn with Railway's PORT variable (use braces for proper expansion)
echo "Starting Gunicorn on port ${PORT}..."
exec gunicorn ecomm.wsgi:application --bind 0.0.0.0:${PORT} --workers 3
