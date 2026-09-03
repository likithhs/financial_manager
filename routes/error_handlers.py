"""
FinAI Backend Foundation - Centralized Error Handlers
Handles 400, 401, 403, 404, 429, 500, and 503 cleanly for both HTML views and JSON APIs.
Does not expose raw Python stack traces in production responses.
"""

import logging
from flask import render_template, request, jsonify

logger = logging.getLogger(__name__)


def register_error_handlers(app):
    @app.errorhandler(400)
    def bad_request(error):
        logger.warning(f"400 Bad Request on {request.path}: {error}")
        if request.path.startswith('/api/'):
            return jsonify({
                "error": "Bad Request",
                "status_code": 400,
                "message": "The server could not understand the request due to invalid syntax or parameters."
            }), 400
        return render_template(
            'error.html',
            status_code=400,
            title="Bad Request (400)",
            error_message="The request could not be processed due to invalid parameters or malformed syntax."
        ), 400

    @app.errorhandler(401)
    def unauthorized(error):
        logger.warning(f"401 Unauthorized on {request.path}")
        if request.path.startswith('/api/'):
            return jsonify({
                "error": "Unauthorized",
                "status_code": 401,
                "message": "Authentication credentials required to access this resource."
            }), 401
        return render_template(
            'error.html',
            status_code=401,
            title="Unauthorized (401)",
            error_message="Please log in with an active account to access this financial dashboard."
        ), 401

    @app.errorhandler(403)
    def forbidden(error):
        logger.warning(f"403 Forbidden on {request.path}")
        if request.path.startswith('/api/'):
            return jsonify({
                "error": "Forbidden",
                "status_code": 403,
                "message": "You do not have permission to access this resource."
            }), 403
        return render_template(
            'error.html',
            status_code=403,
            title="Access Restricted (403)",
            error_message="Elevated administrator privileges are required to access this operator console."
        ), 403

    @app.errorhandler(404)
    def not_found(error):
        logger.info(f"404 Not Found: {request.path}")
        if request.path.startswith('/api/'):
            return jsonify({
                "error": "Not Found",
                "status_code": 404,
                "message": "The requested API endpoint does not exist."
            }), 404
        return render_template(
            'error.html',
            status_code=404,
            title="Page Not Found (404)",
            error_message="The requested page could not be located. It may have moved or been updated."
        ), 404

    @app.errorhandler(429)
    def too_many_requests(error):
        logger.warning(f"429 Too Many Requests on {request.path}")
        if request.path.startswith('/api/'):
            return jsonify({
                "error": "Too Many Requests",
                "status_code": 429,
                "message": "Server is receiving high traffic volume. Please slow down and try again shortly."
            }), 429
        return render_template(
            'error.html',
            status_code=429,
            title="Server Busy / High Traffic (429)",
            error_message="The FinAI server is experiencing elevated request traffic. Please wait a moment and refresh."
        ), 429

    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"500 Internal Server Error on {request.path}: {error}", exc_info=True)
        if request.path.startswith('/api/'):
            return jsonify({
                "error": "Internal Server Error",
                "status_code": 500,
                "message": "An unexpected server fault occurred. Engineering team has been alerted."
            }), 500
        return render_template(
            'error.html',
            status_code=500,
            title="Internal Server Error (500)",
            error_message="An unexpected server fault occurred. Our automated telemetry has logged the event."
        ), 500

    @app.errorhandler(503)
    def service_unavailable(error):
        logger.warning(f"503 Service Unavailable / Server Busy on {request.path}")
        if request.path.startswith('/api/'):
            return jsonify({
                "error": "Service Unavailable",
                "status_code": 503,
                "message": "Server is temporarily busy or undergoing scheduled maintenance. Please retry in a few seconds."
            }), 503
        return render_template(
            'error.html',
            status_code=503,
            title="Server Temporarily Busy (503)",
            error_message="The FinAI database or computing cluster is temporarily busy under heavy workload. Please retry in a few moments."
        ), 503
