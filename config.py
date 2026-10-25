import os
import sys
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file (resolved relative to this file)
basedir = os.path.abspath(os.path.dirname(__file__))
env_file = os.path.join(basedir, '.env')
if os.path.exists(env_file):
    load_dotenv(env_file)
else:
    load_dotenv()

import secrets
import logging

logger = logging.getLogger("finora.config")

# Known insecure/predictable default secrets that are strictly prohibited in production
PREDICTABLE_SECRETS = {
    'dev_academic_secret_key_financial_manager_2026',
    'your_generated_cryptographically_secure_32_byte_secret_key_here',
    'generate_with_python_secrets_token_hex_32',
    'your_secret_key_here',
    'secret',
    'secret_key',
    'secretkey',
    'changeme',
    'change-me',
    '123456',
    'password',
    'admin'
}

def _get_secret_key():
    """
    Retrieves and validates the Flask SECRET_KEY from environment variables.
    - Production: Strictly requires an explicit, cryptographically strong, non-predictable SECRET_KEY.
    - Testing: Uses an ephemeral testing secret key if none provided and not in production.
    - Development: If SECRET_KEY is missing, generates a secure ephemeral 32-byte key for the runtime
      session with a clear logger warning to prevent startup crashes while maintaining security.
    """
    key = os.environ.get('SECRET_KEY', '').strip()
    is_prod = os.environ.get('FLASK_ENV', 'development').strip().lower() == 'production'

    # Production checks take strict precedence
    if is_prod:
        if not key:
            raise RuntimeError(
                "\n" + "=" * 72 + "\n"
                "CRITICAL PRODUCTION CONFIGURATION ERROR: SECRET_KEY is not configured!\n"
                "A cryptographically strong SECRET_KEY is required to sign session cookies\n"
                "and prevent session tampering, credential forgery, and privilege escalation.\n\n"
                "HOW TO RESOLVE:\n"
                "1. Generate a secure 32-byte secret key using Python:\n"
                "   python -c \"import secrets; print(secrets.token_hex(32))\"\n\n"
                "2. Add the generated key to your production environment or local .env file:\n"
                "   SECRET_KEY=<your_generated_secret_key>\n"
                + "=" * 72 + "\n"
            )
        if key.lower() in PREDICTABLE_SECRETS or len(key) < 16:
            raise RuntimeError(
                "\n" + "=" * 72 + "\n"
                "CRITICAL PRODUCTION SECURITY CONFIGURATION ERROR:\n"
                "The configured SECRET_KEY is insecure (<16 chars) or matches a known predictable placeholder.\n"
                "A unique cryptographically secure 32-byte secret key is required in production:\n"
                "   python -c \"import secrets; print(secrets.token_hex(32))\"\n"
                + "=" * 72 + "\n"
            )
        return key

    # If running inside an automated test suite or testing environment (non-production)
    is_testing = (
        os.environ.get('TESTING', 'False').lower() in ('true', '1', 't') or
        'unittest' in sys.modules or
        'pytest' in sys.modules or
        any('test' in arg for arg in sys.argv)
    )
    if is_testing:
        return key or 'testing-ephemeral-secret-key-32-chars-long-min'

    if key:
        return key

    # In development/demo environments, generate a dynamic ephemeral secret key to prevent startup failure
    ephemeral_key = secrets.token_hex(32)
    logger.warning(
        "NOTICE: SECRET_KEY is not set in environment or .env. "
        "Generated an ephemeral 32-byte session secret for development runtime. "
        "Sessions will invalidate upon restart. To persist sessions, set SECRET_KEY in your .env file."
    )
    return ephemeral_key

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
    TEMPLATES_AUTO_RELOAD = True

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
    RATELIMIT_STRATEGY = os.environ.get('RATELIMIT_STRATEGY', 'fixed-window').strip()
    RATELIMIT_DEFAULT = os.environ.get('RATELIMIT_DEFAULT', '200 per day; 60 per hour').strip()

    # Database Engine Selection ('mysql' is primary default, 'sqlite' is supported for demo/offline)
    DB_ENGINE = os.environ.get('DB_ENGINE', 'mysql').strip().lower()

    # SQLite Database Config (used when DB_ENGINE=sqlite or in tests)
    SQLITE_PATH = os.environ.get('SQLITE_PATH', os.path.join(basedir, 'database', 'financial_manager.db'))

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
