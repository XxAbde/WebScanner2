from flask import Blueprint
from flask_restx import Api
from .users import users_ns
from .scans import scans_ns
from .reports import reports_ns

# Create a Blueprint for the API
api_bp = Blueprint('api', __name__, url_prefix='/api/v1')

# Create an API instance
api = Api(
    api_bp,
    title='Vulnerability Scanner API',
    version='1.0',
    description='A comprehensive vulnerability scanning API',
    doc='/docs/'  # Swagger documentation endpoint
)

# Add namespaces
api.add_namespace(users_ns, path='/users')  # Namespace for user authentication and management
api.add_namespace(scans_ns, path='/scans')  # Namespace for scan-related operations
api.add_namespace(reports_ns, path='/reports')  # Namespace for report management

# Optional: Add other namespaces as needed
# Example:
# from .test import test_ns
# api.add_namespace(test_ns, path='/test')