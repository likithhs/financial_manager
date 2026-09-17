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
    
    # AI Service Multi-Provider Config (Gemini, OpenAI, Groq, Local)
    AI_PROVIDER = os.environ.get('AI_PROVIDER', '').strip().lower()
    AI_API_KEY = (
        os.environ.get('AI_API_KEY', '') or 
        os.environ.get('GEMINI_API_KEY', '') or 
        os.environ.get('OPENAI_API_KEY', '') or 
        os.environ.get('GROQ_API_KEY', '')
    ).strip()
    AI_MODEL = os.environ.get('AI_MODEL', '').strip()
    
    # Explicit provider API keys if specified individually
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '').strip()
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '').strip()
    GROQ_API_KEY = os.environ.get('GROQ_API_KEY', '').strip()
    
    # Auto-detect provider if not explicitly specified
    if not AI_PROVIDER:
        if GEMINI_API_KEY or (AI_API_KEY and AI_API_KEY.startswith('AIza')):
            AI_PROVIDER = 'gemini'
        elif OPENAI_API_KEY or (AI_API_KEY and AI_API_KEY.startswith('sk-')):
            AI_PROVIDER = 'openai'
        elif GROQ_API_KEY or (AI_API_KEY and AI_API_KEY.startswith('gsk_')):
            AI_PROVIDER = 'groq'
        elif AI_API_KEY:
            AI_PROVIDER = 'gemini'  # Default to gemini when key provided
        else:
            AI_PROVIDER = 'local'
            
    AI_MODE = 'api' if (AI_API_KEY and AI_PROVIDER != 'local') else 'local_rule_based'
