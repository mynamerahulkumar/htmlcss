#!/bin/bash

# Delta Exchange Trading Bot - Startup Script

echo "🚀 Starting Delta Exchange Trading Bot..."
echo "========================================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip3 first."
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp config.env.example .env
    echo "✅ .env file created. Please update it with your API credentials."
    echo "📋 Edit .env file and add your Delta Exchange API credentials:"
    echo "   - DELTA_API_KEY=your_api_key"
    echo "   - DELTA_API_SECRET=your_api_secret"
    echo ""
    echo "Then run this script again to start the trading bot."
    exit 0
fi

# Start the application
echo "🌐 Starting web application..."
echo "📊 Dashboard will be available at: http://localhost:5003"
echo "🛑 Press Ctrl+C to stop the application"
echo "========================================"

python3 main.py
