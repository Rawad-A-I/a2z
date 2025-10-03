# Simple Dockerfile for minimal app
FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy app files
COPY . /app/

# Expose port
EXPOSE 8000

# Run the minimal app
CMD ["python", "minimal_app.py"]
