#!/usr/bin/env python3
"""
Database initialization script
"""
import sys
import os

# Add the parent directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import User, Scan, ScanResult

def init_database():
    """Initialize the database with tables"""
    app = create_app()
    
    with app.app_context():
        print("Creating database tables...")
        
        # Drop all tables (careful in production!)
        db.drop_all()
        
        # Create all tables
        db.create_all()
        
        print("✅ Database tables created successfully!")
        
        # Create indexes for better performance
        try:
            db.engine.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);')
            db.engine.execute('CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);')
            db.engine.execute('CREATE INDEX IF NOT EXISTS idx_scans_user_id ON scans(user_id);')
            db.engine.execute('CREATE INDEX IF NOT EXISTS idx_scans_status ON scans(status);')
            db.engine.execute('CREATE INDEX IF NOT EXISTS idx_scans_created_at ON scans(created_at);')
            db.engine.execute('CREATE INDEX IF NOT EXISTS idx_scan_results_scan_id ON scan_results(scan_id);')
            db.engine.execute('CREATE INDEX IF NOT EXISTS idx_scan_results_tool_name ON scan_results(tool_name);')
            print("✅ Database indexes created successfully!")
        except Exception as e:
            print(f"⚠️  Warning: Could not create indexes: {e}")

if __name__ == '__main__':
    init_database()