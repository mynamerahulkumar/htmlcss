#!/usr/bin/env python3
"""
Delta Exchange Trading Bot - Production Launcher for Google App Engine
Optimized for cloud deployment
"""

import os
import sys
import logging
from pathlib import Path

# Configure logging for production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_production_environment():
    """Setup environment for production deployment"""
    # Set production environment variables
    os.environ.setdefault('FLASK_ENV', 'production')
    os.environ.setdefault('FLASK_APP', 'backend/app.py')
    
    # Set port for App Engine
    port = os.environ.get('PORT', 8080)
    os.environ['PORT'] = str(port)
    
    # Add current directory to Python path
    current_dir = Path(__file__).parent.absolute()
    sys.path.insert(0, str(current_dir))
    
    logger.info(f"Production environment setup complete. Port: {port}")

def main():
    """Main function for production deployment"""
    logger.info("🚀 Delta Exchange Trading Bot - Production Mode")
    logger.info("=" * 60)
    
    # Setup production environment
    setup_production_environment()
    
    # Import and run the Flask app directly
    try:
        from backend.app import app, socketio
        
        # Get port from environment
        port = int(os.environ.get('PORT', 8080))
        host = '0.0.0.0'  # Cloud Run requires binding to all interfaces
        
        logger.info(f"🌐 Starting web application on {host}:{port}")
        logger.info(f"🔧 Environment: {os.environ.get('FLASK_ENV', 'development')}")
        logger.info(f"📁 Python path: {sys.path}")
        logger.info("📊 Trading bot dashboard is ready")
        
        # Run the application
        socketio.run(
            app,
            host=host,
            port=port,
            debug=False,
            use_reloader=False,
            log_output=True,
            allow_unsafe_werkzeug=True
        )
        
    except ImportError as e:
        logger.error(f"❌ Failed to import application: {e}")
        logger.error(f"📁 Current working directory: {os.getcwd()}")
        logger.error(f"📁 Files in current directory: {os.listdir('.')}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Failed to start application: {e}")
        import traceback
        logger.error(f"📋 Traceback: {traceback.format_exc()}")
        sys.exit(1)

if __name__ == "__main__":
    main()
