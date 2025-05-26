#!/usr/bin/env python3
"""
Fix Flask-Migrate initialization
"""
import os
import sys
import shutil

# Add the parent directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from flask_migrate import init, migrate, upgrade

def fix_migration():
    """Fix migration setup"""
    app = create_app()
    
    with app.app_context():
        print("🔧 Fixing Flask-Migrate setup...")
        
        # Remove existing migrations directory if it exists but is broken
        if os.path.exists('migrations') and not os.path.exists('migrations/env.py'):
            print("📁 Removing broken migrations directory...")
            shutil.rmtree('migrations')
        
        # Initialize migrations if directory doesn't exist
        if not os.path.exists('migrations'):
            print("📝 Initializing Flask-Migrate...")
            init()
        
        # Create initial migration
        print("📝 Creating initial migration...")
        migrate(message='Initial migration - create tables')
        
        # Apply migration
        print("📝 Applying migration...")
        upgrade()
        
        print("✅ Migration setup completed successfully!")

if __name__ == '__main__':
    fix_migration()