import os
from datetime import timedelta
from urllib.parse import urlparse
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True
    WTF_CSRF_SECRET_KEY = os.environ.get('WTF_CSRF_SECRET_KEY') or 'csrf-secret-key-change-in-production'
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.googlemail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', '587'))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=60)
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        print("Running in Development mode with SQLite database")

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # Ensure DATABASE_URL is set in production
        if not cls.SQLALCHEMY_DATABASE_URI:
            raise ValueError("DATABASE_URL environment variable is required in production")
        
        # Parse DATABASE_URL to ensure it's PostgreSQL
        db_url = urlparse(cls.SQLALCHEMY_DATABASE_URI)
        if db_url.scheme != 'postgresql':
            raise ValueError("Production database must be PostgreSQL")
        
        print("Running in Production mode with PostgreSQL database")
        
        # Log to stderr
        import logging
        from logging import StreamHandler
        file_handler = StreamHandler()
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite:///:memory:'

def get_config():
    env = os.environ.get('FLASK_ENV', 'development')
    print(f"Current environment: {env}")
    
    if env == 'production':
        return 'production'
    elif env == 'testing':
        return 'testing'
    return 'development'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
} 