#!/usr/bin/env python3
"""
Development server entry point for Web Vulnerability Scanner
Usage: python run.py [--port PORT] [--host HOST] [--debug]
"""
import os
import sys
import argparse
import logging
from datetime import datetime, timezone

# Add the current directory to Python path to ensure imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import create_app
    # Don't import db here - it will be available through the app context
except ImportError as e:
    print(f"❌ Error importing app modules: {e}")
    print("💡 Make sure you're in the project root directory and virtual environment is activated")
    sys.exit(1)

def setup_logging():
    """Set up logging for development"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('app.log', mode='a')
        ]
    )
    
    # Reduce noise from some libraries
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)

def find_free_port(start_port=5000):
    """Find a free port starting from start_port"""
    import socket
    port = start_port
    while port < start_port + 100:  # Try 100 ports
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('0.0.0.0', port))
                return port
        except OSError:
            port += 1
    return None

def print_startup_info(app, host, port, debug):
    """Print startup information"""
    print("\n" + "="*60)
    print("🛡️  WEB VULNERABILITY SCANNER - BACKEND SERVER")
    print("="*60)
    print(f"📅 Started: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC")
    print(f"👤 User: {os.environ.get('USER', 'unknown')}")
    print(f"🌍 Environment: {app.config.get('FLASK_ENV', 'development')}")
    print(f"🔧 Debug Mode: {'ON' if debug else 'OFF'}")
    print(f"🏠 Server: http://{host}:{port}")
    print(f"📚 API Docs: http://{host}:{port}/docs/")
    print(f"🔍 Health Check: http://{host}:{port}/health")
    print(f"🧪 Test API: http://{host}:{port}/api/v1/test/ping")
    print("="*60)
    
    if debug:
        print("⚠️  WARNING: Debug mode is ON - Not for production use!")
    
    print("🚀 Server starting...")
    print("🛑 Press Ctrl+C to stop\n")

def main():
    """Main application entry point"""
    parser = argparse.ArgumentParser(description='Run the Vulnerability Scanner backend server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=5000, help='Port to bind to (default: 5000)')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--auto-port', action='store_true', help='Automatically find free port if specified port is busy')
    
    args = parser.parse_args()
    
    # Set up logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Get configuration from environment or command line
    flask_env = os.environ.get('FLASK_ENV', 'development')
    debug_mode = args.debug or (flask_env == 'development')
    
    # Handle port conflicts
    port = args.port
    if args.auto_port:
        free_port = find_free_port(port)
        if free_port and free_port != port:
            print(f"⚠️  Port {port} is busy, using port {free_port} instead")
            port = free_port
        elif not free_port:
            print("❌ Could not find a free port")
            sys.exit(1)
    
    try:
        # Create Flask app
        app = create_app(flask_env)
        
        # Print startup information
        print_startup_info(app, args.host, port, debug_mode)
        
        # Start the server
        app.run(
            host=args.host,
            port=port,
            debug=debug_mode,
            use_reloader=debug_mode,
            threaded=True
        )
        
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"❌ Port {port} is already in use")
            print("💡 Try one of these solutions:")
            print(f"   1. Use a different port: python run.py --port {port + 1}")
            print("   2. Use auto-port finding: python run.py --auto-port")
        else:
            print(f"❌ Network error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        print(f"❌ Failed to start server: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()