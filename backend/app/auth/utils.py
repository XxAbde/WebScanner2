import re
import secrets
import string
from datetime import datetime

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
    
    # Optional: Special characters
    # if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
    #     errors.append('Password must contain at least one special character')
    
    return errors

def generate_guest_credentials():
    """Generate random credentials for guest users"""
    timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
    random_suffix = ''.join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(6))
    
    username = f"guest_{timestamp}_{random_suffix}"
    email = f"{username}@guest.vulnscanner.local"
    password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
    
    return email, username, password

def is_safe_url(url):
    """Check if URL is safe to scan (basic validation)"""
    # Implement your URL safety checks here
    # For now, basic validation
    if not url:
        return False
    
    # Block localhost and private IPs for security
    blocked_patterns = [
        r'localhost',
        r'127\.0\.0\.1',
        r'192\.168\.',
        r'10\.',
        r'172\.(1[6-9]|2[0-9]|3[0-1])\.'
    ]
    
    for pattern in blocked_patterns:
        if re.search(pattern, url.lower()):
            return False
    
    return True

def get_user_permissions(user):
    """Get user permissions based on user type"""
    permissions = {
        'can_scan': user.can_scan(),
        'can_create_reports': not user.is_guest,
        'can_save_scans': not user.is_guest,
        'can_schedule_scans': not user.is_guest and not user.is_guest,
        'scan_limit': user.scan_limit,
        'remaining_scans': user.get_remaining_scans(),
        'is_admin': user.is_admin
    }
    
    return permissions