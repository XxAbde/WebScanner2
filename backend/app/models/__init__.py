from ..extensions import db

# Import all models to ensure they're registered
from .user import User
from .scan import Scan, ScanResult

__all__ = ['db', 'User', 'Scan', 'ScanResult']