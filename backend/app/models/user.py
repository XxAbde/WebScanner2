from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from ..extensions import db

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    is_guest = db.Column(db.Boolean, default=False, nullable=False)
    scan_limit = db.Column(db.Integer, default=10, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_login = db.Column(db.DateTime)
    
    def __init__(self, email, username, password, is_guest=False, scan_limit=None):
        self.email = email
        self.username = username
        self.set_password(password)
        self.is_guest = is_guest
        if scan_limit is not None:
            self.scan_limit = scan_limit
        elif is_guest:
            self.scan_limit = 3
        else:
            self.scan_limit = 10
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def get_remaining_scans(self):
        """Get remaining scans for user"""
        if self.is_admin:
            return float('inf')  # Unlimited for admins
        
        # For now, just return scan_limit
        # TODO: Later subtract actual scan count
        return self.scan_limit
    
    def can_scan(self):
        """Check if user can perform a new scan"""
        return self.get_remaining_scans() > 0
    
    def to_dict(self):
        """Convert user to dictionary (excluding sensitive data)"""
        remaining = self.get_remaining_scans()
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'is_guest': self.is_guest,
            'scan_limit': self.scan_limit,
            'is_active': self.is_active,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'remaining_scans': remaining if remaining != float('inf') else 'unlimited'
        }
    
    def __repr__(self):
        return f'<User {self.username}>'