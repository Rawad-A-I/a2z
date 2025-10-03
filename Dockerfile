FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . .

# Create necessary directories
RUN mkdir -p /app/staticfiles /app/mediafiles

# Expose port
EXPOSE 8000

# Run migrations, collect static files, and start the server
CMD ["sh", "-c", "python manage.py migrate && python manage.py collectstatic --noinput && gunicorn ecomm.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 3"]
