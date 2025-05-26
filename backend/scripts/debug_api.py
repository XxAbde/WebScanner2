#!/usr/bin/env python3
"""
Debug API registration
"""
import sys
import os

# Add the parent directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def debug_api():
    """Debug API setup"""
    print("🔍 Debugging API Setup")
    print("=" * 40)
    
    try:
        from app import create_app
        app = create_app()
        
        print("✅ App created successfully")
        
        with app.app_context():
            print(f"📱 App Name: {app.name}")
            print(f"🔧 Debug Mode: {app.debug}")
            
            print("\n📋 All Routes:")
            for rule in app.url_map.iter_rules():
                methods = ','.join(sorted(rule.methods - {'HEAD', 'OPTIONS'}))
                print(f"   {methods:<10} {rule.rule:<40} {rule.endpoint}")
            
            # Check specifically for API routes
            api_routes = [r for r in app.url_map.iter_rules() if '/api/' in str(r.rule)]
            print(f"\n🌐 API Routes Found: {len(api_routes)}")
            for route in api_routes:
                methods = ','.join(sorted(route.methods - {'HEAD', 'OPTIONS'}))
                print(f"   {methods:<10} {route.rule}")
            
            if not api_routes:
                print("❌ No API routes found!")
                print("💡 Checking for registration errors...")
                
                # Try to manually register namespaces
                try:
                    from app.extensions import api
                    print(f"📦 API object: {api}")
                    print(f"📦 API namespaces: {list(api.namespaces)}")
                except Exception as e:
                    print(f"❌ Error accessing API: {e}")
                
    except Exception as e:
        print(f"❌ Error creating app: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    debug_api()