#!/bin/bash

# Delta Exchange Trading Bot - Google App Engine Deployment Script
# This script deploys the trading bot to Google App Engine

set -e

echo "🚀 Delta Exchange Trading Bot - Google App Engine Deployment"
echo "=============================================================="

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ Google Cloud SDK (gcloud) is not installed."
    echo "Please install it from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check if user is authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo "🔐 Please authenticate with Google Cloud:"
    gcloud auth login
fi

# Set default project (you can change this)
PROJECT_ID=${GOOGLE_CLOUD_PROJECT:-"your-project-id"}

echo "📋 Current configuration:"
echo "  Project ID: $PROJECT_ID"
echo "  Service: default"
echo "  Runtime: custom (Docker)"
echo ""

# Set the project
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "🔧 Enabling required APIs..."
gcloud services enable appengine.googleapis.com
gcloud services enable cloudbuild.googleapis.com

# Deploy to App Engine
echo "🚀 Deploying to Google App Engine..."
echo "This may take several minutes..."

gcloud app deploy app.yaml --quiet

echo ""
echo "✅ Deployment completed successfully!"
echo ""
echo "🌐 Your application is now available at:"
echo "   https://$PROJECT_ID.appspot.com"
echo ""
echo "📊 To view logs:"
echo "   gcloud app logs tail -s default"
echo ""
echo "🛑 To stop the service:"
echo "   gcloud app versions stop VERSION_ID"
echo ""
echo "📋 To list versions:"
echo "   gcloud app versions list"
