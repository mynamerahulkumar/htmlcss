#!/usr/bin/env python3
"""
Delta Exchange Trading Bot - Full Stack Application
Main launcher for the trading bot web application
"""

import os
import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """Check if all required dependencies are installed"""
    try:
        import flask
        import flask_cors
        import flask_socketio
        import pandas
        import numpy
        import requests
        from dotenv import load_dotenv
        print("✅ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please install dependencies with: pip install -r requirements.txt")
        return False

def setup_environment():
    """Setup environment variables if .env file doesn't exist"""
    env_file = Path(".env")
    example_file = Path("config.env.example")
    
    if not env_file.exists() and example_file.exists():
        print("📝 Creating .env file from example...")
        with open(example_file, 'r') as f:
            content = f.read()
        with open(env_file, 'w') as f:
            f.write(content)
        print("✅ .env file created. Please update it with your API credentials.")
        return False
    elif not env_file.exists():
        print("⚠️  No .env file found. Please create one with your API credentials.")
        return False
    
    return True

def main():
    """Main function to launch the trading bot web application"""
    print("🚀 Delta Exchange Trading Bot - Full Stack Application")
    print("=" * 60)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Setup environment
    if not setup_environment():
        print("\n📋 Next steps:")
        print("1. Update the .env file with your Delta Exchange API credentials")
        print("2. Run this script again to start the trading bot")
        sys.exit(1)
    
    # Change to backend directory and start the Flask app
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print("❌ Backend directory not found!")
        sys.exit(1)
    
    print("🌐 Starting web application...")
    print("📊 Dashboard will be available at: http://localhost:5003")
    print("🛑 Press Ctrl+C to stop the application")
    print("=" * 60)
    
    try:
        # Change to backend directory and run the Flask app
        original_dir = os.getcwd()
        os.chdir(backend_dir)
        
        # Set environment variable to find .env file in parent directory
        env_path = os.path.join(original_dir, ".env")
        if os.path.exists(env_path):
            os.environ["ENV_FILE_PATH"] = env_path
        
        subprocess.run([sys.executable, "app.py"], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Application stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting application: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
