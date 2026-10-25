"""
Finora - Core Flask Extensions
Centralizes extension singletons for application factory pattern.
"""

from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# CSRF Protection Extension
csrf = CSRFProtect()

# Application-wide Rate Limiter
# Dynamic limits, storage backend, and strategy are loaded directly from app.config
# (RATELIMIT_DEFAULT, RATELIMIT_STORAGE_URI, RATELIMIT_STRATEGY) upon init_app(app).
limiter = Limiter(
    key_func=get_remote_address
)
