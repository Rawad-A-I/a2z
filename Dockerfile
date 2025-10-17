FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . .

# Make startup script executable
RUN chmod +x start.sh

# Expose port
EXPOSE 8000

# Run the application
CMD ["./start.sh"]
