"""
FinAI - Core Flask Extensions
Centralizes extension singletons for application factory pattern.
"""

from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# CSRF Protection Extension
csrf = CSRFProtect()

# Application-wide Rate Limiter
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri="memory://",
    strategy="fixed-window",
    default_limits=["200 per day", "60 per hour"]
)
