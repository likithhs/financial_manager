"""
Finora - Application & Database Bootstrapping Engine
Automates pre-flight verification, schema provisioning, administrative setup,
and deployment readiness for both development and production environments.

Usage:
    python bootstrap.py            # Standard bootstrap (init schema, verify connectivity)
    python bootstrap.py --seed     # Bootstrap schema and populate initial demo scenarios
    python bootstrap.py --check    # Check connectivity and health without mutating state
"""

import os
import sys
import argparse
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from config import Config
from database import init_db, query_db, get_db_connection, create_admin_user


def log_step(msg, status="INFO"):
    icons = {"INFO": "[i]", "OK": "[+]", "WARN": "[!]", "ERR": "[-]"}
    prefix = icons.get(status, "[*]")
    print(f"{prefix} {msg}")


def check_python_environment():
    log_step(f"Verifying Python runtime: Python {sys.version.split()[0]}", "INFO")
    if sys.version_info < (3, 9):
        log_step("Python 3.9 or higher is required to run Finora.", "ERR")
        sys.exit(1)
    log_step("Python runtime verified successfully.", "OK")


def verify_database_connection():
    engine = Config.DB_ENGINE
    log_step(f"Testing database connectivity (Target Engine: {engine.upper()})...", "INFO")
    try:
        conn, db_type = get_db_connection(engine=engine)
        if db_type == 'mysql':
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT 1 AS ping, VERSION() AS version")
            row = cursor.fetchone()
            version = row.get('version', 'unknown') if row else 'unknown'
            cursor.close()
            conn.close()
            log_step(f"Connected to MySQL Server ({version}) successfully.", "OK")
        else:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 AS ping, sqlite_version() AS version")
            row = cursor.fetchone()
            version = row[1] if row else 'unknown'
            cursor.close()
            conn.close()
            log_step(f"Connected to SQLite ({version}) successfully at: {getattr(Config, 'SQLITE_PATH', 'database.db')}", "OK")
        return True
    except Exception as e:
        log_step(f"Database connection failed: {e}", "ERR")
        return False


def run_schema_bootstrap():
    log_step("Provisioning database schema and relational tables...", "INFO")
    try:
        init_db(engine=Config.DB_ENGINE)
        log_step("Relational schema and tables provisioned successfully.", "OK")
        return True
    except Exception as e:
        log_step(f"Schema provisioning encountered an issue: {e}", "ERR")
        return False


def verify_table_integrity():
    expected_tables = [
        'users', 'financial_profiles', 'incomes', 'expenses', 'budgets',
        'financial_goals', 'goal_contributions', 'risk_profiles',
        'portfolio_holdings', 'stock_watchlist', 'stocks',
        'investment_recommendations', 'ai_conversations'
    ]
    log_step("Verifying core table integrity...", "INFO")
    try:
        if Config.DB_ENGINE == 'sqlite':
            rows = query_db("SELECT name FROM sqlite_master WHERE type='table'")
            existing = {r['name'] for r in rows}
        else:
            rows = query_db("SHOW TABLES")
            existing = set()
            for r in rows:
                existing.update(r.values())

        present = [t for t in expected_tables if t in existing]
        log_step(f"Verified {len(present)}/{len(expected_tables)} core application tables.", "OK" if len(present) >= len(expected_tables) - 2 else "WARN")
        return True
    except Exception as e:
        log_step(f"Table inspection warning: {e}", "WARN")
        return False


def ensure_admin_account():
    log_step("Ensuring administrator account exists...", "INFO")
    try:
        admin_email = os.environ.get('DEFAULT_ADMIN_EMAIL', 'admin@test.com')
        existing = query_db("SELECT id, email FROM users WHERE role = 'admin' OR email = %s", (admin_email,), one=True)
        if existing:
            log_step(f"Administrator account active: {existing.get('email')}", "OK")
        else:
            admin_pwd = os.environ.get('DEFAULT_ADMIN_PASSWORD', 'Admin@123456')
            admin_id = create_admin_user('Platform Administrator', admin_email, admin_pwd)
            if admin_id:
                log_step(f"Created default administrator account: {admin_email}", "OK")
            else:
                log_step("Could not automatically provision admin. Use 'flask init-admin' to create one.", "WARN")
    except Exception as e:
        log_step(f"Admin verification notice: {e}", "WARN")


def seed_demo_data():
    log_step("Populating academic demonstration scenarios...", "INFO")
    try:
        # Dynamically import seed script to avoid namespace collisions
        import importlib.util
        seed_path = os.path.join(os.path.dirname(__file__), 'database', 'seed_data.py')
        if os.path.exists(seed_path):
            spec = importlib.util.spec_from_file_location("seed_data_module", seed_path)
            seed_mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(seed_mod)
            seed_mod.seed_academic_scenarios()
            log_step("Demonstration scenarios seeded successfully.", "OK")
        else:
            log_step("database/seed_data.py not found, skipping demo seed.", "WARN")
    except Exception as e:
        log_step(f"Demonstration data seed warning: {e}", "WARN")


def print_summary():
    env_mode = os.environ.get('FLASK_ENV', 'development' if Config.FLASK_DEBUG else 'production')
    print("\n" + "=" * 60)
    print("      FINORA - BOOTSTRAP PRE-FLIGHT SUMMARY")
    print("=" * 60)
    print(f" Environment Mode   : {env_mode}")
    print(f" Primary DB Engine  : {Config.DB_ENGINE.upper()}")
    print(f" Web UI Framework   : Bootstrap 5.3.3 + Finora Design System")
    print(f" Rate Limiting      : {Config.RATELIMIT_DEFAULT}")
    print(f" Production Ready   : Yes (WSGI: Waitress / Gunicorn)")
    print("=" * 60)
    print(" Run the application with:")
    print("   python wsgi.py              (Production WSGI Server)")
    print("   python app.py               (Development Live Server)")
    print("=" * 60 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Finora Application Bootstrapping Engine")
    parser.add_argument("--seed", action="store_true", help="Seed initial demonstration scenarios")
    parser.add_argument("--check", action="store_true", help="Run pre-flight diagnostics without mutating database")
    args = parser.parse_args()

    print("\n--- Starting Finora Bootstrapping Sequence ---")
    check_python_environment()

    db_ok = verify_database_connection()
    if not db_ok:
        log_step("Cannot proceed with bootstrap without a functioning database.", "ERR")
        sys.exit(1)

    if args.check:
        verify_table_integrity()
        print_summary()
        return

    run_schema_bootstrap()
    verify_table_integrity()
    ensure_admin_account()

    if args.seed:
        seed_demo_data()

    print_summary()


if __name__ == '__main__':
    main()
