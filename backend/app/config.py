import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key-change-in-production'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # Database - Use SQLite for development
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///vulnscanner.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Celery
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL') or 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND') or 'redis://localhost:6379/0'
    
    # Mail
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.sendgrid.net'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or 'noreply@vulnscanner.com'
    
    # AI APIs
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    HUGGINGFACE_API_KEY = os.environ.get('HUGGINGFACE_API_KEY')
    
    # Rate Limiting - Use Redis if available, memory otherwise
    RATELIMIT_STORAGE_URI = os.environ.get('RATELIMIT_STORAGE_URI') or 'memory://'
    
    # Scan Settings
    SCAN_TIMEOUT = 300  # 5 minutes
    GUEST_SCAN_LIMIT = 3
    USER_SCAN_LIMIT = 10

class DevelopmentConfig(Config):
    DEBUG = True
    FLASK_ENV = 'development'
    # Use SQLite for easy development
    SQLALCHEMY_DATABASE_URI = 'sqlite:///vulnscanner_dev.db'

class ProductionConfig(Config):
    DEBUG = False
    FLASK_ENV = 'production'
    SECRET_KEY = os.environ.get('SECRET_KEY')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    # For production, use PostgreSQL (we'll fix this later)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql://vulnuser:changeme@localhost/vulnscanner'

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    RATELIMIT_STORAGE_URI = 'memory://'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}