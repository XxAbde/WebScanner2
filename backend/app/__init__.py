from flask import Flask, jsonify, request  # Add 'request' here
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
    
    # Configure CORS FIRST - before any routes
    CORS(app, 
         resources={
             r"/api/*": {
                 "origins": ["http://localhost:3000", "http://127.0.0.1:3000"],
                 "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                 "allow_headers": ["Content-Type", "Authorization"]
             }
         },
         supports_credentials=True)
    
    # Add manual CORS headers for all responses
    @app.after_request
    def after_request(response):
        origin = request.headers.get('Origin')
        if origin in ['http://localhost:3000', 'http://127.0.0.1:3000']:
            response.headers.add('Access-Control-Allow-Origin', origin)
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
            response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
            response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    mail.init_app(app)
    
    # Import models
    try:
        from app.models import User
        print("✅ Models imported successfully")
    except Exception as e:
        print(f"⚠️  Models import error: {e}")
    
    # Configure JWT
    configure_jwt(app)
    
    # Register basic routes
    register_basic_routes(app)
    
    # Initialize and register API with Blueprint approach
    register_api_with_blueprint(app)
    
    # Register CLI commands
    register_cli_commands(app)
    
    # Register error handlers
    register_error_handlers(app)
    
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

def register_basic_routes(app):
    """Register basic routes"""
    
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
            'supported_origins': ['http://localhost:3000', 'http://127.0.0.1:3000'],
            'note': 'Visit /docs/ for interactive API documentation'
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

