"""
Database configuration for SQLite3
"""
import os
from pathlib import Path

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# SQLite database configuration
class DatabaseConfig:
    """SQLite database configuration"""
    
    # Database file path
    DATABASE_PATH = PROJECT_ROOT / 'findjob.db'
    
    # SQLAlchemy database URI for SQLite
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DATABASE_PATH}'
    
    # SQLAlchemy configuration
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False  # Set to True for SQL debugging
    
    @classmethod
    def get_database_url(cls):
        """Get the database URL for SQLAlchemy"""
        return cls.SQLALCHEMY_DATABASE_URI
    
    @classmethod
    def get_database_path(cls):
        """Get the database file path"""
        return str(cls.DATABASE_PATH)
    
    @classmethod
    def database_exists(cls):
        """Check if the database file exists"""
        return cls.DATABASE_PATH.exists()
    
    @classmethod
    def create_database_directory(cls):
        """Ensure the database directory exists"""
        cls.DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

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