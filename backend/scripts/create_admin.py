#!/usr/bin/env python3
"""
Create admin user script
"""
import sys
import os
import getpass

# Add the parent directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import User

def create_admin_user():
    """Create an admin user"""
    app = create_app()
    
    with app.app_context():
        print("=== Create Admin User ===")
        
        # Get admin details
        email = input("Admin email: ").strip()
        username = input("Admin username: ").strip()
        
        # Check if user already exists
        existing_user = User.query.filter(
            (User.email == email) | (User.username == username)
        ).first()
        
        if existing_user:
            print(f"❌ User with email '{email}' or username '{username}' already exists!")
            return
        
        # Get password
        password = getpass.getpass("Admin password: ")
        confirm_password = getpass.getpass("Confirm password: ")
        
        if password != confirm_password:
            print("❌ Passwords don't match!")
            return
        
        if len(password) < 8:
            print("❌ Password must be at least 8 characters long!")
            return
        
        # Create admin user
        admin_user = User(
            email=email,
            username=username,
            password=password,
            is_guest=False,
            scan_limit=100  # High limit for admin
        )
        admin_user.is_admin = True
        
        try:
            db.session.add(admin_user)
            db.session.commit()
            print(f"✅ Admin user '{username}' created successfully!")
            print(f"📧 Email: {email}")
            print(f"🔑 You can now login with these credentials")
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating admin user: {e}")

if __name__ == '__main__':
    create_admin_user()