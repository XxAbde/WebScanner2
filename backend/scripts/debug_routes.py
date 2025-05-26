#!/usr/bin/env python3
"""
Debug script to check registered routes
"""
import sys
import os

# Add the parent directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app

def debug_routes():
    """Debug all registered routes"""
    app = create_app()
    
    print("🔍 Debugging Flask Routes")
    print("=" * 50)
    
    with app.app_context():
        print(f"📱 App Name: {app.name}")
        print(f"🌍 Environment: {app.config.get('FLASK_ENV', 'unknown')}")
        print(f"🔧 Debug Mode: {app.debug}")
        print()
        
        print("📋 All Registered Routes:")
        print("-" * 50)
        
        rules = []
        for rule in app.url_map.iter_rules():
            methods = ','.join(sorted(rule.methods - {'HEAD', 'OPTIONS'}))
            
            # Safe way to get the URL without building it
            url = str(rule.rule)
            
            rules.append({
                'url': url,
                'methods': methods,
                'endpoint': rule.endpoint
            })
        
        # Sort by URL
        rules.sort(key=lambda x: x['url'])
        
        for rule in rules:
            print(f"{rule['methods']:<15} {rule['url']:<40} {rule['endpoint']}")
        
        print()
        print(f"📊 Total Routes: {len(rules)}")
        
        # Check for auth routes specifically
        auth_routes = [r for r in rules if '/auth' in r['url']]
        api_routes = [r for r in rules if '/api/v1' in r['url']]
        
        print(f"🔐 Auth Routes: {len(auth_routes)}")
        print(f"🌐 API Routes: {len(api_routes)}")
        
        if auth_routes:
            print("\n🔐 Auth Routes Found:")
            for route in auth_routes:
                print(f"   {route['methods']:<15} {route['url']}")
        
        if api_routes:
            print(f"\n🌐 API Routes Found:")
            for route in api_routes:
                print(f"   {route['methods']:<15} {route['url']}")
        
        if not auth_routes:
            print("❌ No auth routes found!")
            print("💡 Checking for namespace registration issues...")

if __name__ == '__main__':
    debug_routes()