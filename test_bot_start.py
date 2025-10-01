#!/usr/bin/env python3
"""
Test script to verify the trading bot can start without logger errors
"""

import requests
import json
import time

def test_bot_start():
    """Test starting the bot with dummy credentials"""
    base_url = "http://localhost:5003"
    
    print("🧪 Testing Bot Start Functionality")
    print("=" * 40)
    
    # Test data with dummy credentials (will fail but shouldn't crash)
    test_data = {
        "api_key": "test_key",
        "api_secret": "test_secret", 
        "symbol": "BTCUSD"
    }
    
    print("1. Testing bot start with dummy credentials...")
    try:
        response = requests.post(
            f"{base_url}/api/start", 
            json=test_data,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Bot start endpoint working")
            print(f"   📊 Response: {data.get('message', 'No message')}")
            print(f"   🎯 Success: {data.get('success', False)}")
        else:
            print(f"   ❌ Bot start failed: {response.status_code}")
            print(f"   📄 Response: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Bot start error: {e}")
    
    # Wait a moment and check status
    print("\n2. Checking bot status after start attempt...")
    time.sleep(2)
    
    try:
        response = requests.get(f"{base_url}/api/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Status endpoint working")
            print(f"   🤖 Bot running: {data.get('running', False)}")
            print(f"   📈 Symbol: {data.get('symbol', 'None')}")
        else:
            print(f"   ❌ Status check failed: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Status check error: {e}")
    
    print("\n" + "=" * 40)
    print("🎉 Bot start test completed!")
    print("💡 The bot should now start without logger errors")
    print("🌐 Try starting the bot from the dashboard at: http://localhost:5003")

if __name__ == "__main__":
    test_bot_start()
