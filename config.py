import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///financial_health.db')
    
    # Wave Apps OAuth
    WAVE_CLIENT_ID = os.getenv('WAVE_CLIENT_ID')
    WAVE_CLIENT_SECRET = os.getenv('WAVE_CLIENT_SECRET')
    WAVE_REDIRECT_URI = os.getenv('WAVE_REDIRECT_URI', 'http://localhost:5000/auth/wave/callback')
    WAVE_AUTHORIZATION_URL = os.getenv('WAVE_AUTHORIZATION_URL', 'https://api.waveapps.com/oauth2/authorize/')
    WAVE_TOKEN_URL = os.getenv('WAVE_TOKEN_URL', 'https://api.waveapps.com/oauth2/token/')
    WAVE_API_URL = os.getenv('WAVE_API_URL', 'https://gql.waveapps.com/graphql/public')
    
    # Data Warehouse
    DW_HOST = os.getenv('DW_HOST', 'localhost')
    DW_PORT = os.getenv('DW_PORT', '5432')
    DW_DATABASE = os.getenv('DW_DATABASE', 'financial_dw')
    DW_USER = os.getenv('DW_USER', 'dw_user')
    DW_PASSWORD = os.getenv('DW_PASSWORD', 'dw_password')
    
    # Frontend
    FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:3000')
    
    # JWT
    JWT_TOKEN_LOCATION = ['headers']
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 hour


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
