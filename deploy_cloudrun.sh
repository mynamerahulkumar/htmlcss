#!/bin/bash

# Delta Exchange Trading Bot - Google Cloud Run Deployment Script
# This script deploys the trading bot to Google Cloud Run

set -e

echo "🚀 Delta Exchange Trading Bot - Google Cloud Run Deployment"
echo "============================================================"

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

# Set default project
PROJECT_ID=${GOOGLE_CLOUD_PROJECT:-"gen-lang-client-0423978932"}
SERVICE_NAME="srpaitrade"
REGION="us-central1"

echo "📋 Current configuration:"
echo "  Project ID: $PROJECT_ID"
echo "  Service Name: $SERVICE_NAME"
echo "  Region: $REGION"
echo ""

# Set the project
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "🔧 Enabling required APIs..."
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable containerregistry.googleapis.com

# Build and deploy using Cloud Build
echo "🔨 Building and deploying to Cloud Run..."
echo "This may take several minutes..."

gcloud builds submit --config cloudbuild.yaml .

echo ""
echo "✅ Deployment completed successfully!"
echo ""
echo "🌐 Your application is now available at:"
echo "   https://$SERVICE_NAME-$PROJECT_ID.a.run.app"
echo ""
echo "📊 To view logs:"
echo "   gcloud run services logs tail $SERVICE_NAME --region=$REGION"
echo ""
echo "🛑 To stop the service:"
echo "   gcloud run services update $SERVICE_NAME --region=$REGION --no-traffic"
echo ""
echo "📋 To list services:"
echo "   gcloud run services list"
