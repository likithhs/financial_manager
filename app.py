"""
FinAI - AI-Powered Personal Financial Manager & Investment Recommendation System
Core Flask Application Factory & Module Orchestrator
"""

import os
import sys
import logging
import click
from flask import Flask, redirect, url_for, session
from config import Config
from database import init_db, query_db, create_admin_user
from extensions import csrf, limiter
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

    # Initialize Security Extensions (CSRF Protection & Rate Limiting)
    csrf.init_app(app)
    limiter.init_app(app)

    logger.info("Initializing FinAI Flask Application...")

    # Initialize database tables and seed data
    with app.app_context():
        try:
            init_db()
            logger.info(f"{Config.DB_ENGINE.upper()} Database initialized and verified successfully.")
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

    @app.context_processor
    def inject_user_context():
        """
        Inject currently authenticated user profile dynamically into all templates.
        Ensures strict tenant data isolation (queries only the current session user_id).
        """
        user_id = session.get('user_id')
        if not user_id:
            return {'current_user': None}
        try:
            user = query_db(
                "SELECT id, name, email, phone, address, role, age, occupation, financial_exp, investment_exp, created_at, updated_at FROM users WHERE id = %s",
                (user_id,),
                one=True
            )
            if user:
                created = user.get('created_at')
                if hasattr(created, 'strftime'):
                    user['joined_date'] = created.strftime('%b %d, %Y')
                elif isinstance(created, str) and len(created) >= 10:
                    try:
                        from datetime import datetime
                        dt = datetime.strptime(created[:10], '%Y-%m-%d')
                        user['joined_date'] = dt.strftime('%b %d, %Y')
                    except Exception:
                        user['joined_date'] = created[:10]
                else:
                    user['joined_date'] = 'Active Member'
            return {'current_user': user or {}}
        except Exception as err:
            logger.warning(f"Error injecting user context: {err}")
            return {'current_user': {}}

    # Root route alias
    @app.route('/', endpoint='index')
    def index_root():
        if 'user_id' in session:
            if session.get('user_role') == 'admin':
                return redirect(url_for('admin.dashboard'))
            return redirect(url_for('main.home'))
        return main_bp.view_functions.get('landing', main_bp.view_functions.get('index'))()

    @app.route('/dashboard', endpoint='dashboard')
    def dashboard_root():
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        if session.get('user_role') == 'admin':
            return redirect(url_for('admin.dashboard'))
        return dashboard_bp.view_functions['dashboard']()

    return app


app = create_app()

@app.cli.command("init-admin")
@click.option("--email", prompt="Admin Email", help="Administrator email address")
@click.option("--password", prompt="Admin Password", hide_input=True, confirmation_prompt=True, help="Secure administrator password")
@click.option("--name", default="System Administrator", help="Administrator display name")
def init_admin_command(email, password, name):
    """Securely initialize or reset an administrator account."""
    try:
        user_id, is_new = create_admin_user(email, password, name)
        status = "Created new" if is_new else "Updated existing"
        click.echo(f"SUCCESS: {status} administrator account for '{email}' (User ID #{user_id}).")
    except ValueError as val_err:
        click.echo(f"VALIDATION ERROR: {val_err}", err=True)
        sys.exit(1)
    except Exception as err:
        click.echo(f"ADMIN PROVISIONING ERROR: {err}", err=True)
        sys.exit(1)

if __name__ == '__main__':
    # Check if invoked directly with init-admin argument: python app.py init-admin
    if len(sys.argv) > 1 and sys.argv[1] == 'init-admin':
        import getpass
        admin_email = input("Administrator Email: ").strip()
        admin_pass = getpass.getpass("Administrator Password (min 8 chars): ")
        admin_confirm = getpass.getpass("Confirm Password: ")
        if admin_pass != admin_confirm:
            print("ERROR: Passwords do not match.")
            sys.exit(1)
        admin_name = input("Administrator Name [System Administrator]: ").strip() or "System Administrator"
        try:
            uid, created = create_admin_user(admin_email, admin_pass, admin_name)
            print(f"SUCCESS: {'Created new' if created else 'Updated existing'} administrator account for '{admin_email}' (User ID #{uid}).")
        except Exception as e:
            print(f"ERROR: {e}")
            sys.exit(1)
        sys.exit(0)

    host = Config.FLASK_HOST
    port = Config.PORT
    debug = Config.FLASK_DEBUG
    logger.info(f"Starting FinAI on http://{host}:{port} (Debug: {debug})")
    app.run(host=host, port=port, debug=debug)
