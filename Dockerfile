FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . .

# Expose port
EXPOSE 8000

# Use the Procfile command
CMD ["gunicorn", "wsgi_app:application", "--bind", "0.0.0.0:8000", "--workers", "3"]