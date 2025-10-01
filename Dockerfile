# Use Python 3.11 slim image for better performance
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PORT=8080 \
    FLASK_ENV=production

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies using uv with system installation
RUN uv pip install --system --no-cache -r requirements.txt

# Copy the entire application
COPY . .

# Create necessary directories
RUN mkdir -p backend/static backend/templates

# Expose the port
EXPOSE 8080

# Set Python path
ENV PYTHONPATH=/app

# Start the application directly
CMD ["python", "main_production.py"]
