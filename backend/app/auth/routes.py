from flask import request, jsonify, current_app
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import (
    create_access_token, create_refresh_token, 
    jwt_required, get_jwt_identity, get_jwt
)
from datetime import datetime, timedelta
import re

from ..extensions import db
from ..models import User

# Create namespace for auth endpoints
auth_ns = Namespace('auth', description='Authentication operations')

# Define models for API documentation
login_model = auth_ns.model('Login', {
    'email': fields.String(required=True, description='User email', example='user@example.com'),
    'password': fields.String(required=True, description='User password', example='password123')
})

register_model = auth_ns.model('Register', {
    'email': fields.String(required=True, description='User email', example='user@example.com'),
    'username': fields.String(required=True, description='Username', example='johndoe'),
    'password': fields.String(required=True, description='Password (min 8 chars)', example='Password123'),
    'confirm_password': fields.String(required=True, description='Password confirmation', example='Password123')
})

user_response = auth_ns.model('UserResponse', {
    'id': fields.Integer(description='User ID'),
    'email': fields.String(description='User email'),
    'username': fields.String(description='Username'),
    'is_guest': fields.Boolean(description='Is guest user'),
    'scan_limit': fields.Integer(description='Scan limit'),
    'remaining_scans': fields.Raw(description='Remaining scans')
})

token_response = auth_ns.model('TokenResponse', {
    'message': fields.String(description='Response message'),
    'access_token': fields.String(description='JWT access token'),
    'refresh_token': fields.String(description='JWT refresh token'),
    'expires_in': fields.Integer(description='Token expiration time in seconds'),
    'user': fields.Nested(user_response, description='User information')
})

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validate password strength"""
    errors = []
    
    if len(password) < 8:
        errors.append('Password must be at least 8 characters long')
    
    if not re.search(r'[A-Z]', password):
        errors.append('Password must contain at least one uppercase letter')
    
    if not re.search(r'[a-z]', password):
        errors.append('Password must contain at least one lowercase letter')
    
    if not re.search(r'\d', password):
        errors.append('Password must contain at least one number')
    
    return errors

@auth_ns.route('/register')
class Register(Resource):
    @auth_ns.expect(register_model)
    @auth_ns.response(201, 'User registered successfully', token_response)
    @auth_ns.response(400, 'Invalid input or user already exists')
    def post(self):
        """Register a new user"""
        try:
            data = request.get_json()
            
            if not data:
                return {'error': 'No data provided'}, 400
            
            # Extract and validate data
            email = data.get('email', '').strip().lower()
            username = data.get('username', '').strip()
            password = data.get('password', '')
            confirm_password = data.get('confirm_password', '')
            
            # Validation
            errors = []
            
            if not email:
                errors.append('Email is required')
            elif not validate_email(email):
                errors.append('Invalid email format')
            
            if not username:
                errors.append('Username is required')
            elif len(username) < 3:
                errors.append('Username must be at least 3 characters')
            elif not re.match(r'^[a-zA-Z0-9_]+$', username):
                errors.append('Username can only contain letters, numbers, and underscores')
            
            if not password:
                errors.append('Password is required')
            else:
                password_errors = validate_password(password)
                errors.extend(password_errors)
            
            if password != confirm_password:
                errors.append('Passwords do not match')
            
            if errors:
                return {'error': 'Validation failed', 'details': errors}, 400
            
            # Check if user already exists
            existing_user = User.query.filter(
                (User.email == email) | (User.username == username)
            ).first()
            
            if existing_user:
                if existing_user.email == email:
                    return {'error': 'Email already registered'}, 400
                else:
                    return {'error': 'Username already taken'}, 400
            
            # Create new user
            new_user = User(
                email=email,
                username=username,
                password=password,
                is_guest=False
            )
            
            db.session.add(new_user)
            db.session.commit()
            
            # Create tokens
            access_token = create_access_token(
                identity=new_user.id,
                additional_claims={'user_type': 'registered'}
            )
            refresh_token = create_refresh_token(identity=new_user.id)
            
            return {
                'message': 'User registered successfully',
                'access_token': access_token,
                'refresh_token': refresh_token,
                'expires_in': current_app.config['JWT_ACCESS_TOKEN_EXPIRES'].total_seconds(),
                'user': new_user.to_dict()
            }, 201
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Registration error: {e}")
            return {'error': 'Registration failed', 'message': str(e)}, 500

@auth_ns.route('/login')
class Login(Resource):
    @auth_ns.expect(login_model)
    @auth_ns.response(200, 'Login successful', token_response)
    @auth_ns.response(401, 'Invalid credentials')
    def post(self):
        """User login"""
        try:
            data = request.get_json()
            
            if not data:
                return {'error': 'No data provided'}, 400
            
            email = data.get('email', '').strip().lower()
            password = data.get('password', '')
            
            if not email or not password:
                return {'error': 'Email and password are required'}, 400
            
            # Find user
            user = User.query.filter_by(email=email).first()
            
            if not user or not user.check_password(password):
                return {'error': 'Invalid email or password'}, 401
            
            if not user.is_active:
                return {'error': 'Account is disabled'}, 401
            
            # Update last login
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            # Create tokens
            access_token = create_access_token(
                identity=user.id,
                additional_claims={
                    'user_type': 'guest' if user.is_guest else 'registered',
                    'is_admin': user.is_admin
                }
            )
            refresh_token = create_refresh_token(identity=user.id)
            
            return {
                'message': 'Login successful',
                'access_token': access_token,
                'refresh_token': refresh_token,
                'expires_in': current_app.config['JWT_ACCESS_TOKEN_EXPIRES'].total_seconds(),
                'user': user.to_dict()
            }, 200
            
        except Exception as e:
            current_app.logger.error(f"Login error: {e}")
            return {'error': 'Login failed', 'message': str(e)}, 500

@auth_ns.route('/me')
class UserProfile(Resource):
    @jwt_required()
    @auth_ns.response(200, 'User profile retrieved')
    @auth_ns.response(401, 'Authentication required')
    def get(self):
        """Get current user profile"""
        try:
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)
            
            if not user:
                return {'error': 'User not found'}, 404
            
            return {
                'user': user.to_dict(),
                'permissions': {
                    'can_scan': user.can_scan(),
                    'remaining_scans': user.get_remaining_scans(),
                    'is_admin': user.is_admin
                }
            }, 200
            
        except Exception as e:
            current_app.logger.error(f"Profile error: {e}")
            return {'error': 'Failed to retrieve profile'}, 500