"""
FinAI Backend Foundation - Centralized Error Handlers
Handles 400, 401, 403, 404, and 500 cleanly for both HTML views and JSON APIs.
Does not expose raw Python stack traces in production responses.
"""

import logging
from flask import render_template, request, jsonify

logger = logging.getLogger(__name__)


def register_error_handlers(app):
    @app.errorhandler(400)
    def bad_request(error):
        logger.warning(f"400 Bad Request: {request.path}")
        if request.path.startswith('/api/'):
            return jsonify({"error": "Bad Request", "message": str(error)}), 400
        return render_template('error.html', status_code=400, title="Bad Request", error_message="The server could not understand the request."), 400

    @app.errorhandler(401)
    def unauthorized(error):
        logger.warning(f"401 Unauthorized: {request.path}")
        if request.path.startswith('/api/'):
            return jsonify({"error": "Unauthorized", "message": "Authentication required."}), 401
        return render_template('error.html', status_code=401, title="Unauthorized", error_message="Please log in to access this resource."), 401

    @app.errorhandler(403)
    def forbidden(error):
        logger.warning(f"403 Forbidden: {request.path}")
        if request.path.startswith('/api/'):
            return jsonify({"error": "Forbidden", "message": "You do not have permission to access this resource."}), 403
        return render_template('error.html', status_code=403, title="Access Denied", error_message="Administrator privileges required to access this resource."), 403

    @app.errorhandler(404)
    def not_found(error):
        logger.info(f"404 Not Found: {request.path}")
        if request.path.startswith('/api/'):
            return jsonify({"error": "Not Found", "message": "Requested endpoint does not exist."}), 404
        return render_template('error.html', status_code=404, title="Page Not Found", error_message="The requested URL was not found on this server."), 404

    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"500 Internal Server Error on {request.path}: {error}", exc_info=True)
        if request.path.startswith('/api/'):
            return jsonify({"error": "Internal Server Error", "message": "An unexpected server error occurred."}), 500
        return render_template('error.html', status_code=500, title="Internal Server Error", error_message="An unexpected server error occurred. Our team has been notified."), 500

