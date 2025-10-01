#!/usr/bin/env python3
"""
Test script to verify API credential logging is working
"""

import requests
import json
import time

def test_api_logging():
    """Test starting the bot to see API credential logging"""
    base_url = "http://localhost:5003"
    
    print("🧪 Testing API Credential Logging")
    print("=" * 40)
    
    # Test data with sample credentials
    test_data = {
        "api_key": "test_api_key_12345",
        "api_secret": "test_secret_67890", 
        "symbol": "BTCUSD"
    }
    
    print("1. Starting bot with test credentials to see logging...")
    print("   📝 Check the terminal/console where the Flask app is running")
    print("   📝 You should see masked API credentials in the logs")
    print("   📝 Format: API Key: test_api...2345")
    print("   📝 Format: API Secret: test_secr...7890")
    
    try:
        response = requests.post(
            f"{base_url}/api/start", 
            json=test_data,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Bot start request sent successfully")
            print(f"   📊 Response: {data.get('message', 'No message')}")
        else:
            print(f"   ❌ Bot start failed: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Bot start error: {e}")
    
    print("\n" + "=" * 40)
    print("🎉 API logging test completed!")
    print("💡 Check the Flask app console for detailed API credential logs")
    print("🔍 Look for lines like:")
    print("   - 'Starting bot with API Key: test_api...2345'")
    print("   - 'WebTradingBot initialized with API Key: test_api...2345'")
    print("   - 'DeltaExchangeAPI initialized with API Key: test_api...2345'")
    print("   - 'Making API request: GET https://api.india.delta.exchange/...'")

if __name__ == "__main__":
    test_api_logging()
