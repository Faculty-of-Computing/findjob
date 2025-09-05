"""
Database configuration for SQLite3 and PostgreSQL
"""
import os
from pathlib import Path
from urllib.parse import urlparse

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# Database configuration
class DatabaseConfig:
    """Database configuration for SQLite and PostgreSQL"""
    
    @classmethod
    def get_database_url(cls):
        """Get the database URL from environment or default to SQLite"""
        return os.environ.get('DATABASE_URL', f'sqlite:///{PROJECT_ROOT / "findjob.db"}')
    
    @classmethod
    def get_database_type(cls):
        """Determine the database type from the URL"""
        url = cls.get_database_url()
        parsed = urlparse(url)
        if parsed.scheme == 'sqlite':
            return 'sqlite'
        elif parsed.scheme == 'postgresql':
            return 'postgresql'
        else:
            return 'unknown'
    
    @classmethod
    def is_sqlite(cls):
        return cls.get_database_type() == 'sqlite'
    
    @classmethod
    def is_postgresql(cls):
        return cls.get_database_type() == 'postgresql'
    
    # SQLAlchemy configuration
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False  # Set to True for SQL debugging

# Environment-specific configurations
class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'bvaIbwm7Ctm2Gf2CZUUfaHU--qYbVUknAEwGcAcP_qs='
    SQLALCHEMY_DATABASE_URI = DatabaseConfig.get_database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_ECHO = True  # Show SQL queries in development

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY')  # Must be set in production

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # In-memory database for testing

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}