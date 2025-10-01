# Use Python 3.11 slim image for better performance
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    UV_CACHE_DIR=/opt/uv-cache

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

# Set the port that Google App Engine expects
ENV PORT=8080

# Expose the port
EXPOSE 8080

# Create a startup script for App Engine
RUN echo '#!/bin/bash\n\
# Set environment variables for App Engine\n\
export FLASK_APP=backend/app.py\n\
export FLASK_ENV=production\n\
export PYTHONPATH=/app\n\
\n\
# Start the application using production launcher\n\
cd /app && python main_production.py\n\
' > /app/start.sh && chmod +x /app/start.sh

# Use the startup script
CMD ["/app/start.sh"]
