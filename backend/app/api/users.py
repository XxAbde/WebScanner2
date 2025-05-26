from flask_restx import Namespace, Resource
from flask import request
from app.models import User
from flask_jwt_extended import create_access_token, create_refresh_token
from app.extensions import db

# Create a namespace for user-related operations
users_ns = Namespace('users', description='User authentication and management')

@users_ns.route('/register')
class Register(Resource):
    def post(self):
        """Register a new user"""
        data = request.get_json() or {}

        email = data.get('email', '').strip().lower()
        username = data.get('username', '').strip()
        password = data.get('password', '')

        # Validate inputs
        if not email or not username or not password:
            return {'error': 'Email, username, and password are required'}, 400

        # Check if user already exists
        existing_user = User.query.filter((User.email == email) | (User.username == username)).first()
        if existing_user:
            return {'error': 'User already exists'}, 400

        # Create and save the new user
        new_user = User(email=email, username=username, password=password)
        db.session.add(new_user)
        db.session.commit()

        # Generate authentication tokens
        access_token = create_access_token(identity=new_user.id)
        refresh_token = create_refresh_token(identity=new_user.id)

        return {
            'message': 'User registered successfully',
            'user': new_user.to_dict(),
            'access_token': access_token,
            'refresh_token': refresh_token,
            'expires_in': 3600
        }, 201

@users_ns.route('/login')
class Login(Resource):
    def post(self):
        """Log in an existing user"""
        data = request.get_json() or {}

        email = data.get('email', '').strip().lower()
        password = data.get('password', '')

        # Validate inputs
        if not email or not password:
            return {'error': 'Email and password are required'}, 400

        # Check if user exists and password is correct
        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            return {'error': 'Invalid credentials'}, 401

        # Generate authentication tokens
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)

        return {
            'message': 'Login successful',
            'user': user.to_dict(),
            'access_token': access_token,
            'refresh_token': refresh_token,
            'expires_in': 3600
        }, 200

@users_ns.route('/<int:user_id>')
class UserProfile(Resource):
    def get(self, user_id):
        """Get user profile by ID"""
        user = User.query.get_or_404(user_id)
        return user.to_dict(), 200

    def delete(self, user_id):
        """Delete a user by ID"""
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return {'message': 'User deleted successfully'}, 200