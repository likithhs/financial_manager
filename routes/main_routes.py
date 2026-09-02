"""
FinAI Backend Foundation - Main Routes Blueprint
Handles public entrypoint (/) and system health check (/health).
"""

from flask import Blueprint, render_template, redirect, url_for, session, jsonify
from database import query_db

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Landing page route."""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')


@main_bp.route('/health', methods=['GET'])
def health_check():
    """
    Application & Database Health Verification Endpoint.
    Returns status: ok if application and database connection are operational.
    Does not expose sensitive credentials.
    """
    db_status = "disconnected"
    try:
        res = query_db("SELECT 1 as ping", one=True)
        if res and res.get('ping') == 1:
            db_status = "connected"
    except Exception:
        db_status = "error"

    return jsonify({
        "status": "ok" if db_status == "connected" else "degraded",
        "service": "FinAI Financial Manager",
        "database": db_status
    }), 200 if db_status == "connected" else 503
