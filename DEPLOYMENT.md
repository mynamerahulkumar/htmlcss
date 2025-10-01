# 🚀 Google App Engine Deployment Guide

This guide will help you deploy the Delta Exchange Trading Bot to Google App Engine using Docker and `uv` for fast dependency management.

## 📋 Prerequisites

1. **Google Cloud Account**: Sign up at [Google Cloud Console](https://console.cloud.google.com/)
2. **Google Cloud SDK**: Install from [here](https://cloud.google.com/sdk/docs/install)
3. **Docker**: Install from [here](https://docs.docker.com/get-docker/)

## 🔧 Setup Steps

### 1. Initialize Google Cloud Project

```bash
# Login to Google Cloud
gcloud auth login

# Create a new project (or use existing)
gcloud projects create your-trading-bot-project

# Set the project
gcloud config set project your-trading-bot-project

# Enable required APIs
gcloud services enable appengine.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

### 2. Configure Environment Variables

Create a `.env` file with your API credentials:

```bash
# Copy the example file
cp config.env.example .env

# Edit the .env file with your actual credentials
nano .env
```

Required environment variables:
- `DELTA_API_KEY`: Your Delta Exchange API key
- `DELTA_SECRET_KEY`: Your Delta Exchange secret key
- `NEWS_API_KEY`: Your news API key (optional)

### 3. Deploy to App Engine

#### Option A: Using the deployment script (Recommended)

```bash
# Make the script executable
chmod +x deploy.sh

# Set your project ID
export GOOGLE_CLOUD_PROJECT="your-trading-bot-project"

# Deploy
./deploy.sh
```

#### Option B: Manual deployment

```bash
# Deploy using gcloud
gcloud app deploy app.yaml --quiet
```

## 🐳 Docker Configuration

The application uses a custom Dockerfile optimized for Google App Engine:

### Key Features:
- **Python 3.11**: Latest stable Python version
- **uv**: Fast Python package manager
- **Multi-stage optimization**: Efficient image size
- **Production ready**: Optimized for cloud deployment

### Docker Commands:

```bash
# Build the Docker image locally (for testing)
docker build -t trading-bot .

# Run locally (for testing)
docker run -p 8080:8080 --env-file .env trading-bot

# Test the application
curl http://localhost:8080
```

## 📊 App Engine Configuration

The `app.yaml` file configures:

- **Runtime**: Custom (Docker)
- **Scaling**: Automatic (1-10 instances)
- **Resources**: 1 CPU, 2GB RAM
- **Health Checks**: Automatic monitoring
- **Port**: 8080 (App Engine standard)

## 🌐 Accessing Your Application

After deployment, your application will be available at:
```
https://your-project-id.appspot.com
```

## 📝 Monitoring and Logs

### View Logs:
```bash
# Real-time logs
gcloud app logs tail -s default

# Historical logs
gcloud app logs read -s default
```

### Monitor Performance:
- Visit [Google Cloud Console](https://console.cloud.google.com/)
- Navigate to App Engine > Services
- View metrics, logs, and performance data

## 🔧 Management Commands

### Stop/Start Service:
```bash
# List versions
gcloud app versions list

# Stop a version
gcloud app versions stop VERSION_ID

# Start a version
gcloud app versions start VERSION_ID
```

### Update Application:
```bash
# Deploy new version
gcloud app deploy app.yaml

# Set traffic to new version
gcloud app services set-traffic default --splits=VERSION_ID=1
```

## 🛡️ Security Considerations

1. **Environment Variables**: Never commit `.env` files to version control
2. **API Keys**: Use Google Secret Manager for production
3. **HTTPS**: App Engine provides automatic HTTPS
4. **Firewall**: Configure VPC firewall rules if needed

## 🚨 Troubleshooting

### Common Issues:

1. **Build Failures**:
   ```bash
   # Check build logs
   gcloud app logs read -s default --severity=ERROR
   ```

2. **Port Issues**:
   - Ensure your app listens on `0.0.0.0:8080`
   - Check the `PORT` environment variable

3. **Dependency Issues**:
   ```bash
   # Test locally with Docker
   docker build -t test-app .
   docker run -p 8080:8080 test-app
   ```

4. **Memory Issues**:
   - Increase memory in `app.yaml`
   - Optimize your application code

### Getting Help:

- [Google App Engine Documentation](https://cloud.google.com/appengine/docs)
- [Docker Documentation](https://docs.docker.com/)
- [uv Documentation](https://github.com/astral-sh/uv)

## 📈 Performance Optimization

1. **Use uv**: Faster dependency installation
2. **Optimize Docker layers**: Copy requirements first
3. **Enable caching**: Use `.dockerignore` effectively
4. **Monitor resources**: Adjust CPU/memory as needed

## 💰 Cost Optimization

1. **Set instance limits**: Configure min/max instances
2. **Use automatic scaling**: Scale down when not in use
3. **Monitor usage**: Check Cloud Console billing
4. **Optimize resources**: Right-size CPU/memory allocation

---

**Happy Trading! 🚀📈**
