from flask import Blueprint

# Create the auth blueprint
auth_bp = Blueprint('auth', __name__)

# Import routes after blueprint creation to avoid circular imports
from . import routes