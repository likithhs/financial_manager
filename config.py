import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base application configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default_academic_secret_key_2026')
    FLASK_DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() in ('true', '1', 't')
    PORT = int(os.environ.get('PORT', 5000))
    
    # MySQL Database Config
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_USER = os.environ.get('DB_USER', 'root')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
    DB_NAME = os.environ.get('DB_NAME', 'financial_manager')
    DB_PORT = int(os.environ.get('DB_PORT', 3306))
    
    # Stock Service Config
    STOCK_API_KEY = os.environ.get('STOCK_API_KEY', '')
    STOCK_API_PROVIDER = os.environ.get('STOCK_API_PROVIDER', 'demo')
    
    # AI Service Config
    AI_API_KEY = os.environ.get('AI_API_KEY', '')
    AI_MODE = 'api' if AI_API_KEY else 'local_rule_based'