def register_api_with_blueprint(app):
    """Register Flask-RESTX API using Blueprint approach"""
    try:
        print("🔄 Setting up API with Blueprint...")
        
        from flask import Blueprint
        from flask_restx import Api, Namespace, Resource
        
        # Create a Blueprint for API
        api_bp = Blueprint('api', __name__, url_prefix='/api/v1')
        
        # Create API instance on the blueprint
        api = Api(
            api_bp,
            version='1.0',
            title='Vulnerability Scanner API',
            description='A comprehensive vulnerability scanning API',
            doc='/docs/'
        )
        
        print("✅ API Blueprint created")
        
        # Create test namespace
        test_ns = Namespace('test', description='Test operations')
        
        @test_ns.route('/ping')
        class TestPing(Resource):
            def get(self):
                return {
                    'message': 'pong', 
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'path': '/api/v1/test/ping',
                    'method': 'GET',
                    'cors_enabled': True
                }
            
            def options(self):
                return {'message': 'CORS preflight successful'}
        
        @test_ns.route('/cors-test')
        class CorsTest(Resource):
            def get(self):
                return {
                    'message': 'CORS test successful',
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'origin': request.headers.get('Origin', 'unknown'),
                    'method': 'GET'
                }
            
            def post(self):
                return {
                    'message': 'CORS POST test successful',
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'data_received': request.get_json() or {},
                    'origin': request.headers.get('Origin', 'unknown'),
                    'method': 'POST'
                }
            
            def options(self):
                return {'message': 'CORS preflight for cors-test successful'}
        
        api.add_namespace(test_ns, path='/test')
        print("✅ Test namespace registered")
        
        # Create auth namespace
        auth_ns = Namespace('auth', description='Authentication operations')
        
        @auth_ns.route('/ping')
        class AuthPing(Resource):
            def get(self):
                return {
                    'message': 'Auth service is working!', 
                    'path': '/api/v1/auth/ping',
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'cors_enabled': True
                }
            
            def options(self):
                return {'message': 'CORS preflight for auth ping successful'}
        
        @auth_ns.route('/register')
        class Register(Resource):
            def options(self):
                """Handle preflight requests explicitly"""
                return {
                    'message': 'CORS preflight successful for register',
                    'methods': ['GET', 'POST', 'OPTIONS'],
                    'headers': ['Content-Type', 'Authorization']
                }, 200
            
            def post(self):
                try:
                    data = request.get_json() or {}
                    print(f"🔄 Registration attempt for: {data.get('email', 'unknown')}")
                    
                    # Simple validation
                    email = data.get('email', '').strip().lower()
                    username = data.get('username', '').strip()
                    password = data.get('password', '')
                    
                    if not all([email, username, password]):
                        return {'error': 'Email, username, and password are required'}, 400
                    
                    # Check if user exists
                    try:
                        from app.models import User
                        existing_user = User.query.filter(
                            (User.email == email) | (User.username == username)
                        ).first()
                        
                        if existing_user:
                            return {'error': 'User already exists'}, 400
                        
                        # Create user
                        new_user = User(
                            email=email,
                            username=username,
                            password=password
                        )
                        
                        db.session.add(new_user)
                        db.session.commit()
                        print(f"✅ User created successfully: {username}")
                        
                        # Create access token
                        from flask_jwt_extended import create_access_token, create_refresh_token
                        access_token = create_access_token(identity=new_user.id)
                        refresh_token = create_refresh_token(identity=new_user.id)
                        
                        return {
                            'message': 'User registered successfully',
                            'user': new_user.to_dict(),
                            'access_token': access_token,
                            'refresh_token': refresh_token,
                            'expires_in': 3600
                        }, 201
                        
                    except Exception as model_error:
                        print(f"❌ Database error during registration: {model_error}")
                        db.session.rollback()
                        return {
                            'error': 'Registration failed',
                            'details': str(model_error),
                            'note': 'Database error occurred'
                        }, 500
                    
                except Exception as e:
                    print(f"❌ General error during registration: {e}")
                    return {'error': 'Registration failed', 'details': str(e)}, 500
            
            def get(self):
                return {
                    'message': 'Registration endpoint',
                    'method': 'POST',
                    'required_fields': ['email', 'username', 'password'],
                    'path': '/api/v1/auth/register',
                    'cors_enabled': True
                }
        
        @auth_ns.route('/login')
        class Login(Resource):
            def options(self):
                """Handle preflight requests explicitly"""
                return {
                    'message': 'CORS preflight successful for login',
                    'methods': ['POST', 'OPTIONS'],
                    'headers': ['Content-Type', 'Authorization']
                }, 200
            
            def post(self):
                try:
                    data = request.get_json() or {}
                    print(f"🔄 Login attempt for: {data.get('email', 'unknown')}")
                    
                    email = data.get('email', '').strip().lower()
                    password = data.get('password', '')
                    
                    if not email or not password:
                        return {'error': 'Email and password are required'}, 400
                    
                    try:
                        from flask_jwt_extended import create_access_token, create_refresh_token
                        from app.models import User
                        
                        user = User.query.filter_by(email=email).first()
                        
                        if not user or not user.check_password(password):
                            print(f"❌ Invalid login attempt for: {email}")
                            return {'error': 'Invalid credentials'}, 401
                        
                        # Create tokens
                        access_token = create_access_token(identity=user.id)
                        refresh_token = create_refresh_token(identity=user.id)
                        
                        # Update last login
                        user.last_login = datetime.utcnow()
                        db.session.commit()
                        
                        print(f"✅ User logged in successfully: {user.username}")
                        
                        return {
                            'message': 'Login successful',
                            'access_token': access_token,
                            'refresh_token': refresh_token,
                            'user': user.to_dict(),
                            'expires_in': 3600
                        }, 200
                        
                    except Exception as model_error:
                        print(f"❌ Database error during login: {model_error}")
                        return {
                            'error': 'Login failed',
                            'details': str(model_error),
                            'note': 'Database error occurred'
                        }, 500
                    
                except Exception as e:
                    print(f"❌ General error during login: {e}")
                    return {'error': 'Login failed', 'details': str(e)}, 500
        
        api.add_namespace(auth_ns, path='/auth')
        print("✅ Auth namespace registered")
        
        # Register the blueprint with the app
        app.register_blueprint(api_bp)
        print("✅ API Blueprint registered with app")
        
        # Also register docs at root level for convenience
        @app.route('/docs/')
        def docs_redirect():
            from flask import redirect
            return redirect('/api/v1/docs/')
        
        print("\n📋 Expected API Routes:")
        print("   GET        /api/v1/test/ping")
        print("   GET,POST   /api/v1/test/cors-test")
        print("   GET        /api/v1/auth/ping")
        print("   GET,POST   /api/v1/auth/register")
        print("   POST       /api/v1/auth/login")
        print("   GET        /api/v1/docs/")
        
        return api
        
    except Exception as e:
        print(f"❌ Error setting up API: {e}")
        import traceback
        traceback.print_exc()

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

def register_error_handlers(app):
    """Register error handlers"""
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found', 'message': 'The requested resource was not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        try:
            db.session.rollback()
        except:
            pass
        return jsonify({'error': 'Internal server error', 'message': 'An internal error occurred'}), 500

# Export db and other commonly needed objects at module level
__all__ = ['create_app', 'db', 'migrate', 'jwt', 'mail']
