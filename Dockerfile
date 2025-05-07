# Use an official Python image
FROM python:3.10-slim

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    ssh \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose port for Uvicorn
EXPOSE 8000

# Default command (overridden by docker-compose)
CMD ["uvicorn", "vmwebsocket.asgi:application", "--host", "0.0.0.0", "--port", "8000"]
