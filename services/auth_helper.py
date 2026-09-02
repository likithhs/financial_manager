"""
FinAI Backend Foundation - Authentication & Authorization Helpers
Provides session validation, role enforcement, and current user retrieval.
"""

from functools import wraps
from flask import session, redirect, url_for, flash, request, jsonify


def is_authenticated():
    """Returns True if the current request has an active authenticated user session."""
    return 'user_id' in session and session.get('user_id') is not None


def get_current_user_id():
    """
    Returns the authenticated user's ID from session.
    Never trusts user-supplied input from query params or form bodies.
    """
    return session.get('user_id')


def get_current_user_role():
    """Returns the authenticated user's role from session."""
    return session.get('user_role', 'user')


def is_admin():
    """Returns True if the current user has administrator privileges."""
    return is_authenticated() and get_current_user_role() == 'admin'


def login_required(f):
    """
    Decorator protecting routes requiring an authenticated user session.
    Returns 401 JSON response for API endpoints or redirects to login for HTML views.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_authenticated():
            if request.path.startswith('/api/'):
                return jsonify({"error": "Unauthorized", "message": "Authentication required"}), 401
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)

    return decorated_function


def admin_required(f):
    """
    Decorator protecting administrative routes.
    Restricts access strictly to users with role == 'admin'.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_authenticated():
            if request.path.startswith('/api/'):
                return jsonify({"error": "Unauthorized", "message": "Authentication required"}), 401
            flash('Please log in to access the administrator panel.', 'warning')
            return redirect(url_for('auth.login'))

        if not is_admin():
            if request.path.startswith('/api/'):
                return jsonify({"error": "Forbidden", "message": "Admin privileges required"}), 403
            flash('Access denied: Administrator privileges required.', 'danger')
            return redirect(url_for('dashboard'))

        return f(*args, **kwargs)

    return decorated_function
