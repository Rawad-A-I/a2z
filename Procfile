web: python manage.py migrate && python manage.py collectstatic --noinput && gunicorn ecomm.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 3
