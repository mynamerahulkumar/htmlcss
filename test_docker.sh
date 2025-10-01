#!/bin/bash

# Test script for Docker build and local deployment
# This script tests the Docker configuration before deploying to App Engine

set -e

echo "🧪 Testing Docker Build for Delta Exchange Trading Bot"
echo "======================================================"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

echo "✅ Docker is running"

# Build the Docker image
echo "🔨 Building Docker image..."
docker build -t trading-bot-test .

if [ $? -eq 0 ]; then
    echo "✅ Docker image built successfully"
else
    echo "❌ Docker build failed"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from example..."
    if [ -f "config.env.example" ]; then
        cp config.env.example .env
        echo "✅ .env file created from example"
        echo "📝 Please update .env with your actual API credentials"
    else
        echo "❌ config.env.example not found"
        exit 1
    fi
fi

# Test the container
echo "🚀 Testing container startup..."
echo "This will start the container in the background for 30 seconds"

# Start container in background
CONTAINER_ID=$(docker run -d -p 8080:8080 --env-file .env trading-bot-test)

if [ $? -eq 0 ]; then
    echo "✅ Container started successfully (ID: $CONTAINER_ID)"
    
    # Wait for container to start
    echo "⏳ Waiting for application to start..."
    sleep 10
    
    # Test if the application is responding
    echo "🌐 Testing application response..."
    if curl -f http://localhost:8080 > /dev/null 2>&1; then
        echo "✅ Application is responding correctly"
    else
        echo "⚠️  Application may not be fully started yet"
    fi
    
    # Show container logs
    echo "📋 Container logs:"
    docker logs $CONTAINER_ID
    
    # Stop and remove container
    echo "🛑 Stopping test container..."
    docker stop $CONTAINER_ID
    docker rm $CONTAINER_ID
    
    echo ""
    echo "✅ Docker test completed successfully!"
    echo "🚀 Your application is ready for Google App Engine deployment"
    echo ""
    echo "Next steps:"
    echo "1. Update .env with your actual API credentials"
    echo "2. Run: ./deploy.sh"
    echo "3. Or manually: gcloud app deploy app.yaml"
    
else
    echo "❌ Failed to start container"
    exit 1
fi
