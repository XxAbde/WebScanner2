#!/usr/bin/env python3
"""
Seed database with sample data for development
"""
import sys
import os
from datetime import datetime, timedelta

# Add the parent directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import User, Scan, ScanResult

def seed_database():
    """Seed database with sample data"""
    app = create_app()
    
    with app.app_context():
        print("=== Seeding Database ===")
        
        # Create sample users
        users_data = [
            {'email': 'demo@example.com', 'username': 'demo_user', 'password': 'demo123456'},
            {'email': 'guest@example.com', 'username': 'guest_user', 'password': 'guest123456', 'is_guest': True},
            {'email': 'john@example.com', 'username': 'john_doe', 'password': 'john123456'}
        ]
        
        created_users = []
        for user_data in users_data:
            # Check if user exists
            existing_user = User.query.filter_by(email=user_data['email']).first()
            if not existing_user:
                user = User(
                    email=user_data['email'],
                    username=user_data['username'],
                    password=user_data['password'],
                    is_guest=user_data.get('is_guest', False)
                )
                db.session.add(user)
                created_users.append(user)
                print(f"✅ Created user: {user.username}")
            else:
                created_users.append(existing_user)
                print(f"ℹ️  User already exists: {existing_user.username}")
        
        db.session.commit()
        
        # Create sample scans
        if created_users:
            sample_scans = [
                {
                    'user': created_users[0],
                    'target_url': 'https://example.com',
                    'status': 'completed',
                    'scan_type': 'full'
                },
                {
                    'user': created_users[0],
                    'target_url': 'https://test.com',
                    'status': 'running',
                    'scan_type': 'quick'
                },
                {
                    'user': created_users[1] if len(created_users) > 1 else created_users[0],
                    'target_url': 'https://demo.com',
                    'status': 'failed',
                    'scan_type': 'full'
                }
            ]
            
            for i, scan_data in enumerate(sample_scans):
                scan = Scan(
                    user_id=scan_data['user'].id,
                    target_url=scan_data['target_url'],
                    scan_type=scan_data['scan_type']
                )
                scan.status = scan_data['status']
                scan.created_at = datetime.utcnow() - timedelta(days=i)
                
                if scan_data['status'] in ['completed', 'failed']:
                    scan.started_at = scan.created_at + timedelta(minutes=1)
                    scan.finished_at = scan.started_at + timedelta(minutes=5)
                elif scan_data['status'] == 'running':
                    scan.started_at = scan.created_at + timedelta(minutes=1)
                
                if scan_data['status'] == 'failed':
                    scan.error_message = "Network timeout occurred"
                
                db.session.add(scan)
                print(f"✅ Created scan: {scan.target_url} ({scan.status})")
        
        db.session.commit()
        
        # Create sample scan results for completed scans
        completed_scans = Scan.query.filter_by(status='completed').all()
        for scan in completed_scans:
            # Sample nmap result
            nmap_result = ScanResult(
                scan_id=scan.id,
                tool_name='nmap',
                tool_version='7.94',
                raw_data={
                    'ports': [
                        {'port': 22, 'state': 'open', 'service': 'ssh'},
                        {'port': 80, 'state': 'open', 'service': 'http'},
                        {'port': 443, 'state': 'open', 'service': 'https'}
                    ],
                    'os': 'Linux 3.X'
                },
                processing_time=2.5
            )
            nmap_result.ai_analysis = {
                'has_vulnerabilities': True,
                'vulnerability': 'Open SSH Port',
                'severity': 'medium',
                'description': 'SSH port is open and accessible',
                'solution': 'Ensure SSH is properly configured with key-based auth'
            }
            
            # Sample nikto result
            nikto_result = ScanResult(
                scan_id=scan.id,
                tool_name='nikto',
                tool_version='2.5.0',
                raw_data={
                    'findings': [
                        {'message': 'X-XSS-Protection header not set', 'severity': 'Medium'},
                        {'message': 'Server version disclosure', 'severity': 'Low'}
                    ]
                },
                processing_time=15.3
            )
            nikto_result.ai_analysis = {
                'has_vulnerabilities': True,
                'vulnerability': 'Missing Security Headers',
                'severity': 'medium',
                'description': 'Security headers are missing',
                'solution': 'Add X-XSS-Protection and other security headers'
            }
            
            db.session.add(nmap_result)
            db.session.add(nikto_result)
            print(f"✅ Created results for scan: {scan.id}")
        
        db.session.commit()
        print("✅ Database seeded successfully!")

if __name__ == '__main__':
    seed_database()