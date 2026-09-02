"""
FinAI - AI-Powered Personal Financial Manager & Investment Recommendation System
Core Flask Application Factory & Module Orchestrator (Phase 3 Foundation)
"""

import os
import logging
from flask import Flask, redirect, url_for, session
from config import Config
from database import init_db
from routes.error_handlers import register_error_handlers

# Import Modular Blueprints
from routes.main_routes import main_bp
from routes.auth_routes import auth_bp
from routes.dashboard_routes import dashboard_bp
from routes.profile_routes import profile_bp
from routes.income_routes import income_bp
from routes.expense_routes import expense_bp
from routes.goal_routes import goal_bp
from routes.risk_routes import risk_bp
from routes.market_routes import market_bp
from routes.assistant_routes import assistant_bp
from routes.investment_routes import investment_bp
from routes.admin_routes import admin_bp
from routes.api_routes import api_bp

# Preserved Modules for existing templates
from routes.financial_routes import financial_bp
from routes.budget_routes import budget_bp
from routes.analysis_routes import analysis_bp
from routes.stock_routes import stock_bp
from routes.portfolio_routes import portfolio_bp
from routes.ai_routes import ai_bp

# Set up sensible application logging (never logging sensitive credentials)
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

    # Register Core Foundation Blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(income_bp)
    app.register_blueprint(expense_bp)
    app.register_blueprint(goal_bp)
    app.register_blueprint(risk_bp)
    app.register_blueprint(market_bp)
    app.register_blueprint(assistant_bp)
    app.register_blueprint(investment_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)

    # Register Preserved Blueprints for complete template backward compatibility
    app.register_blueprint(financial_bp)
    app.register_blueprint(budget_bp)
    app.register_blueprint(analysis_bp)
    app.register_blueprint(stock_bp)
    app.register_blueprint(portfolio_bp)
    app.register_blueprint(ai_bp)

    # Register Centralized Error Handlers (400, 401, 403, 404, 500)
    register_error_handlers(app)

    # Root route aliases to ensure complete template compatibility
    @app.route('/', endpoint='index')
    def index_root():
        if 'user_id' in session:
            return redirect(url_for('dashboard'))
        return render_template('index.html')

    @app.route('/dashboard', endpoint='dashboard')
    def dashboard_root():
        from routes.dashboard_routes import dashboard as render_dashboard
        return render_dashboard()

    return app


app = create_app()

if __name__ == '__main__':
    logger.info(f"Starting FinAI on port {Config.PORT} (Debug: {Config.FLASK_DEBUG})")
    app.run(host='0.0.0.0', port=Config.PORT, debug=Config.FLASK_DEBUG)
