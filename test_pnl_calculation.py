#!/usr/bin/env python3
"""
Test script to verify P&L calculation is working correctly
"""

import requests
import json
import time

def test_pnl_calculation():
    """Test P&L calculation with simulated position data"""
    base_url = "http://localhost:5003"
    
    print("🧪 Testing P&L Calculation")
    print("=" * 40)
    
    # Test 1: Check current status
    print("1. Checking current bot status...")
    try:
        response = requests.get(f"{base_url}/api/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Status endpoint working")
            print(f"   🤖 Bot running: {data.get('running', False)}")
            print(f"   💰 Current price: ${data.get('current_price', 0)}")
            print(f"   📊 P&L: ${data.get('pnl', 0)}")
            print(f"   📈 Position: {data.get('position', 'None')}")
            
            if data.get('position'):
                pos = data['position']
                print(f"   📋 Position details:")
                print(f"      - Side: {pos.get('side', 'N/A')}")
                print(f"      - Size: {pos.get('size', 'N/A')}")
                print(f"      - Entry Price: ${pos.get('entry_price', 'N/A')}")
                print(f"      - Unrealized P&L: ${pos.get('unrealized_pnl', 'N/A')}")
        else:
            print(f"   ❌ Status check failed: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Status check error: {e}")
    
    # Test 2: Check positions endpoint
    print("\n2. Checking positions endpoint...")
    try:
        response = requests.get(f"{base_url}/api/positions", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Positions endpoint working")
            print(f"   📈 Success: {data.get('success', False)}")
            positions = data.get('positions', [])
            print(f"   📊 Number of positions: {len(positions)}")
            
            if positions:
                for i, pos in enumerate(positions):
                    print(f"   📋 Position {i+1}:")
                    print(f"      - Symbol: {pos.get('product_symbol', 'N/A')}")
                    print(f"      - Size: {pos.get('size', 'N/A')}")
                    print(f"      - Entry Price: {pos.get('entry_price', 'N/A')}")
                    print(f"      - Unrealized P&L: {pos.get('unrealized_pnl', 'N/A')}")
            else:
                print("   📝 No positions found (this is normal if no trades have been executed)")
        else:
            print(f"   ❌ Positions check failed: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Positions check error: {e}")
    
    # Test 3: Manual trade to create a position (if bot is running)
    print("\n3. Testing manual trade to create position...")
    try:
        # First check if bot is running
        status_response = requests.get(f"{base_url}/api/status", timeout=5)
        if status_response.status_code == 200:
            status_data = status_response.json()
            if status_data.get('running'):
                print("   🤖 Bot is running, attempting manual buy order...")
                
                trade_data = {
                    "side": "buy",
                    "size": 1
                }
                
                response = requests.post(
                    f"{base_url}/api/manual-trade", 
                    json=trade_data,
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"   📊 Trade response: {data.get('message', 'No message')}")
                    print(f"   🎯 Success: {data.get('success', False)}")
                    
                    if data.get('success'):
                        print("   ⏳ Waiting 5 seconds for position to be created...")
                        time.sleep(5)
                        
                        # Check status again to see P&L
                        status_response = requests.get(f"{base_url}/api/status", timeout=5)
                        if status_response.status_code == 200:
                            status_data = status_response.json()
                            print(f"   📊 Updated P&L: ${status_data.get('pnl', 0)}")
                            if status_data.get('position'):
                                pos = status_data['position']
                                print(f"   📋 Position P&L: ${pos.get('unrealized_pnl', 0)}")
                else:
                    print(f"   ❌ Manual trade failed: {response.status_code}")
            else:
                print("   ⚠️  Bot is not running, skipping manual trade test")
        else:
            print("   ❌ Could not check bot status")
            
    except Exception as e:
        print(f"   ❌ Manual trade error: {e}")
    
    print("\n" + "=" * 40)
    print("🎉 P&L calculation test completed!")
    print("💡 P&L will show:")
    print("   - $0.00 when no position exists")
    print("   - Calculated value when position exists")
    print("   - Real-time updates via WebSocket")

if __name__ == "__main__":
    test_pnl_calculation()
