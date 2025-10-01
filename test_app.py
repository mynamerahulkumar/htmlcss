#!/usr/bin/env python3
"""
Test script to verify the trading bot application is working correctly
"""

import requests
import json
import time

def test_api_endpoints():
    """Test all API endpoints"""
    base_url = "http://localhost:5003"
    
    print("🧪 Testing Delta Exchange Trading Bot API")
    print("=" * 50)
    
    # Test 1: Status endpoint
    print("1. Testing /api/status endpoint...")
    try:
        response = requests.get(f"{base_url}/api/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Status endpoint working")
            print(f"   📊 Bot running: {data.get('running', False)}")
            print(f"   💰 Current price: ${data.get('current_price', 0)}")
        else:
            print(f"   ❌ Status endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Status endpoint error: {e}")
    
    # Test 2: Main page
    print("\n2. Testing main dashboard page...")
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print(f"   ✅ Dashboard page accessible")
            print(f"   📄 Content length: {len(response.text)} characters")
        else:
            print(f"   ❌ Dashboard page failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Dashboard page error: {e}")
    
    # Test 3: Positions endpoint
    print("\n3. Testing /api/positions endpoint...")
    try:
        response = requests.get(f"{base_url}/api/positions", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Positions endpoint working")
            print(f"   📈 Success: {data.get('success', False)}")
        else:
            print(f"   ❌ Positions endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Positions endpoint error: {e}")
    
    # Test 4: Orders endpoint
    print("\n4. Testing /api/orders endpoint...")
    try:
        response = requests.get(f"{base_url}/api/orders", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Orders endpoint working")
            print(f"   📋 Success: {data.get('success', False)}")
        else:
            print(f"   ❌ Orders endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Orders endpoint error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 API testing completed!")
    print("🌐 Dashboard available at: http://localhost:5003")
    print("📊 You can now:")
    print("   - Open the dashboard in your browser")
    print("   - Configure your API credentials")
    print("   - Start automated trading")
    print("   - Monitor real-time signals and positions")

if __name__ == "__main__":
    test_api_endpoints()
