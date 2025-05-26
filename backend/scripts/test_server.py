#!/usr/bin/env python3
"""
Test server endpoints
"""
import requests
import json
from datetime import datetime

def test_endpoints():
    """Test all available endpoints"""
    base_url = "http://localhost:5001"
    
    endpoints = [
        "/",
        "/health", 
        "/status",
        "/docs/",
        "/api/v1/"
    ]
    
    print("🧪 Testing Web Vulnerability Scanner API")
    print("=" * 50)
    print(f"🕒 Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌍 Base URL: {base_url}")
    print()
    
    for endpoint in endpoints:
        try:
            url = f"{base_url}{endpoint}"
            response = requests.get(url, timeout=5)
            
            status_icon = "✅" if response.status_code == 200 else "❌"
            print(f"{status_icon} {endpoint:<15} Status: {response.status_code}")
            
            if response.headers.get('content-type', '').startswith('application/json'):
                try:
                    data = response.json()
                    if endpoint == "/":
                        print(f"   📝 Message: {data.get('message', 'N/A')}")
                        print(f"   📊 Status: {data.get('status', 'N/A')}")
                    elif endpoint == "/health":
                        print(f"   💾 Database: {data.get('database', 'N/A')}")
                        print(f"   🌍 Environment: {data.get('environment', 'N/A')}")
                    elif endpoint == "/status":
                        services = data.get('services', {})
                        print(f"   💾 Database: {services.get('database', {}).get('status', 'N/A')}")
                        print(f"   🔴 Redis: {services.get('redis', {}).get('status', 'N/A')}")
                except:
                    print(f"   📄 Response: {response.text[:100]}...")
            else:
                print(f"   📄 Content-Type: {response.headers.get('content-type', 'N/A')}")
            
            print()
            
        except requests.exceptions.RequestException as e:
            print(f"❌ {endpoint:<15} Error: {e}")
            print()
    
    print("🎯 Quick API Test Commands:")
    print(f"   curl {base_url}/")
    print(f"   curl {base_url}/health")
    print(f"   curl {base_url}/status")
    print(f"   curl {base_url}/api/v1/")

if __name__ == '__main__':
    test_endpoints()