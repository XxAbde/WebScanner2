from flask import Flask, jsonify, request  # Ensure 'request' is imported
from flask_cors import CORS
import os
from datetime import datetime, timezone
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import and initialize extensions
from .extensions import db, migrate, jwt, mail

def create_app(config_name='development'):
    app = Flask(__name__)
    
    # Load configuration
    from app.config import config
    app.config.from_object(config[config_name])
    
    # Configure CORS
    CORS(app, 
         resources={
             r"/api/*": {
                 "origins": ["http://localhost:3000"],  # Allow requests from React dev server
                 "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                 "allow_headers": ["Content-Type", "Authorization"],
                 "supports_credentials": True
             }
         })
    
    # Add a global after_request handler for additional CORS headers
    @app.after_request
    def after_request(response):
        origin = request.headers.get('Origin')
        if origin == "http://localhost:3000":
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
            response.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,DELETE,OPTIONS"
            response.headers["Access-Control-Allow-Credentials"] = "true"
        return response
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    mail.init_app(app)
    
    # Register routes and blueprints
    register_routes(app)
    
    print("✅ CORS configured for frontend integration")
    print("📱 Server will accept requests from: http://localhost:3000")
    
    return app

def configure_jwt(app):
    """Configure JWT settings"""
    
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({'error': 'Token has expired'}), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({'error': 'Invalid token'}), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({'error': 'Authentication token required'}), 401

def register_routes(app):
    """Register all routes and blueprints"""
    @app.route('/')
    def index():
        return jsonify({
            'message': 'Web Vulnerability Scanner API',
            'version': '1.0.0',
            'status': 'running',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'documentation': '/docs/',
            'api_base': '/api/v1/',
            'cors_enabled': True,
            'supported_origins': ['http://localhost:3000']
        })
    
    @app.route('/health')
    def health_check():
        try:
            from sqlalchemy import text
            db.session.execute(text('SELECT 1'))
            db_status = "healthy"
        except Exception as e:
            db_status = f"unhealthy: {str(e)}"
        
        return jsonify({
            'status': 'healthy' if 'healthy' in db_status else 'degraded',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'database': db_status,
            'version': '1.0.0',
            'cors_enabled': True
        })

    # Register API blueprints
    from app.api import api_bp
    app.register_blueprint(api_bp)

def register_error_handlers(app):
    """Register error handlers"""
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found', 'message': 'The requested resource was not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        try:
            db.session.rollback()
        except Exception:
            pass
        return jsonify({'error': 'Internal server error', 'message': 'An internal error occurred'}), 500

def register_cli_commands(app):
    """Register custom CLI commands"""
    @app.cli.command()
    def init_db():
        db.create_all()
        print("✅ Database initialized!")
    
    @app.cli.command()
    def drop_db():
        db.drop_all()
        print("✅ Database tables dropped!")

# Export db and other commonly needed objects at module level
__all__ = ['create_app', 'db', 'migrate', 'jwt', 'mail']