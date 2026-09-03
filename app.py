"""
FinAI - AI-Powered Personal Financial Manager & Investment Recommendation System
Core Flask Application Factory & Module Orchestrator
"""

import os
import logging
from flask import Flask, redirect, url_for, session
from config import Config
from database import init_db
from routes.error_handlers import register_error_handlers

# Import Core Feature Blueprints
from routes.main_routes import main_bp
from routes.auth_routes import auth_bp
from routes.dashboard_routes import dashboard_bp
from routes.financial_routes import financial_bp
from routes.budget_routes import budget_bp
from routes.goal_routes import goal_bp
from routes.analysis_routes import analysis_bp
from routes.investment_routes import investment_bp
from routes.stock_routes import stock_bp
from routes.portfolio_routes import portfolio_bp
from routes.ai_routes import ai_bp
from routes.admin_routes import admin_bp
from routes.api_routes import api_bp

# Application logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] in %(module)s: %(message)s'
)
logger = logging.getLogger("finai")


def create_app(config_class=Config):
    """
    Application factory pattern for FinAI Flask backend.
    Loads configuration, initializes MySQL connection, registers blueprints and error handlers.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    logger.info("Initializing FinAI Flask Application...")

    # Initialize database tables and seed data
    with app.app_context():
        try:
            init_db()
            logger.info("MySQL Database initialized and verified successfully.")
        except Exception as e:
            logger.error(f"Database initialization encountered an error: {e}")

    # Register Feature Blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(financial_bp)
    app.register_blueprint(budget_bp)
    app.register_blueprint(goal_bp)
    app.register_blueprint(analysis_bp)
    app.register_blueprint(investment_bp)
    app.register_blueprint(stock_bp)
    app.register_blueprint(portfolio_bp)
    app.register_blueprint(ai_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)

    # Register Centralized Error Handlers (400, 401, 403, 404, 500)
    register_error_handlers(app)

    # Root route alias
    @app.route('/', endpoint='index')
    def index_root():
        if 'user_id' in session:
            if session.get('user_role') == 'admin':
                return redirect(url_for('admin.dashboard'))
            return redirect(url_for('dashboard.dashboard'))
        return main_bp.view_functions['landing']()

    @app.route('/dashboard', endpoint='dashboard')
    def dashboard_root():
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        if session.get('user_role') == 'admin':
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('dashboard.dashboard'))

    return app


app = create_app()

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() in ('true', '1', 't')
    logger.info(f"Starting FinAI on port {port} (Debug: {debug})")
    app.run(host='0.0.0.0', port=port, debug=debug)
