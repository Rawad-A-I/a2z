#!/bin/bash

# Run database migrations
python manage.py migrate

# Start the application
gunicorn ecomm.wsgi:application --bind 0.0.0.0:$PORT --workers 3
