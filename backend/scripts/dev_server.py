#!/usr/bin/env python3
"""
Development helper script with additional features
"""
import os
import sys
import subprocess
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def check_services():
    """Check if required services are running"""
    services = {
        'postgresql': 'postgres',
        'redis': 'redis-server'
    }
    
    print("🔍 Checking required services...")
    all_running = True
    
    for service_name, process_name in services.items():
        try:
            result = subprocess.run(['pgrep', '-x', process_name], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ {service_name} is running")
            else:
                print(f"❌ {service_name} is not running")
                all_running = False
        except FileNotFoundError:
            print(f"⚠️  Could not check {service_name} status")
    
    return all_running

def start_services():
    """Start required services"""
    print("🚀 Starting services...")
    
    services = [
        ('postgresql', 'sudo systemctl start postgresql'),
        ('redis', 'sudo systemctl start redis-server')
    ]
    
    for service_name, command in services:
        try:
            print(f"   Starting {service_name}...")
            subprocess.run(command.split(), check=True, capture_output=True)
            print(f"   ✅ {service_name} started")
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Failed to start {service_name}: {e}")

def main():
    """Main function"""
    print("🛡️  Vulnerability Scanner - Development Server Starter")
    print("=" * 55)
    
    # Check if virtual environment is activated
    if not os.environ.get('VIRTUAL_ENV'):
        print("❌ Virtual environment not activated!")
        print("💡 Run: source venv/bin/activate")
        sys.exit(1)
    
    # Check if services are running
    if not check_services():
        response = input("\n🤔 Some services are not running. Start them? (y/N): ")
        if response.lower() == 'y':
            start_services()
            print("⏳ Waiting for services to start...")
            time.sleep(3)
        else:
            print("⚠️  Continuing without starting services...")
    
    # Set environment variables if not set
    if not os.environ.get('FLASK_APP'):
        os.environ['FLASK_APP'] = 'run.py'
    
    # Start the development server
    print("\n🚀 Starting Flask development server...")
    try:
        subprocess.run([sys.executable, 'run.py', '--debug'], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Development server stopped")
    except subprocess.CalledProcessError as e:
        print(f"❌ Server failed to start: {e}")

if __name__ == '__main__':
    main()