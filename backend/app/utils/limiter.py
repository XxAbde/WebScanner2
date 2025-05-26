from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Global limiter instance that will be initialized in create_app
limiter = None

def get_limiter():
    """Get the global limiter instance"""
    return limiter

def init_limiter(app):
    """Initialize the global limiter with app context"""
    global limiter
    
    try:
        # Try Redis backend first
        limiter = Limiter(
            key_func=get_remote_address,
            default_limits=["200 per day", "50 per hour"],
            storage_uri=app.config.get('RATELIMIT_STORAGE_URI', 'redis://localhost:6379/1')
        )
        limiter.init_app(app)
        print("✅ Rate limiter initialized with Redis backend")
        return limiter
    except Exception as e:
        print(f"⚠️  Redis not available, using memory storage: {e}")
        # Fall back to memory storage
        limiter = Limiter(
            key_func=get_remote_address,
            default_limits=["200 per day", "50 per hour"],
            storage_uri="memory://"
        )
        limiter.init_app(app)
        print("✅ Rate limiter initialized with memory storage")
        return limiter