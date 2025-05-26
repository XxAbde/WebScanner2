#!/usr/bin/env python3
"""
Fix Flask-Migrate initialization with proper error handling
"""
import os
import sys
import shutil

# Add the parent directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from flask_migrate import init, migrate, upgrade
import sqlalchemy

def test_database_permissions():
    """Test if the database user has necessary permissions"""
    app = create_app()
    
    with app.app_context():
        try:
            # Test basic connection
            result = db.engine.execute('SELECT current_user, current_database();')
            user, database = result.fetchone()
            print(f"✅ Connected as user: {user} to database: {database}")
            
            # Test table creation permissions
            db.engine.execute('''
                CREATE TABLE IF NOT EXISTS test_permissions (
                    id SERIAL PRIMARY KEY,
                    test_col TEXT
                );
            ''')
            
            # Test if we can drop the test table
            db.engine.execute('DROP TABLE IF EXISTS test_permissions;')
            
            print("✅ Database permissions are sufficient")
            return True
            
        except Exception as e:
            print(f"❌ Database permission test failed: {e}")
            return False

def fix_migration():
    """Fix migration setup with error handling"""
    app = create_app()
    
    with app.app_context():
        print("🔧 Fixing Flask-Migrate setup...")
        
        # Test permissions first
        if not test_database_permissions():
            print("❌ Insufficient database permissions. Please run:")
            print("   ./scripts/fix_db_permissions.sh")
            print("   or")
            print("   ./scripts/setup_db_complete.sh")
            return False
        
        # Remove existing migrations directory if it exists but is broken
        if os.path.exists('migrations') and not os.path.exists('migrations/env.py'):
            print("📁 Removing broken migrations directory...")
            shutil.rmtree('migrations')
        
        try:
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
            return True
            
        except sqlalchemy.exc.ProgrammingError as e:
            if "permission denied" in str(e).lower():
                print("❌ Permission denied error. Please run:")
                print("   ./scripts/fix_db_permissions.sh")
                print("   or recreate the database with proper permissions:")
                print("   ./scripts/setup_db_complete.sh")
            else:
                print(f"❌ Database error: {e}")
            return False
        except Exception as e:
            print(f"❌ Migration setup failed: {e}")
            return False

if __name__ == '__main__':
    success = fix_migration()
    sys.exit(0 if success else 1)