import os
import sys
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def _get_secret_key():
    """
    Retrieves the Flask SECRET_KEY from environment.
    Fails safely with a clear configuration error if the secret is missing.
    In automated testing environments, uses an ephemeral key.
    """
    key = os.environ.get('SECRET_KEY', '').strip()
    if key:
        return key

    # If running inside an automated test suite or testing environment
    is_testing = (
        os.environ.get('TESTING', 'False').lower() in ('true', '1', 't') or
        'unittest' in sys.modules or
        'pytest' in sys.modules or
        any('test' in arg for arg in sys.argv)
    )
    if is_testing:
        return 'testing-ephemeral-secret-key-32-chars-long-min'

    # Missing SECRET_KEY in runtime: fail immediately with clear instructions
    raise RuntimeError(
        "\n" + "=" * 72 + "\n"
        "CRITICAL SECURITY CONFIGURATION ERROR: SECRET_KEY is not configured!\n"
        "A cryptographically strong SECRET_KEY is required to sign session cookies\n"
        "and prevent session tampering, credential forgery, and privilege escalation.\n\n"
        "HOW TO RESOLVE:\n"
        "1. Generate a secure 32-byte secret key using Python:\n"
        "   python -c \"import secrets; print(secrets.token_hex(32))\"\n\n"
        "2. Add the generated key to your local .env file:\n"
        "   SECRET_KEY=<your_generated_secret_key>\n"
        + "=" * 72 + "\n"
    )

def _get_flask_debug():
    """
    Enforces debug security:
    - Debug mode is FALSE by default.
    - If FLASK_ENV == 'production', debug mode is strictly forbidden.
    """
    env = os.environ.get('FLASK_ENV', 'production').strip().lower()
    raw_debug = os.environ.get('FLASK_DEBUG', 'False').strip().lower()
    debug_requested = raw_debug in ('true', '1', 't')

    if env == 'production' and debug_requested:
        # Prevent accidental production debug exposure
        return False
    return debug_requested

def _get_session_cookie_secure():
    """
    Determines if session cookies should have the 'Secure' flag.
    - True if explicitly set via SESSION_COOKIE_SECURE ('true'/'1').
    - False if explicitly set via SESSION_COOKIE_SECURE ('false'/'0').
    - True if FLASK_ENV == 'production' AND ENABLE_HTTPS is enabled.
    - Defaults to False for local HTTP development.
    """
    raw_secure = os.environ.get('SESSION_COOKIE_SECURE', '').strip().lower()
    if raw_secure in ('true', '1', 't'):
        return True
    if raw_secure in ('false', '0', 'f'):
        return False
    
    is_prod = os.environ.get('FLASK_ENV', 'development').strip().lower() == 'production'
    is_https = os.environ.get('ENABLE_HTTPS', 'False').strip().lower() in ('true', '1', 't')
    return is_prod and is_https

class Config:
    """Base application configuration."""
    SECRET_KEY = _get_secret_key()
    FLASK_DEBUG = _get_flask_debug()
    FLASK_HOST = os.environ.get('FLASK_HOST', '127.0.0.1').strip()
    PORT = int(os.environ.get('PORT', 5000))

    # Browser Session Cookie Security
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = _get_session_cookie_secure()
    PERMANENT_SESSION_LIFETIME = timedelta(hours=int(os.environ.get('SESSION_LIFETIME_HOURS', 12)))
    SESSION_REFRESH_EACH_REQUEST = True

    # Flask-WTF CSRF Protection
    WTF_CSRF_ENABLED = os.environ.get('WTF_CSRF_ENABLED', 'True').strip().lower() in ('true', '1', 't')
    WTF_CSRF_TIME_LIMIT = int(os.environ.get('WTF_CSRF_TIME_LIMIT', 14400))  # 4 hours
    WTF_CSRF_CHECK_DEFAULT = True

    # Rate Limiting Configuration
    RATELIMIT_STORAGE_URI = os.environ.get('RATELIMIT_STORAGE_URI', 'memory://').strip()
    RATELIMIT_STRATEGY = 'fixed-window'
    RATELIMIT_DEFAULT = os.environ.get('RATELIMIT_DEFAULT', '200 per day; 60 per hour')

    
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
