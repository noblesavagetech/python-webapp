import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'railway-production-secret-key-2025')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'railway-jwt-secret-key-2025')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Database - Railway automatically sets DATABASE_URL for PostgreSQL
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///financial_health.db')
    
    # Wave Apps OAuth - Set defaults to prevent crashes, user must configure
    WAVE_CLIENT_ID = os.getenv('WAVE_CLIENT_ID', 'dummy-client-id')
    WAVE_CLIENT_SECRET = os.getenv('WAVE_CLIENT_SECRET', 'dummy-client-secret')
    # Dynamic redirect URI based on Railway domain
    railway_domain = os.getenv('RAILWAY_STATIC_URL', 'http://localhost:5000')
    WAVE_REDIRECT_URI = os.getenv('WAVE_REDIRECT_URI', f'{railway_domain}/api/wave/callback')
    WAVE_AUTHORIZATION_URL = os.getenv('WAVE_AUTHORIZATION_URL', 'https://api.waveapps.com/oauth2/authorize/')
    WAVE_TOKEN_URL = os.getenv('WAVE_TOKEN_URL', 'https://api.waveapps.com/oauth2/token/')
    WAVE_API_URL = os.getenv('WAVE_API_URL', 'https://gql.waveapps.com/graphql/public')
    
    # Data Warehouse - Use same DB as main app for simplicity
    DW_HOST = os.getenv('DW_HOST', os.getenv('PGHOST', 'localhost'))
    DW_PORT = os.getenv('DW_PORT', os.getenv('PGPORT', '5432'))
    DW_DATABASE = os.getenv('DW_DATABASE', os.getenv('PGDATABASE', 'financial_dw'))
    DW_USER = os.getenv('DW_USER', os.getenv('PGUSER', 'dw_user'))
    DW_PASSWORD = os.getenv('DW_PASSWORD', os.getenv('PGPASSWORD', 'dw_password'))
    
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
