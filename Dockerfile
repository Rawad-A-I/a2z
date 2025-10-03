FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . .

# Create startup script
RUN echo '#!/bin/bash\npython manage.py migrate\npython manage.py create_superuser\npython manage.py collectstatic --noinput\nexec gunicorn ecomm.wsgi:application --bind 0.0.0.0:$PORT' > start.sh && chmod +x start.sh

# Expose port
EXPOSE 8000

# Run the application
CMD ["./start.sh"]
