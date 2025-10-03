web: python manage.py migrate && python manage.py collectstatic --noinput && gunicorn ecomm.wsgi:application --bind 0.0.0.0:$PORT --workers 3
