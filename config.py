import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    HOST = 'localhost'
    PORT = 5000
    BASE_URL = 'http://localhost:5000'
    
class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    HOST = '0.0.0.0'
    PORT = int(os.environ.get('PORT', 5000))
    BASE_URL = os.environ.get('BASE_URL', 'https://your-domain.com')
    
class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True
    BASE_URL = 'http://localhost:5000'

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}