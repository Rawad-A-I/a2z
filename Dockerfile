FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . .

# Expose port (Railway will set PORT environment variable)
EXPOSE $PORT

# Use Railway's PORT environment variable
CMD ["sh", "-c", "gunicorn wsgi_app:application --bind 0.0.0.0:$PORT --workers 3"]